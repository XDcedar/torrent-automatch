#!/usr/bin/env python3
# coding=utf8

import argparse
from dataclasses import dataclass, field
from hashlib import sha1
import random
import sys
from pathlib import Path

import torrent_parser


@dataclass
class PieceMeta:
    """记录种子的每个Piece的信息"""

    id: int = 0
    # the piece contains bytes in index range [first_byte, last_byte)
    first_byte: int = 0
    last_byte: int = 0
    hash: str = ""
    in_single_file: bool = False
    first_byte_in_file: int = 0
    last_byte_in_file: int = 0


@dataclass
class DiskFileMeta:
    """记录硬盘中找到的文件的信息"""

    path: Path = field(default_factory=Path)
    length: int = 0


@dataclass
class FileMeta:
    """记录种子中的文件的信息"""

    path: Path = field(default_factory=Path)
    length: int = 0
    first_byte: int = 0
    last_byte: int = 0
    pieces: list[PieceMeta] = field(default_factory=list)
    match_candidates: list[DiskFileMeta] = field(default_factory=list)  # 该 FileMeta 的候选，目前会把所有大小相同的文件加进来
    matches: list[DiskFileMeta] = field(default_factory=list)  # 已确定对应该 FileMeta。不知为何要用list，按理说只会有一个才对


def do_arg_parse():
    parser = argparse.ArgumentParser(description="“浮肿一时爽，一直浮肿一直爽。”")
    parser.add_argument(
        "--src-list",
        type=Path,
        dest="src_list",
        help="specify a textfile, each line contains a folder or file as a potential linking source.",
    )
    parser.add_argument("--torrent", type=Path, dest="torrent", help="the torrent file to work with")
    parser.add_argument("--dst", type=Path, dest="dst", help="the destination directory")
    parser.add_argument("--pieces-to-check", type=int, dest="pieces_to_check", default=10)
    parser.add_argument("--create-symlinks", dest="create_symlinks", action="store_true")
    args = parser.parse_args()
    return args, parser


def parse_files_meta(root_directory_path: Path, files_info: list, piece_hashes: list, piece_length: int):
    """根据种子信息向构建 file_metas 用于记录种子中每个文件对应的 Piece"""
    file_metas = []
    current_byte = 0
    num_pieces = len(piece_hashes)
    piece_id = 0
    current_piece = PieceMeta()
    current_piece.last_byte = 0
    for f in files_info:
        fm = FileMeta(
            path=root_directory_path.joinpath(*f["path"]),
            length=int(f["length"]),
            first_byte=current_byte,
            last_byte=current_byte + int(f["length"]),
        )
        current_byte += fm.length
        file_metas.append(fm)
        if current_piece.last_byte > fm.first_byte:
            fm.pieces.append(current_piece)
        if current_piece.last_byte >= fm.last_byte:
            continue
        # 把所有属于该 FileMeta 的 PieceMeta() 放进来。
        # 如果这个 PieceMeta() 只有一部分属于该 FileMeta，
        # 则直接 break 而不让 piece_id 自增，
        # 以便下一个外层 for 循环把它放到下一个 FileMeta 中去。
        while piece_id < num_pieces:
            current_piece = PieceMeta(
                id=piece_id,
                first_byte=piece_id * piece_length,
                last_byte=piece_id * piece_length + piece_length,
                hash=piece_hashes[piece_id].strip(),
            )
            piece_id += 1
            # 当前 piece_meta 已越过 file_meta 的位置
            if current_piece.first_byte >= fm.last_byte:
                break
            fm.pieces.append(current_piece)
            # 当前 piece_meta 只有一部分处于 file_meta 之中
            if current_piece.last_byte > fm.last_byte:
                break
            current_piece.in_single_file = True
            current_piece.first_byte_in_file = current_piece.first_byte - fm.first_byte
            current_piece.last_byte_in_file = current_piece.last_byte - fm.first_byte
        if piece_id >= num_pieces:
            break
    return file_metas


def parse_disk_file_metas(file_list: list):
    """根据输入的 file_list 读取硬盘中的文件，构建 DiskFileMeta 信息"""
    path_list = map(lambda line: Path(line.strip()).resolve(), file_list)
    res = [DiskFileMeta(path=p, length=p.stat().st_size) for p in path_list]
    return res


def pass1_check_identical(fm: FileMeta, dfm: DiskFileMeta, pieces_to_check: int):
    """如果文件至少包含1个完整的Piece，则调用这个函数可以进行匹配"""
    pieces_in_single_file = [x for x in fm.pieces if x.in_single_file]
    k = min(len(pieces_in_single_file), pieces_to_check)
    sampled_bms = random.sample(pieces_in_single_file, k)
    if not sampled_bms:
        return False
    with open(dfm.path, "rb") as ef:
        for bm in sampled_bms:
            ef.seek(bm.first_byte_in_file)
            hashhex = sha1(ef.read(bm.last_byte_in_file - bm.first_byte_in_file)).hexdigest()
            if hashhex != bm.hash:
                return False
    return True


# this function has side-effect!
def pass2_check_identical(bm, file_metas):
    """文件不包含完整Piece，则调用这个函数进行匹配。这种文件的大小要么<1个Piece，要么横跨两个Piece。"""
    hasher = sha1()
    fm_covered = []
    # 找到所有跟 bm 有交集的 file_meta，
    # 以它们在 file_metas 中的默认顺序依次读取，计算它们拼起来的片段对应的 sha1
    # TODO: 本来应该计算所有顺序组合的情况
    for fm in file_metas:
        if not (fm.first_byte >= bm.last_byte or fm.last_byte <= bm.first_byte):
            if not fm.match_candidates:
                return False
            intersect_first_byte = max(fm.first_byte, bm.first_byte)
            intersect_last_byte = min(fm.last_byte, bm.last_byte)
            # print(intersect_first_byte, intersect_last_byte)
            if intersect_first_byte == fm.first_byte and intersect_last_byte == fm.last_byte:
                fm_covered.append(fm)
            intersect_first_byte_in_file = intersect_first_byte - fm.first_byte
            intersect_last_byte_in_file = intersect_last_byte - fm.first_byte
            # TODO: should enumerate over all possible combinations
            dfm = fm.match_candidates[0]
            with open(dfm.path, "rb") as ef:
                ef.seek(intersect_first_byte_in_file)
                hasher.update(ef.read(intersect_last_byte_in_file - intersect_first_byte_in_file))
    hash = hasher.hexdigest()
    if hash == bm.hash:
        for fm in fm_covered:
            if not fm.matches:
                fm.matches.append(fm.match_candidates[0])
        return True
    return False


if __name__ == "__main__":
    args, parser = do_arg_parse()
    file_metas = []

    try:
        args.dst = args.dst.resolve()
    except Exception as e:
        print(e, file=sys.stderr)
        print("Wrong destination path!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        data = torrent_parser.parse_torrent_file(args.torrent)
        piece_length = int(data["info"]["piece length"])
        file_metas = parse_files_meta(
            args.dst / data["info"]["name"], data["info"]["files"], data["info"]["pieces"], piece_length
        )
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read the torrent file, or it is not a multiple-file torrent!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        file_list = args.src_list.read_text(encoding="utf8").splitlines()
        disk_file_metas = parse_disk_file_metas(file_list)
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read disk files (or the list)!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        # pass 1, find matchings by pieces completely contained in a file
        pieces_to_check = args.pieces_to_check
        for fm in file_metas:
            # just proceed in the brute-force way
            for dfm in disk_file_metas:
                if fm.length != dfm.length:
                    continue
                fm.match_candidates.append(dfm)
                if pass1_check_identical(fm, dfm, pieces_to_check):
                    fm.matches.append(dfm)

        # t1 = []
        # for fm in file_metas:
        #     if fm.matches:
        #         t1.append(fm)

        # pass 2, try to match some files, each contained in a whole piece
        for fm in file_metas:
            if len(fm.pieces) == 1 and not fm.matches:
                pass2_check_identical(fm.pieces[0], file_metas)

        # also, it may be the case where a file is covered by two pieces
        for fm in file_metas:
            if (
                not fm.matches
                and len(fm.pieces) == 2
                and pass2_check_identical(fm.pieces[0], file_metas)
                and pass2_check_identical(fm.pieces[1], file_metas)
            ):
                fm.matches.append(fm.match_candidates[0])

        # t2 = []
        # for fm in file_metas:
        #     if fm.matches:
        #         t2.append(fm)

    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read some data pieces!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    num_linked = 0
    try:
        # finally, create hard links
        for fm in (x for x in file_metas if x.matches):
            dfm = fm.matches[0]
            fm.path.parent.mkdir(parents=True, exist_ok=True)
            if args.create_symlinks:
                dfm.path.symlink_to(fm.path)
            else:
                dfm.path.link_to(fm.path)
            num_linked += 1
    except Exception as e:
        print(e, file=sys.stderr)
        print("Error occurs when creating links!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    print(f"Successfully linked {num_linked}/{len(file_metas)} files.")

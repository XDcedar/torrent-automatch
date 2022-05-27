#!/usr/bin/env python3
# coding=utf8

import argparse
from dataclasses import dataclass, field
from hashlib import sha1
from itertools import tee, accumulate
import random
import sys
from pathlib import Path

import torrent_parser


@dataclass
class PieceMeta:
    """记录种子的每个 piece 的信息

    每个 piece 包含的 bytes 的下标区间为 [first_byte, last_byte)
    first_byte: 在 torrent 拼接成的大文件中的起始位置
    last_byte: 在 torrent 拼接成的大文件中的结束位置
    """

    id: int = 0
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
    length: int = field(init=False)

    def __post_init__(self):
        self.length = self.path.stat().st_size


@dataclass
class FileMeta:
    """记录种子中的文件的信息"""

    path: Path = field(default_factory=Path)
    length: int = 0
    first_byte: int = 0
    last_byte: int = field(init=False)
    pieces: list[PieceMeta] = field(default_factory=list)
    match_candidates: list[DiskFileMeta] = field(default_factory=list)  # 该 FileMeta 的候选，目前会把所有大小相同的文件加进来
    matches: list[DiskFileMeta] = field(default_factory=list)  # 已确定对应该 FileMeta。不知为何要用list，按理说只会有一个才对

    def __post_init__(self):
        self.last_byte = self.first_byte + self.length


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
    try:
        args.dst = args.dst.resolve(strict=True)
    except FileNotFoundError:
        print("Wrong destination path!", file=sys.stderr)
        sys.exit(1)

    return args


def parse_files_meta(root: Path, torrent: dict):
    """根据种子信息向构建 file_metas 用于记录种子中每个文件对应的 Piece"""

    root = root / torrent["info"]["name"]
    files_info = torrent["info"]["files"]
    piece_hashes = torrent["info"]["pieces"]
    piece_length = torrent["info"]["piece length"]

    # 生成所有 filemetas
    file_lengths = (int(f["length"]) for f in files_info)
    file_lengths, for_accumulate = tee(file_lengths)
    tempiter = zip(files_info, file_lengths, accumulate(for_accumulate, initial=0))
    filemetas = [
        FileMeta(
            path=root.joinpath(*f["path"]),
            length=length,
            first_byte=first_byte,
        )
        for f, length, first_byte in tempiter
    ]
    # 利用 piece_hashes 构造 PieceMeta 迭代器
    piecemetas = (
        PieceMeta(
            id=i,
            first_byte=i * piece_length,
            last_byte=i * piece_length + piece_length,
            hash=x.strip(),
        )
        for i, x in enumerate(piece_hashes)
    )
    # 关联二者
    # 外层 for 循环用于 pm 包含多个 fm 时让 fm 递增
    # 内层 while 循环用于 fm 包含多个 pm 时 让 pm 递增
    breakpoint()
    pm = next(piecemetas, None)
    for fm in filemetas:
        if not pm:
            break
        if pm.last_byte > fm.first_byte:  # 若 pm 不完全在 fm 中
            fm.pieces.append(pm)
        if pm.last_byte >= fm.last_byte:  # 若 pm 有一部分超出 fm 的范围
            continue
        # fm 囊括了多个 piecemeta 时
        while True:
            pm = next(piecemetas, None)
            if not pm:
                break
            if pm.first_byte >= fm.last_byte:  # 若 pm 有一部分超出 fm 的范围
                break
            fm.pieces.append(pm)
            if pm.last_byte > fm.last_byte:  # 若 pm 不完全在 fm 中
                break
            # pm 完全在 fm 之中。
            # pm 自增并设置 first_byte_in_file 和 last_byte_in_file
            pm.in_single_file = True
            pm.first_byte_in_file = pm.first_byte - fm.first_byte
            pm.last_byte_in_file = pm.last_byte - fm.first_byte
    return filemetas


def parse_disk_file_metas(file_list: list):
    """根据输入的 file_list 读取硬盘中的文件，构建 DiskFileMeta 信息

    file_list 中可以有文件夹，但文件夹不能相互包含，否则会得到重复文件，降低效率。"""
    result = []
    for path in file_list:
        path = Path(path.strip()).resolve()
        if path.is_dir():
            result.extend(DiskFileMeta(p) for p in path.rglob("*") if p.is_file())
        else:
            result.append(DiskFileMeta(path))
    return result


def pass1_check_identical(fm: FileMeta, dfm: DiskFileMeta, pieces_to_check: int):
    """如果文件至少包含1个完整的Piece，则调用这个函数可以进行匹配"""
    pieces_in_single_file = [x for x in fm.pieces if x.in_single_file]
    k = min(len(pieces_in_single_file), pieces_to_check)
    sampled_bms = random.sample(pieces_in_single_file, k)
    sampled_bms.sort(key=lambda x: x.first_byte)  # 排序以增加随机读取的效率
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
    """文件不包含完整Piece，则调用本函数进行匹配。这种文件的大小要么<1个Piece，要么横跨2个Piece。"""
    hasher = sha1()
    fm_covered = []
    # 找到所有跟该 bm 有交集的 file_meta（注意 fm 的区间是左闭右开的，两个比较都应该是"<="）
    intersected_file_metas = (
        fm
        for fm in file_metas  # not (fm完全在bm左侧 or fm完全在bm右侧)
        if not (fm.last_byte <= bm.first_byte or fm.first_byte >= bm.last_byte)
    )
    # 以它们在 file_metas 中的默认顺序依次读取，计算它们拼起来的片段对应的 sha1
    for fm in intersected_file_metas:
        if not fm.match_candidates:
            return False
        intersect_first_byte = max(fm.first_byte, bm.first_byte)
        intersect_last_byte = min(fm.last_byte, bm.last_byte)
        # 如果当前 fm 完全在该 bm 中，那么添加到 fm_covered 中
        if intersect_first_byte == fm.first_byte and intersect_last_byte == fm.last_byte:
            fm_covered.append(fm)
        intersect_first_byte_in_file = intersect_first_byte - fm.first_byte
        intersect_last_byte_in_file = intersect_last_byte - fm.first_byte
        # TODO: 目前仅取了 fm.match_candidates[0]，本来应该计算所有match_candidates组合的情况
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
    args = do_arg_parse()

    try:
        torrent = torrent_parser.parse_torrent_file(args.torrent)
        file_metas = parse_files_meta(root=args.dst, torrent=torrent)
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read the torrent file, or it is not a multiple-file torrent!", file=sys.stderr)
        sys.exit(1)

    try:
        file_list = args.src_list.read_text(encoding="utf8").splitlines()
        disk_file_metas = parse_disk_file_metas(file_list)
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read disk files (or the list)!", file=sys.stderr)
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
        sys.exit(1)

    print(f"Successfully linked {num_linked}/{len(file_metas)} files.")

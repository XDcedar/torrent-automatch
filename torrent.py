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
class BlockMeta:
    """记录种子的每个block的信息"""

    id: int = 0
    # the block contains bytes in index range [first_byte, last_byte)
    first_byte: int = 0
    last_byte: int = 0
    hash: str = ""
    in_single_file: bool = False
    first_byte_in_file: int = 0
    last_byte_in_file: int = 0


@dataclass
class ExistedFileMeta:
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
    blocks: list[BlockMeta] = field(default_factory=list)
    match_candidates: list[ExistedFileMeta] = field(default_factory=list)  # 该 FileMeta 的候选，目前会把所有大小相同的文件加进来
    matches: list[ExistedFileMeta] = field(default_factory=list)  # 已确定对应该 FileMeta。不知为何要用list，按理说只会有一个才对


def do_arg_parse():
    parser = argparse.ArgumentParser(description="“浮肿一时爽，一直浮肿一直爽。”")
    parser.add_argument(
        "--src-list",
        type=Path,
        dest="src_list",
        help="specify a textfile, each line contains a file path of existing file as the potential linking source.",
    )
    parser.add_argument("--torrent", type=Path, dest="torrent", help="the torrent file to work with")
    parser.add_argument("--dst", type=Path, dest="dst", help="the destination directory")
    parser.add_argument("--blocks-to-check", type=int, dest="blocks_to_check", default=10)
    parser.add_argument("--create-symlinks", dest="create_symlinks", action="store_true")
    args = parser.parse_args()
    return args, parser


def parse_files_meta(root_directory_path: Path, files_info: list, block_hashes: list, block_size: int):
    """根据种子信息向构建 file_metas 用于记录种子中每个文件对应的 Block"""
    file_metas = []
    current_byte = 0
    num_blocks = len(block_hashes)
    block_id = 0
    current_block = BlockMeta()
    current_block.last_byte = 0
    for f in files_info:
        fm = FileMeta(
            path=root_directory_path.joinpath(*f["path"]),
            length=int(f["length"]),
            first_byte=current_byte,
            last_byte=current_byte + int(f["length"]),
        )
        current_byte += fm.length
        file_metas.append(fm)
        if current_block.last_byte > fm.first_byte:
            fm.blocks.append(current_block)
        if current_block.last_byte >= fm.last_byte:
            continue
        # 把所有属于该 FileMeta 的 BlockMeta() 放进来。
        # 如果这个 BlockMeta() 只有一部分属于该 FileMeta，
        # 则直接 break 而不让 block_id 自增，
        # 以便下一个外层 for 循环把它放到下一个 FileMeta 中去。
        while block_id < num_blocks:
            current_block = BlockMeta(
                id=block_id,
                first_byte=block_id * block_size,
                last_byte=block_id * block_size + block_size,
                hash=block_hashes[block_id].strip(),
            )
            block_id += 1
            # 当前 block_meta 已越过 file_meta 的位置
            if current_block.first_byte >= fm.last_byte:
                break
            fm.blocks.append(current_block)
            # 当前 block_meta 只有一部分处于 file_meta 之中
            if current_block.last_byte > fm.last_byte:
                break
            current_block.in_single_file = True
            current_block.first_byte_in_file = current_block.first_byte - fm.first_byte
            current_block.last_byte_in_file = current_block.last_byte - fm.first_byte
        if block_id >= num_blocks:
            break
    return file_metas


def parse_existed_files_meta(file_list: list):
    """根据输入的 file_list 读取硬盘中的文件，构建 ExistedFileMeta 信息"""
    path_list = map(lambda line: Path(line.strip()).resolve(), file_list)
    res = [ExistedFileMeta(path=p, length=p.stat().st_size) for p in path_list]
    return res


def pass1_check_identical(fm: FileMeta, efm: ExistedFileMeta, blocks_to_check: int):
    """如果文件至少包含1个完整的Block，则调用这个函数可以进行匹配"""
    blocks_in_single_file = [x for x in fm.blocks if x.in_single_file]
    k = min(len(blocks_in_single_file), blocks_to_check)
    sampled_bms = random.sample(blocks_in_single_file, k)
    if not sampled_bms:
        return False
    with open(efm.path, "rb") as ef:
        for bm in sampled_bms:
            ef.seek(bm.first_byte_in_file)
            hashhex = sha1(ef.read(bm.last_byte_in_file - bm.first_byte_in_file)).hexdigest()
            if hashhex != bm.hash:
                return False
    return True


# this function has side-effect!
def pass2_check_identical(bm, file_metas):
    """文件不包含完整Block，则调用这个函数进行匹配。这种文件的大小要么<1个Block，要么横跨两个Block。"""
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
            efm = fm.match_candidates[0]
            with open(efm.path, "rb") as ef:
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
        block_size = int(data["info"]["piece length"])
        file_metas = parse_files_meta(
            args.dst / data["info"]["name"], data["info"]["files"], data["info"]["pieces"], block_size
        )
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read the torrent file, or it is not a multiple-file torrent!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        file_list = args.src_list.read_text(encoding="utf8").splitlines()
        existed_file_metas = parse_existed_files_meta(file_list)
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read existed files (or the list)!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        # pass 1, find matchings by blocks completely contained in a file
        blocks_to_check = args.blocks_to_check
        for fm in file_metas:
            # just proceed in the brute-force way
            for efm in existed_file_metas:
                if fm.length != efm.length:
                    continue
                fm.match_candidates.append(efm)
                if pass1_check_identical(fm, efm, blocks_to_check):
                    fm.matches.append(efm)

        # t1 = []
        # for fm in file_metas:
        #     if fm.matches:
        #         t1.append(fm)

        # pass 2, try to match some files, each contained in a whole block
        for fm in file_metas:
            if len(fm.blocks) == 1 and not fm.matches:
                pass2_check_identical(fm.blocks[0], file_metas)

        # also, it may be the case where a file is covered by two blocks
        for fm in file_metas:
            if (
                not fm.matches
                and len(fm.blocks) == 2
                and pass2_check_identical(fm.blocks[0], file_metas)
                and pass2_check_identical(fm.blocks[1], file_metas)
            ):
                fm.matches.append(fm.match_candidates[0])

        # t2 = []
        # for fm in file_metas:
        #     if fm.matches:
        #         t2.append(fm)

    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read some data blocks!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    num_linked = 0
    try:
        # finally, create hard links
        for fm in (x for x in file_metas if x.matches):
            efm = fm.matches[0]
            fm.path.parent.mkdir(parents=True, exist_ok=True)
            if args.create_symlinks:
                efm.path.symlink_to(fm.path)
            else:
                efm.path.link_to(fm.path)
            num_linked += 1
    except Exception as e:
        print(e, file=sys.stderr)
        print("Error occurs when creating links!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    print(f"Successfully linked {num_linked}/{len(file_metas)} files.")

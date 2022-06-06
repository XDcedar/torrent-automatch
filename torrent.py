#!/usr/bin/env python3
# coding=utf8

import argparse
from dataclasses import dataclass, field
from hashlib import sha1
from itertools import accumulate, tee, product
from pathlib import Path
import random
import sys
from types import SimpleNamespace

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
def pass2_check_identical(pm: PieceMeta, filemetas: list[FileMeta]):
    """文件不包含完整Piece，则调用本函数进行匹配。这种文件的长度要么<1个Piece，要么横跨2个Piece。

    如果有多个候选项，采用简单粗暴的枚举法找到符合条件的文件。"""
    # 找到所有跟该 pm 有交集的 filemeta，
    # 构建 SimpleNamespace 用于稍后保存其他临时数据
    intersected_filemetas = [
        SimpleNamespace(filemeta=fm)
        for fm in filemetas  # not (fm完全在pm左侧 or fm完全在pm右侧)。fm 区间左闭右开，比较要用"<="和">="
        if not (fm.last_byte <= pm.first_byte or fm.first_byte >= pm.last_byte)
    ]
    # 确保有交集的 filemeta 在硬盘上必定有对应的候选文件
    if any(not ifm.filemeta.match_candidates for ifm in intersected_filemetas):
        return False
    # 计算并记录每个 filemeta 的区间数据供稍后使用
    for ifm in intersected_filemetas:
        fm = ifm.filemeta
        ifm.intersect_first_byte = max(fm.first_byte, pm.first_byte)
        ifm.intersect_last_byte = min(fm.last_byte, pm.last_byte)
        ifm.intersect_length = ifm.intersect_last_byte - ifm.intersect_first_byte
        ifm.intersect_first_byte_in_file = ifm.intersect_first_byte - fm.first_byte
    # 利用 itertools.product() 生成所有 match_candidates 的笛卡尔积，
    # 以它们在 filemetas 中的默认顺序依次读取，暴力枚举全部可能性，计算对应的 sha1
    combinations = product(*(x.filemeta.match_candidates for x in intersected_filemetas))
    for combination in combinations:
        hasher = sha1()
        for ifm, dfm in zip(intersected_filemetas, combination):
            with open(dfm.path, "rb") as ef:
                ef.seek(ifm.intersect_first_byte_in_file)
                hasher.update(ef.read(ifm.intersect_length))
        hexdigest = hasher.hexdigest()
        # 如果sha1值匹配，则为所有完全被该 pm 包含的 filemeta 添加 matches
        # （对于横跨两个 piece 的 fm，会在调用本函数后执行该操作）
        if hexdigest != pm.hash:
            continue
        for ifm, dfm in zip(intersected_filemetas, combination):
            if (
                ifm.intersect_first_byte == ifm.filemeta.first_byte
                and ifm.intersect_last_byte == ifm.filemeta.last_byte
            ):
                if not ifm.filemeta.matches:
                    ifm.filemeta.matches.append(dfm)
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

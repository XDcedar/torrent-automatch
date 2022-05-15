#!/usr/bin/env python3
# coding=utf8

import torrent_parser
import argparse
import sys
from dataclasses import dataclass
from hashlib import sha1
import os
import random


@dataclass
class BlockMeta:
    id: int = 0
    # the block contains bytes in index range [first_byte, last_byte)
    first_byte: int = 0
    last_byte: int = 0
    hash: str = ""
    in_single_file: bool = False
    first_byte_in_file: int = 0
    last_byte_in_file: int = 0


@dataclass
class FileMeta:
    path: str
    length: int
    first_byte: int
    last_byte: int
    blocks: list
    match_candidates: list
    matches: list

    def __init__(self):
        self.path = ""
        self.length = 0
        self.first_byte = 0
        self.last_byte = 0
        self.blocks = []
        self.match_candidates = []
        self.matches = []


@dataclass
class ExistedFileMeta:
    path: str = ""
    length: int = 0


def do_arg_parse():
    parser = argparse.ArgumentParser(description="“浮肿一时爽，一直浮肿一直爽。”")
    parser.add_argument(
        "--src-list",
        type=str,
        dest="src_list",
        help="specify a textfile, each line contains a file path of existing file as the potential linking source.",
    )
    parser.add_argument("--torrent", type=str, dest="torrent", help="the torrent file to work with")
    parser.add_argument("--dst", type=str, dest="dst", help="the destination directory")
    parser.add_argument("--blocks-to-check", type=int, dest="blocks_to_check", default=10)
    parser.add_argument("--create-symlinks", dest="create_symlinks", action="store_true")
    args = parser.parse_args()
    return args, parser


def parse_files_meta(root_directory_path, files_info, block_hashes, block_size):
    file_metas = []
    current_byte = 0
    num_blocks = len(block_hashes)
    block_id = 0
    current_block = BlockMeta()
    current_block.last_byte = 0
    for f in files_info:
        fm = FileMeta()
        fm.path = root_directory_path
        for p in f["path"]:
            fm.path = os.path.join(fm.path, p)
        fm.length = int(f["length"])
        fm.first_byte = current_byte
        fm.last_byte = current_byte + fm.length
        fm.blocks = []
        current_byte += fm.length
        file_metas.append(fm)
        if current_block.last_byte > fm.first_byte:
            fm.blocks.append(current_block)
        if current_block.last_byte >= fm.last_byte:
            continue
        while block_id < num_blocks:
            current_block = BlockMeta()
            current_block.id = block_id
            current_block.first_byte = block_id * block_size
            current_block.last_byte = current_block.first_byte + block_size
            current_block.hash = block_hashes[block_id].strip()
            block_id += 1
            if current_block.first_byte < fm.last_byte:
                fm.blocks.append(current_block)
                if current_block.last_byte <= fm.last_byte:
                    current_block.in_single_file = True
                    current_block.first_byte_in_file = current_block.first_byte - fm.first_byte
                    current_block.last_byte_in_file = current_block.last_byte - fm.first_byte
                else:
                    break
            else:
                break
        if block_id >= num_blocks:
            break
    return file_metas


def parse_existed_files_meta(file_list):
    res = []
    for line in file_list:
        efm = ExistedFileMeta()
        efm.path = os.path.abspath(line.strip())
        efm.length = os.stat(efm.path).st_size
        res.append(efm)
    return res


def pass1_check_identical(fm, efm, blocks_to_check):
    bms = fm.blocks[:]
    random.shuffle(bms)
    sampled_bms = []
    for bm in bms:
        if bm.in_single_file:
            sampled_bms.append(bm)
        if len(sampled_bms) >= blocks_to_check:
            break
    if len(sampled_bms) == 0:
        return False
    ef = open(efm.path, "rb")
    identical = True
    for bm in sampled_bms:
        hasher = sha1()
        ef.seek(bm.first_byte_in_file)
        hasher.update(ef.read(bm.last_byte_in_file - bm.first_byte_in_file))
        hash = hasher.hexdigest()
        if hash != bm.hash:
            identical = False
            break
    ef.close()
    return identical


# this function has side-effect!
def pass2_check_identical(bm, file_metas):
    hasher = sha1()
    fm_covered = []
    for fm in file_metas:
        if not (fm.first_byte >= bm.last_byte or fm.last_byte <= bm.first_byte):
            if len(fm.match_candidates) == 0:
                return False
            intersect_first_byte = max(fm.first_byte, bm.first_byte)
            intersect_last_byte = min(fm.last_byte, bm.last_byte)
            # print(intersect_first_byte, intersect_last_byte)
            if intersect_first_byte == fm.first_byte and intersect_last_byte == fm.last_byte:
                fm_covered.append(fm)
            intersect_first_byte_in_file = intersect_first_byte - fm.first_byte
            intersect_last_byte_in_file = intersect_last_byte - fm.first_byte
            # TODO: should emumerate over all possible combinations
            efm = fm.match_candidates[0]
            ef = open(efm.path, "rb")
            ef.seek(intersect_first_byte_in_file)
            hasher.update(ef.read(intersect_last_byte_in_file - intersect_first_byte_in_file))
            ef.close()
    hash = hasher.hexdigest()
    if hash == bm.hash:
        for fm in fm_covered:
            if len(fm.matches) == 0:
                fm.matches.append(fm.match_candidates[0])
        return True
    return False


if __name__ == "__main__":
    args, parser = do_arg_parse()
    file_metas = []

    try:
        abs_dst = os.path.abspath(args.dst)
    except Exception as e:
        print(e, file=sys.stderr)
        print("Wrong destination path!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        data = torrent_parser.parse_torrent_file(args.torrent)
        block_size = int(data["info"]["piece length"])
        file_metas = parse_files_meta(
            os.path.join(abs_dst, data["info"]["name"]), data["info"]["files"], data["info"]["pieces"], block_size
        )
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read the torrent file, or it is not a multiple-file torrent!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        file_list = open(args.src_list, "r", encoding="utf8")
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

        """
        t1 = []
        for fm in file_metas:
            if len(fm.matches) > 0:
                t1.append(fm)
        """

        # pass 2, try to match some files, each contained in a whole block
        for fm in file_metas:
            if len(fm.blocks) == 1 and len(fm.matches) == 0:
                pass2_check_identical(fm.blocks[0], file_metas)

        # also, it may be the case where a file is covered by two blocks
        for fm in file_metas:
            if (
                len(fm.matches) == 0
                and len(fm.blocks) == 2
                and pass2_check_identical(fm.blocks[0], file_metas)
                and pass2_check_identical(fm.blocks[1], file_metas)
            ):
                fm.matches.append(fm.match_candidates[0])

        """
        t2 = []
        for fm in file_metas:
            if len(fm.matches) > 0:
                t2.append(fm)
        """
    except Exception as e:
        print(e, file=sys.stderr)
        print("Failed to read some data blocks!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    num_linked = 0
    try:
        # finally, create hard links
        for fm in file_metas:
            if len(fm.matches) > 0:
                efm = fm.matches[0]
                os.makedirs(os.path.dirname(fm.path), exist_ok=True)
                if args.create_symlinks:
                    os.symlink(efm.path, fm.path)
                else:
                    os.link(efm.path, fm.path)
                num_linked += 1
    except Exception as e:
        print(e, file=sys.stderr)
        print("Error occurs when creating links!", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    print("Successfully linked %d/%d files." % (num_linked, len(file_metas)))

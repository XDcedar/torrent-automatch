#!/usr/bin/env python3
# coding: utf-8

from itertools import zip_longest
from pathlib import Path
from pprint import pprint

import torrent_parser

import torrent

"""
需要考虑的边缘情况：
1. 不同种子中包含相同的文件。
   当一个文件夹中存在与种子A匹配的文件时，不能保证整个文件夹的文件都来自该种子。
2. 同一个文件夹包含来自多个种子的文件的情况。

TODO:
增加 --dry-run 选项
添加 requirements.txt `pip install -r requirements.txt`
"""

"""
文件的首尾位置有3种情况：在piece边界的前、中、后。
文件的长度也有3种情况：小于1个piece、小于2个pieces、大于等于3个pieces

files  |-A-|----B----|--C--|-D-|E|F|-G-|----H----|--------I--------|---J---|-K-|
pieces |-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
hashes    a     b     c     d     e     f     g     h     i     j     k     l

根据以上来构造 torrent 例子。
注意，'|' 代表的长度与 '-' 相同，计算长度时只算左侧的 '|'。
"""
my_test_torrent = {
    "announce": "http://example.com:8888/announce",
    "announce-list": [
        ["http://example.com:8888/announce"],
        ["udp://example.com:80/announce"],
        ["udp://example.com:6969/announce"],
    ],
    "comment": "test torrent",
    "created by": "Ceder",
    "creation date": 1555905670,
    "info": {
        "files": [
            {"length": 4, "path": ["A"]},
            {"length": 10, "path": ["B"]},
            {"length": 6, "path": ["C"]},
            {"length": 4, "path": ["D"]},
            {"length": 2, "path": ["E"]},
            {"length": 2, "path": ["F"]},
            {"length": 4, "path": ["G"]},
            {"length": 10, "path": ["H"]},
            {"length": 18, "path": ["I"]},
            {"length": 8, "path": ["J"]},
            {"length": 4, "path": ["K"]},
        ],
        "name": "test torrent",
        "piece length": 6,
        "pieces": list("abcdefghijkl"),
    },
}


def test_torrent_parser():
    torrent = torrent_parser.parse_torrent_file(
        "./testcase/[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p].torrent"
    )
    return torrent


def test_parsing_my_torrent():
    filemetas = torrent.parse_files_meta(root=Path(r"D:/"), torrent=my_test_torrent)

    def same_hash_value(piecemetas: list[torrent.PieceMeta], hashes: list[str]):
        piece_hashes = (p.hash for p in piecemetas)
        return all(x == y for x, y in zip_longest(piece_hashes, hashes))

    # files  |-A-|----B----|--C--|-D-|E|F|-G-|----H----|--------I--------|---J---|-K-|
    # pieces |-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
    # hashes    a     b     c     d     e     f     g     h     i     j     k     l
    assert same_hash_value(filemetas[0].pieces, ["a"])
    assert same_hash_value(filemetas[1].pieces, ["a", "b", "c"])
    assert same_hash_value(filemetas[2].pieces, ["c", "d"])
    assert same_hash_value(filemetas[3].pieces, ["d"])
    assert same_hash_value(filemetas[4].pieces, ["e"])
    assert same_hash_value(filemetas[5].pieces, ["e"])
    assert same_hash_value(filemetas[6].pieces, ["e", "f"])
    assert same_hash_value(filemetas[7].pieces, ["f", "g"])
    assert same_hash_value(filemetas[8].pieces, ["h", "i", "j"])
    assert same_hash_value(filemetas[9].pieces, ["k", "l"])
    assert same_hash_value(filemetas[10].pieces, ["l"])
    print("All Green!")


if __name__ == "__main__":
    # test_torrent_parser()
    test_parsing_my_torrent()
    pass

"""
torrent example

{'announce': 'http://sukebei.tracker.wf:8888/announce',
 'announce-list': [['http://sukebei.tracker.wf:8888/announce'],
                   ['http://208.67.16.113:8000/annonuce'],
                   ['udp://208.67.16.113:8000/annonuce'],
                   ['udp://tracker.openbittorrent.com:80/announce'],
                   ['udp://exodus.desync.com:6969/announce']],
 'comment': 'https://sukebei.nyaa.si/view/2620925',
 'created by': 'NyaaV2',
 'creation date': 1545905570,
 'info': {'files': [{'length': 264,
                     'path': ['CDs',
                              '[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)',
                              'ACUDL-1001-CD.cue']},
                    {'length': 201853,
                     'path': ['CDs',
                              '[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)',
                              'ACUDL-1001-CD.jpg']},
                    {'length': 1757,
                     'path': ['CDs',
                              '[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)',
                              'ACUDL-1001-CD.log']},
                    {'length': 45250583,
                     'path': ['CDs',
                              '[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)',
                              'ACUDL-1001-CD.tak']},
                    {'length': 672098, 'path': ['Scans', 'DVD', '01.webp']},
                    {'length': 500972, 'path': ['Scans', 'DVD', '02.webp']},
                    {'length': 205490, 'path': ['Scans', 'DVD', '03.webp']},
                    {'length': 212836, 'path': ['Scans', 'DVD', '04.webp']},
                    {'length': 2719648,
                     'path': ['SPs',
                              '[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ '
                              'Anata to Koibito Tsunagi [Menu].png']},
                    {'length': 493227377,
                     'path': ['[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ '
                              'Anata to Koibito Tsunagi '
                              '[Ma10p_1080p][x265_flac].mkv']},
                    {'length': 1186, 'path': ['readme about WebP.txt']}],
          'name': '[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito '
                  'Tsunagi [Ma10p_1080p]',
          'piece length': 1048576,
          'pieces': ['d15fa1ef3bdaf102e9bdba1c9256f17900e149de',
                     '4b5b7cc280e9cc7a996a95e136cd4f71d87eab72',
                     '93a77223bba7eaee7f44810e838ce4ef5e6e6ee1',
                     'c2f81cf9f23a32d91a1018fb797bdd46d53adf5d',
                     '...',
                     '5a97ec299e18385638dac78b9bc9c40b437ff6d4']}}
"""

"""
filemetas example

[
    FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ... [Ma10p_1080p]\\CDs\\[100730] SPCD ... (tak)\\ACUDL-1001-CD.cue', length=264, first_byte=0, last_byte=264, blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa...149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
    FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ... [Ma10p_1080p]\\CDs\\[100730] SPCD ... (tak)\\ACUDL-1001-CD.jpg', length=201853, first_byte=264, last_byte=202117, blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa...149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
    FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ... [Ma10p_1080p]\\CDs\\[100730] SPCD ... (tak)\\ACUDL-1001-CD.log', length=1757, first_byte=202117, last_byte=203874, blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa...149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
    FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ... [Ma10p_1080p]\\CDs\\[100730] SPCD ... (tak)\\ACUDL-1001-CD.tak', length=45250583, first_byte=203874, last_byte=45454457,
             blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa...149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0),
                     BlockMeta(id=1, first_byte=1048576, last_byte=2097152, hash='4b5b7...eab72', in_single_file=True, first_byte_in_file=844702, last_byte_in_file=1893278),
                     ...,
                     BlockMeta(id=43, first_byte=45088768, last_byte=46137344, hash='8f842...4bd9d', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)],
                     match_candidates=[], matches=[]),
    FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p]\\Scans\\DVD\\01.webp', length=672098, first_byte=45454457, last_byte=46126555, blocks=[BlockMeta(id=43, first_byte=45088768, last_byte=46137344, hash='8f842...4bd9d', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
    ...,
]
"""

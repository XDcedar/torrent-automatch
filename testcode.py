#!/usr/bin/env python3
# coding: utf-8

import torrent_parser
from pprint import pprint

"""
需要考虑的边缘情况：
1. 不同种子中包含相同的文件。
   当一个文件夹中存在与种子A匹配的文件时，不能保证整个文件夹的文件都来自该种子。
2. 同一个文件夹包含来自多个种子的文件的情况。

TODO:
增加 --dry-run 选项
block 更名为 piece
existed 前缀更名为 disk
添加 requirements.txt `pip install -r requirements.txt`
"""


def test():
    breakpoint()
    torrent = torrent_parser.parse_torrent_file(
        "./testcase/[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p].torrent"
    )
    return torrent


if __name__ == "__main__":
    pprint(test())

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

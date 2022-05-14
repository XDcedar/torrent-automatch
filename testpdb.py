#!/usr/bin/env python3
# coding: utf-8

import torrent_parser
from pprint import pprint

def test():
    breakpoint()
    torrent = torrent_parser.parse_torrent_file('./testcase/[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p].torrent')
    return torrent

if __name__ == '__main__':
    pprint(test())

'''
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
'''

'''
file_metas
[FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p]\\CDs\\[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)\\ACUDL-1001-CD.cue', length=264, first_byte=0, last_byte=264, blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa1ef3bdaf102e9bdba1c9256f17900e149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
 FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p]\\CDs\\[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)\\ACUDL-1001-CD.jpg', length=201853, first_byte=264, last_byte=202117, blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa1ef3bdaf102e9bdba1c9256f17900e149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
 FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p]\\CDs\\[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)\\ACUDL-1001-CD.log', length=1757, first_byte=202117, last_byte=203874, blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa1ef3bdaf102e9bdba1c9256f17900e149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
 FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p]\\CDs\\[100730] SPCD ドラマ ｢スキスキ麻衣さん……♥｣ (tak)\\ACUDL-1001-CD.tak', length=45250583, first_byte=203874, last_byte=45454457, blocks=[BlockMeta(id=0, first_byte=0, last_byte=1048576, hash='d15fa1ef3bdaf102e9bdba1c9256f17900e149de', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0), BlockMeta(id=1, first_byte=1048576, last_byte=2097152, hash='4b5b7cc280e9cc7a996a95e136cd4f71d87eab72', in_single_file=True, first_byte_in_file=844702, last_byte_in_file=1893278), BlockMeta(id=2, first_byte=2097152, last_byte=3145728, hash='93a77223bba7eaee7f44810e838ce4ef5e6e6ee1', in_single_file=True, first_byte_in_file=1893278, last_byte_in_file=2941854), BlockMeta(id=3, first_byte=3145728, last_byte=4194304, hash='c2f81cf9f23a32d91a1018fb797bdd46d53adf5d', in_single_file=True, first_byte_in_file=2941854, last_byte_in_file=3990430), BlockMeta(id=4, first_byte=4194304, last_byte=5242880, hash='87234aaa105a5bd971a24f2af7051ff2fe312519', in_single_file=True, first_byte_in_file=3990430, last_byte_in_file=5039006), BlockMeta(id=5, first_byte=5242880, last_byte=6291456, hash='f533fb77bd9c09115087d125becc6d9ca427c0c4', in_single_file=True, first_byte_in_file=5039006, last_byte_in_file=6087582), BlockMeta(id=6, first_byte=6291456, last_byte=7340032, hash='74be8a84f64842b7633435eaff08f68bc0ee4988', in_single_file=True, first_byte_in_file=6087582, last_byte_in_file=7136158), BlockMeta(id=7, first_byte=7340032, last_byte=8388608, hash='fd8874c7a1af2447c0dabc375acd491be90b8b88', in_single_file=True, first_byte_in_file=7136158, last_byte_in_file=8184734), BlockMeta(id=8, first_byte=8388608, last_byte=9437184, hash='8c5713cba44d811aa4eb67d5b767154a416d5b2f', in_single_file=True, first_byte_in_file=8184734, last_byte_in_file=9233310), BlockMeta(id=9, first_byte=9437184, last_byte=10485760, hash='d0f4ad04afcdea9d836e9fa43286358834251c32', in_single_file=True, first_byte_in_file=9233310, last_byte_in_file=10281886), BlockMeta(id=10, first_byte=10485760, last_byte=11534336, hash='45a072870b0f7e862d350f07fab04668b5811000', in_single_file=True, first_byte_in_file=10281886, last_byte_in_file=11330462), BlockMeta(id=11, first_byte=11534336, last_byte=12582912, hash='8a9131b151ab9a54379d3ec0f080cf79b7b187b7', in_single_file=True, first_byte_in_file=11330462, last_byte_in_file=12379038), BlockMeta(id=12, first_byte=12582912, last_byte=13631488, hash='1f6d3ae1ee01cf34dac0f2a50df54dd7e3041479', in_single_file=True, first_byte_in_file=12379038, last_byte_in_file=13427614), BlockMeta(id=13, first_byte=13631488, last_byte=14680064, hash='a985cece20a4c79af461a937b99370df56435bbc', in_single_file=True, first_byte_in_file=13427614, last_byte_in_file=14476190), BlockMeta(id=14, first_byte=14680064, last_byte=15728640, hash='79b1da46e2e77a68ef3ab58802f3af4c86da3401', in_single_file=True, first_byte_in_file=14476190, last_byte_in_file=15524766), BlockMeta(id=15, first_byte=15728640, last_byte=16777216, hash='22e42eecb65a3d56390eecfcf44931207cc0b0de', in_single_file=True, first_byte_in_file=15524766, last_byte_in_file=16573342), BlockMeta(id=16, first_byte=16777216, last_byte=17825792, hash='6fc4b7a4b53894d4dbac762ab93518bcd98baa46', in_single_file=True, first_byte_in_file=16573342, last_byte_in_file=17621918), BlockMeta(id=17, first_byte=17825792, last_byte=18874368, hash='ad60111a61c4604298023ee5361503246fee57a3', in_single_file=True, first_byte_in_file=17621918, last_byte_in_file=18670494), BlockMeta(id=18, first_byte=18874368, last_byte=19922944, hash='ad115c6ea4acf742f2aca22e64bc5544fe888dda', in_single_file=True, first_byte_in_file=18670494, last_byte_in_file=19719070), BlockMeta(id=19, first_byte=19922944, last_byte=20971520, hash='a76f5f814552ecbc1243b2208bee4e397f8275a0', in_single_file=True, first_byte_in_file=19719070, last_byte_in_file=20767646), BlockMeta(id=20, first_byte=20971520, last_byte=22020096, hash='3670fbd9accb4bd09e1189dd7f8099bf0eb72526', in_single_file=True, first_byte_in_file=20767646, last_byte_in_file=21816222), BlockMeta(id=21, first_byte=22020096, last_byte=23068672, hash='a2b86cf9e02993cceb6d7e7c9d19de669f1892b0', in_single_file=True, first_byte_in_file=21816222, last_byte_in_file=22864798), BlockMeta(id=22, first_byte=23068672, last_byte=24117248, hash='bf9103f291947549fba9c4aec39495702b932aa5', in_single_file=True, first_byte_in_file=22864798, last_byte_in_file=23913374), BlockMeta(id=23, first_byte=24117248, last_byte=25165824, hash='c996469d7f1f00efc85966ea0a728f9e7e587e3f', in_single_file=True, first_byte_in_file=23913374, last_byte_in_file=24961950), BlockMeta(id=24, first_byte=25165824, last_byte=26214400, hash='6be1ad9e3d2b8ebb795dad0ed5125035cbdfacf4', in_single_file=True, first_byte_in_file=24961950, last_byte_in_file=26010526), BlockMeta(id=25, first_byte=26214400, last_byte=27262976, hash='09986a52d5420b10a45241d66184cda8205e5b60', in_single_file=True, first_byte_in_file=26010526, last_byte_in_file=27059102), BlockMeta(id=26, first_byte=27262976, last_byte=28311552, hash='bd9e774bede838030abb0ea3e9f492396f0d8bd3', in_single_file=True, first_byte_in_file=27059102, last_byte_in_file=28107678), BlockMeta(id=27, first_byte=28311552, last_byte=29360128, hash='16d8c19bab45612174bf61abc78d91a5720cced0', in_single_file=True, first_byte_in_file=28107678, last_byte_in_file=29156254), BlockMeta(id=28, first_byte=29360128, last_byte=30408704, hash='b426fd11b81b32c4bbfba7ea140e354da81c9434', in_single_file=True, first_byte_in_file=29156254, last_byte_in_file=30204830), BlockMeta(id=29, first_byte=30408704, last_byte=31457280, hash='b03361228161754420e88acd1d642d06310e0010', in_single_file=True, first_byte_in_file=30204830, last_byte_in_file=31253406), BlockMeta(id=30, first_byte=31457280, last_byte=32505856, hash='cf97071ee90c81c71a2ff4779e61bafd3bcd9b0c', in_single_file=True, first_byte_in_file=31253406, last_byte_in_file=32301982), BlockMeta(id=31, first_byte=32505856, last_byte=33554432, hash='c30b0cb0faf9a858705176ee733ac8290461eabb', in_single_file=True, first_byte_in_file=32301982, last_byte_in_file=33350558), BlockMeta(id=32, first_byte=33554432, last_byte=34603008, hash='58c1f3c0d4c1193d559a7856160b049b148d5990', in_single_file=True, first_byte_in_file=33350558, last_byte_in_file=34399134), BlockMeta(id=33, first_byte=34603008, last_byte=35651584, hash='7f2ab9f1a837489c7c32c6d4fccaec82a94d6235', in_single_file=True, first_byte_in_file=34399134, last_byte_in_file=35447710), BlockMeta(id=34, first_byte=35651584, last_byte=36700160, hash='89111a280cc320b3f5ea300aeb8a631246d14921', in_single_file=True, first_byte_in_file=35447710, last_byte_in_file=36496286), BlockMeta(id=35, first_byte=36700160, last_byte=37748736, hash='da4569828eb3e6dab547ef5698690d404106d5b8', in_single_file=True, first_byte_in_file=36496286, last_byte_in_file=37544862), BlockMeta(id=36, first_byte=37748736, last_byte=38797312, hash='4509c44822c4f3a8a1f84ae00db6730af902ff58', in_single_file=True, first_byte_in_file=37544862, last_byte_in_file=38593438), BlockMeta(id=37, first_byte=38797312, last_byte=39845888, hash='a7da6dafefcb720237e4dde5ca749c2d40ff1021', in_single_file=True, first_byte_in_file=38593438, last_byte_in_file=39642014), BlockMeta(id=38, first_byte=39845888, last_byte=40894464, hash='678fbc60669000c452b58320810e47dc979c4168', in_single_file=True, first_byte_in_file=39642014, last_byte_in_file=40690590), BlockMeta(id=39, first_byte=40894464, last_byte=41943040, hash='ae53f1dfa232749e56f84d2e744cd5d49a887b97', in_single_file=True, first_byte_in_file=40690590, last_byte_in_file=41739166), BlockMeta(id=40, first_byte=41943040, last_byte=42991616, hash='f3b55e830339738c5cd067b3f8f197c8d4416f49', in_single_file=True, first_byte_in_file=41739166, last_byte_in_file=42787742), BlockMeta(id=41, first_byte=42991616, last_byte=44040192, hash='27bac80af5b0b819b4cb5f716ef7392b1e579b25', in_single_file=True, first_byte_in_file=42787742, last_byte_in_file=43836318), BlockMeta(id=42, first_byte=44040192, last_byte=45088768, hash='0e2fe28941a932a7abea75531a41c8a6f6140ae7', in_single_file=True, first_byte_in_file=43836318, last_byte_in_file=44884894), BlockMeta(id=43, first_byte=45088768, last_byte=46137344, hash='8f842dfdb8ecfab853a56b725d72f7d49764bd9d', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
 FileMeta(path='D:\\github\\torrent\\result\\[VCB-Studio] Sono Hanabira ni Kuchizuke o꞉ Anata to Koibito Tsunagi [Ma10p_1080p]\\Scans\\DVD\\01.webp', length=672098, first_byte=45454457, last_byte=46126555, blocks=[BlockMeta(id=43, first_byte=45088768, last_byte=46137344, hash='8f842dfdb8ecfab853a56b725d72f7d49764bd9d', in_single_file=False, first_byte_in_file=0, last_byte_in_file=0)], match_candidates=[], matches=[]),
 ...]
'''

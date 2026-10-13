from sj2 import Saimin2, UraSaimin
from repack import *

sj2_path = 'sj2/'
sj2_scr_path = sj2_path + 'scr/'
sj2_pack_path = sj2_path + 'pack/'


usj2_path = 'us2/'
usj2_scr_path = usj2_path + 'scr/'
usj2_pack_path = usj2_path + 'pack/'


# sj2_output_path = 'F:/vn portable/Blackrainbow/sj2/'
# usj2_output_path = 'F:/vn portable/Blackrainbow/us2/'
sj2_output_path = ''
usj2_output_path = ''


def repack_sj2():
    repack_dat(sj2_pack_path, sj2_output_path + 'sj_spt.dat', 5, 87090, 192)


def repack_usj2():
    repack_dat(usj2_pack_path, usj2_output_path + 'sjfd_spt.dat', 5, 2459749, 77)


def sj2():
    for src in [
        # 'pro_001', 'pro_002', 'pro_003', 'MA1007',
        'MA1008'
    ]:
        a = Saimin2(sj2_scr_path + src + '.spt', sj2_path)
        lst = a.tr_run()
        print('writing %s' % src)
        write_spt(sj2_pack_path + src + '.spt', a.header, lst)
    print('repacking...')
    repack_sj2()


def usj():
    src = '01_yoko_a'

    a = UraSaimin(usj2_scr_path + src + '.spt', usj2_path)
    lst = a.tr_run()
    print('writing %s' % src)
    write_spt(usj2_pack_path + src + '.spt', a.header, lst)
    print('repacking...')
    repack_usj2()


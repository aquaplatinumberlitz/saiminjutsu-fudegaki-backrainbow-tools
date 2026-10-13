import pathlib, struct, glob


def repack_dat(src, dst, h1, h2, c=-1):

    class br_entry:
        def __init__(self, f):
            pth = pathlib.Path(f)
            self.name = pth.name
            self.size = pth.stat().st_size

    entries = []
    for fs in glob.glob(src+'*.spt'):
        entries.append(br_entry(fs))
    count = len(entries)
    if c != -1 and count != c:
        raise ValueError('count mismatch')
    base = (count + 4) * 4
    with open(dst, 'wb') as go:
        go.write(struct.pack('<4I', h1, h2, count, base))
        off = 0
        for i in range(count):
            go.write(struct.pack('<I', off))
            off += entries[i].size + 0x24
        for e in entries:
            n = e.name.encode('cp932')
            go.write(n)
            go.write(b'\0' * (0x20 - len(n)))
            go.write(struct.pack('<I', e.size))
            with open(src+e.name, 'rb') as fo:
                go.write(fo.read())


def write_spt(dst, head, cmd_list):
    with open(dst, 'wb') as go:
        if len(head) != 68:
            raise ValueError('header size')
        go.write(head)
        go.write(struct.pack('<2I', 0, 0))
        total = 0
        for c in cmd_list:
            sz = len(c.args)
            go.write(struct.pack('<2I', c.cmd, sz))
            total += sz + 8
            go.write(c.args)
        go.seek(68)
        go.write(struct.pack('<2I', len(cmd_list), total))

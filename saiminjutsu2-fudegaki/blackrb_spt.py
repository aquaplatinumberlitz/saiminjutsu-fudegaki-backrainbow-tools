from utils import BinaryFile, BinaryFileError
import struct, pathlib


class RawCommand:
    def __init__(self, cmd, args, pos=-1):
        self.cmd, self.args, self.pos = cmd, args, pos

    def __repr__(self):
        a = ' %s' % self.args.__repr__() if self.args else ''
        return '_%x%s' % (self.cmd, a)


def mess_decrypt(txt):
    txt = bytearray(txt)
    for i in range(0, len(txt), 4):
        txt[i] ^= 1
    return txt


def wrap(msg):
    words = msg.split()
    lst, limit = [], 58
    line = words[0]
    for i in range(1, len(words)):
        new = line + ' ' + words[i]
        if len(new) > limit:
            lst.append(line)
            line = words[i]
        else:
            line = new

    lst.append(line)
    return lst


class SptMessage:
    def __init__(self, arg):
        self.flag, self.voice, self.n, s1, s2 = struct.unpack('<5i', arg[:20])
        if s2 + s1 != len(arg) - 20:
            raise ValueError('MSG sizes')
        if s1 != 0:
            self.channel = arg[20:20 + s1]
        else:
            self.channel = b''

        self.msg = mess_decrypt(arg[20 + s1:]).decode('cp932')
        self.name = None
        if self.msg.startswith('【'):
            e = self.msg.find('】\r\n')
            if e != -1:
                self.name = self.msg[:e + 1]
                self.msg = self.msg[e + 3:]

    def __repr__(self):
        return '%s %s' % (self.name, self.msg.__repr__())

    def to_spt(self):
        msg = self.msg
        if self.name is not None:
            msg = self.name + '\r\n' + msg
        msg = mess_decrypt(msg.encode('cp932'))
        s1 = len(self.channel)
        s2 = len(msg)
        ret = struct.pack('<5i', self.flag, self.voice, self.n, s1, s2)
        return ret + self.channel + msg


class ScriptSpt(BinaryFile):
    def __init__(self, bf, n_dick, ch_dic, tr_path):
        self.choices_dick, self.names_dick, self.tr_path = ch_dic, n_dick, tr_path
        BinaryFile.__init__(self, bf)

    def open(self):
        self.header = self.read_exactly(68)
        n = self.header.find(b'\0')
        if n == -1:
            raise BinaryFileError('header nul')
        for i in range(n, 68):
            if self.header[i] != 0:
                raise BinaryFileError('header zero')

        n, sz = self.unpack('<2I')
        if self.size - (68+8) != sz:
            raise BinaryFileError('boobs mismatch')

        self.raw_commands = []
        for i in range(n):
            cmd, sz = self.unpack('<2I')
            self.raw_commands.append(RawCommand(cmd, self.read_exactly(sz)))

    def load_translation(self, tr_path):
        n = pathlib.Path(self.bfile.name).stem + '_msg.txt'
        f = pathlib.Path(tr_path).joinpath(n)
        self.translation = []
        if not f.exists():
            return
        with open(f, 'r', encoding='utf8') as fo:
            for ll in fo:
                if ll.startswith('*'):
                    fo.readline()
                    tr = fo.readline().rstrip()
                    if tr.startswith('[M]'):
                        tr = tr[3:]
                    self.translation.append(tr)

    def tr_run(self, lst=None):

        cmd_dick = {
            0x8: self.message, 0xe: self.choice,
            0x1d: self.title, 0x1e: self.title2,
        }

        if lst is None:
            lst = self.raw_commands
        self.load_translation(self.tr_path)
        ret, self.counter = [], 0
        for c in lst:
            try:
                hint = cmd_dick[c.cmd]
                cmd = hint(c.args)
            except KeyError:
                cmd = c
            if cmd is not None:
                ret.append(cmd)
        return ret

    def t1_tr(self, txt):
        return txt

    def t2_tr(self, txt):
        return txt

    def title(self, args):
        txt = self.t1_tr(args[4:].decode('cp932'))
        return RawCommand(0x1d, int.to_bytes(len(txt), 4, 'little') + txt.encode('cp932'))

    def title2(self, args):
        txt = self.t2_tr(args[4:].decode('cp932'))
        return RawCommand(0x1e, int.to_bytes(len(txt), 4, 'little') + txt.encode('cp932'))

    def choice_tr(self, txt):
        try:
            return self.choices_dick[txt]
        except KeyError:
            print('missing choice: %s' % txt)
        return txt

    def choice(self, args):
        flag, a2, sz = struct.unpack('<3I', args[:12])
        items = args[12:]
        if len(items) != sz:
            raise ValueError('choice arg size')
        if a2 != 0:
            print('choice second arg')
        items = items.decode('cp932').split('\\0')[:-1]
        lst = []
        for ch in items:
            lst.append(self.choice_tr(ch))
        ret = b''
        for ch in lst:
            ret += (ch + '\\0').encode('cp932')
        return RawCommand(0xe, struct.pack('<3I', flag, a2, len(ret)) + ret)

    def process_name(self, txt):
        quoted = False
        if txt.startswith('【') and txt.endswith('】'):
            txt = txt[1:-1]
            quoted = True
        try:
            txt = self.names_dick[txt]
        except KeyError:
            print('missing name: %s' % txt)
        if quoted:
            return '【%s】' % txt
        return txt

    def process_message(self, msg):
        return msg

    def message(self, args):
        msg = SptMessage(args)
        if msg.name:
            msg.name = self.process_name(msg.name)
        msg.msg = self.process_message(msg.msg)
        return RawCommand(0x8, msg.to_spt())








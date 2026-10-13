# %%
import shlex
from itertools import groupby
from dataclasses import dataclass, field
from struct import unpack, pack
from enum import Enum

HALF_ASCII = list('!"#$%&\'()*+,-./:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                  '[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ 0123456789')

FULL_ASCII = list('！＂＃＄％＆’（）＊＋，―．／：；＜＝＞？＠'
                  'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
                  '［＼］＾＿｀ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔ'
                  'ｕｖｗｘｙｚ｛｜｝～　０１２３４５６７８９')

H2F = {h: f for h, f in zip(HALF_ASCII, FULL_ASCII)}

unpack_uint8 = lambda x: unpack("B", x)[0]
unpack_uint16 = lambda x: unpack("<H", x)[0]
unpack_uint32 = lambda x: unpack("<I", x)[0]

pack_uint8 = lambda x: pack("B", x)
pack_uint16 = lambda x: pack("<H", x)
pack_uint32 = lambda x: pack("<I", x)

read_until = lambda f, x: b"".join(iter(lambda: f.read(1), x))
DELIM = "&&"
split_delim = lambda l: [tuple(y) for x, y in groupby(l, lambda d: d == DELIM) if not x]

ref_strings = set()

class TYPE(Enum):
    INT8 = 0, 1
    INT16 = 1, 2
    STRING = 2, 2
    REPEAT = 3, 0

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj
    
    def __init__(self, _, size):
        self.size = size

    def read(self, f):
        if self.size == 1:
            return unpack_uint8(f.read(1))
        elif self.size == 2:
            res = unpack_uint16(f.read(2))
            if self == TYPE.STRING:
                ref_strings.add(res)
            return res
        elif self.size == 0:
            raise ValueError("Cannot read a REPEAT type")

class OPCODE(Enum):
    NEWLINE = 0, "nl", ()
    PRINT_TEXT = 1, "t", (TYPE.STRING, )
    COMMENT = 2, "//", (TYPE.STRING, )
    CLEAR_TEXT = 4, "cls", ()
    CHOICE = 10, "choice", (TYPE.STRING, TYPE.INT8, TYPE.INT8, TYPE.INT8, TYPE.INT8, TYPE.INT8, TYPE.INT8)
    PRINT_NAME = 13, "n", (TYPE.STRING, )
    SET_BG = 16, "bg", (TYPE.INT8, TYPE.STRING)
    DISPLAY_CHAR = 18, "char", (TYPE.INT8, TYPE.INT8, TYPE.STRING, TYPE.REPEAT)
    PLAY_VOICE = 20, "voice", (TYPE.STRING, )
    PLAY_SE = 21, "se", (TYPE.STRING, )
    GOTO = 26, "goto", (TYPE.INT8, TYPE.STRING)
    TITLE = 44, "title", (TYPE.STRING, )
    ITEM = 59, "item", (TYPE.INT8, TYPE.STRING, TYPE.INT16, TYPE.INT8, TYPE.INT8, TYPE.INT8)
    EFFECT = 108, "effect", (TYPE.STRING, )
    PLAY_BGVOICE = 106, "bgvoice", (TYPE.STRING, )
    UNK3 = 3
    UNK5 = 5
    UNK6 = 6
    UNK7 = 7
    UNK8 = 8
    UNK9 = 9
    UNK12 = 12
    UNK14 = 14
    UNK17 = 17
    UNK19 = 19
    UNK22 = 22
    UNK23 = 23
    UNK25 = 25
    UNK27 = 27
    UNK28 = 28
    UNK29 = 29
    UNK41 = 41
    UNK30 = 30
    UNK31 = 31
    UNK32 = 32
    UNK33 = 33
    UNK34 = 34
    UNK42 = 42
    UNK52 = 52
    UNK35 = 35
    UNK36 = 36
    UNK37 = 37
    UNK38 = 38
    UNK39 = 39
    UNK40 = 40
    UNK43 = 43
    UNK45 = 45
    UNK46 = 46
    UNK47 = 47
    UNK48 = 48
    UNK49 = 49
    UNK50 = 50
    UNK51 = 51
    UNK53 = 53
    UNK54 = 54
    UNK55 = 55
    UNK56 = 56
    UNK57 = 57
    UNK58 = 58
    UNK60 = 60
    UNK61 = 61
    UNK64 = 64
    UNK65 = 65
    UNK66 = 66
    UNK67 = 67
    UNK68 = 68
    UNK69 = 69
    UNK70 = 70
    UNK71 = 71
    UNK72 = 72
    UNK73 = 73
    UNK75 = 75
    UNK76 = 76
    UNK77 = 77
    UNK78 = 78
    UNK79 = 79
    UNK80 = 80
    UNK81 = 81
    UNK82 = 82
    UNK83 = 83
    UNK84 = 84
    UNK85 = 85
    UNK86 = 86
    UNK87 = 87
    UNK88 = 88
    UNK89 = 89
    UNK90 = 90
    UNK91 = 91
    UNK92 = 92
    UNK93 = 93
    UNK94 = 94
    UNK95 = 95
    UNK96 = 96
    UNK97 = 97
    UNK98 = 98
    UNK99 = 99
    UNK100 = 100
    UNK101 = 101
    UNK102 = 102
    UNK103 = 103
    UNK104 = 104
    UNK105 = 105
    UNK107 = 107

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj
    
    def __init__(self, _, cmd_str="unk", args_type=(TYPE.INT8, TYPE.REPEAT)):
        self.cmd_str = cmd_str if cmd_str != "unk" else f"unk{self.value}"
        self.args_type = args_type

    def __repr__(self):
        return self.name

OPCODE.get_opcode = {opcode.cmd_str: opcode for opcode in OPCODE}

@dataclass
class OP():
    offset: int
    line_n: int
    size: int = field(repr=False)
    opcode: OPCODE
    args: tuple
    
    @staticmethod
    def _get_args(f, size, opcode):
        size -= 1 # opcode
        args = []
        last_type = None
        if size == 0:
            return tuple()
        for t in opcode.args_type:
            if t != TYPE.REPEAT:
                args.append(t.read(f))
                size -= t.size
                last_type = t
            else:
                while size > 0:
                    args.append(last_type.read(f))
                    size -= last_type.size
        assert size == 0, f"Size mismatch: {size}"
        return tuple(args)
    
    def _expand_repeat_args(args_type, args):
        if TYPE.REPEAT in args_type:
            args_type = args_type[:-1] + (args_type[-2], ) * (len(args) - len(args_type) + 1)
        return args_type

    @staticmethod
    def read_binary(f):
        line_n = unpack_uint16(f.read(2))
        size = unpack_uint8(f.read(1))
        offset = f.tell()
        opcode = OPCODE(unpack_uint8(f.read(1)))
        args = OP._get_args(f, size, opcode)
        return OP(offset, line_n, size, opcode, args)
    

    @staticmethod
    def read_text(line_n: int, op: list[str], strings: dict[str], h2f=False):
        args = []
        line_n = line_n
        offset = 0
        opcode = OPCODE.get_opcode[op[0]]
        args_type = OP._expand_repeat_args(opcode.args_type, op[1:])

        for arg, type in zip(op[1:], args_type):
            if type == TYPE.INT8 or type == TYPE.INT16:
                args.append(int(arg))
            if type == TYPE.STRING:
                if h2f and (op[0] == "t" or op[0] == "n"):
                    arg = "".join([H2F.get(c, c) for c in arg])
                if arg == "":
                    args.append(0xFFFF)
                    continue
                elif strings.get(arg) is None:
                    strings[arg] = len(strings)
                args.append(strings[arg])
        
        size = 1 + sum(args_type[i].size for i, _ in enumerate(args))
        
        return OP(offset, line_n, size, opcode, tuple(args))
    
    def to_text(self, strings):
        args = []
        args_type = OP._expand_repeat_args(self.opcode.args_type, self.args)

        for type, arg in zip(args_type, self.args):
            if type == TYPE.INT8 or type == TYPE.INT16:
                args.append(str(arg))
            elif type == TYPE.STRING:
                if arg >= len(strings):
                    args.append(str('""'))
                    continue
                quoted = f'"{strings[arg]}"'
                args.append(quoted)
            else:
                raise ValueError(f"Unknown type {type}")

        return f"{self.opcode.cmd_str} {' '.join(args)}".strip()
    
    def to_bytes(self):
        res = bytearray()
        res += pack_uint16(self.line_n)
        res += pack_uint8(self.size)
        res += pack_uint8(self.opcode.value)
        
        args_type = OP._expand_repeat_args(self.opcode.args_type, self.args)

        for type, arg in zip(args_type, self.args):
            if type == TYPE.INT8 or type == TYPE.INT16:
                res += pack_uint8(arg) if type == TYPE.INT8 else pack_uint16(arg)
            elif type == TYPE.STRING:
                res += pack_uint16(arg)
            else:
                raise ValueError(f"Unknown type {type}")
            
        return res

@dataclass
class SCE():
    size: int
    string_offset: int
    string_count: int
    line_count: int
    ops: list[OP] = field(repr=False)
    strings: list[str] = field(repr=False)
    xrefs: list[tuple[int, str]] = field(repr=False)

    @staticmethod
    def read_binary(f):
        size = unpack_uint32(f.read(4))
        string_offset = unpack_uint32(f.read(4))
        string_count = unpack_uint16(f.read(2))
        xref_count = unpack_uint16(f.read(2))
        line_count = unpack_uint32(f.read(4))
        ops = []
        strings = []

        while True:
            if f.tell() + 1 >= string_offset + 0x10:
                break
            ops.append(OP.read_binary(f))

        f.read(1)
        bc = 1
        xref_offsets = []
        for _ in range(xref_count):
            xref_offsets.append(unpack_uint16(f.read(2)))
            bc += 2
        
        for _ in range(string_count):
            x = read_until(f, b"\x00")
            bc += len(x) + 1
            strings.append(x.decode("sjis"))

        xrefs = []
        for offset in xref_offsets:
            x = read_until(f, b"\x00")
            bc += len(x) + 1
            xrefs.append((offset, x.decode("sjis")))


        # some sanity checks to make sure we read everything correctly
        bc += sum(map(lambda x: x.size + 1 + 2, ops)) # size: 1 byte, line_n: 2 bytes
        assert bc == size, f"Size mismatch: {bc} != {size}"
        assert ops[-1].line_n == line_count, f"Line count mismatch: {ops[-1].line_n} != {line_count}"
        assert len(strings) == string_count, f"String count mismatch: {len(strings)} != {string_count}"
        print("SCE read successfully:")
        print(f"Size: 0x{size:x}, String offset: 0x{string_offset:x}, String count: {string_count}, xRef count: {xref_count}, Line count: {line_count + 1}")
        unref_strings = set(range(string_count)) - ref_strings
        if len(unref_strings) != 0:
            print(f"Warning: strings {unref_strings} are not referenced")
            print("\ttxt2bin on the output will fail if the relevant OPCODE args are not implemented")
            print("\tStrings:")
            for i in unref_strings:
                print(f"\t{i}: {repr(strings[i])}")
        return SCE(size, string_offset, string_count, line_count, ops, strings, xrefs)
    
    @staticmethod
    def read_text(f, h2f=False):
        ops = []
        strings = {}
        lines = f.readlines()
        xrefs = lines[0][7:]
        if xrefs == "\n":
            xrefs = []
        else:
            xrefs = [(int(x.split(":")[0]), x.split(":")[1]) for x in xrefs.strip().split(",")]   
        try:
            for line_n, line in enumerate(lines[1:]):
                for op in split_delim(shlex.split(line.strip())):
                    ops.append(OP.read_text(line_n, op, strings, h2f))
        except Exception as e:
            print(f"Error reading line {line_n + 1}: {line}")
            print(e)
            return None
        
        strings, _ = zip(*sorted(strings.items(), key=lambda x: x[1]))
        string_offset = sum(i.size + 3 for i in ops) + 1
        size = string_offset + sum(len(s.encode("sjis")) + 1 for s in strings) \
                             + sum(len(xref.encode("sjis")) + 1 + 2 for _, xref in xrefs)

        return SCE(size, string_offset, len(strings), ops[-1].line_n, ops, list(strings), xrefs)

    def to_text(self):
        line_n = 0
        line = []
        res = ""
        res += f"xrefs: "
        for offset, xref in self.xrefs:
            res += f"{offset}:{xref},"
        res = res.strip(",") + "\n"

        for op in self.ops:
            if op.line_n != line_n:
                res += f" {DELIM} ".join(line) + "\n"
                line_n = op.line_n
                line = []
            line.append(op.to_text(self.strings))
        res += f" {DELIM} ".join(line) + "\n"
        return res.strip()
    
    def to_bytes(self):
        res = bytearray()
        res += pack_uint32(self.size)
        res += pack_uint32(self.string_offset)
        res += pack_uint16(self.string_count)
        res += pack_uint16(len(self.xrefs))
        res += pack_uint32(self.line_count)

        for op in self.ops:
            res += op.to_bytes()
        
        res += b"\x00"

        for offset, _ in self.xrefs:
            res += pack_uint16(offset)

        for s in self.strings:
            res += s.encode("sjis") + b"\x00"

        for _, xref in self.xrefs:
            res += xref.encode("sjis") + b"\x00"

        return res
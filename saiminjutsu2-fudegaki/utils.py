import pathlib, struct, io, os


class BinaryFileError(Exception):
    pass


class UnexpectedEof(BinaryFileError):
    pass


class RecognitionError(BinaryFileError):
    pass


class DecompressionError(BinaryFileError):
    def __init__(self, comp_rem, result_rem):
        self.comp_rem = comp_rem
        self.result_rem = result_rem


class BinaryFile:
    def __init__(self, bf, entry=None, rec_only=False):
        self.bfile = bf
        if isinstance(self.bfile, (str, pathlib.PurePath)):
            self.bfile = open(self.bfile, 'rb')
        if entry is not None:
            self.offset = entry.offset
            self.size = entry.size
            self.name = entry.name
        else:
            self.offset = 0
            if isinstance(self.bfile, io.BytesIO):
                self.bfile.seek(0, io.SEEK_END)
                self.size = self.bfile.tell()
                self.bfile.seek(0, io.SEEK_SET)
            elif isinstance(self.bfile, (bytearray, bytes)):
                self.size = len(self.bfile)
                self.bfile = io.BytesIO(self.bfile)
            else:
                self.size = os.stat(self.bfile.name).st_size

        try:
            self.recognize()
        except UnexpectedEof:
            raise RecognitionError('too small file')
        if not rec_only:
            self.open()

    def recognize(self):
        pass

    def open(self):
        pass

    def read_exactly(self, num):
        bts = self.bfile.read(num)
        if len(bts) != num:
            raise UnexpectedEof('%d bytes expected to be available (reading)' % num)
        return bts

    def peek_enough(self, num):
        bts = self.bfile.peek(num)
        if len(bts) < num:
            pos = self.bfile.tell()
            bts = self.bfile.read(num)
            self.bfile.seek(pos, io.SEEK_SET)
            if len(bts) != num:
                raise UnexpectedEof('%d bytes expected to be available (peeking)' % num)
        return bts

    def checked_seek(self, off, relative=False):
        if not relative:
            dst = self.offset + off
        else:
            dst = self.bfile.tell() + off
        if dst > (self.offset + self.size) or dst < self.offset:
            raise BinaryFileError('seek offset is beyond limits')
        self.bfile.seek(dst, io.SEEK_SET)

    def unpack(self, fmt):
        sz = struct.calcsize(fmt)
        return struct.unpack(fmt, self.read_exactly(sz))

    def read_uint32(self):
        return int.from_bytes(self.read_exactly(4), 'little', signed=False)

    def read_cstring(self, max_len=500):
        bts = self.bfile.peek(max_len)
        null = bts.find(b'\x00')
        if null < 0 and len(bts) < max_len:
            pos = self.bfile.tell()
            bts = self.bfile.read(max_len)
            self.bfile.seek(pos, io.SEEK_SET)
            null = bts.find(b'\x00')
        if null < 0:
            raise BinaryFileError("couldn't find the null")
        self.read_exactly(null+1)
        return bts[0:null]

    def limited_cstring(self, size):
        st = self.read_exactly(size)
        null = st.find(b'\x00')
        if null < 0:
            null = len(st)
        return st[0:null]

    def file_size(self):
        return self.size

    @staticmethod
    def ensure_outpath(out_path):
        if isinstance(out_path, str):
            out_path = pathlib.Path(out_path)
        if not out_path.exists():
            out_path.mkdir(parents=True)
        return out_path

    def decomp_init(self, comped_size, decomped_size):
        test_size(comped_size)
        test_size(decomped_size)
        comped = self.read_exactly(comped_size)
        decomped = bytearray(decomped_size)
        return comped, decomped


# ---------------------------------------------------------------------------------------------------------------


SIZE_LIMIT = 10000 * 10000 * 4


def test_size(sz):
    if sz > SIZE_LIMIT:
        raise BinaryFileError('%d is probably a really huge size.' % sz)

# ---------------------------------------------------------------------------------------------------------------



import os
import re
import json
import sqlite3
import struct

def _init_():
    file_all = os.listdir()
    if 'intermediate_file' not in file_all:
        os.mkdir('intermediate_file')
    if 'output' not in file_all:
        os.mkdir('output')
    if 'input' not in file_all:
        os.mkdir('input')

_init_()

def create_dict(extract_jp_line):
    '''
    jp_all.txt文本建立空value字典，保存到 jp_chs.json
    '''
    encoding = 'utf8'
    with open('intermediate_file/jp_all.txt', 'r', encoding=encoding) as f:
        text_jp = f.readlines()
    try:
        with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
            j_c = json.loads(f.read())
    except Exception:
        print('First time building a dictionary!')
        j_c = dict()
    print('Total', len(text_jp), 'words')
    cnt = 0
    for line in text_jp:
        # 去掉每行多余的符号
        _t = extract_jp_line(line)
        if _t not in j_c:
            j_c[_t] = ''
            cnt += 1
    print('Add keyword：', cnt, 'words')
    with open('intermediate_file/jp_chs.json', 'w', encoding=encoding) as f:
        f.write(json.dumps(j_c, ensure_ascii=False, indent=4))


def check_dict():
    '''
    打开jp-chs.json文件检查
    '''
    encoding = 'utf8'
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        js = json.loads(f.read())
    with open('intermediate_file/jp_all.txt', 'r', encoding=encoding) as f:
        text_jp = f.readlines()
    cnt = 0
    for key in js:
        if not js[key]:
            cnt += 1
    print(list(js.keys())[:10])
    print('需要翻译：', len(list(js.keys())), '条')
    print('剩余翻译：', cnt, '条')

    print('共有日文：', len(text_jp), '条， 应翻译：', len(set(text_jp)), '条')

def to_bytes(a: int, _len: int) -> int:
    return int.to_bytes(a, _len, byteorder='little')


def from_bytes(a: bytes):
    return int.from_bytes(a, byteorder='little')


def byte_add(*args):
    ans = 0
    for i in args:
        ans += i
    return ans & 0xff

def delete_zero(name: bytes, encoding='utf8'):
    while not name[-1]:
        name = name[:-1]
    return name.decode(encoding)
    
def open_json(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.loads(f.read())


def save_json(path, data):
    with open(path, 'w', encoding='utf8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))


def open_file(path, encoding='utf8'):
    if encoding == '':
        with open(path, 'rb') as f:
            return f.read()
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def save_file(path, data):
    with open(path, 'w', encoding='utf8') as f:
        f.write(data)


def open_file_b(path):
    with open(path, 'rb') as f:
        return f.read()


def save_file_b(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def to_hex(data: bytes):
    '''
    将字节串输出为a5 ea a5 e9 a5 af a5的格式
    '''
    return ' '.join([hex(x)[-2:] for x in data])

class MED():
    '''
    _VIEW 前24字节完全一样
    name: [120224][ルネ Team Bitters] マリッジブルー[婚約者がいるのに、どうしてこんな男に……]
    key: KASAYA

    name: [110325][ルネ Team Bitters] それでも妻を愛してる
    key: _NEWNANAMI

    name: [130222][ルネ Team Bitters]魔法少女はキスして変身る
    key: IORI

    name: [150529]光翼戦姫エクスティア1
    key: e010exstia01lusteris

    name: [160129]光翼戦姫エクスティア２
    key: e012exstia02lusteris

    name: [170512]光翼戦姫エクスティアA
    key: 013exstiaAlusterise

    CreateFontIndirectA  8D 45 BC 8B 55 FC 83 C2 1B   -0x6   B0 86 90
                         70 23 00 00   -> 00 60 00 00
    读取对话文字的点阵    00 00 00 89 55 F0 83 7D F0 40 0F 8C
    读取人名、log、对话框点阵 7D 21 8B 55 FC 83 C2 E0
    存储字体点阵的函数    8B 45 C8 25 FF 00 00 00  81 7D C8 00 A0 00 00 
    让生成文字点阵的范围包含0xA000-0xE040的编码 75 07 C7 45 BC E0 00 00 00

    ＄０ 主人公名字
    ^([fbps]|CH|#|[0-9]).+\n
    '''
    # key = b'\xd0\xcd\xce\xc9\x9b\x88\x8d\x8c\x97\x9f\xcd\x94\x8b\x8d\x8c\x9b\x8e\x97\x8d\x9b'
    def extract_med_by_file():
        '''
        从input文件夹内的脚本文件抽取文本
        文本自动存入intermediate_file/jp_all.txt        
        '''
        def _has_jp(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            for ch in line:
                if ('\u0800' <= ch and ch <= '\u9fa5') or ('\uff01' <= ch <= '\uff5e'):
                    return True
            return False

        file_all = os.listdir('input')
        ans = []
        for f in file_all:
            _ans = []
            _data = pf.open_file_b(f'input/{f}')
            # _data = MED.decrypt(_data)
            _offset = int.from_bytes(_data[4:8], byteorder='little') + 0x10
            _str = _data[_offset:]
            _buff = b''
            for i in _str:
                if i:
                    _buff += pf.to_bytes(i, 1)
                else:
                    try:
                        _buff = _buff.decode('cp932')
                        if _has_jp(_buff) and _buff[0] not in ';#':
                            # if name:
                            #     _buff = _buff.replace('＄０', name)
                            _ans.append(_buff)
                    except Exception as e:
                        print(e)
                        print(f, _buff)
                    _buff = b''
            _t = {}
            for i in _ans:
                _t[i]=""
            pf.save_file(f"chs/{f}", json.dumps(_t, ensure_ascii=False, indent=2))

    def create_talbe(target:str, chs:str):
        '''
        创建替换的行
        '''
        a = target
        b = ('b\'\\x'+'\\x'.join(a.split())+'\'')
        b = (eval(b))
        c = b'\x00'+chs.encode('sjis')+b'\x00'*(len(b)-len(chs.encode('sjis'))-1)
        ans = (b, 0, b,c, 1,chs)
        print(ans)

    def decrypt(_data: bytes, _key=None):
        '''

        '''
        if _key:
            MED.key = _key
        _data = bytearray(_data)

        for i in range(0x10, len(_data)):
            _data[i] = (_data[i]+MED.key[(i-0x10) % len(MED.key)]) & 0xff

        return _data

    def encrypt(_data: bytes, _key=None):
        if _key:
            MED.key = _key
        _data = bytearray(_data)

        for i in range(0x10, len(_data)):
            _data[i] = (_data[i]-MED.key[(i-0x10) % len(MED.key)]) & 0xff

        return _data

    def extract_med():
        '''
        从input文件夹内的脚本文件抽取文本
        文本自动存入intermediate_file/jp_all.txt        
        '''
        def _has_jp(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            for ch in line:
                if ('\u0800' <= ch and ch <= '\u9fa5') or ('\uff01' <= ch <= '\uff5e'):
                    return True
            return False

        file_all = os.listdir('input')
        ans = []
        for f in file_all:
            _data = open_file_b(f'input/{f}')
            # _data = MED.decrypt(_data)
            _offset = int.from_bytes(_data[4:8], byteorder='little') + 0x10
            _str = _data[_offset:]
            _buff = b''
            for i in _str:
                if i:
                    _buff += to_bytes(i, 1)
                else:
                    try:
                        _buff = _buff.decode('cp932', errors='ignore')
                        if _has_jp(_buff) and _buff[0] not in ';#':
                            # if name:
                            #     _buff = _buff.replace('＄０', name)
                            ans.append(_buff)
                    except Exception as e:
                        print(e)
                        print(f, _buff)
                    _buff = b''
        save_file('intermediate_file/jp_all.txt', '\n'.join(ans))

    def fix_dict():
        '''
        只支持gb2312编码，所以要把所有的繁体都转为简体
        不要出现半角符号
        '''
        table = {
            "増": "增",
            "発": "发",
            "▁": "_",
            "様": "样",
            '変': '变',
            '駄': '驭',
            '関': '关',
            '対': '对',
            '単': '单',
            '増': '增',
            '弾': '弹',
            '効': '效',
            '実': '实',
            '晩': '晚',
            '楽': '乐',
            '験': '验',
            '悪': '恶',
            '戦': '战',
            '駅': '驿',
            '姫': '姬',
            '険': '险',
            '栄': '容',
            '円': '圆',
            '気': '气',
            '巣': '巢',
            '発': '发',
            '拠': '处',
            '撃': '击',
            '圧': '压',
            '応': '应',
            '沢': '尺',
            '姉': '姐',
            '臓': '脏',
            '薬': '药',
            '覚': '觉',
            '闘': '斗'
        }
        jp_chs = open_json('intermediate_file/jp_chs.json')
        # cnt = 0
        failed = {}
        for key in jp_chs:
            value = jp_chs[key]
            # value = strB2Q(value)
            value = lc.Converter('zh-hans').convert(value)
            for ch in table:
                value = value.replace(ch, table[ch])

            jp_chs[key] = value
        save_json('intermediate_file/jp_chs.json', jp_chs)
        print('繁体转换简体成功！')
        # print('无法编码：', len(failed), failed)

    def format_med(text: str, name=None):
        if name:
            text = text.replace('＄０', name)
        return text

    def output():
        '''
        替换原文件中的文本，将替换后的结果放入output文件夹
        使用前需要利用jp_all.txt生成翻译字典，并将字典翻译放入intermediate_file文件夹，字典的格式为
        {
            'Japanese':'chinese',
            'Japanese':'chinese',
            ...
        }
        '''
        def _has_jp(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            for ch in line:
                if ('\u0800' <= ch and ch <= '\u9fa5') or ('\uff01' <= ch <= '\uff5e'):
                    return True
            return False

        file_all = os.listdir('input')
        jp_chs = open_json('intermediate_file/jp_chs.json')
        cnt = 0
        failed = []
        for f in file_all:
            _data = open_file_b(f'input/{f}')
            _data = bytearray(_data)
            _offset = int.from_bytes(_data[4:8], byteorder='little') + 0x10
            _str = _data[_offset:]
            _buff = b''
            while _offset < len(_data):
                if _data[_offset]:
                    _buff += _data[_offset:_offset+1]
                else:
                    try:
                        _str = _buff.decode('cp932')
                        # print(_str)
                        # if len(failed) >5:
                        #     return
                        if not _has_jp(_str) or _str[0] in ';#':
                            _offset += 1
                            continue
                        # if name:
                        #     _str = _str.replace('＄０', name)
                        if _str in jp_chs:
                            if jp_chs[_str]:
                                _offset -= len(_buff)
                                jp_chs[_str] = jp_chs[_str].replace('——','――')
                                _new_bytes = jp_chs[_str].encode('sjis', errors='ignore')
                                _data[_offset:_offset+len(_buff)] = _new_bytes
                                _offset += len(_new_bytes)
                                cnt += 1
                            else:
                                failed.append(_str)
                                # 这里会将日文用GBK编码
                                # _offset -= len(_buff)
                                # _new_bytes = _str.encode('gb2312', errors='ignore')
                                # _data[_offset:_offset+len(_buff)] = _new_bytes
                                # _offset += len(_new_bytes)
                        else:
                            failed.append(_str)
                    except Exception as e:
                        print('Fail')
                        print(f, _buff)
                        print(e)
                        print()
                    finally:
                        _buff = b''
                _offset += 1
            _data[:4] = to_bytes(len(_data)-0x10, 4)
            save_file_b(f'output/{f}', _data)
        save_file('intermediate_file/failed.txt', '\n'.join(failed))
        print('Replaced:', cnt)
        print('Failed:', len(failed))

    def unpack(path='md_scr.med', output='input'):
        def remove_dumplicate_str(key):
            for i in range(2, len(key)+1):
                cnt = int(len(key) / i + 1)
                tmp = key[:i]
                ans = bytearray(tmp)
                tmp *= cnt
                tmp = tmp[:len(key)]
                # print(tmp, len(tmp))
                if tmp == key:
                    # print(ans)
                    return ans
            return None
        data = open_file_b(path)
        entry_length = from_bytes(data[4:6])
        entry_count = from_bytes(data[6:8])
        name_list = []
        if not os.path.exists(output):
            os.mkdir(output)
        for i in range(entry_count):
            entry = data[16+i*entry_length:16+(i+1)*entry_length]
            offset = from_bytes(entry[-4:])
            length = from_bytes(entry[-8:-4])
            unk = from_bytes(entry[-12:-8])
            name = ''
            for i in entry:
                if not i:
                    break
                else:
                    name += chr(i)

            _file_data = data[offset:offset+length]
            file_name = f'{name}_{unk}'
            save_file_b(f'{output}/{file_name}', _file_data)
            # print(file_name, offset, length)
            name_list.append(file_name)
        key = None
        file_all = os.listdir(output)
        for f in file_all:
            if f[:5] == '_VIEW':
                _view = open_file_b(f'{output}/{f}')
                _raw = _view[0x10:0x28]
                _base = b'\x00\x23\x52\x55\x4C\x45\x5F\x56\x49\x45\x57\x45\x52\x00\x3A\x56\x49\x45\x57\x5F\x30\x00\x7B\x00'
                key = []
                for i in range(24):
                    t = _raw[i] - _base[i]
                    t = -t
                    if t < 0:
                        t += 256
                    key.append(t)
                break
        if key:
            print(bytearray(key))
            key = bytearray(map(lambda x: x & 0xff, key))
            key = remove_dumplicate_str(key)
            # print(bytearray(key))
            ans = {
                'name_list': name_list,
                'key': key.decode('cp932'),
                'entry_length': entry_length
            }
            print(key, len(key))
            for f in file_all:
                _data = open_file_b(f'{output}/{f}')
                _data = MED.decrypt(_data, ans['key'].encode())
                save_file_b(f'{output}/{f}', _data)
            if not os.path.exists('intermediate_file'):
                os.mkdir('intermediate_file')

            save_json(f'intermediate_file/file_index.json', ans)
        else:
            print('Unable to decrypt')

    def repack(path='output'):
        '''
        
        '''
        file_index = open_json(f'intermediate_file/file_index.json')
        name_list = file_index['name_list']

        entry_length = file_index['entry_length']
        header = b'MDE0'+to_bytes(entry_length, 1)+b'\x00'
        header += to_bytes(len(name_list), 2) + b'\x00' * 8
        entry_all = []
        file_data = []
        offset = 0x10 + len(name_list)*entry_length

        for f in name_list:

            _p = len(f)-1
            while f[_p] != '_':
                _p -= 1
            name = f[:_p].encode()
            name += b'\x00'*(entry_length-len(name)-12)
            unk = int(f[_p+1:])
            unk = to_bytes(unk, 4)
            _file_data = open_file_b(f'{path}/{f}')
            _file_data = MED.encrypt(_file_data, file_index['key'].encode())
            entry = name + unk + \
                to_bytes(len(_file_data), 4) + to_bytes(offset, 4)
            entry_all.append(entry)
            file_data.append(_file_data)
            offset += len(_file_data)

        save_file_b('_new.med', header +
                    b''.join(entry_all) + b''.join(file_data))

    def fix_exe(path):
        '''
        一键汉化exe
        表格式 (特征码, 偏移, 原目标码, 替换目标码, 次数, 名称)
        '''
        table = [
            #(b'\x8D\x45\xBC\x8B\x55\xFC\x83\xC2\x1B', -0x6, b'\x8A\x40\x1A',
            # b'\xB0\x86\x90', 1, 'CreateFontIndirectA Charset'),
            #(b'\x70\x23\x00\x00', 0, b'\x70\x23\x00\x00',
            # b'\x00\x60\x00\x00', 4, '缓冲区大小'),
            (b'\x00\x00\x00\x89\x55\xF0\x83\x7D\xF0\x40\x0F\x8C', -0x25, 
             b'\xF0', b'\xFE', 1, '读取对话文字的点阵 0xF0->0xFE'),
            (b'\x00\x00\x00\x89\x55\xF0\x83\x7D\xF0\x40\x0F\x8C', -0x18, 
             b'\xA0', b'\xFE', 1, '读取对话文字的点阵 0xA0->0xFE'),
            (b'\x00\x00\x00\x89\x55\xF0\x83\x7D\xF0\x40\x0F\x8C', -0xF, 
             b'\xE0', b'\xFE', 1, '读取对话文字的点阵 0xE0->0xFE'),
            (b'\x00\x00\x00\x89\x55\xF0\x83\x7D\xF0\x40\x0F\x8C', 0x13, 
             b'\xFC', b'\xFE', 1, '读取对话文字的点阵 0xFC->0xFE'),
            (b'\x00\x00\x00\x89\x55\xF0\x83\x7D\xF0\x40\x0F\x8C', 0x34, 
             b'\xBD', b'\xBF', 1, '读取对话文字的点阵 0xBD->0xBF'),
            (b'\x00\x00\x00\x89\x55\xF0\x83\x7D\xF0\x40\x0F\x8C', 0x53, 
             b'\x3F', b'\x7F', 1, '读取对话文字的点阵 0x3F->0x7F'),
            (b'\x00\x00\x00\x89\x55\xF0\x83\x7D\xF0\x40\x0F\x8C', 0x59, 
             b'\xBD', b'\xBF', 1, '读取对话文字的点阵 0xBD->0xBF'),
            (b'\x7D\x21\x8B\x55\xFC\x83\xC2\xE0', 0x30,
             b'\xF0', b'\xFE', 1, '读取人名、log、对话框点阵 0xF0->0xFE'),
            (b'\x7D\x21\x8B\x55\xFC\x83\xC2\xE0', 0x40,
             b'\xA0', b'\xFE', 1, '读取人名、log、对话框点阵 0xA0->0xFE'),
            (b'\x7D\x21\x8B\x55\xFC\x83\xC2\xE0', 0x49,
             b'\xE0', b'\xFE', 1, '读取人名、log、对话框点阵 0xE0->0xFE'),
            (b'\x7D\x21\x8B\x55\xFC\x83\xC2\xE0', 0x6A,
             b'\xFC', b'\xFE', 1, '读取人名、log、对话框点阵 0xFC->0xFE'),
            (b'\x7D\x21\x8B\x55\xFC\x83\xC2\xE0', 0x8E,
             b'\xBD', b'\xBF', 1, '读取人名、log、对话框点阵 0xBD->0xBF'),
            (b'\x7D\x21\x8B\x55\xFC\x83\xC2\xE0', 0xAC,
             b'\x3F', b'\x7F', 1, '读取人名、log、对话框点阵 0x3F->0x7F'),
            (b'\x7D\x21\x8B\x55\xFC\x83\xC2\xE0', 0xB2,
             b'\xBD', b'\xBF', 1, '读取人名、log、对话框点阵 0xBD->0xBF'),
            (b'\x81\x7D\xC8\x00\xA0\x00\x00', 0x17,
             b'\xBD', b'\xBF', 1, '存储字体点阵的函数 0xBD->0xBF'),
            (b'\x81\x7D\xC8\x00\xA0\x00\x00', 0x35,
             b'\xE0', b'\x81', 1, '存储字体点阵的函数 0xE0->0x81'),
            (b'\x81\x7D\xC8\x00\xA0\x00\x00', 0x39, b'\x83\xC2\x1F',
             b'\x90\x90\x90', 1, '存储字体点阵的函数 0x83C2EF->0x909090'),
            (b'\x81\x7D\xC8\x00\xA0\x00\x00', 0x3E,
             b'\xBD', b'\xBF', 1, '存储字体点阵的函数 0xBD->0xBF'),
            (b'u\x07\xc7E\xc0\xe0\x00\x00\x00', 0x2C, 
             b'\xFC', b'\xFE', 1, '第二个字节的上限改为FE'),
            (b'u\x07\xc7E\xc0\xe0\x00\x00\x00', 0x38, 
             b'\xF0', b'\xF8', 1, '第一个字节的上限改为F8'),
            (b'u\x07\xc7E\xc0\xe0\x00\x00\x00', 0x5, 
             b'\xe0', b'\xa0', 1, '不跳过0xA0-0xE0'),
            #(b'\x00\x83\x8D\x81\x5B\x83\x68\x00', 0, b'\x00\x83\x8D\x81\x5B\x83\x68\x00',
            # b'\x00\xd4\xd8\xc8\xeb\x00\x00\x00', -1, '载入'),
            #(b'\x00\x83\x5A\x81\x5B\x83\x75\x00', 0, b'\x00\x83\x5A\x81\x5B\x83\x75\x00',
            # b'\x00\xb1\xa3\xb4\xe6\x00\x00\x00', -1, '保存'),
            #(b'\x00\x90\xDD\x92\xE8\x00', 0, b'\x00\x90\xDD\x92\xE8\x00',
            # b'\x00\xc9\xe8\xb6\xa8\x00', -1, '设定'),
            #(b'\x00\x8F\x49\x97\xB9\x00', 0, b'\x00\x8F\x49\x97\xB9\x00',
            # b'\x00\xbd\xe1\xca\xf8\x00', -1, '结束'),
            #(b'\x00\x83\x51\x81\x5B\x83\x80\x8F\x49\x97\xB9\x00', 0, b'\x00\x83\x51\x81\x5B\x83\x80\x8F\x49\x97\xB9\x00',
            # b'\x00\xd3\xce\xcf\xb7\xbd\xe1\xca\xf8\x00\x00\x00', -1, '游戏结束'),
            #(b'\x00\x89\xF1\x91\x7A\x8F\x49\x97\xB9\x00', 0, b'\x00\x89\xF1\x91\x7A\x8F\x49\x97\xB9\x00',
            # b'\x00\xbb\xd8\xcf\xeb\xbd\xe1\xca\xf8\x00', -1, '回想结束'),
            #(b'\x00\x83\x5E\x83\x43\x83\x67\x83\x8B\x82\xD6\x96\xDF\x82\xE9\x00', 0,
            # b'\x00\x83\x5E\x83\x43\x83\x67\x83\x8B\x82\xD6\x96\xDF\x82\xE9\x00',
            # b'\x00\xb7\xb5\xbb\xd8\xb1\xea\xcc\xe2\x00\x00\x00\x00\x00\x00\x00', -1, '返回标题'),
            #(b'\x00\x8D\xC5\x91\xE5\x89\xBB\x00', 0, b'\x00\x8D\xC5\x91\xE5\x89\xBB\x00',
            # b'\x00\xd7\xee\xb4\xf3\xbb\xaf\x00', -1, '最大化'),
            #(b'\x00\x83\x5E\x83\x43\x83\x67\x83\x8B\x82\xD6\x96\xDF\x82\xE8\x82\xDC\x82\xB7\x82\xA9\x81\x48\x00', 0, 
            # b'\x00\x83\x5E\x83\x43\x83\x67\x83\x8B\x82\xD6\x96\xDF\x82\xE8\x82\xDC\x82\xB7\x82\xA9\x81\x48\x00',
            # b'\x00\xb7\xb5\xbb\xd8\xb1\xea\xcc\xe2\xc2\xf0\xa3\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', -1, '返回标题吗？'),
            #(b'\x00\x83Q\x81[\x83\x80\x82\xf0\x8fI\x97\xb9\x82\xb5\x82\xdc\x82\xb7\x82\xa9\x81H\x00', 0,
            # b'\x00\x83Q\x81[\x83\x80\x82\xf0\x8fI\x97\xb9\x82\xb5\x82\xdc\x82\xb7\x82\xa9\x81H\x00',
            # b'\x00\xbd\xe1\xca\xf8\xd3\xce\xcf\xb7\xc2\xf0\xa3\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', -1, '结束游戏吗？'),
            #(b'\x00\x83\x8d\x81[\x83h\x82\xb5\x82\xdc\x82\xb7\x82\xa9\x81H\x00', 0,
            # b'\x00\x83\x8d\x81[\x83h\x82\xb5\x82\xdc\x82\xb7\x82\xa9\x81H\x00',
            # b'\x00\xc8\xb7\xc8\xcf\xb6\xc1\xb5\xb5\xc2\xf0\xa3\xbf\x00\x00\x00\x00\x00', -1, '确认读档吗？'),
            #(b'\x00\x82p\x83Z\x81[\x83u\x82\xb5\x82\xdc\x82\xb5\x82\xbd\x00', 0, 
            # b'\x00\x82p\x83Z\x81[\x83u\x82\xb5\x82\xdc\x82\xb5\x82\xbd\x00', 
            # b'\x00\xbf\xec\xcb\xd9\xb1\xa3\xb4\xe6\xb3\xc9\xb9\xa6\x00\x00\x00\x00\x00', -1, '快速保存成功')
        ]
        data = open_file_b(path)
        data = bytearray(data)
        for t in table:
            if t[-2] == -1:
                while True:
                    if len(t[3]) != len(t[2]):
                        print('元组错误：', t)
                        return
                    pos = data.find(t[0])
                    if pos == -1:
                        break
                    pos += t[1]
                    _len = len(t[2])
                    if data[pos:pos+_len] != t[2]:
                        print('目标不匹配：', data[pos:pos+_len], t)
                        return
                    data[pos:pos+_len] = t[3]
                    print('替换成功：', t)

            for _ in range(t[-2]):
                if len(t[3]) != len(t[2]):
                    print('元组错误：', t)
                    return
                pos = data.find(t[0])
                if pos == -1:
                    print('未找到：', t)
                    return
                pos += t[1]
                _len = len(t[2])
                if data[pos:pos+_len] != t[2]:
                    print('目标不匹配：', data[pos:pos+_len], t)
                    return
                data[pos:pos+_len] = t[3]
                print('替换成功：', t)
        save_file_b('new_'+path, data)
   
 
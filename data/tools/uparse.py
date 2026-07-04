"""Minimal UE3 (KF2, ver 871) .u package parser: name/import/export tables + defaultproperties."""
import struct, sys, json

class Pkg:
    def __init__(self, path):
        self.data = open(path, 'rb').read()
        d = self.data
        magic, ver, lic = struct.unpack_from('<IHH', d, 0)
        assert magic == 0x9E2A83C1, hex(magic)
        self.ver, self.lic = ver, lic
        off = 8
        self.header_size, = struct.unpack_from('<I', d, off); off += 4
        flen, = struct.unpack_from('<i', d, off); off += 4
        off += flen  # folder name (ascii, incl null)
        self.pkg_flags, = struct.unpack_from('<I', d, off); off += 4
        (self.name_count, self.name_off, self.exp_count, self.exp_off,
         self.imp_count, self.imp_off) = struct.unpack_from('<6I', d, off)
        self.read_names()
        self.read_imports()
        self.read_exports()

    def read_names(self):
        d = self.data; off = self.name_off
        self.names = []
        for _ in range(self.name_count):
            ln, = struct.unpack_from('<i', d, off); off += 4
            if ln < 0:
                s = d[off:off - ln*2 - 2].decode('utf-16-le', 'replace'); off += -ln*2
            else:
                s = d[off:off+ln-1].decode('latin1'); off += ln
            off += 8  # name flags u64
            self.names.append(s)
        self.names_end = off

    def fname(self, off):
        idx, num = struct.unpack_from('<ii', self.data, off)
        s = self.names[idx]
        if num: s = f'{s}_{num-1}'
        return s

    def read_imports(self):
        d = self.data; off = self.imp_off
        self.imports = []
        for _ in range(self.imp_count):
            cls_pkg = self.fname(off); cls = self.fname(off+8)
            outer, = struct.unpack_from('<i', d, off+16)
            name = self.fname(off+20)
            self.imports.append(dict(cls_pkg=cls_pkg, cls=cls, outer=outer, name=name))
            off += 28
        self.imp_end = off

    def read_exports(self):
        d = self.data; off = self.exp_off
        self.exports = []
        for i in range(self.exp_count):
            cls_i, sup_i, outer_i = struct.unpack_from('<iii', d, off)
            name = self.fname(off+12)
            arch_i, = struct.unpack_from('<i', d, off+20)
            objflags, = struct.unpack_from('<Q', d, off+24)
            ssize, soff, expflags = struct.unpack_from('<iii', d, off+32)
            ngen, = struct.unpack_from('<i', d, off+44)
            entry_len = 48 + ngen*4 + 16 + 4
            self.exports.append(dict(i=i+1, cls_i=cls_i, sup_i=sup_i, outer=outer_i,
                                     name=name, size=ssize, off=soff, flags=objflags))
            off += entry_len
        self.exp_end = off

    def objname(self, idx):
        """Resolve a package index to object name."""
        if idx == 0: return 'None'
        if idx > 0: return self.exports[idx-1]['name']
        return self.imports[-idx-1]['name']

    def fullname(self, idx):
        if idx == 0: return 'None'
        parts = []
        while idx != 0:
            if idx > 0:
                e = self.exports[idx-1]; parts.append(e['name']); idx = e['outer']
            else:
                e = self.imports[-idx-1]; parts.append(e['name']); idx = e['outer']
        return '.'.join(reversed(parts))

    # ---- property parsing ----
    def read_fstring(self, off):
        ln, = struct.unpack_from('<i', self.data, off); off += 4
        if ln < 0:
            s = self.data[off:off - ln*2 - 2].decode('utf-16-le', 'replace'); off += -ln*2
        elif ln > 0:
            s = self.data[off:off+ln-1].decode('latin1'); off += ln
        else:
            s = ''
        return s, off

    def parse_props(self, off, end, depth=0):
        props = []
        d = self.data
        while off < end - 7:
            name = self.fname(off)
            if name == 'None':
                off += 8
                break
            typ = self.fname(off+8)
            size, arridx = struct.unpack_from('<ii', d, off+16)
            off += 24
            val = None
            if typ == 'BoolProperty':
                val = d[off] != 0; off += 1
            elif typ == 'StructProperty':
                sname = self.fname(off); off += 8
                val = ('struct:'+sname, d[off:off+size].hex()); off += size
            elif typ == 'ByteProperty':
                ename = self.fname(off); off += 8
                if ename == 'None':
                    val = d[off]; off += 1
                else:
                    val = ename + '::' + self.fname(off); off += 8
            elif typ == 'IntProperty':
                val, = struct.unpack_from('<i', d, off); off += size
            elif typ == 'FloatProperty':
                val, = struct.unpack_from('<f', d, off); val = round(val, 6); off += size
            elif typ == 'ObjectProperty' or typ == 'ComponentProperty' or typ == 'ClassProperty':
                oi, = struct.unpack_from('<i', d, off); val = self.fullname(oi); off += size
            elif typ == 'NameProperty':
                val = self.fname(off); off += size
            elif typ == 'StrProperty':
                val, _ = self.read_fstring(off); off += size
            elif typ == 'ArrayProperty':
                cnt, = struct.unpack_from('<i', d, off)
                val = ('array', cnt, d[off+4:off+size].hex()); off += size
            else:
                val = ('raw:'+typ, d[off:off+size].hex()); off += size
            props.append((name, arridx, typ, val))
        return props, off

    def find(self, pat):
        pat = pat.lower()
        return [e for e in self.exports if pat in e['name'].lower()]

if __name__ == '__main__':
    p = Pkg(sys.argv[1])
    print('names', len(p.names), 'imports', len(p.imports), 'exports', len(p.exports))
    print('sample names:', p.names[:10])
    print('sample exports:')
    for e in p.exports[:8]:
        print(' ', e['name'], 'cls=', p.objname(e['cls_i']), 'outer=', p.objname(e['outer']), 'off=', e['off'], 'size=', e['size'])

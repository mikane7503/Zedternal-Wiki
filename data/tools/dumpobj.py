"""Dump default-object properties by export name; decodes string/float/int arrays.

Usage: python dumpobj.py <package.u> <ExportName>
e.g.   python data/tools/dumpobj.py ZedternalRBPerkpackage.u Default__DKHollowWeaponData
"""
import sys, struct, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uparse import Pkg

def decode_array(hexdata, cnt):
    raw = bytes.fromhex(hexdata)
    n = len(raw)
    if cnt == 0: return []
    # try float array
    if n == cnt*4:
        vals = [round(v,6) for v in struct.unpack(f'<{cnt}f', raw)]
        ints = struct.unpack(f'<{cnt}i', raw)
        # heuristic: floats if values look sane
        if all(-1e7 < v < 1e7 for v in vals) and any(abs(v)>1e-30 and abs(v)<1e6 or v==0 for v in vals):
            return {'floats': vals, 'ints': list(ints)}
        return {'ints': list(ints)}
    # try string array
    out = []
    off = 0
    try:
        for _ in range(cnt):
            ln, = struct.unpack_from('<i', raw, off); off += 4
            if ln < 0:
                out.append(raw[off:off-ln*2-2].decode('utf-16-le','replace')); off += -ln*2
            elif ln > 0:
                out.append(raw[off:off+ln-1].decode('latin1')); off += ln
            else:
                out.append('')
        if off == n:
            return out
    except Exception:
        pass
    return {'rawhex': hexdata[:200], 'count': cnt}

def dump(pkgfile, objname):
    p = Pkg(pkgfile)
    matches = [e for e in p.exports if e['name'].lower() == objname.lower()]
    if not matches:
        matches = [e for e in p.exports if objname.lower() in e['name'].lower()]
    result = {}
    for e in matches[:3]:
        off = e['off'] + 4  # skip netindex
        props, _ = p.parse_props(off, e['off'] + e['size'])
        rec = {}
        for (name, arridx, typ, val) in props:
            if typ == 'ArrayProperty':
                _, cnt, hexdata = val
                val = decode_array(hexdata, cnt)
            key = name if arridx == 0 else f'{name}[{arridx}]'
            rec[key] = val
        result[p.fullname(e['i'])] = rec
    return result

if __name__ == '__main__':
    r = dump(sys.argv[1], sys.argv[2])
    print(json.dumps(r, indent=1, ensure_ascii=False, default=str))

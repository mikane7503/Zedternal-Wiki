"""Extract every embedded UnrealScript source (TextBuffer/ScriptText) from a .u package.

The mod's .u packages (UE3 ver 871) ship with un-stripped ScriptText, so the
complete original source of all ~2,300 classes can be pulled out directly --
no decompiler needed. defaultproperties blocks are NOT part of the text; read
those with dumpobj.py against the class's Default__<name> export instead.

Usage: python data/tools/extract_sources.py <package.u> <output_dir>
e.g.   python data/tools/extract_sources.py ZedternalRBPerkpackage.u extracted_src
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uparse import Pkg


def extract(pkg_path, outdir):
    p = Pkg(pkg_path)
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for e in p.exports:
        if p.objname(e['cls_i']) != 'TextBuffer':
            continue
        off = e['off'] + 4          # NetIndex
        assert p.fname(off) == 'None'
        off += 8 + 8                # 'None' terminator + Pos + Top
        text, _ = p.read_fstring(off)
        cls = p.fullname(e['i']).split('.')[0]
        with open(os.path.join(outdir, cls + '.uc'), 'w', encoding='utf-8', errors='replace') as f:
            f.write(text)
        n += 1
    print(f'{pkg_path}: {n} sources extracted to {outdir}')


if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2])

import ast, subprocess, re, sys, json
from pathlib import Path
root = Path('.')
py = [p for p in subprocess.check_output(['git','ls-files','*.py'],text=True).split()]
lits=set()
for p in py:
    t=ast.parse(Path(p).read_text())
    for n in ast.walk(t):
        if isinstance(n,ast.Constant) and isinstance(n.value,str):
            for piece in re.split(r'\{[^}]*\}|\n', n.value):
                piece=piece.strip()
                if len(piece)>=10 and re.search(r'[A-Za-z]{3}',piece): lits.add(piece)
md=[p for p in subprocess.check_output(['git','ls-files','*.md'],text=True).split()]
out={}
for p in md:
    text=Path(p).read_text()
    hits=sorted(l for l in lits if l in text and ' ' in l)
    if hits: out[p]=hits
json.dump(out,open(sys.argv[1],'w'),indent=1)
for p,h in out.items(): print(len(h),p)

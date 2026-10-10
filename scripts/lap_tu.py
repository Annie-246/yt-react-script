"""List sentences in the spoken part that repeat a word (syllable or 2-syllable compound)."""
import re, sys, pathlib, collections
sys.path.insert(0, r"C:\Users\pthao\.claude\skills\yt-react-script\scripts")
from check_script import read_aloud, cau_trong
STOP = set("và là thì mà của có một không những các cho để với đã được bị nó này đó rồi cũng lại sẽ trong ở khi nên vì như hay hoặc còn chỉ đều nhưng từ tới đến theo lúc đang vẫn mới chứ thể gì nào ra vào".split())
md = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
body = read_aloud(md)
n = 0
for para in body.split("\n"):
    for s in cau_trong(para):
        w = [x for x in re.findall(r"[\w./@]+", s.lower())]
        c = collections.Counter(x for x in w if x not in STOP)
        bi = collections.Counter(" ".join(w[i:i+2]) for i in range(len(w)-1))
        rep = [k for k, v in c.items() if v > 1] + [k for k, v in bi.items() if v > 1]
        if rep:
            n += 1
            print(f"- [{', '.join(rep)}] {s}")
print("TONG", n)

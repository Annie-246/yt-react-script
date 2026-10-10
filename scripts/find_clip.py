"""Find exact timestamps in a .vtt for a short phrase (3-5 words work best).

Usage:
  python find_clip.py <file.vtt> "phrase" ["phrase2" ...]
Prints h:mm:ss of every cue containing the phrase (case-insensitive, whitespace-normalized).
"""
import html
import pathlib
import re
import sys


def cues(path):
    raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    ts_re = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.\d{3} -->")
    out, prev, sec = [], "", None
    for block in re.split(r"\n\n+", raw):
        sec, texts = None, []
        for line in block.strip().split("\n"):
            m = ts_re.match(line)
            if m:
                h, mi, s = map(int, m.groups())
                sec = h * 3600 + mi * 60 + s
                continue
            if line.startswith(("WEBVTT", "Kind:", "Language:")) or not line.strip():
                continue
            t = html.unescape(re.sub(r"<[^>]+>", "", line)).strip()
            if t:
                texts.append(t)
        if sec is None:
            continue
        for t in texts:
            if t != prev:
                out.append((sec, t))
                prev = t
    return out


def norm(s):
    return re.sub(r"[^\w\s']", " ", s.lower())


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cs = cues(sys.argv[1])
    # also build a rolling window of 3 cues so phrases spanning cue breaks still match
    windows = []
    for i in range(len(cs)):
        text = " ".join(t for _, t in cs[i:i + 3])
        windows.append((cs[i][0], text))
    for phrase in sys.argv[2:]:
        p = re.sub(r"\s+", " ", norm(phrase)).strip()
        hits = [sec for sec, text in windows if p in re.sub(r"\s+", " ", norm(text))]
        uniq = []
        for h in hits:
            if not uniq or h - uniq[-1] > 8:
                uniq.append(h)
        print(f'"{phrase}":', ", ".join("%d:%02d:%02d" % (h // 3600, (h % 3600) // 60, h % 60) for h in uniq) or "KHÔNG THẤY (thử cụm ngắn hơn)")


if __name__ == "__main__":
    main()

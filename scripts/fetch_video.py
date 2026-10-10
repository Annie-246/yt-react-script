"""Fetch YouTube metadata + subtitles with yt-dlp and build a chaptered transcript.

Usage:
  python fetch_video.py <URL> <out_dir> [--langs vi-orig,vi,en-orig,en] [--vtt existing.vtt]

Writes into out_dir:
  video-info.md   metadata + chapters + words per chapter
  transcript.md   sentence-level transcript with [h:mm:ss] marks, split by chapters
  <id>.<lang>.vtt raw subtitles (kept for find_clip.py)
"""
import argparse
import html
import json
import pathlib
import re
import subprocess
import sys
import time


def run(cmd, timeout=300):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")


def hms(s):
    s = int(s)
    return "%d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)


def parse_chapters(description, duration):
    chapters = []
    for line in (description or "").splitlines():
        m = re.match(r"^\s*\(?(\d{1,2}):(\d{2})(?::(\d{2}))?\)?\s*[-–:]?\s*(.+?)\s*$", line)
        if not m:
            continue
        a, b, c, title = m.groups()
        sec = (int(a) * 3600 + int(b) * 60 + int(c)) if c else (int(a) * 60 + int(b))
        chapters.append((sec, title.strip()))
    chapters = sorted(set(chapters))
    if not chapters:
        chapters = [(0, "Toàn bộ")]
    chapters.append((10**9, "END"))
    return chapters


def clean_vtt(path):
    raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n\n+", raw)
    ts_re = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.\d{3} -->")
    cues, prev = [], ""
    for b in blocks:
        sec, texts = None, []
        for line in b.strip().split("\n"):
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
                cues.append((sec, t))
                prev = t
    return cues


def group_sentences(cues, max_words=40):
    groups, cur, cur_t = [], [], None
    for sec, t in cues:
        if cur_t is None:
            cur_t = sec
        cur.append(t)
        joined = " ".join(cur)
        if re.search(r"[.?!…]$", t) or len(joined.split()) >= max_words:
            groups.append((cur_t, joined))
            cur, cur_t = [], None
    if cur:
        groups.append((cur_t, " ".join(cur)))
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out_dir")
    ap.add_argument("--langs", default="vi-orig,vi,en-orig,en")
    ap.add_argument("--vtt", default=None, help="use an existing .vtt instead of downloading")
    args = ap.parse_args()

    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1. metadata
    print("[1/3] metadata ...")
    res = run(["yt-dlp", "--skip-download", "--dump-single-json", "--no-warnings", args.url])
    if res.returncode != 0 or not res.stdout.strip():
        print("yt-dlp metadata failed:", res.stderr[-800:])
        sys.exit(1)
    info = json.loads(res.stdout)
    vid = info.get("id")
    duration = info.get("duration") or 0
    chapters = parse_chapters(info.get("description", ""), duration)
    if info.get("chapters"):
        chapters = sorted({(int(c["start_time"]), c.get("title", "")) for c in info["chapters"]}) + [(10**9, "END")]

    # 2. subtitles
    vtt = None
    if args.vtt:
        vtt = pathlib.Path(args.vtt)
    else:
        print("[2/3] subtitles ...")
        langs = [l.strip() for l in args.langs.split(",") if l.strip()]
        for lang in langs:
            target = out / f"{vid}.{lang}.vtt"
            if target.exists():
                vtt = target
                break
            for attempt in range(3):
                r = run([
                    "yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
                    "--sub-langs", lang, "--sub-format", "vtt", "--sleep-subtitles", "2",
                    "-o", str(out / vid), "--no-warnings", args.url,
                ])
                if target.exists():
                    vtt = target
                    break
                if "429" in (r.stderr + r.stdout):
                    wait = 15 * (attempt + 1)
                    print(f"   429 for {lang}, waiting {wait}s ...")
                    time.sleep(wait)
                else:
                    break
            if vtt:
                break
    if not vtt or not vtt.exists():
        print("KHÔNG có phụ đề. Dùng whisper để bóc lời thoại rồi chạy lại với --vtt.")
        (out / "video-info.md").write_text(
            f"# {info.get('title')}\n\nKhông có phụ đề. Kênh: {info.get('channel')} · Dài: {hms(duration)}\n", encoding="utf-8")
        sys.exit(2)

    # 3. transcript
    print("[3/3] transcript ...")
    cues = clean_vtt(vtt)
    groups = group_sentences(cues)
    lines, ci = [], -1
    for sec, t in groups:
        while ci + 1 < len(chapters) - 1 and sec >= chapters[ci + 1][0]:
            ci += 1
            lines += ["", "## [%s] %s" % (hms(chapters[ci][0]), chapters[ci][1]), ""]
        if ci == -1:
            ci = 0
            lines += ["", "## [%s] %s" % (hms(chapters[0][0]), chapters[0][1]), ""]
        lines.append("[%s] %s" % (hms(sec), t))
    (out / "transcript.md").write_text("\n".join(lines), encoding="utf-8")

    total_words = sum(len(t.split()) for _, t in cues)
    info_lines = [
        f"# {info.get('title')}",
        "",
        f"- Kênh: {info.get('channel') or info.get('uploader')}",
        f"- Đăng: {info.get('upload_date')}",
        f"- Dài: {hms(duration)} · View: {info.get('view_count')} · Like: {info.get('like_count')} · Comment: {info.get('comment_count')}",
        f"- Link: {info.get('webpage_url')}",
        f"- Phụ đề: {vtt.name} · Tổng từ: {total_words} · Số câu: {len(groups)}",
        "",
        "## Chương và số từ",
        "",
        "| Mốc | Chương | Từ |",
        "|---|---|---|",
    ]
    for i in range(len(chapters) - 1):
        a, b = chapters[i][0], chapters[i + 1][0]
        w = sum(len(t.split()) for s, t in cues if a <= s < b)
        info_lines.append(f"| {hms(a)} | {chapters[i][1]} | {w} |")
    info_lines += ["", "## Mô tả video", "", (info.get("description") or "").strip()]
    (out / "video-info.md").write_text("\n".join(info_lines), encoding="utf-8")

    print(f"OK  words={total_words}  sentences={len(groups)}  chapters={len(chapters)-1}")
    print(f"    {out / 'transcript.md'}")
    print(f"    {out / 'video-info.md'}")
    print(f"    {vtt}")


if __name__ == "__main__":
    main()

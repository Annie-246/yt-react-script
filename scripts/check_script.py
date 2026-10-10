"""Rà kịch bản theo hồ sơ đo được từ MẪU THẬT của user.

Ngưỡng KHÔNG do Claude tự đặt. Tất cả đo từ `references/mau-kich-ban.md`,
tức kịch bản Lauren Tan do user tự sửa bằng tay:

    209 câu · trung bình 19 từ · trung vị 19
    p75 = 26 · p90 = 34 · p95 = 36 · p99 = 45 · dài nhất 54
    20% số câu dài hơn 28 từ  → ngưỡng 28 cũ là SAI, đã bỏ
    4 câu từ 3 chữ trở xuống trên 4.138 từ → câu chốt ngắn là hợp lệ

Dùng: python check_script.py <kich-ban.md> [--mau <mau-kich-ban.md>]
"""
import pathlib
import re
import sys

# Hồ sơ đo từ mẫu thật. Sửa số ở đây chỉ khi đo lại mẫu mới.
MAU = dict(tb_min=15, tb_max=24, dai_toi_da=55, cau_cut_moi_n_tu=500)

BANNED = [
    "bạn có bao giờ tự hỏi", "đúng vậy", "wow", "thì wow", "đó chính là", "tạm dịch",
    "không quá lời", "nên là", "còn bạn,", "bạn biết mình cần làm gì rồi đó",
    "cùng chơi với mình", "let's go", "mình thề", "nghe đi nghe lại", "rất là",
    "sủa gâu", "năm 19 tuổi", "rồi, dừng", "ghi vào sổ",
]
RELAY = [
    "steven hỏi", "alex đáp", "ông đáp", "ông bảo", "rồi hỏi lại", "hỏi lại rằng",
    "ông kia nói", "alex trả lời:", "steven nói:", "alex nói:", "ông nói:", "anh ấy hỏi",
]
ENGLISH = [
    "fortitude", "tolerance", "resilience", "adaptability", "cộng cộng", "trừ trừ",
    "tử số", "mẫu số", "scalable", "retention", "proof of outcome", "framework", "mindset",
]
CAU_CHOT_HOP_LE = {
    "Nghĩa là", "Ví dụ", "Thứ nhất", "Thứ hai", "Thứ ba", "Thứ tư",
    "Một", "Hai", "Ba", "Bốn", "Chỉ có vậy", "Không", "Hết",
}


def read_aloud(md):
    body = md
    if "## 0." in body:
        body = body.split("## 0.", 1)[1]
    body = body.split("## PHỤ LỤC", 1)[0]
    body = re.sub(r"`\[CLIP[^\n]*\n[^\n]*", "", body)
    body = re.sub(r"🟨[^\n]*|🟦[^\n]*", "", body)
    body = re.sub(r"^#.*$", "", body, flags=re.M)
    body = re.sub(r"^\*\*Thời lượng.*$", "", body, flags=re.M)
    return body


def cau_trong(text):
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]


def main():
    path = pathlib.Path(sys.argv[1])
    md = path.read_text(encoding="utf-8")
    body = read_aloud(md)
    words = len(body.split())
    sents = cau_trong(body)
    lens = sorted(len(s.split()) for s in sents)
    n = max(len(lens), 1)
    tb = sum(lens) // n

    print(f"Lời đọc: {words} từ · {words/230:.0f} phút đọc nhanh · {words/180:.0f} phút đọc thong thả")
    print(f"Câu: {n} · trung bình {tb} từ · dài nhất {lens[-1] if lens else 0}")
    print(f"(mẫu của user: trung bình 19, dài nhất 54)")

    problems = 0

    # 1. Nhịp ở cấp cả bài, không bắt bẻ từng câu
    if tb < MAU["tb_min"]:
        print(f"  NHỊP     trung bình {tb} từ/câu, thấp hơn mẫu nhiều. Câu đang nhát gừng, nối lại cho mượt.")
        problems += 1
    elif tb > MAU["tb_max"]:
        print(f"  NHỊP     trung bình {tb} từ/câu, cao hơn mẫu. Câu đang lê thê, tách bớt.")
        problems += 1

    cau_cut = [s for s in sents if len(s.split()) <= 3
               and not re.match(r"^[\d.,%]+$", s)
               and s.rstrip(".!?") not in CAU_CHOT_HOP_LE]
    cho_phep = max(1, words // MAU["cau_cut_moi_n_tu"])
    if len(cau_cut) > cho_phep:
        print(f"  CÂU CỤT  {len(cau_cut)} câu dưới 4 chữ, mẫu chỉ có khoảng {cho_phep}. Ví dụ: {cau_cut[:3]}")
        problems += 1

    # 2. Rà từng dòng
    lines = md.splitlines()
    in_body = False
    for i, line in enumerate(lines, 1):
        if line.startswith("## 0."):
            in_body = True
        if line.startswith("## PHỤ LỤC"):
            in_body = False
        if not in_body or line.startswith(("`[CLIP", "🟨", "🟦", "#", "|", "---", "*")):
            continue
        low = line.lower()
        for p in BANNED:
            if re.search(re.escape(p) + r"(?![\wÀ-ỹ])", low):
                print(f"  CẤM      dòng {i}: '{p}' → {line[:80]}")
                problems += 1
        for p in RELAY:
            if p in low:
                print(f"  HỘI THOẠI dòng {i}: '{p}' → {line[:80]}")
                problems += 1
        for p in ENGLISH:
            if p in low:
                print(f"  TIẾNG ANH dòng {i}: '{p}' → {line[:80]}")
                problems += 1
        for s in cau_trong(line):
            if len(s.split()) > MAU["dai_toi_da"]:
                print(f"  QUÁ DÀI  dòng {i}: câu {len(s.split())} từ, vượt cả câu dài nhất của mẫu → {s[:70]}...")
                problems += 1
            m = re.search(r",\s*(hay|tức là|nghĩa là|ví dụ|chẳng hạn|hoặc)\s+[^,]{2,30},", s)
            if m:
                print(f"  CỤM CHÈN dòng {i}: '{m.group(0)[:45]}' → tách thành câu riêng")
                problems += 1

    # 3. Cấu trúc, lấy từ mẫu thật
    print("Cấu trúc:")
    checks = [
        ("Mục 0 tên 'THÔNG ĐIỆP CHÍNH, NÓI NGAY'", "THÔNG ĐIỆP CHÍNH" in md),
        ("Có 'Bài học rút ra' ở cuối các mục", md.count("Bài học rút ra") >= 2),
        ("Phần kết mở bằng 'Tóm lại'", "Tóm lại" in md),
        ("Có xin like share subscribe và bật chuông", "bật chuông" in md),
        ("Có Phụ lục A bảng clip", "PHỤ LỤC A" in md),
        ("Có Phụ lục B nguồn và số cần kiểm", "PHỤ LỤC B" in md),
        ("Có ít nhất 3 ô cho user tự nói", md.count("BẠN TỰ NÓI") >= 3),
    ]
    for ten, ok in checks:
        print(f"  {'ok  ' if ok else 'THIẾU'} {ten}")
        if not ok:
            problems += 1

    for tag in ("[SỬA SỐ]", "[KIỂM]"):
        c = md.count(tag)
        if c:
            print(f"Có {c} chỗ {tag}, nhớ liệt kê cho user.")

    print("SẠCH" if problems == 0 else f"{problems} chỗ cần xem lại")


if __name__ == "__main__":
    main()

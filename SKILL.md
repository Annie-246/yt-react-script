---
name: yt-react-script
description: Viết kịch bản video YouTube dạng reaction hoặc tóm tắt từ một link video/podcast. Tự tải phụ đề bằng yt-dlp, đọc trọn transcript, viết brief và kịch bản đọc theo bằng văn nói tiếng Việt mượt (mặc định góc marketing cho chủ shop, doanh nghiệp nhỏ, người làm content và ads), tự rà lỗi câu chữ, xuất PDF khổ điện thoại và gửi cho user. Dùng khi user gửi link YouTube và nói "viết kịch bản", "làm script", "react video này", "làm như lần trước", "brief lại video này", hoặc gõ /yt-react-script.
---

# /yt-react-script — kịch bản video YouTube từ một link

Nguồn chuẩn duy nhất về giọng là `references/mau-kich-ban.md`, tức kịch bản Lauren Tan do CHÍNH USER tự sửa bằng tay. Đọc file đó trước khi viết bất cứ câu nào.

`references/quy-tac-viet.md` là suy diễn của Claude từ góp ý trong hội thoại, có chỗ đã được chứng minh là sai. Khi hai file mâu thuẫn thì theo mẫu.

Thư mục skill: `C:\Users\pthao\.claude\skills\yt-react-script\`

## Đầu vào và đầu ra

**Đầu vào:** một link YouTube. Có thể kèm góc nhìn, số điều, đối tượng. Nếu user không nói thì dùng mặc định, không hỏi lại:
- Đối tượng: chủ shop, chủ doanh nghiệp nhỏ, người làm content, người chạy quảng cáo. Góc nhìn: marketing.
- Số điều: 8 cho podcast trên 90 phút, 5 hoặc 6 cho video dưới 60 phút.
- Dạng: reaction có clip gốc, có ô cho user tự nói kinh nghiệm.

**Đầu ra** trong thư mục `C:\Users\pthao\Downloads\kich-ban-yt\<yymmdd>-<slug>\`:

| File | Nội dung |
|---|---|
| `video-info.md` | Tiêu đề, kênh, ngày đăng, view, thời lượng, số từ từng chương |
| `transcript.md` | Lời thoại đầy đủ có mốc giây, chia theo chương |
| `<id>.<lang>.vtt` | Phụ đề gốc, dùng để tìm mốc clip chính xác |
| `brief.md` | Tóm tắt podcast: luận điểm chính, bảng từng chương 1 dòng, 10–12 câu đắt nhất có dịch, số liệu, ý đã dùng và để dành |
| `kich-ban.md` | Kịch bản đọc theo, đúng khung và quy tắc |
| `kich-ban.pdf` | Bản in khổ điện thoại, gửi cho user bằng SendUserFile |

## Công cụ cần có

`yt-dlp`, `python` với `markdown` và `pypdfium2` (pip), Google Chrome hoặc Edge để in PDF. Kiểm nhanh: `yt-dlp --version && python -c "import markdown, pypdfium2"`. Thiếu thì `pip install markdown pypdfium2`.

## Quy trình

### Bước 1. Tải phụ đề và dựng transcript (2–3 phút)

```bash
python "C:\Users\pthao\.claude\skills\yt-react-script\scripts\fetch_video.py" "<URL>" "<thư mục ra>"
```

Script tự lấy metadata, chương từ mô tả, phụ đề theo thứ tự ưu tiên `vi-orig, vi, en-orig, en`, rồi dọn thành `transcript.md` và `video-info.md`. Có sẵn `.vtt` rồi thì thêm `--vtt <file>` để khỏi tải lại.

Đọc `video-info.md` để biết video dài bao nhiêu, bao nhiêu chương, chương nào nhiều từ. Nếu không có phụ đề nào thì báo user và dùng whisper (skill `media-processing` hoặc `reel-scrape` nếu có).

### Bước 2. Đọc TRỌN transcript

Đọc hết bằng `sed -n 'a,bp' transcript.md` từng khối 180 dòng, không đọc mỗi chương đầu. Lý do: những đoạn đắt nhất (chuyện mẹ mất, 4 câu hỏi sức chịu đựng) nằm ở 30 phút cuối của tập Hormozi. Vừa đọc vừa ghi ra nháp: ý chính từng chương, số liệu, câu trích nguyên văn, chuyện có đầu có cuối.

### Bước 3. Tra thêm về nhân vật (5 phút)

Dùng WebSearch tìm 4–6 sự thật để mở đầu kiểu hồ sơ nhân vật: chức danh, công ty, doanh thu, sách, kỷ lục, và đặc biệt là những việc nhân vật đã làm liên quan tới chủ đề video (ví dụ Alex từng bán một công ty AI trước khi bảo đừng chạy theo AI). Số nào lấy từ bài phân tích không chính chủ thì đánh `[KIỂM]` và ghi nguồn vào Phụ lục B. Không gọi ai là "tỷ phú" nếu tài sản thật dưới 1 tỷ đô.

### Bước 4. Viết `brief.md`

Theo mẫu trong `references/khung-kich-ban.md` phần "Brief". Bảng chương mỗi dòng 1 câu, 10–12 câu đắt nhất kèm mốc giây và dịch, số liệu đáng nhớ, và cuối cùng là danh sách "đã dùng trong kịch bản / để dành cho phần 2".

### Bước 5. Chọn điều và chọn clip

- Chọn 6–8 điều theo tiêu chí: đổi được cách người xem làm marketing hoặc bán hàng; có một chuyện hoặc một ví dụ kể được từ đầu đến cuối; có ít nhất một câu trích nguyên văn. Xếp thứ tự có mạch: từ chủ đề nóng của video → cách làm → giá và khách → cách thử → điều cảm xúc nhất để cuối.
- Mỗi điều 2–3 clip, mỗi clip dưới 90 giây, tổng clip dưới 40% thời lượng video, luôn xen mặt user giữa các clip (The Diary Of A CEO và các kênh lớn hay claim bản quyền).
- Mốc giây lấy bằng script, không ước tay:

```bash
python "C:\Users\pthao\.claude\skills\yt-react-script\scripts\find_clip.py" "<file .vtt>" "câu tiếng Anh ngắn 3-5 chữ"
```

### Bước 6. Viết `kich-ban.md`

Đọc lại `references/mau-kich-ban.md` TRƯỚC TIÊN, rồi mới tới `references/quy-tac-viet.md`.

`mau-kich-ban.md` là kịch bản Lauren Tan do CHÍNH USER tự sửa bằng tay. Đây là nguồn chuẩn duy nhất về giọng. Khi quy tắc mâu thuẫn với mẫu thì theo mẫu.

File `mau-cu-claude-tu-viet-KHONG-DUNG.md` là kịch bản Claude tự viết, user KHÔNG duyệt. Đừng dùng làm mẫu.

**Cấu trúc lấy từ mẫu thật, không lấy từ `khung-kich-ban.md`** (file đó Claude tự nghĩ ra, đã lỗi thời):

- **Mục 0 tên là "THÔNG ĐIỆP CHÍNH, NÓI NGAY"**, dài khoảng 600 từ. Nói hết đáp án ngay trong mở màn, liệt kê đủ các ý chính và giải thích từng ý một hai câu. KHÔNG giấu để lật ở cuối.
- **Mỗi mục nội dung** đi bốn bước: một hai câu nêu vấn đề, rồi `[CLIP]`, rồi giải thích lại nội dung clip bằng tiếng Việt, rồi kéo về việc của người xem. Kết mục bằng "**Bài học rút ra là**".
- **Tiêu đề mục** viết hoa nửa đầu: `## 2. VIỆC THỨ NHẤT: đặt quy chuẩn để AI tự kiểm tra bài của chính nó`.
- **Mục kết** mở bằng "Tóm lại", nhắc lại các ý, giao một việc nhỏ cho người xem, nhá phần hai, rồi xin like share subscribe và bật chuông.
- **Hai phụ lục:** A là bảng clip cho người dựng (tổng clip dưới 20% video gốc), B là nguồn và số cần kiểm.
- **Độ dài:** bản user duyệt là 3.900 từ cho video 31 tới 35 phút. Dài không phải lỗi.

Ba quy tắc quan trọng nhất, vì user đã chê đúng 3 lỗi này:
1. **Văn nói mượt:** câu đủ chủ ngữ vị ngữ, nối bằng "thì, mà, nên, nhưng, vì, còn, cho nên". Không câu rời rạc kiểu "Mẹ mất. Tai nạn."
2. **Không kể lại hội thoại** kiểu "Steven hỏi, Alex đáp, ông bảo, rồi hỏi lại". Clip đã chiếu hội thoại, lời đọc chỉ nói ý.
3. **Ví dụ phải hiểu ngay lần đầu:** nói ý trước, kể một ví dụ từ đầu đến cuối, chốt bằng "nghĩa là". Không chồng nhiều ví dụ, bớt số, không thuật ngữ tiếng Anh khi có từ Việt.

Và tuyệt đối không dùng câu cửa miệng của kênh mẫu Trương Phương (danh sách trong quy tắc), vì user sợ bị nhận ra là bắt chước.

### Bước 6b. NotebookLM viết lại từng phần cho tự nhiên

Đọc `references/notebooklm-viet-lai.md` rồi làm theo. Tóm tắt: dùng skill `notebooklm`, một notebook chung "Kịch bản YT react"; mỗi video là một nguồn đặt tên theo mã `<yymmdd>-<slug>`; từng mục kịch bản được gửi kèm yêu cầu văn phong và khoá nguồn; Claude kiểm câu trích rồi ghép vào `kich-ban.md`. Giữ bản nháp ở `kich-ban-v0-nhap.md`. Nếu NotebookLM chưa đăng nhập, chưa có nguồn của video, hoặc lỗi thì bỏ qua bước này, giữ bản nháp và báo user, không chặn cả quy trình.

### Bước 7. Rà máy trước khi giao

```bash
python "C:\Users\pthao\.claude\skills\yt-react-script\scripts\check_script.py" "<thư mục ra>\kich-ban.md"
```

Script đếm số từ lời đọc, ước thời lượng, và liệt kê từng dòng còn dính cụm cấm, cụm kể lại hội thoại, câu rời dưới 5 từ, thuật ngữ tiếng Anh thừa. Sửa cho tới khi báo sạch rồi mới sang bước 8. Cập nhật dòng "Thời lượng" ở đầu kịch bản theo số từ thật.

### Bước 8. Xuất PDF và gửi

```bash
python "C:\Users\pthao\.claude\skills\yt-react-script\scripts\md2pdf.py" "<thư mục ra>\kich-ban.md" "<thư mục ra>\kich-ban.pdf" "<tên ngắn>"
```

PDF khổ 120 x 213 mm, chữ 12 pt, mỗi điều bắt đầu ở trang mới, ô màu: xanh dương là clip, vàng là chỗ user tự nói, xanh lá là CTA, tím là bài học rút ra, đỏ là số cần sửa hoặc kiểm. Kiểm 1–2 trang bằng pypdfium2 render ra PNG rồi Read, xong gửi bằng `SendUserFile` với `display: attach`.

### Bước 9. Báo cáo

Nói ngắn: thư mục, số điều đã chọn và vì sao, số từ và thời lượng ước tính, các số `[SỬA SỐ]` và `[KIỂM]` user cần đụng trước khi quay, ý để dành cho phần 2. Không kể lại quy trình.

## Bẫy đã gặp

- YouTube trả 429 khi tải nhiều ngôn ngữ phụ đề liền nhau. Script đã có sleep và retry; nếu vẫn lỗi thì tải một ngôn ngữ mỗi lần.
- Phụ đề tự động tiếng Việt (`vi-orig`) hiện đã có dấu câu, tốt cho phân tích. Phụ đề tiếng Anh tự động ngắt câu khác lời nói, nên tìm mốc bằng cụm 3–5 chữ, đừng tìm cả câu.
- `--flat-playlist` không có ngày đăng, phải lấy metadata riêng. Script đã lo.
- Mốc giây từ phụ đề tự động lệch 1–2 giây so với hình, ghi chú điều này trong Phụ lục A.
- Người dùng nói khoảng 180–230 từ/phút. Ước thời lượng bằng số từ ÷ 230 và ÷ 180, đưa cả hai. Cộng thêm tổng clip và 1 phút cho mỗi ô user tự nói.
- Đừng để tên thiết bị tự chế lạ tai ("Ghi vào sổ"). Đừng viết "Hết." làm câu kết. Dùng "Bài học rút ra" và "Hẹn gặp lại bạn ở video sau".
- Mỗi lần user góp ý, giữ bản cũ bằng cách đổi tên `kich-ban-vN-<mô tả>.md`, ghi ở đầu bản mới "Bản N sửa gì so với bản trước", rồi mới ghi đè `kich-ban.md` và in lại PDF.

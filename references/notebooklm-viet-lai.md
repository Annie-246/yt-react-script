# Bước 6b: nhờ NotebookLM viết lại từng phần cho tự nhiên

Skill dùng: `C:\Users\pthao\.claude\skills\notebooklm\` (tự động hóa trình duyệt, KHÔNG phải MCP). Mọi lệnh chạy qua `python scripts/run.py ...` trong thư mục skill đó.

## Một notebook dùng chung, không lẫn video

Notebook chung tên **"Kịch bản YT react"**, id trong thư viện: `kich-ban-yt-react` (đã đăng ký và kích hoạt, link `https://notebook.google.com/notebook/40c7fcd9-2855-4c3b-9f00-6f8bf00fcee0`). Gọi bằng `--notebook-id kich-ban-yt-react`. Nguồn có thể là tên mã video hoặc đúng tiêu đề YouTube (khi user thêm bằng link YouTube); chỗ nào ghi "mã video" bên dưới thì dùng tên nguồn thật hiện trong notebook. Không dùng notebook "Under30 Idea Video", đó là notebook nghiên cứu podcast khác). Nó chứa transcript của nhiều video, nên chống lẫn bằng 3 lớp:

1. **Mỗi video một mã** `<yymmdd>-<slug>` (chính là tên thư mục ra). Transcript được thêm vào notebook thành một nguồn đặt tên đúng mã đó, ví dụ `250920-alex-hormozi`.
2. **Mọi câu hỏi gửi NotebookLM đều mở đầu bằng khoá nguồn** (xem mẫu dưới): chỉ được dùng nguồn có tên mã đó, cấm dùng nguồn khác, và phải trích nguyên văn một câu từ transcript để chứng minh đã đọc đúng nguồn.
3. **Claude kiểm câu trích**: câu trích đó phải có thật trong `transcript.md` của video đang làm (grep). Không khớp hoặc nhắc tên người/số liệu không có trong transcript thì bỏ cả bản viết lại, giữ bản nháp, báo user.

## Việc user phải làm tay (skill không upload được nguồn)

Skill notebooklm chỉ hỏi đáp, không thêm nguồn. Nên mỗi video mới:
- User kéo file `transcript.md` của video vào notebook chung, đổi tên nguồn thành mã video.
- Claude nhắc user việc này ở đầu bước 6b nếu chưa chắc nguồn đã có. Kiểm bằng một câu hỏi: "Liệt kê tên các nguồn trong notebook". Không thấy mã video thì dừng, báo user thêm nguồn.

## Chia phần

Chia `kich-ban.md` theo mục: 0 (thông điệp chính), từng điều, mục kết. Phụ lục A và B không gửi. Giữ nguyên các thẻ `[CLIP]`, ô user tự nói, `[SỬA SỐ]`, `[KIỂM]`: chỉ gửi phần lời đọc, ghép lại đúng chỗ.

## Mẫu câu hỏi (mỗi phần một lần, mỗi lần độc lập vì mỗi câu mở một phiên trình duyệt mới)

```
CHỈ dùng nguồn tên "<mã video>". Bỏ qua mọi nguồn khác trong notebook.
Trước khi viết, trích nguyên văn một câu trong nguồn đó nói về nội dung phần dưới đây.

Dưới đây là phần "<tên mục>" của kịch bản đọc theo video <tiêu đề video> (kênh <kênh>).
Hãy viết lại phần này bằng văn nói tiếng Việt tự nhiên, đúng ý nguồn:
- <dán nguyên văn các quy tắc văn phong cốt lõi từ mau-kich-ban.md và quy-tac-viet.md: văn nói mượt, câu đủ chủ vị, nối bằng thì/mà/nên/nhưng/vì/còn; không kể lại hội thoại; ví dụ nói ý trước, kể một ví dụ từ đầu đến cuối, chốt bằng "nghĩa là"; không thuật ngữ Anh khi có từ Việt; không dùng câu cửa miệng nào trong danh sách cấm>
- Giữ nguyên mọi số liệu, tên riêng, độ dài tương đương (± 15% số từ).
- Không thêm ý, số hay câu trích không có trong nguồn.
- Mục này kết bằng "Bài học rút ra là" thì bản viết lại cũng phải kết như vậy.

Phần cần viết lại:
"""
<nội dung phần>
"""
```

Theo `SKILL.md` của notebooklm, câu trả lời kết thúc bằng "Is that ALL you need to know?": bỏ dòng đó khi ghép, và chỉ hỏi thêm nếu bản viết lại thiếu ý.

## Ghép và bàn giao

- Trước khi ghép, đổi tên bản nháp thành `kich-ban-v0-nhap.md` (bản Claude viết, chưa qua NotebookLM) để user so sánh được.
- Ghép bản NotebookLM vào `kich-ban.md`, ghi ở đầu: "Bản này đã được NotebookLM viết lại các mục: …".
- Phần nào NotebookLM lỗi, lẫn nguồn hoặc hết lượt (free: 50 câu/ngày, một kịch bản 8 điều tốn khoảng 10 câu) thì giữ bản nháp ở phần đó và ghi rõ trong báo cáo.
- Sau đó chạy `check_script.py` (bước 7) trên bản đã ghép: NotebookLM có thể đưa lại cụm cấm hoặc câu cửa miệng.
- User chưa duyệt thì chưa xuất PDF cuối; xuất PDF như bình thường ở bước 8, user xem một thể.

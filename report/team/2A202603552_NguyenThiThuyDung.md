# Báo cáo cá nhân — 2A202603552_NguyenThiThuyDung

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thị Thùy Dung
- MSSV: 2A202603552
- Email: nttdungk5@gmail.com
- GitHub: Dunnguyn

## 2. Phần việc phụ trách

- CP2: viết shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`) — tách orchestrator và investigator chỉ đọc.
- CP3: dựng handoff (`lab8.handoff.make_handoff`), ledger, xử lý crash cho shape của mình.
- CP4: tìm và vá lỗi rò dữ liệu nhạy cảm vào trace của `single.py`, viết test chặn tái diễn; thêm test chống giả mạo tham số tool (ý tưởng ban đầu đặt sai chỗ ở `runtime.py`, sau đó được chuyển lại đúng vào trong `single.py`).
- Tham gia đánh giá, nhận xét các PR trong nhóm.

## 3. Đóng góp cụ thể

- Commit `85bc805`: viết đầy đủ `orchestrator.py` — dùng `make_handoff` với `allowed_tools` chỉ gồm tool đọc, `facts={}` (không nhét dữ liệu claim thô), investigator chạy qua `run_readonly_investigators`.
- Commit `c0ae98e` ("cp3"): xử lý `TODO CP3` — truyền `crash_at` vào `durability.issue_refund`, không bắt `InjectedCrash` một cách sai cách.
- Commit `e629726` ("crash/secret cp4"): phát hiện và vá lỗi `single.py` ghi nguyên `last_result` (có thể chứa `ticket` thô) vào trace khi thoát sớm ở nhánh `needs_info`; thêm test `src/tests/test_shape_trace_privacy.py` chứng minh lỗi có thật (fail trên code cũ, pass trên code đã vá) cho cả 3 shape.
- Đề xuất ý tưởng chặn worker giả mạo `principal_id`/order facts khi gọi tool đọc (ban đầu thực hiện ở `src/lab8/runtime.py` — PR #6 — nhưng vì file này nằm ngoài phạm vi grader hidden đọc được nên không được merge; ý tưởng sau đó được viết lại đúng cách bên trong `single.py`).

## 4. Bằng chứng

- Commit `85bc805`, `c0ae98e`, `e629726` trên nhánh `feature/cp2-orchestrator` (đã merge vào `main` qua PR #3, #4, #5/#7).
- Test `src/tests/test_shape_trace_privacy.py` — chạy trên code chưa vá cho kết quả FAIL thật (`CANARY_SECRET_PRIVATE_TICKET` lọt vào trace), chạy trên code đã vá thì PASS.

## 5. Công cụ AI đã dùng

*(Mục này do Dung tự điền — ghi rõ công cụ đã dùng, dùng vào việc gì, và cách đã tự kiểm tra lại kết quả, theo [RULES.md](../../RULES.md). Không được AI tự bịa hộ phần này.)*

## 6. Tự đánh giá

*(Mục này do Dung tự viết — nhìn lại phần mình phụ trách, điểm làm tốt, điểm cần cải thiện.)*

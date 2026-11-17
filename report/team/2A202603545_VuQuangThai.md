# Báo cáo cá nhân — 2A202603545_VuQuangThai

## 1. Thông tin thành viên

- Họ tên: Vũ Quang Thái
- MSSV: 2A202603545
- Email: qtvu2k5@gmail.com
- GitHub: vuThai05

## 2. Phần việc phụ trách

- Tạo repo nhóm (fork repo đề bài về `K5-L3A-DAY08-4H45-FromWorkflowsToAgents`).
- CP2: viết shape B `single` (`src/lab8/shapes/single.py`) — vòng ReAct tối đa 8 bước qua `lab8.runtime.run_react` với `worker=True`.
- CP4: tham gia xử lý phần approval hợp lệ trong luồng xử lý claim.
- Tham gia đánh giá, nhận xét các PR trong nhóm.

## 3. Đóng góp cụ thể

- Commit `16496be` ("single content"): viết đầy đủ `single.py` theo docstring — `decide()` đi theo chuỗi tool cố định (`get_claim_view → lookup_order → compute_compensation`), số tiền lấy từ `compute_compensation`, model không tự quyết.
- Viết lại `report/team/research_card.md` (câu R4, sau đó chỉnh sang các trường SOURCE/HYPOTHESIS có trích nguồn và link cụ thể).

## 4. Bằng chứng

- Commit `16496be` trên nhánh `thai` (đã merge vào `main` qua PR #2).
- `python -m pytest -q -m student -k "single]"` chạy trên commit này pass 62/62 (đã được xác minh lại trong quá trình review PR #2).

## 5. Công cụ AI đã dùng

- Tôi đã dùng ChatGPT (Codex) để rà soát repo, hỗ trợ đồng bộ nhánh Git, soạn báo cáo và viết test hồi quy src/tests/test_single_react_flow.py.
- Tôi đối chiếu mô tả đóng góp với single.py, commit 16496be và hướng dẫn trong RULES.md. Test mới kiểm tra chuỗi get_claim_view → lookup_order → compute_compensation và xác nhận issue_refund nhận số tiền từ quote. python -m py_compile tests/test_single_react_flow.py chạy thành công; pytest chưa chạy được vì môi trường hiện không cài pytest.
- Lab dùng MockLLM cố định theo seed, không gọi model bên ngoài hay cần API key.

## 6. Tự đánh giá

- Điểm làm tốt: phần single giữ luồng xử lý rõ ràng trong tối đa 8 bước ReAct. decide() lấy claim, tra cứu order theo định danh tin cậy rồi dùng kết quả compute_compensation làm số tiền đề xuất; thao tác ghi refund vẫn do host xử lý.
- Điểm cần cải thiện: commit ban đầu cho single chưa kèm test riêng. Tôi đã bổ sung test hồi quy cho thứ tự tool và số tiền quote trong thay đổi này; lần sau nên đưa kiểm thử cùng commit triển khai ngay từ đầu và ghi rõ hơn bằng chứng cho phần approval ở CP4.

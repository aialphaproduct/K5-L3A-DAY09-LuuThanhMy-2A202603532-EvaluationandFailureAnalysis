# Báo cáo cá nhân — 2A202603532_LuuThanhMy

## 1. Thông tin thành viên

- Họ tên: Lưu Thanh Mỹ
- MSSV: 2A202603532
- Email: data97688@gmail.com
- GitHub: aialphaproduct

## 2. Phần việc phụ trách

- CP2: viết shape A `workflow` (`src/lab8/shapes/workflow.py`) — các bước Python cố định, không có bước nào model tự quyết tiền.
- CP4: vá lỗi rò ticket vào trace và khóa tham số tool theo đúng claim trong `single.py` (gộp đúng phần ý tưởng tốt từ một PR bị lỗi khác, không đụng `src/lab8/runtime.py`).
- CP5: chạy benchmark 4 shape × 5 seed, viết `decision_adr.md`, viết bonus topic B3 (verifier chống khuếch đại lỗi cho swarm).
- Review và test thực tế toàn bộ các PR trong nhóm trước khi merge (chạy lại `pytest`, `check_submission`, `crash_test` trên từng PR, không chỉ đọc diff).

## 3. Đóng góp cụ thể

- Commit `76aab20`: viết đầy đủ `workflow.py` theo docstring — `get_claim_view → lookup_order → compute_compensation → durability.issue_refund` (truyền quote đầy đủ, không bắt `InjectedCrash` sai cách).
- Commit `76709c4`: vá `single.py` — trace chỉ ghi `last_tool` thay vì toàn bộ `last_result` (chặn rò `CANARY_SECRET_*`/ticket); `decide()` chốt `principal_id`/`order_id` một lần từ `get_claim_view`, dùng lại cho mọi tool call sau, fail closed (`order_scope_mismatch`) nếu `lookup_order` từng trả nhầm order.
- Commit `76709c4` cũng thêm `src/tests/test_shape_trace_privacy.py` và `src/tests/test_single_arg_integrity.py`.
- Commit `2ddce84`: chạy và commit `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed).
- Nhánh `bonus/b3-swarm-verified` (commit `83d0e8d`): viết `src/bonus/swarm_verified.py` (verifier bằng code chặn điểm yếu tin ticket của swarm), 8 claim đối kháng viết tay (`src/bonus/cases.jsonl`, `src/bonus/world.json`), 22 test mới (`src/tests/test_bonus_swarm_verified.py`), `report/team/bonus_report.md`.
- Phát hiện và chặn merge 2 PR có lỗi nghiêm trọng trước khi vào `main`: một PR revert `orchestrator.py` về stub kèm sửa sai `runtime.py` (đã kiểm chứng bằng cách chạy test thật: 62/62 fail nếu merge), một PR có merge commit vô tình revert `TEAM.md`/`decision_adr.md`/`benchmark.json` về rỗng (9 FAIL khi chạy `check_submission`).

## 4. Bằng chứng

- Commit `76aab20`, `76709c4`, `2ddce84`, `83d0e8d` trên `main` (qua PR #1, #7, #8, #14).
- `python -m pytest -q` (cổng host) pass 81/81 sau khi gộp đủ bonus; `python -m lab8.check_submission` ra 0 FAIL.
- `src/reports/benchmark.json`, `src/reports/bonus_benchmark.json`, `src/reports/bonus_adversarial.json` — số liệu benchmark do chính `lab8.benchmark` sinh ra, không chép tay.

## 5. Công cụ AI đã dùng

- Dùng Claude Code (Anthropic) trong suốt quá trình: viết code 3 phần được giao (workflow, vá single.py, bonus B3), chạy test/benchmark/crash suite thật trên từng thay đổi trước khi commit, đọc và review diff của các PR khác trong nhóm (phát hiện 2 PR có lỗi nghiêm trọng kể trên bằng cách tạo worktree riêng và chạy `pytest`/`check_submission` thật, không chỉ đọc code).
- Tự kiểm tra: mọi số liệu trong báo cáo (benchmark, crash safety, số test pass) đều lấy từ kết quả chạy lệnh thật trong phiên làm việc, có thể tái lập bằng đúng lệnh ghi trong `decision_adr.md`/`bonus_report.md`, không để AI tự suy ra số liệu.

## 6. Tự đánh giá

- Làm tốt: phần test thực tế trước khi merge — nhờ chạy lại test trên từng PR (kể cả PR của người khác) thay vì chỉ đọc diff, đã chặn được 2 lỗi nghiêm trọng (revert orchestrator, sửa sai runtime.py) trước khi lọt vào `main`.
- Cần cải thiện: phối hợp nhánh git giữa 3 người đôi lúc bị lệch (một vài PR dựa trên nhánh cũ gây conflict/revert ngoài ý muốn) — lần sau nên thống nhất quy tắc luôn `git pull` từ `main` trước khi tạo nhánh mới.

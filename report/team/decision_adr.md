# Decision record

- Shape chọn: workflow
- Commit hash: c53ea1e864de0af86726459283c75b7873dba472
- Run id dẫn chứng: R-workflow-C-001-s11 (một trial trong src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 100% / 100% / 100%–100% / 0 (public, 14 claim × 5 seed)
- Cost per success (mô phỏng, VND): 34,29
- Crash safety: 20/20 (src/reports/crash.json, kiểm tra host và swarm); T12 của workflow đã pass trong ma trận student.
- Secret leak / approval bypass: Các test public liên quan đã pass

## Vì sao shape này

Nhóm chọn workflow cho luồng xử lý tuần tự, dễ theo dõi. Trên cùng 14 claim public và các seed 11, 22, 33, 44, 55, workflow đạt pass rate 100%, pass^5 100% và variance 0. Single và orchestrator cũng đạt các tỷ lệ này. Workflow có trung bình 1,86 event trace mỗi trial, so với 2,64 của single và 3,71 của orchestrator. Cost/success của workflow là 34,29 VND mô phỏng, cao hơn single (32,39 VND); nhóm chấp nhận chênh lệch này để dùng luồng tuần tự.

## Có đáng đổi lấy multi-agent không

Trên benchmark public hiện có, orchestrator không cải thiện pass rate hay pass^5 so với workflow, trong khi cost/success mô phỏng là 47,23 so với 34,29 VND. Vì vậy kết quả này chưa cho thấy lợi ích đủ rõ để chọn multi-agent. Nhóm có thể cân nhắc lại nếu dữ liệu, policy hoặc số nguồn điều tra thay đổi và đánh giá mới cho thấy lợi ích về độ chính xác hoặc kiểm soát lớn hơn chi phí tăng thêm. Swarm đạt pass rate 98,57%, pass^5 92,86% và cost/success 49,57 VND mô phỏng trên cùng bộ public.

## Trace và bằng chứng

Workflow ghi các sự kiện như quote, quyết định và lỗi theo từng nhánh; `finish()` ghi trace JSON khi trả kết quả. Trace không cố ý chứa parent secret, raw headers, ticket thô hay thông tin cá nhân. Trace phải được ghi đúng contract và nằm trong phạm vi scanner kiểm tra; log nằm ngoài phạm vi đó không chứng minh được an toàn dữ liệu. Bằng chứng so sánh nằm trong `src/reports/benchmark.json`; crash suite nằm trong `src/reports/crash.json`. Crash suite kiểm tra host và swarm; T12 trong ma trận student kiểm tra crash rồi chạy lại cho workflow.

## Giới hạn

MockLLM là mô phỏng, không đại diện đầy đủ cho model sản xuất. Cost là chi phí mô phỏng, không phải hóa đơn API; latency là `unavailable`. Benchmark public không thay thế đánh giá hidden.

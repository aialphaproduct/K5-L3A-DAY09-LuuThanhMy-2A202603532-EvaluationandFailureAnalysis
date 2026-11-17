# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | EMNLP 2026, [*Rethinking Evaluation of MAS Efficiency*](https://aclanthology.org/2026.emnlp-main.798/) (slide 44, 59) — benchmark/thực nghiệm |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | "Efficiency gain" quan sát được giữa các kiến trúc agent có thể đến từ cách thiết kế benchmark (seed, corpus, tool khác nhau), không hẳn từ bản thân kiến trúc. Phải giữ cố định runtime/model/tool để kết luận đáng tin |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Giới hạn ở các benchmark multi-agent cụ thể paper khảo sát; không khẳng định đúng cho mọi hệ agent hay mọi benchmark |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi đổi từ `single` sang `orchestrator` trên cùng bộ claim public và năm seed, nhóm dự đoán pass rate của cả hai vẫn gần 100%, chênh lệch không quá 5 điểm phần trăm. Cost/success mô phỏng của `orchestrator` dự kiến cao hơn `single` ít nhất 20% do cấu hình xử lý có thêm bước điều phối và điều tra. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, seed `11,22,33,44,55`, 14 claim trong `data/public_claims.jsonl`, `config/pricing.yaml`, evaluator `lab8.metrics`. Biến duy nhất thay đổi: shape (`workflow`/`single`/`orchestrator`/`swarm`) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: một shape fail nhiều hơn chỉ vì seed xấu/corpus khác, không phải vì kiến trúc kém. Đo bằng `seed_variance`, `seed_min`/`seed_max` trong `benchmark.json` — nếu variance ≈ 0 trên 3 shape thì chênh lệch pass_rate giữa shape là thật, không phải nhiễu đo lường |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json` (`by_shape.workflow`, `by_shape.single`, `by_shape.orchestrator`, `by_shape.swarm`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Cả 4 shape chạy trên đúng cùng `controlled_variables` (cùng 14 claim, cùng 5 seed, cùng pricing) ghi trong chính file benchmark. `workflow`/`single`/`orchestrator` đạt `pass_rate = 1.000`, `seed_variance = 0.000000` trên cả 5 seed — không có nhiễu do seed. `swarm` đạt `pass_rate = 0.986`, `seed_variance = 0.000816`, fail đúng 1 trial ở seed chia hết cho 5 (lý do ghi rõ trong code: `REFERENCE_WEAKNESS`, swarm tin vào delay ghi tay trong ticket khi `seed % 5 == 0`). Vì corpus và seed giống hệt nhau cho cả 4 shape, chênh lệch pass_rate và cost/success (34.29 / 32.39 / 47.23 so với 49.57 VND mô phỏng) phản ánh đúng khác biệt kiến trúc, không phải do thiết kế benchmark thiên lệch.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Corpus public chỉ có 14 claim (bộ hidden có 40 claim × 5 seed nhưng nhóm không tự chạy được, chỉ giảng viên có grader riêng).

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).

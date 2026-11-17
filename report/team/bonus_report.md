# Bonus report: B3

- Topic + nguồn (tên, năm, slide): B3 · Verifier/aggregator chống khuếch đại lỗi — Google Research 2026, error amplification (agent độc lập khuếch đại lỗi tới 17,2×, orchestration tập trung còn 4,4×), slide 17, 22, 42.
- CLAIM của nguồn (1 câu): Một bước kiểm chứng tập trung (verifier) trước khi ghi kết quả làm giảm mạnh mức khuếch đại lỗi so với để agent độc lập tự quyết.
- BOUNDARY (model / dataset / setup): Số 17,2×/4,4× đo trên hệ multi-agent LLM thật và benchmark của nguồn; không có dữ liệu cho hệ MockLLM hay task hoàn phí vận chuyển.
- HYPOTHESIS trên LogiX: Nếu thêm một verifier **bằng code** (không gọi thêm model) đối chiếu `delay_days`/`status`/`damage_verified` dùng để tính tiền với order có cấu trúc, trước khi `swarm` ghi refund, thì pass rate của `swarm_verified` sẽ bằng hoặc cao hơn `swarm`, với chi phí mô phỏng tăng nhẹ (thêm đúng 1 tool call xác minh mỗi trial).
- Biến cố định / biến thay đổi: Cố định MockLLM, seed, corpus (public 14 claim và bộ đối kháng tự viết 8 claim), bảng giá, evaluator. Biến duy nhất: có verifier (`swarm_verified`) hay không (`swarm`).
- Lệnh tái lập (copy-paste được):
  ```
  python -m lab8.benchmark --shapes workflow,swarm,swarm_verified \
    --extra-shape swarm_verified=bonus.swarm_verified:run_claim \
    --cases data/public_claims.jsonl --seeds 11,22,33,44,55 \
    --out reports/bonus_benchmark.json

  python -m lab8.benchmark --shapes swarm,swarm_verified \
    --extra-shape swarm_verified=bonus.swarm_verified:run_claim \
    --cases bonus/cases.jsonl --world bonus/world.json \
    --seeds 11,22,33,44,55 --out reports/bonus_adversarial.json

  python -m pytest -q tests/test_bonus_swarm_verified.py
  ```
- File report + run id: `src/reports/bonus_benchmark.json` (bộ public), `src/reports/bonus_adversarial.json` (bộ 8 claim đối kháng `bonus/cases.jsonl`).

## Kết quả

**Trên bộ public (14 claim × 5 seed, đúng điều kiện đo của lab):**

| Shape | pass | pass^5 | variance | cost/success (VND mô phỏng) | mean steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 0.000000 | 34.29 | 1.86 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 | 2.80 |
| **swarm_verified** | **1.000** | **1.000** | **0.000000** | 57.29 | 1.89 |

**Trên 8 claim đối kháng tự viết (`bonus/cases.jsonl`, nhãn viết tay theo `docs/business_rules.md`, × 5 seed):**

| Shape | pass | pass^5 | variance | cost/success (VND mô phỏng) |
| --- | ---: | ---: | ---: | ---: |
| swarm | 0.875 | 0.375 | 0.062500 | 61.75 |
| **swarm_verified** | **1.000** | **1.000** | **0.000000** | 62.53 |

Verifier can thiệp (ghi `verifier_override` vào trace) ở **6/40 trial** trên bộ đối kháng — đúng bằng số claim có cấu tạo để kích hoạt điểm yếu (`seed % 5 == 0`, tức seed 55 trong 5 seed đo) nhân với số claim mà ticket có nhắc một con số ngày khác với `delay_days` thật (6/8 claim: AC-01, AC-02, AC-03, AC-04, AC-07, AC-08).

**Một trace minh họa** (claim `AC-03`, seed 55 — ticket nói "trễ 1 ngày" nhưng đơn thật trễ 5 ngày):
```json
{"kind": "model_override", "payload": {"delay_days": 1}},
{"kind": "verifier_override", "payload": {"fields": {"delay_days": {"model": 1, "structured": 5}}}},
{"kind": "quote", "payload": {"amount_vnd": 40000, "reason": "entitled", ...}}
```
`swarm` (không có verifier) dừng ở bước `model_override`, tính quote từ `delay_days=1` → `1 < 3` → `denied`, sai hoàn toàn so với thực tế (đơn trễ 5 ngày, phải hoàn 40.000đ). `swarm_verified` phát hiện `delay_days` mô hình dùng (1) khác với order có cấu trúc (5), phục hồi lại giá trị đúng trước khi tính tiền.

## Kết luận

**Ủng hộ hypothesis**, trong phạm vi đo được. Trên cả hai bộ dữ liệu, `swarm_verified` đạt pass rate và pass^5 cao hơn hoặc bằng `swarm`, và variance giữa các seed giảm về 0 — đúng như dự đoán cho một cơ chế chỉ kiểm tra dữ kiện chứ không đoán thêm. Trên bộ public, nơi điểm yếu chỉ trúng 1/70 trial, chênh lệch nhỏ (98,6% → 100%). Trên bộ đối kháng tự viết — nơi 6/8 claim có ticket nhắc một con số ngày sai — chênh lệch rõ hơn nhiều (87,5% → 100%, pass^5 37,5% → 100%).

Chi phí mô phỏng tăng nhẹ (+15,6% trên bộ public: 49,57 → 57,29 VND/success) vì verifier luôn gọi lại `compute_compensation` một lần nữa sau khi đối chiếu, bất kể có phát hiện sai lệch hay không — đây là chi phí cố định của việc "luôn kiểm tra" chứ không phải chi phí của riêng các lần sửa lỗi.

**Điều kiện đảo ngược kết luận:** nếu `swarm_reference` không còn override `delay_days` từ ticket (sửa tận gốc thay vì vá ở lớp verifier), `swarm` và `swarm_verified` sẽ cho kết quả giống hệt nhau và phần chi phí thêm của verifier trở thành lãng phí thuần túy. Verifier chỉ đáng giá khi nguồn dữ kiện đưa vào bước tính tiền còn có khả năng bị nhiễu (ticket, tool không đáng tin, bước điều tra khác) — đúng tinh thần của nguồn: kiểm chứng tập trung có giá trị khi còn nhiều điểm có thể khuếch đại lỗi độc lập với nhau.

Verifier **không** thay thế phần quyết định của `swarm` — nó chỉ phục hồi dữ kiện trước khi `swarm` tự quyết như cũ (vẫn chính code `compute_compensation` tính tiền, vẫn chính `durability.issue_refund` ghi sổ). Nếu verifier đã tự tính và tự quyết thay, thì `swarm_verified` chỉ còn khác `workflow` ở việc có đi qua đường ReAct/handoff hay không, chứ không còn giữ lại giá trị gì đặc trưng cho "swarm".

## Giới hạn

- MockLLM không phải model sản xuất thật; một model ngôn ngữ thật có thể bị dẫn dắt theo những cách mà fixture 8 claim ở đây chưa bao phủ (ví dụ chèn hướng dẫn giả vào ticket thay vì chỉ một con số).
- 8 claim đối kháng là nhãn tay, quy mô nhỏ, chỉ nhắm đúng điểm yếu đã biết của `swarm_reference` (ghi đè `delay_days`); không phủ được các điểm yếu chưa biết hoặc các trường khác (`status`, `damage_verified`) vì `swarm_reference` hiện tại không ghi đè hai trường đó — 2 claim (AC-05, AC-06) phục vụ như case đối chứng cho thấy verifier không đổi hành vi đúng sẵn có.
- Chi phí là VND mô phỏng (`config/pricing.yaml`), không phải hóa đơn API thật; latency không đo được (`unavailable`).
- Không chạy được trên bộ hidden của giảng viên; mọi số liệu trên chỉ có giá trị trên 2 corpus đã nêu.

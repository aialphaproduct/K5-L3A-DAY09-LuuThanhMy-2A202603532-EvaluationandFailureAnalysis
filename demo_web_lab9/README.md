# Demo web Lab 9 (không nằm trong phạm vi chấm điểm)

Trang demo để thuyết trình trước lớp, cùng phong cách với `demo_web/` của Lab 8: 1 trang, chạy
code thật (không mock dữ liệu), chia 3 phần theo đúng mạch M1 → M3 → M4/M5-M7 của Lab 9.

- **Trace case** (trái: cây `docs/failure_taxonomy.md` theo FM-01..09, mỗi FM liệt kê claim đã gắn
  mã; phải: chọn shape + seed rồi "Chạy trial" → gọi thật `lab9.trace_case.investigate`, hiển thị
  ticket, từng event trong trace dạng bong bóng chat (badge ⚠ khi có `model_override`), và badge
  PASS/FAIL cho từng grader trong `lab9/graders.py` chạy trên đúng trial đó).
  - Ví dụ nên demo: **FM-03 → C-002 → seed 55** (bug thật: `model_override` đè DB fact) so với
    **seed 11** (không trúng bug) để thấy rõ "bước sai đầu tiên".
- **Gate (M4)**: chọn `fixed` hoặc `seeded_regression`, gọi thật `lab9.gate.check` so với
  `reports/baseline_v1.json` → in đúng bảng metric + `exit 0`/`exit 1` như CLI.
- **Mutation (M5-M7)**: mặc định đọc `reports/mutation_scorecard.json` đã chạy sẵn offline (hiện
  ngay, vì chạy live 5 variant × 28 item × 5 seed ≈ 1-2 phút, không hợp để bấm giữa buổi demo).
  Nút "Chạy lại trực tiếp" gọi thật `lab9.mutation.scorecard` nếu cần chứng minh trước lớp là
  không có số liệu dựng sẵn.

Không nằm trong `src/`, không ảnh hưởng điểm số — chỉ phục vụ thuyết trình.

## Chạy

Cần môi trường đã cài trong `src/` (xem `src/requirements.txt` + `src/requirements-lab9.txt`),
cài thêm Flask:

```bash
cd src
python -m pip install flask
```

Chạy server (từ thư mục gốc repo):

```bash
python demo_web_lab9/server.py
```

Mở trình duyệt tại `http://localhost:5056`.

Để số liệu "Mutation" luôn mới nếu đổi `config/metric_spec_v2.yaml` hoặc `src/lab9/variants.py`,
chạy lại cache trước buổi demo:

```bash
cd src
python -c "
import json
from pathlib import Path
from lab9 import variants
from lab9.eval import load_spec
from lab9.mutation import scorecard

variants.register()
spec = load_spec(Path('config/metric_spec_v2.yaml'))
base = json.load(open('reports/baseline_v2.json', encoding='utf-8'))
rows = scorecard(spec, base, None)
out = [{'variant': n, 'expect': w, 'got': g, 'why': wh} for n, w, g, wh in rows]
killed = sum(r['expect'] == r['got'] == 'block' for r in out)
regs = sum(r['expect'] == 'block' for r in out)
fa = sum(r['expect'] == 'merge' and r['got'] == 'block' for r in out)
json.dump({'rows': out, 'killed': killed, 'regressions': regs, 'false_alarms': fa},
          open('reports/mutation_scorecard.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
"
```

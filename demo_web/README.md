# Demo web (không nằm trong phạm vi chấm điểm)

Trang demo nhỏ để thuyết trình, gồm 2 phần:

- **Dashboard benchmark**: đọc trực tiếp `src/reports/benchmark.json`, hiển thị bảng pass rate / cost / steps của 4 shape.
- **Chạy thử claim**: form chọn claim + shape + seed, gọi thật `lab8.app.run_shape` (tạo SQLite tạm, chạy claim thật qua code của nhóm), hiển thị `RunResult` + trace.

File này nằm ngoài `src/`, **không được grader hidden đọc tới** — chỉ phục vụ demo/thuyết trình, không ảnh hưởng điểm số.

## Chạy

Cần đã cài môi trường trong `src/.venv` (xem [src/README.md](../src/README.md)) và cài thêm Flask:

```bash
cd ../src
.venv/Scripts/python -m pip install flask
```

Chạy server:

```bash
cd ..
src/.venv/Scripts/python demo_web/server.py
```

Mở trình duyệt tại `http://localhost:5055`.

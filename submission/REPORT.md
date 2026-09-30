# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Hoàng Nam
- **MSSV:** 2A202602485
- **Lớp:** K4-L3B
- **Repository URL:** [github.com/namchip2003-beep/K4-L3B-Day13-NguyenHoangNam-2A202602485-Monitoring-LLMOps.git](https://github.com/namchip2003-beep/K4-L3B-Day13-NguyenHoangNam-2A202602485-Monitoring-LLMOps.git)
- **Commit SHA cuối:  ef57656**
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:**  **day13-k4-l3b-2A202602485**

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence            | Đường dẫn                           |
| ------------------- | --------------------------------------- |
| Pytest cuối        | `evidence/01-pytest.png`              |
| Log validator       | `evidence/02-log-validator.png`       |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log      | `evidence/04-structured-log.png`      |
| PII redaction       | `evidence/05-pii-redaction.png`       |
| Trace list          | `evidence/06-trace-list.png`          |
| Trace waterfall     | `evidence/07-trace-waterfall.png`     |
| Trace metadata      | `evidence/08-trace-metadata.png`      |
| Prompt versions     | `evidence/09-prompt-versions.png`     |
| Prompt rollback     | `evidence/10b-prompt-rollback.png`    |
| Dashboard runtime   | `evidence/11-dashboard-overview.png`  |
| Incident metric     | `evidence/12-incident-metric.png`     |
| Incident log        | `evidence/13-incident-log.png`        |
| Incident trace      | `evidence/14-incident-trace.png`      |

## 3. Kết quả kỹ thuật

| Nội dung                 | Baseline | Kết quả cuối | Nhận xét                                                        |
| ------------------------- | -------- | --------------- | ----------------------------------------------------------------- |
| `validate_logs.py`      | 0/100    | 100/100         | Đã xử lý log đúng cấu trúc jsonl và ẩn PII thành công |
| `validate_dashboard.py` | 0/6      | 6/6             | Đủ 6 panel Metrics như hợp đồng                             |
| `pytest`                | Failed   | Passed (24/24)  | Vượt qua toàn bộ bài test                                    |
| Số traces hợp lệ       | 0        | > 10            | Trace hiển thị đầy đủ trên Langfuse                        |
| Số PII leak              | > 0      | 0               | Các số thẻ, CCCD đều bị thay thế bằng [REDACTED_...]      |
| Latency P95 / TTFT P95    | > 3000ms | < 200ms / 50ms  | Tốc độ đáp ứng rất nhanh khi không có sự cố            |
| Retrieval success rate    | < 90%    | > 95%           | Mô phỏng RAG trả kết quả tốt                                |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Sử dụng middleware để sinh UUID (hoặc lấy từ header `x-request-id`), sau đó gán vào structlog `contextvars` để tự động đính kèm vào mọi dòng log của request đó.
- **Các metadata được ghi vào structured log:** `event`, `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `correlation_id`, `session_id`, `user_id_hash`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Sử dụng Regex Pattern trong file `pii.py` để nhận diện và thay thế (redact) các chuỗi số nhạy cảm (CCCD, Thẻ tín dụng, Số điện thoại) trước khi đưa vào payload của Log.
- **Cách kiểm chứng kết quả:** Chạy script `validate_logs.py` để máy tự động dò tìm cấu trúc JSON và quét regex phát hiện PII leak.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Các trace xuất hiện trên giao diện dự án Langfuse tương ứng với cặp khóa public/secret khai báo trong `.env`.
- **Cấu trúc root/retrieval/generation observations:** Quan sát gốc là `lab-agent-run` (type `agent`), gọi ra 2 child spans là `retrieval` (type `retriever`) và `generation` (type `generation`) sử dụng `@observe`.
- **Cách nối trace với log:** Truyền `correlation_id` (được middleware tạo) vào tham số của `LabAgent.run`, từ đó lưu vào metadata của root trace trên Langfuse.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1, label `baseline` và `production`
- **Version/label candidate:** Version 2, label `candidate`
- **Trace ID của mỗi version:** (Học viên tự điền ID v1 và v2)
- **Cách promote và rollback `production`:** Để promote, đổi nhãn `production` từ v1 sang v2. Để rollback, đổi nhãn `production` quay về v1 (thao tác trực tiếp trên giao diện Langfuse).

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Code vẽ 6 panel (Latency, Traffic, Error Rate, Cost, Tokens, Quality) đọc dữ liệu từ `data/logs.jsonl` đảm bảo tính chính xác và bám sát contract của `config/dashboard.yaml`.
- **SLO và lý do chọn:** Chọn SLO 99.5% cho p95 latency < 3000ms, đảm bảo trải nghiệm người dùng không bị gián đoạn.
- **Cách tính error budget:** Nếu hệ thống phục vụ 10,000 requests trong 28 ngày, error budget 0.5% nghĩa là tối đa 50 requests bị quá hạn hoặc gặp lỗi.
- **Ba alert và runbook tương ứng:** `High_Latency_P95` (Cảnh báo độ trễ cao), `High_Error_Rate` (Cảnh báo lỗi tăng cao) và `Quality_Score_Drop` (Cảnh báo chất lượng LLM giảm sút). Toàn bộ runbook lưu trong `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1
- **Khoảng thời gian điều tra:** 2026-09-30 03:47 UTC
- **Triệu chứng từ metrics:** P95 Latency tăng vọt bất thường (từ mức baseline ~160ms lên hơn ~2600ms), vượt xa ngưỡng an toàn.
- **Log line và correlation ID liên quan:** `{"service": "api", "latency_ms": 2654, ... "correlation_id": "req-00092967"}`.
- **Trace ID và span gây ảnh hưởng:** `32cbaf5eff1cf8ecd08e24eb35c9ff7a`. Span gây ảnh hưởng chính là `retrieval` (tốn mất ~2.51 giây).
- **Root cause:** Hệ thống RAG (Retrieval) bị chậm/nghẽn, dẫn tới thời gian truy xuất tài liệu lâu bất thường, kéo theo toàn bộ request bị chậm.
- **Fix action:** Tạm thời tắt hoặc rollback cấu hình RAG/Vector store gây chậm, kiểm tra lại index của database hoặc tăng tài nguyên cho dịch vụ Retrieval (Trong Lab thì tắt incident bằng `--disable`).
- **Preventive measure:** Áp dụng Alert `High_Latency_P95` (như đã định nghĩa ở CP2) qua Slack để đội ngũ trực on-call nhận thông báo ngay lập tức khi RAG có dấu hiệu timeout/delay kéo dài, đồng thời áp dụng timeout cứng cho bước Retrieval.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Quyết định không log nguyên bản input/output của người dùng vào Langfuse và structured logs. Lý do là để tuân thủ bảo mật (redact PII), tránh việc lộ lọt các thông tin nhạy cảm (thẻ tín dụng, số điện thoại) lên hệ thống bên ngoài. Thay vào đó, sử dụng hàm băm (hash) cho `user_id` và tóm tắt (`query_preview`) cho câu hỏi.
- **Một lỗi/blocker đã gặp:** Gặp khó khăn trong việc thiết lập đúng các thông số API cho Langfuse SDK v4 khi dùng `client.update_current_generation()`.
- **Cách tìm nguyên nhân và xử lý:** Đọc kỹ tài liệu phiên bản v4, kiểm tra kwargs, chuyển đổi tham số từ `usage` thành `usage_details` và `cost` thành `cost_details` để đảm bảo tương thích API mới.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics đóng vai trò như "Chuông báo cháy", báo hiệu có bất thường tổng thể (ví dụ: Latency tăng vọt). Logs đóng vai trò như "Định vị", chỉ ra chính xác request nào (thông qua `correlation_id`) đang gặp lỗi. Traces đóng vai trò như "Biên bản khám nghiệm hiện trường", bóc tách chi tiết từng mili-giây để xác định lỗi xuất phát từ khâu nào (VD: `retrieval` hay `generation`).
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Quản lý prompt version giúp an toàn thử nghiệm và rollback ngay lập tức mà không cần sửa code khi prompt mới gặp lỗi. Theo dõi token/cost giúp ngăn chặn lãng phí (cost spike). SLO định hình ngưỡng chấp nhận được của hệ thống, giúp team biết khi nào cần dừng tính năng mới để tập trung vá lỗi.
- **Điều quan trọng nhất đã học:** Hiểu được tính toàn vẹn của một hệ thống LLMOps không chỉ nằm ở việc xây dựng Agent tốt, mà phải đảm bảo khả năng Giám sát (Observability) bằng "chiếc kiềng 3 chân" (Metrics, Logs, Traces) để truy xuất nguyên nhân (Root cause analysis) cực kỳ nhanh chóng khi hệ thống sập.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Không có. Toàn bộ các checklist và cấu hình đã được áp dụng thành công.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.

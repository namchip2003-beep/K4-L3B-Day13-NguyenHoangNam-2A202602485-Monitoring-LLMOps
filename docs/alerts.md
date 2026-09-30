# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: High_Latency_P95
- Severity: high
- Duration: 5m
- Kênh thông báo: Slack
- SLI/SLO liên quan: latency_ms
- Điều kiện và thời gian duy trì: p95_latency > 3000ms trong 5m
- Ảnh hưởng tới người dùng: Người dùng phải đợi lâu để nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên: 
  1. Kiểm tra dashboard Latency để xác định khoảng thời gian bị ảnh hưởng.
  2. Lọc log để lấy correlation_id của các request chậm.
  3. Mở Langfuse trace để xem span nào (retrieval hay generation) bị chậm.
- Mitigation tạm thời: Rollback phiên bản prompt nếu có thay đổi gần đây, hoặc vô hiệu hóa retriever phụ nếu retriever chính quá tải.
- Owner: on-call

## Alert 2

- Tên: High_Error_Rate
- Severity: critical
- Duration: 5m
- Kênh thông báo: Slack
- SLI/SLO liên quan: error_rate
- Điều kiện và thời gian duy trì: error_rate > 2% trong 5m
- Ảnh hưởng tới người dùng: Người dùng không nhận được câu trả lời hoặc bị gián đoạn dịch vụ.
- Ba bước kiểm tra đầu tiên:
  1. Xem dashboard Errors để xác nhận mức độ tăng error rate.
  2. Tìm kiếm các log có mức độ ERROR hoặc `tool_success`=false để xác định nguyên nhân.
  3. Sử dụng correlation_id tìm trace liên quan để kiểm tra xem LLM hay retriever gây lỗi.
- Mitigation tạm thời: Bật fallback model nếu API LLM lỗi, hoặc sử dụng fallback retriever nếu database lỗi.
- Owner: on-call

## Alert 3

- Tên: Quality_Score_Drop
- Severity: warning
- Duration: 10m
- Kênh thông báo: Slack
- SLI/SLO liên quan: quality_score_avg
- Điều kiện và thời gian duy trì: quality_score_avg < 0.75 trong 10m
- Ảnh hưởng tới người dùng: Chất lượng câu trả lời bị giảm sút, sai lệch thông tin hoặc trả lời chung chung.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel Quality trên dashboard.
  2. Kiểm tra retrieval success rate xem chất lượng giảm có phải do không tìm được ngữ cảnh.
  3. Mở trace trên Langfuse để xem LLM sinh câu trả lời sai lệch ra sao so với context.
- Mitigation tạm thời: Rollback phiên bản prompt cũ, hoặc xem xét cập nhật tài liệu trong RAG.
- Owner: product-team

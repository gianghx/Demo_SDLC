---
name: test-report
description: Tạo báo cáo kiểm thử (test report / test completion report / test summary) theo IEEE 29119-3 từ kết quả test, gồm tóm tắt pass/fail, truy vết về yêu cầu (BR/US/AC), danh sách lỗi, đánh giá cổng phát hành và khuyến nghị Go/No-Go. Dùng skill này bất cứ khi nào người dùng nhắc đến báo cáo test, báo cáo kiểm thử, kết quả test, test summary, test result, Go/No-Go, nghiệm thu, "tổng hợp kết quả test", hoặc dán/đính kèm output của pytest, JUnit XML, Jest, bảng test case, ngay cả khi họ không nói chữ "report".
---

# Test Report

Viết báo cáo kiểm thử để người ra quyết định phát hành đọc và tin được. Giá trị của báo cáo nằm ở chỗ con số đúng và truy vết được. Một báo cáo đẹp nhưng bịa hoặc làm tròn số fail sẽ dẫn tới quyết định phát hành sai, nên mọi con số phải tính ra từ dữ liệu thật.

## Quy trình

1. **Thu thập đầu vào.** Hỏi hoặc tìm trong repo, không đoán:
   - Kết quả test: file JUnit XML, log pytest/Jest, bảng test case (Markdown/CSV/Excel), hoặc nội dung người dùng dán.
   - Yêu cầu để truy vết: `docs/requirements/PRD.md`, `docs/requirements/BRD.md` nếu có (US-xxx, BR-xxx, AC-xxx, cổng phát hành G1..Gn).
   - Môi trường và phiên bản được test (build, commit, ngày chạy).
2. **Tóm tắt kết quả bằng script khi có JUnit XML.**
   `python .claude/skills/test-report/scripts/parse_junit.py <file.xml> [--id-pattern "TC-\d+"] [--json]`
   Script đếm pass/fail/error/skipped và liệt kê test lỗi kèm thông báo. Dùng script thay vì đếm bằng mắt, vì đếm tay sai dễ xảy ra khi có hàng trăm test. Với định dạng khác, đếm cẩn thận và ghi rõ nguồn.
3. **Truy vết.** Gắn mỗi test case với yêu cầu (US/BR/AC) mà nó kiểm tra. Test không gắn được thì ghi vào mục "không truy vết được". Yêu cầu không có test nào thì ghi vào mục "chưa được kiểm thử". Hai danh sách này thường là phần hữu ích nhất cho người đọc.
4. **Đánh giá cổng phát hành** nếu PRD có định nghĩa (G1..Gn). Mỗi cổng ghi Đạt / Không đạt / Chưa đo, kèm bằng chứng. "Chưa đo" khác "Đạt": không được coi cổng chưa đo là đạt.
5. **Viết báo cáo** theo cấu trúc trong `references/report-template.md`, đọc file đó trước khi viết. Lưu tại `docs/testing/TEST_REPORT.md` (tạo thư mục nếu chưa có) trừ khi người dùng chỉ định chỗ khác.
6. **Tự kiểm tra** trước khi giao (xem danh sách bên dưới).

## Nguyên tắc dữ liệu

- **Không bịa.** Số lượng test, thời gian chạy, độ phủ, tên lỗi đều phải đến từ đầu vào. Thiếu thì ghi `[TBD]` và thêm vào mục câu hỏi mở. Lý do: người đọc sẽ dùng báo cáo để quyết định phát hành, một số liệu bịa gây hại hơn một chỗ trống.
- **Con số phải khớp nhau.** Tổng = pass + fail + error + blocked + skipped. Tỷ lệ pass tính trên số test đã thực thi hay tổng số? Nêu rõ công thức ngay dưới bảng.
- **Phân biệt fail, error, blocked, skipped.** Fail: chạy và sai kết quả. Error: lỗi hạ tầng hoặc ngoại lệ ngoài dự kiến. Blocked: không chạy được vì phụ thuộc hỏng. Skipped: bỏ qua có chủ ý. Gộp lại sẽ che mất vấn đề thật (ví dụ 30 test blocked không phải là 30 test ổn).
- **Test chập chờn (flaky).** Nếu cùng test lúc pass lúc fail, ghi riêng, không tính là pass.
- **Error hạ tầng không phải lỗi sản phẩm.** Test error do môi trường (timeout DB, thiếu API key, CI hỏng) xếp riêng, không tính vào số lỗi mở, nhưng cũng không tính là pass: chức năng đó chưa được xác minh, nên story tương ứng ở trạng thái "chưa xác định" và báo cáo nêu cần chạy lại. Nếu chạy lại mà fail thật thì mới mở lỗi.
- **Phủ một phần.** Một story có nhiều tình huống Given-When-Then mà chỉ một vài tình huống có test thì ghi "một phần" ở cột Ghi chú. Một test pass không có nghĩa story đã đạt.
- **Hai nguồn lệch nhau** (ví dụ tổng thời gian từng test khác thời gian của suite) thì ghi sự chênh lệch vào mục 8, đừng âm thầm chọn một số.
- **Mức độ lỗi** dùng thang Sev1 (chặn hoàn toàn / mất dữ liệu / lỗ hổng bảo mật), Sev2 (chức năng chính sai, có cách tạm), Sev3 (chức năng phụ, giao diện), Sev4 (thẩm mỹ). Nếu người dùng đã có thang khác thì dùng thang của họ. Khi dữ liệu không ghi mức độ, đề xuất một mức tạm kèm lý do (ví dụ "Sev2: chức năng chính sai, chưa rõ có cách tạm"), gắn nhãn "đề xuất" và đưa vào câu hỏi mở để QA hoặc PO xác nhận. Để trống hoàn toàn khiến người đọc không biết lỗi nặng cỡ nào, còn gán mức mà không nhãn thì giả vờ là dữ liệu có thật.
- Giữ ID, tên kỹ thuật bằng tiếng Anh (TC-001, BUG-001, US-005). Nội dung diễn giải bằng tiếng Việt, trừ khi người dùng viết bằng ngôn ngữ khác.

## Khuyến nghị Go / No-Go

Đưa ra một kết luận rõ ràng, kèm lý do ngắn:
- **Go**: mọi cổng bắt buộc (P0) đạt, không còn lỗi Sev1/Sev2 mở.
- **Go có điều kiện**: cổng bắt buộc đạt nhưng còn lỗi Sev2 có cách tạm hoặc cổng không bắt buộc chưa đạt; liệt kê điều kiện và người chịu trách nhiệm.
- **No-Go**: còn lỗi Sev1, hoặc có cổng bắt buộc không đạt hoặc chưa đo.

Báo cáo đưa khuyến nghị, người có thẩm quyền quyết định. Không ghi như thể quyết định đã được duyệt, và để trống chữ ký.

## Tự kiểm tra trước khi giao

- Tổng các trạng thái bằng tổng số test; công thức tỷ lệ pass được nêu.
- Mọi lỗi trong bảng lỗi đều có mức độ, test sinh ra nó và yêu cầu bị ảnh hưởng.
- Mọi `[TBD]` đều có câu hỏi mở tương ứng.
- Mọi cổng phát hành đều có trạng thái và bằng chứng, hoặc ghi "Chưa đo".
- Khuyến nghị khớp với bảng cổng và bảng lỗi (không có "Go" khi còn Sev1).
- Không có nhận định nào không có dữ liệu đỡ.

Khi giao, nói ngắn gọn: kết luận, các con số chính, và những chỗ còn `[TBD]` cần người dùng bổ sung.

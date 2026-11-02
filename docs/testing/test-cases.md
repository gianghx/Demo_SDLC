# Test cases — Chat với tài liệu (MVP)

> Nguồn: `use-cases.md` v0.1 (mỗi luồng chính và luồng thay thế thành một ca thử), `PRD.md` v0.5, `BRD.md` v0.11.
> Cách dùng: cập nhật cột **Trạng thái** sau khi chạy (`Pass`, `Fail`, `Error`, `Blocked`, `Skipped`, `Not run`), rồi chạy lại skill `test-report` để lập báo cáo.

## 0. Kiểm soát tài liệu

| Mục | Giá trị |
|---|---|
| Số tài liệu | TCS-CDT-001 |
| Phiên bản | 0.2 |
| Ngày | 2026-11-02 |
| Tác giả | Business Analyst |
| Trạng thái thực thi | 36 ca Pass, 23 ca Not run. Nguồn: pytest lần 2, `docs/testing/runs/run-2.xml` (35 test, 35 pass), chế độ stub, chưa có mô hình thật |

Ghi chú về cách đánh dấu: một ca chỉ được đánh `Pass` khi có test tự động kiểm tra đúng kết quả mong đợi (mã ca nằm trong tên hàm test, ví dụ `test_tc019_...`). Các ca chất lượng câu trả lời (CL), hiệu năng (HN) và các ca thao tác trên giao diện trình duyệt vẫn `Not run`: ca CL cần mô hình thật, ca giao diện cần chạy tay hoặc công cụ điều khiển trình duyệt.

Quy ước:
- **P0**: bắt buộc cho phát hành (story P0 hoặc cổng G1..G10). **P1**: nên có.
- **Loại**: CN = chức năng, BI = biên, BM = bảo mật, HN = hiệu năng, LI = lỗi hoặc ngoại lệ, CL = chất lượng câu trả lời, DL = đo lường.
- Ca có "(đo)" cần số liệu thật từ bộ câu hỏi chuẩn hoặc tài liệu mẫu (DEP-002), không chạy được bằng một lần thử tay.

## 1. UC-01 Tự đăng ký tài khoản

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-001 | US-001 | BR-018 / AC-018 | P0 | CN | Đăng ký với dữ liệu hợp lệ | Tạo `User` `PENDING`, hiển thị "chờ admin duyệt", ghi `REGISTER_SUBMITTED` | Pass |
| TC-002 | US-001 | BR-018 | P1 | LI | Đăng ký với dữ liệu không hợp lệ | Báo lỗi, giữ dữ liệu đã nhập | Pass |
| TC-003 | US-001 | BR-018 | P1 | LI | Đăng ký bằng email đã có tài khoản `PENDING` hoặc `APPROVED` | Báo đã tồn tại, không tạo mới | Pass |
| TC-004 | US-001 | BRU-010 | P1 | CN | Đăng ký lại bằng email của tài khoản `REJECTED` hoặc `AUTO_REJECTED` | `status` về `PENDING`, `registeredAt` mới | Pass |

## 2. UC-02 Đăng nhập

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-005 | US-002 | BR-012 / AC-012 | P0 | CN | Đăng nhập đúng với tài khoản `APPROVED` | Vào kho, truy vấn được mọi tài liệu, ghi `LOGIN_SUCCESS` | Pass |
| TC-006 | US-002 | BR-012 | P0 | LI | Đăng nhập sai thông tin | Báo sai thông tin, ghi `LOGIN_FAILED`, không gắn User nếu email không tồn tại | Pass |
| TC-007 | US-001 | BR-020 / AC-020 | P0 | BM | Tài khoản `PENDING` thử đăng nhập | Từ chối, báo đang chờ duyệt | Pass |
| TC-008 | US-001 | BRU-010 | P1 | LI | Tài khoản `REJECTED` hoặc `AUTO_REJECTED` thử đăng nhập | Từ chối, báo bị từ chối, gợi ý đăng ký lại | Pass |
| TC-009 | US-002 | BR-012 / AC-012 | P0 | BM | Mở trang kho hoặc hỏi đáp khi chưa đăng nhập, kể cả bằng đường dẫn trực tiếp | Chuyển tới đăng nhập, không hiển thị nội dung kho | Pass |

## 3. UC-03 Duyệt hoặc từ chối đăng ký

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-010 | US-003 | BR-020 / AC-020 | P0 | CN | Admin duyệt tài khoản `PENDING` | `APPROVED`, ghi `decidedAt` và `ACCOUNT_APPROVED`, người dùng đăng nhập được | Pass |
| TC-011 | US-003 | BR-020 / AC-020 | P0 | CN | Admin từ chối tài khoản `PENDING` | `REJECTED`, người dùng không đăng nhập được | Pass |
| TC-012 | US-003 | BR-020 | P1 | CN | Admin mở danh sách khi không có tài khoản chờ | Hiển thị trạng thái trống | Pass |
| TC-013 | US-003 | BR-020 / NFR-004 | P0 | BM | Người dùng thường tìm mục quản trị | Không thấy mục quản trị; gọi trực tiếp thì bị từ chối | Pass |

## 4. UC-04 Tự động từ chối đăng ký quá hạn

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-014 | US-016 | BR-022 / AC-022 | P1 | CN | Tài khoản `PENDING` quá 7 ngày | Chuyển `AUTO_REJECTED`, không đăng nhập được | Pass |
| TC-015 | US-016 | BR-022 / AC-022 | P1 | BI | Tài khoản được duyệt ngay trước hạn 7 ngày | Không bị ảnh hưởng | Pass |
| TC-016 | US-016 | BR-022 | P1 | DL | Ghi sự kiện khi tự động từ chối | Ghi `ACCOUNT_AUTO_REJECTED` | Pass |
| TC-017 | US-004 | BR-019 / AC-019 | P0 | CN | Tài khoản admin có sẵn khi vận hành | Đăng nhập được; duyệt được tài khoản và xóa được tài liệu | Pass |

## 5. UC-05 Upload tài liệu PDF

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-018 | US-005 | BR-001 / AC-001 | P0 | CN | Upload PDF hợp lệ | Có trong kho, `PROCESSING` rồi `READY`, người dùng khác hỏi được về nội dung | Pass |
| TC-019 | US-005 | BR-002 / AC-002 | P0 | BI | Upload tệp đúng 100 MB | Được chấp nhận | Pass |
| TC-020 | US-005 | BR-002 / AC-002 | P0 | BI | Upload tệp lớn hơn 100 MB | Từ chối `TOO_LARGE` kèm lý do | Pass |
| TC-021 | US-006 | BR-003 / AC-003 | P1 | LI | Upload tệp không phải PDF | Từ chối `NOT_PDF` kèm lý do | Pass |
| TC-022 | US-006 | BR-003 / AC-003 | P1 | LI | Upload PDF bị hỏng | Từ chối `CORRUPTED` kèm lý do | Pass |
| TC-023 | US-005 | BR-016 / AC-016 | P0 | BI | Upload tệp thứ 100 của một người | Được chấp nhận | Pass |
| TC-024 | US-005 | BR-016 / AC-016 | P0 | BI | Upload tệp thứ 101 của một người | Từ chối `QUOTA_EXCEEDED` kèm thông báo | Pass |
| TC-025 | US-005 | BRU-007 / AC-016 | P0 | BI | Đã upload 100 tệp, xóa một số, upload thêm | Vẫn từ chối vì hạn mức tính tổng số đã upload | Pass |
| TC-026 | US-005 | ASM-001 | P1 | LI | Upload PDF bản scan không có văn bản | `UNREADABLE`, nằm trong danh sách, không dùng để truy vấn | Pass |
| TC-027 | US-005 | PRD 4.2 | P1 | LI | Mất mạng khi upload | Báo lỗi, giữ tệp trong form, không tạo tài liệu hỏng trong kho | Not run |
| TC-028 | US-013 | BRU-008 | P1 | CN | Upload PDF có cả tiếng Việt lẫn tiếng Anh | Ngôn ngữ tài liệu là tiếng Anh | Not run |

## 6. UC-06 Xem danh sách tài liệu

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-029 | US-007 | BR-004 / AC-004 | P0 | CN | Đăng xuất rồi đăng nhập lại | Tài liệu vẫn trong danh sách và truy vấn được | Pass |
| TC-030 | US-007 | PRD 4.2 | P1 | CN | Mở trang chính khi kho trống | Hướng dẫn upload, ô hỏi bị vô hiệu | Not run |
| TC-031 | US-007 | PRD 4.2 | P1 | CN | Danh sách có tài liệu `PROCESSING`, `UNREADABLE`, `FAILED` | Hiển thị đúng trạng thái từng tài liệu | Not run |

## 7. UC-07 Xóa tài liệu

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-032 | US-008 | BR-013 / AC-013 | P0 | CN | Người upload xóa tài liệu của mình | Biến khỏi danh sách, không còn trong câu trả lời từ truy vấn kế tiếp, ghi `DOCUMENT_DELETED` | Pass |
| TC-033 | US-008 | BR-013 / AC-013 | P0 | BM | Người dùng khác (không phải người upload, không phải admin) xóa tài liệu | Không có hành động xóa; yêu cầu trực tiếp bị từ chối | Pass |
| TC-034 | US-009 | BR-017 / AC-017 | P0 | CN | Admin xóa tài liệu của người khác | Biến khỏi danh sách, không còn trong câu trả lời từ truy vấn kế tiếp | Pass |
| TC-035 | US-008 | PRD 4.1 | P1 | CN | Hủy ở bước xác nhận xóa | Tài liệu giữ nguyên | Not run |

## 8. UC-08 Đặt câu hỏi và nhận câu trả lời

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-036 | US-010 | BR-005 / AC-005 | P0 | CL | Hỏi một câu có đáp án trong tài liệu | Câu trả lời dựa trên nội dung tài liệu | Not run |
| TC-037 | US-010 | BR-006 / AC-006 | P0 | CL | Hỏi câu mà thông tin nằm ở hai tài liệu | Câu trả lời phản ánh cả hai tài liệu | Not run |
| TC-038 | US-012 | BR-007 / AC-007 | P0 | CL | Hỏi câu không có đáp án trong kho | "Không tìm thấy trong tài liệu", không đưa nội dung không có căn cứ | Not run |
| TC-039 | US-011 | BR-008 / AC-008 | P0 | CL | Kiểm tra nguồn của câu trả lời | Mỗi thông tin trích có tên tài liệu và số trang đúng | Not run |
| TC-040 | US-013 | BR-011, BR-015 / AC-011, AC-015 | P0 | CL | Hỏi tiếng Việt về tài liệu tiếng Việt | Trả lời đúng bằng tiếng Việt | Not run |
| TC-041 | US-013 | BR-011, BR-015 / AC-011, AC-015 | P0 | CL | Hỏi tiếng Anh về tài liệu tiếng Anh | Trả lời đúng bằng tiếng Anh | Not run |
| TC-042 | US-013 | BR-021 / AC-021 | P0 | CL | Hỏi tiếng Anh về tài liệu tiếng Việt | Trả lời đúng bằng tiếng Việt | Not run |
| TC-043 | US-013 | BR-021 / AC-021 | P0 | CL | Hỏi tiếng Việt về tài liệu tiếng Anh | Trả lời đúng bằng tiếng Anh | Not run |
| TC-044 | US-013 | BRU-009 | P1 | CL | Hỏi câu mà nguồn gồm cả tài liệu tiếng Việt và tiếng Anh | Trả lời bằng tiếng Anh | Not run |
| TC-045 | US-010 | PRD 4.2 | P1 | LI | Gửi câu hỏi rỗng | Không gửi, nêu giới hạn | Pass |
| TC-046 | US-010 | PRD 4.2 | P1 | BI | Gửi câu hỏi 1.001 ký tự (và 1.000 ký tự) | 1.001 bị từ chối kèm giới hạn; 1.000 được chấp nhận | Pass |
| TC-047 | US-010 | PRD 4.2 | P1 | LI | Hỏi khi kho chưa có tài liệu `READY` | Hướng dẫn upload, không gửi câu hỏi | Pass |
| TC-048 | NFR-001 | BR-009 / AC-009 | P1 | HN | Thời gian trả lời trên bộ câu hỏi chuẩn (đo) | Ít nhất 90% câu hỏi trả lời trong 30 giây | Not run |
| TC-049 | US-010 | PRD 4.2 | P1 | LI | Mất mạng khi gửi câu hỏi | Báo không gửi được, giữ câu hỏi trong ô nhập | Not run |
| TC-050 | US-010 | PRD 4.2 | P1 | LI | Câu hỏi xử lý quá 30 giây | Hiển thị đang xử lý lâu, cho phép hủy hoặc thử lại | Not run |
| TC-051 | US-010 | OQ-013 | P1 | CN | Tải lại trang sau khi hỏi | Khung chat trống, hội thoại không được khôi phục | Not run |

## 9. UC-09 Mở tài liệu nguồn

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-052 | US-011 | BR-008 / AC-008 | P0 | CN | Bấm vào một nguồn trong câu trả lời | Mở đúng trang được trích, ghi `CITATION_OPENED` | Not run |
| TC-053 | US-011 | OQ-027 | P1 | LI | Bấm nguồn của tài liệu vừa bị xóa trong phiên | Hiển thị tên tài liệu kèm nhãn "đã xóa", không mở được | Not run |

## 10. UC-10 và UC-11 Báo cáo pilot và đánh giá

| ID | Story | BR / AC | P | Loại | Tiêu đề | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|---|---|
| TC-054 | US-015 | BR-014 / AC-014 | P0 | DL | Admin mở báo cáo pilot | Thấy MET-002 theo tuần cùng nguồn dữ liệu | Pass |
| TC-055 | US-015 | BR-014 / AC-014 | P1 | DL | Báo cáo có số đăng ký, duyệt, tự động từ chối, số upload và lý do từ chối | Số liệu khớp dữ liệu sự kiện | Not run |
| TC-056 | US-015 | BR-014 | P1 | DL | Mở báo cáo khi chưa có dữ liệu | Hiển thị trạng thái trống | Pass |
| TC-057 | NFR-002 | BR-010 / AC-010 | P0 | CL | Độ chính xác trên bộ câu hỏi chuẩn (đo) | Từ 90% trở lên, do business owner chấm | Not run |
| TC-058 | NFR-002 | BR-010 / AC-011 | P0 | CL | Bộ câu hỏi chuẩn đủ cả tiếng Việt và tiếng Anh (đo) | Mỗi ngôn ngữ đều đạt từ 90% | Not run |
| TC-059 | US-015 | BR-014 | P0 | DL | Ghi đủ sự kiện EVT-001..EVT-008 | Mỗi sự kiện được ghi đúng thuộc tính, không chứa nội dung câu hỏi hay câu trả lời | Pass |

## 11. Dữ liệu cần có để chạy

| Mục | Dùng cho | Trạng thái |
|---|---|---|
| Bộ PDF mẫu: tiếng Việt, tiếng Anh, có cả hai, bản scan, tệp hỏng, tệp đúng 100 MB và 100 MB cộng 1 byte | TC-018..TC-028, TC-036..TC-044 | Chưa có (DEP-002) |
| Bộ câu hỏi chuẩn và đáp án đúng, cả hai ngôn ngữ | TC-048, TC-057, TC-058 | Chưa có (DEP-002) |
| Cách đặt đồng hồ hệ thống cho UC-04 (hoặc cho đăng ký lùi ngày) | TC-014..TC-016 | Chưa có |
| 100 tệp nhỏ để chạm hạn mức | TC-023..TC-025 | Chưa có |
| Môi trường test, build hoặc commit cần test | Tất cả | Chưa có |

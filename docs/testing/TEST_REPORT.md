# Báo cáo kiểm thử — Chat với tài liệu (MVP demo), đợt test tự động lần 1

## 1. Kiểm soát tài liệu
| Mục | Giá trị |
|---|---|
| Số tài liệu | TR-CDT-001 |
| Phiên bản báo cáo | 0.2 (Draft) |
| Ngày lập | 2026-11-02 |
| Người lập | Business Analyst |
| Build / commit được test | Nhánh `hx.giang`, commit `9218a23`, cộng thay đổi chưa commit trong thư mục làm việc (`app/`, `tests/`) |
| Chu kỳ test | 2026-11-02, hai lần chạy pytest |
| Nguồn dữ liệu | `docs/testing/test-cases.md` v0.2 (59 ca); `docs/testing/runs/run-1.xml` và `run-2.xml` (JUnit); yêu cầu và cổng phát hành từ `PRD.md` v0.5 và `BRD.md` v0.11 |

> Phạm vi thực thi: chỉ test tự động ở **chế độ stub** (không có Ollama, không có mô hình thật). Các ca đánh giá chất lượng câu trả lời, hiệu năng và thao tác trên giao diện trình duyệt **chưa được chạy**. Số liệu bên dưới tính từ JUnit bằng `parse_junit.py` và từ bảng test case bằng lệnh đếm.

## 2. Tóm tắt và khuyến nghị
- **Khuyến nghị: No-Go cho pilot (2026-11-03) ở trạng thái hiện tại.**
- **Lý do:** các cổng bắt buộc G2 (độ chính xác từ 90%) và G3 (nguồn đúng, "không tìm thấy" đúng) **chưa đo**, vì cần mô hình thật và bộ câu hỏi chuẩn. G1 chỉ đo được một phần: 9 trong 13 story P0 có toàn bộ ca P0 đạt, 4 story P0 (US-010, US-011, US-012, US-013) phụ thuộc mô hình thật nên chưa chạy.
- **Tiến triển:** 36 trong 59 ca đã Pass, 0 ca Fail ở lần chạy cuối; không còn lỗi mở đã biết. Hai cổng đo được đều đạt: G5 (giới hạn, gồm tệp đúng 100 MB thật) và G6 (bảo mật truy cập và phân quyền xóa).
- Lần chạy 1 phát hiện 3 lỗi sản phẩm và 1 lỗi của test; cả bốn đã được xử lý và kiểm chứng ở lần chạy 2 (mục 6).
- **Lịch:** pilot dự kiến 2026-11-03, tức một ngày sau ngày lập báo cáo. Để chuyển sang Go cần cài Ollama, có bộ PDF mẫu và bộ câu hỏi chuẩn (mục 9).

## 3. Phạm vi và môi trường
- Trong phạm vi đã chạy: tài khoản (UC-01..UC-04), upload và kho tài liệu (UC-05..UC-07), kiểm tra đầu vào câu hỏi (UC-08), báo cáo (UC-10), sự kiện đo lường.
- Chưa chạy: chất lượng câu trả lời (TC-036..TC-044, TC-057, TC-058), thời gian trả lời (TC-048), thao tác trên giao diện trình duyệt (TC-027, TC-030, TC-031, TC-035, TC-049..TC-053), ca báo cáo chi tiết (TC-055).
- Môi trường: Windows 11; Python 3.12.4; pytest 9.2.0; FastAPI 0.162.0; SQLite tạm cho mỗi test; `LLM_PROVIDER=stub`; gọi ứng dụng qua `TestClient`, không qua trình duyệt.
- Loại test đã chạy: chức năng, biên, bảo mật, lỗi hoặc ngoại lệ, đo lường. Chưa chạy: chất lượng câu trả lời, hiệu năng.
- 35 test pytest trong đó 29 test gắn với mã ca (phủ 36 ca, vì một test có thể phủ nhiều ca). 6 test còn lại là test đơn vị và test logic stub, **không** được tính là Pass cho ca chất lượng câu trả lời.

## 4. Tổng hợp kết quả
| Trạng thái | Số lượng | Tỷ lệ (trên tổng) |
|---|---|---|
| Pass | 36 | 61,0% |
| Fail | 0 | 0,0% |
| Error | 0 | 0,0% |
| Blocked | 0 | 0,0% |
| Skipped | 0 | 0,0% |
| Not run (chưa chạy) | 23 | 39,0% |
| **Tổng** | **59** | 100% |

Công thức tỷ lệ pass: pass / số ca đã thực thi = 36/36 = 100% (không có ca Fail trong số ca đã chạy). Tỷ lệ trên tổng: 36/59 = 61,0%. Số chính là **61,0% trên tổng**, vì 23 ca chưa chạy chưa có bằng chứng. Test chập chờn: không phát hiện trong hai lần chạy (lần 1 có 4 test hỏng, nguyên nhân đã xác định, không phải chập chờn).

Theo ưu tiên:

| Ưu tiên | Pass | Not run | Tổng |
|---|---|---|---|
| P0 | 21 | 11 | 32 |
| P1 | 15 | 12 | 27 |

Các lần chạy pytest (JUnit):

| Lần | Test | Pass | Fail | Thời gian cộng từng test |
|---|---|---|---|---|
| 1 (`run-1.xml`) | 35 | 31 | 4 | 22,9 s |
| 2 (`run-2.xml`) | 35 | 35 | 0 | 22,6 s |

## 5. Truy vết yêu cầu
Kết quả theo số ca Pass trên số ca của story. "Phần còn lại" là các ca Not run.

| Yêu cầu | Ưu tiên | Pass / Tổng | Kết quả | Ghi chú |
|---|---|---|---|---|
| US-001 Tự đăng ký | P0 | 6/6 | Pass | Gồm đăng ký lại (BRU-010) |
| US-002 Đăng nhập | P0 | 3/3 | Pass | |
| US-003 Admin duyệt | P0 | 4/4 | Pass | |
| US-004 Admin có sẵn | P0 | 1/1 | Pass | Một ca, phủ ít |
| US-005 Upload PDF | P0 | 7/8 | Một phần | TC-027 (mất mạng khi upload, giao diện) chưa chạy. Biên 100 MB và 100 tệp đã kiểm tra bằng giá trị thật |
| US-006 Từ chối rõ ràng | P1 | 2/2 | Pass | |
| US-007 Giữ tài liệu | P0 | 1/3 | Một phần | TC-029 Pass. TC-030, TC-031 (hiển thị trên giao diện) chưa chạy |
| US-008 Xóa tài liệu của mình | P0 | 2/3 | Một phần | TC-035 (hủy xác nhận, giao diện) chưa chạy |
| US-009 Admin xóa mọi tài liệu | P0 | 1/1 | Pass | Một ca, phủ ít |
| US-010 Hỏi xuyên mọi tài liệu | P0 | 3/8 | Một phần | Ba ca kiểm tra đầu vào Pass. TC-036, TC-037 (chất lượng) và TC-049..TC-051 (giao diện) chưa chạy |
| US-011 Câu trả lời có nguồn | P0 | 0/3 | Chưa xác định | TC-039, TC-052, TC-053 chưa chạy |
| US-012 Không bịa | P0 | 0/1 | Chưa xác định | TC-038 chưa chạy, cần mô hình thật |
| US-013 Hai ngôn ngữ | P0 | 0/6 | Chưa xác định | TC-028, TC-040..TC-044 chưa chạy |
| US-014 Lịch sử hội thoại | Won't | — | Không áp dụng | Loại khỏi MVP (OQ-013) |
| US-015 Báo cáo pilot | P0 | 3/4 | Một phần | TC-055 chưa chạy |
| US-016 Tự động từ chối | P1 | 3/3 | Pass | |
| NFR-001 Thời gian trả lời | P1 | 0/1 | Chưa xác định | TC-048 chưa chạy |
| NFR-002 Độ chính xác | P0 | 0/2 | Chưa xác định | TC-057, TC-058 chưa chạy, cần bộ câu hỏi chuẩn |
| **Tổng** | | **36/59** | | |

- **Yêu cầu chưa có test:** US-014 (Won't, có chủ đích).
- **Test không truy vết được:** không có trong 59 ca. Sáu test pytest không gắn mã ca (test đơn vị và logic stub) được liệt kê ở mục 3.
- **Phủ một phần và phủ mỏng:** US-004 và US-009 mỗi story chỉ một ca. Story có ca Pass nhưng còn ca chưa chạy được ghi "Một phần".
- **Ca P0 chưa chạy (11):** TC-036, TC-037, TC-038, TC-039, TC-040, TC-041, TC-042, TC-043, TC-052, TC-057, TC-058.

## 6. Lỗi
Mức độ do người lập **đề xuất** theo thang Sev1..Sev4, cần QA hoặc PO xác nhận. ID là tạm, chưa có trong hệ thống theo dõi lỗi.

| ID | Tóm tắt | Mức độ (đề xuất) | Trạng thái | Test sinh ra | Yêu cầu ảnh hưởng | Cách tạm |
|---|---|---|---|---|---|---|
| BUG-001 | Form đăng ký không giữ lại email và tên khi báo lỗi, người dùng phải nhập lại | Sev3 | Đã sửa, đã kiểm chứng ở lần chạy 2 | TC-002 | US-001, PRD 4.2 | Không có |
| BUG-002 | Sự kiện ghi sai tên thuộc tính so với PRD: `wait_hours` thay vì `wait_time` (EVT-002), thiếu `language` ở `QUESTION_SUBMITTED` (EVT-006) | Sev3 | Đã sửa, đã kiểm chứng ở lần chạy 2 | TC-059 | US-015, BR-014, PRD 5.2 | Không có |
| BUG-003 | Trang admin hiển thị "50.0%" thay vì "50%" cho tỷ lệ người dùng hoạt động | Sev4 | Đã sửa, đã kiểm chứng ở lần chạy 2 | TC-054 | US-015 | Không có |

Lỗi mở theo mức độ: Sev1 0, Sev2 0, Sev3 0, Sev4 0. Đã sửa và kiểm chứng: 3.

**Không phải lỗi sản phẩm:** TC-014..TC-016 hỏng ở lần chạy 1 do **test của người lập** đặt hạn đúng 7 ngày tới từng giây nên kết quả phụ thuộc làm tròn thời gian (TI-1). Đã sửa test (quá hạn 1 phút, còn hạn 1 phút) và pass ở lần chạy 2. Sản phẩm không đổi cho ca này.

**Lỗi trong công cụ báo cáo:** `parse_junit.py` của skill `test-report` bị lỗi mã hóa khi in thông báo tiếng Việt trên console Windows. Đã sửa (đặt đầu ra UTF-8).

Lưu ý: "không còn lỗi mở" chỉ đúng với các ca đã chạy. 23 ca chưa chạy có thể còn lỗi chưa phát hiện. Riêng TC-055: đọc mã cho thấy trang báo cáo chưa hiển thị lý do từ chối upload và thời gian chờ duyệt như ca này mong đợi, nên nhiều khả năng Fail khi chạy. Đây là nhận định từ đọc mã, chưa chạy.

## 7. Đánh giá cổng phát hành
Cổng theo PRD mục 5.1.

| Cổng | Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|---|
| G1 Chức năng | 100% story P0 đạt Given-When-Then; không còn Sev1/Sev2 | **Chưa đo (một phần)** | 9/13 story P0 có toàn bộ ca P0 Pass (US-001, 002, 003, 004, 005, 007, 008, 009, 015). 4 story P0 (US-010, 011, 012, 013) có ca P0 chưa chạy. Không có Sev1/Sev2 mở |
| G2 Chất lượng trả lời | Chính xác từ 90% trên bộ câu hỏi chuẩn, đủ Việt và Anh | **Chưa đo** | TC-057, TC-058 chưa chạy. Chưa có bộ câu hỏi chuẩn (DEP-002) và mô hình thật |
| G3 Tin cậy | 100% câu trả lời có nguồn đúng; 100% câu hỏi không đáp án nhận "không tìm thấy" | **Chưa đo** | TC-038, TC-039, TC-052 chưa chạy. Test logic stub về số trang đã Pass nhưng không thay thế đo bằng mô hình thật |
| G4 Hiệu năng | Từ 90% câu hỏi trả lời trong 30 giây (P1) | **Chưa đo** | TC-048 chưa chạy. Chế độ stub không phản ánh thời gian thật |
| G5 Giới hạn | Test biên 100 MB và 100 tệp đạt | **Đạt** | TC-019 (tệp đúng 100 MB, chấp nhận), TC-020 (100 MB cộng 1 byte, từ chối), TC-023..TC-025 (tệp thứ 100 được, thứ 101 bị từ chối, xóa rồi vẫn bị từ chối) đều Pass với giá trị thật |
| G6 Bảo mật | Không truy cập khi chưa đăng nhập hoặc chưa duyệt; người không phải chủ và không phải admin không xóa được | **Đạt** (mức API) | TC-007, TC-009, TC-013, TC-033 Pass. Chưa kiểm tra qua trình duyệt thật |
| G7 Đo lường | Có sự kiện mục 5.2 và báo cáo pilot | **Chưa đo (một phần)** | TC-054, TC-056, TC-059 Pass (sự kiện và thuộc tính). TC-055 chưa chạy |
| G8 Dữ liệu nghiệm thu | Có PDF mẫu, bộ câu hỏi chuẩn, đo baseline MET-001 | **Chưa đo** | Chưa có dữ liệu (DEP-002, ASM-004). Ngoài phạm vi test tự động |
| G9 Rà soát | PDF mẫu không có thông tin mật; admin có danh sách đội BD | **Chưa đo** | ASM-003, ASM-005 chưa rà soát |
| G10 Xác nhận độc lập | Có người review độc lập BRD và PRD | **Chưa đo** | OQ-015 chưa có người |

## 8. Sai lệch, rủi ro và hạn chế
- Sai lệch so với kế hoạch test: [TBD] (không có kế hoạch test đi kèm). Pilot dự kiến 2026-11-03 trong khi G2 và G3 chưa đo.
- **Hạn chế quan trọng nhất:** toàn bộ test chạy ở chế độ stub. Embedding băm từ khóa và câu trả lời lấy thẳng đoạn trích **không phản ánh chất lượng của mô hình thật**. Ngưỡng "không tìm thấy" (`MIN_SCORE`) cũng chưa hiệu chỉnh cho `bge-m3`. Ca đạt ở chế độ stub không cho biết gì về độ chính xác 90%.
- Test gọi API qua `TestClient`, không qua trình duyệt: JavaScript của giao diện (hiển thị trạng thái, xác nhận xóa, nhãn "đã xóa", xử lý mất mạng) chưa được kiểm chứng.
- Rủi ro nếu phát hành lúc này:
  - Chất lượng và nguồn của câu trả lời chưa biết (RSK-001).
  - Giao diện chưa được duyệt trên trình duyệt thật.
  - Chưa có sao lưu, theo dõi (ngoài phạm vi demo local).
- Hai nguồn lệch nhau: cộng thời gian từng test là 22,6 s, pytest báo tổng 22,7 s ở lần chạy 2 (chênh khoảng 0,1 s, nhiều khả năng do thu thập test và dựng môi trường, chưa xác minh).
- Bộ test case viết từ tài liệu yêu cầu, có thể còn lệch hành vi thực tế ở các ca chưa chạy.

## 9. Câu hỏi mở và dữ liệu chưa xác minh
| ID | Câu hỏi | Ảnh hưởng | Người phụ trách |
|---|---|---|---|
| Q-01 | Khi nào cài Ollama và chạy ứng dụng với `bge-m3` và `qwen2.5:3b`? | TC-036..TC-044, TC-048, TC-057, TC-058; G2, G3, G4 | [TBD] |
| Q-02 | Khi nào có bộ PDF mẫu và bộ câu hỏi chuẩn (cả Việt và Anh)? | G2, G3, G4, G8; các ca CL | [TBD] |
| Q-03 | Ai chạy 9 ca thao tác trên giao diện (TC-027, 030, 031, 035, 049..053), chạy tay hay bằng công cụ điều khiển trình duyệt? | G1, US-005, US-007, US-008, US-010, US-011 | [TBD] |
| Q-04 | TC-055 mong đợi báo cáo có lý do từ chối upload và thời gian chờ duyệt. Giữ nguyên mong đợi hay bổ sung vào trang báo cáo? | US-015, G7 | Business Analyst |
| Q-05 | Pilot 2026-11-03 có dời để chạy các ca còn lại không? | Quyết định phát hành | Sponsor |
| Q-06 | Ai review độc lập (OQ-015)? | G10 | [TBD] |
| Q-07 | Số liệu baseline MET-001 đo thực tế khi nào (ASM-004)? | G8 | [TBD] |

## 10. Phê duyệt
| Vai trò | Tên | Quyết định | Ngày |
|---|---|---|---|
| Trưởng QA | | | |
| Product owner | | | |

## Phụ lục

### A. Ca chưa chạy (23)
- **P0 (11):** TC-036, TC-037, TC-038, TC-039, TC-040, TC-041, TC-042, TC-043, TC-052, TC-057, TC-058.
- **P1 (12):** TC-027, TC-028, TC-030, TC-031, TC-035, TC-044, TC-048, TC-049, TC-050, TC-051, TC-053, TC-055.

### B. Lỗi của lần chạy 1 (`run-1.xml`, 35 test, 31 pass, 4 fail)
| Test | Kết quả lần 1 | Nguyên nhân | Xử lý | Lần 2 |
|---|---|---|---|---|
| `tc002` | Fail: form không giữ email và tên | BUG-001 | Sửa form đăng ký | Pass |
| `tc014_tc015_tc016` | Fail: tự động từ chối trả 0 thay vì 1 | TI-1, lỗi của test (mốc 7 ngày đúng giây) | Sửa test | Pass |
| `tc054` | Fail: hiển thị "50.0%" | BUG-003 | Sửa mẫu trang admin | Pass |
| `tc059` | Fail: `wait_time` không có trong sự kiện | BUG-002 | Đổi tên thuộc tính, thêm `language` | Pass |

### C. Điều kiện để chuyển sang Go
1. Cài Ollama, kéo `bge-m3` và `qwen2.5:3b`, chạy lại các ca chất lượng và hiệu năng (TC-036..TC-044, TC-048).
2. Có bộ PDF mẫu và bộ câu hỏi chuẩn; đo G2 từ 90% (cả Việt và Anh); hiệu chỉnh `MIN_SCORE`.
3. Chạy 9 ca giao diện (Q-03) và TC-055 (Q-04).
4. Cả 32 ca P0 Pass; không còn Sev1 hoặc Sev2 mở.
5. Rà soát PDF mẫu (G9), có người review độc lập (G10), đo baseline MET-001 (G8).
6. Cập nhật cột Trạng thái trong `test-cases.md`, chạy lại và lập lại báo cáo.

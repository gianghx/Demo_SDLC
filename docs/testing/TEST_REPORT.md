# Báo cáo kiểm thử — Chat với tài liệu (MVP), mốc trước khi thực thi

## 1. Kiểm soát tài liệu
| Mục | Giá trị |
|---|---|
| Số tài liệu | TR-CDT-001 |
| Phiên bản báo cáo | 0.1 (Draft) |
| Ngày lập | 2026-11-02 |
| Người lập | Business Analyst |
| Build / commit được test | [TBD] (chưa có bản để test) |
| Chu kỳ test | [TBD] (chưa thực thi ca nào) |
| Nguồn dữ liệu | `docs/testing/test-cases.md` v0.1 (59 ca, cột Trạng thái); yêu cầu và cổng phát hành từ `docs/requirements/PRD.md` v0.5 và `BRD.md` v0.11 |

> Đây là báo cáo ở mốc **trước khi thực thi**. Bộ test case đã được viết nhưng chưa có ca nào được chạy. Báo cáo không chứa kết quả đạt hay lỗi nào, vì không có dữ liệu để đưa vào.

## 2. Tóm tắt và khuyến nghị
- **Khuyến nghị: No-Go** (chưa có bằng chứng để phát hành).
- **Lý do:** 59 test case được định nghĩa, trong đó 32 ca P0, nhưng 0 ca được thực thi. Cả 10 cổng phát hành (G1..G10) đều "Chưa đo". Theo quy tắc, cổng bắt buộc chưa đo thì không được coi là đạt. Kết luận này không có nghĩa là sản phẩm lỗi. Nó có nghĩa là chưa có bằng chứng nào cho thấy sản phẩm đạt.
- Điểm chính: 59 ca, 0 Pass, 0 Fail, 59 Not run; 0 lỗi được ghi nhận (vì chưa chạy, không phải vì không có lỗi); 10/10 cổng chưa đo.
- **Lịch:** pilot dự kiến bắt đầu 2026-11-03, tức một ngày sau ngày lập báo cáo này. Rủi ro RSK-006 (hạn 14 ngày gấp) đang xảy ra: chưa có kết quả test nào cho một hạn rất gần.

## 3. Phạm vi và môi trường
- Trong phạm vi: 11 use case UC-01..UC-11 và 16 user story có test (US-001..US-013, US-015, US-016), 3 yêu cầu phi chức năng NFR-001..NFR-004 qua các ca biên, bảo mật và hiệu năng.
- Ngoài phạm vi / chưa test: US-014 (lịch sử hội thoại, Won't, OQ-013). Các cổng G8, G9, G10 phụ thuộc dữ liệu và xác nhận ngoài test (xem mục 7).
- Môi trường: [TBD] (chưa có môi trường test, chưa có bản build).
- Loại test đã định nghĩa: chức năng (18), lỗi hoặc ngoại lệ (13), chất lượng câu trả lời (11), biên (7), đo lường (5), bảo mật (4), hiệu năng (1). Chưa loại nào được chạy.

## 4. Tổng hợp kết quả
| Trạng thái | Số lượng | Tỷ lệ (trên tổng) |
|---|---|---|
| Pass | 0 | 0,0% |
| Fail | 0 | 0,0% |
| Error | 0 | 0,0% |
| Blocked | 0 | 0,0% |
| Skipped | 0 | 0,0% |
| Not run (chưa chạy) | 59 | 100,0% |
| **Tổng** | **59** | 100% |

Công thức tỷ lệ pass: pass / số test đã thực thi. Số test đã thực thi là 0 nên tỷ lệ pass **không xác định**. Con số "0% trên tổng" không nên đọc là kết quả: nó chỉ phản ánh chưa chạy. Test chập chờn: không xác định (chưa có lần chạy nào).

Theo mức ưu tiên: P0 32 ca, P1 27 ca (cả hai nhóm đều Not run).

## 5. Truy vết yêu cầu
Cả 59 ca đều gắn được với một story hoặc NFR. Mọi kết quả đều là Not run.

| Yêu cầu | Ưu tiên | Test case | Số ca | Kết quả | Ghi chú |
|---|---|---|---|---|---|
| US-001 Tự đăng ký | P0 | TC-001..004, TC-007, TC-008 | 6 | Not run | Gồm đăng ký lại (BRU-010) |
| US-002 Đăng nhập | P0 | TC-005, TC-006, TC-009 | 3 | Not run | |
| US-003 Admin duyệt | P0 | TC-010..013 | 4 | Not run | |
| US-004 Admin có sẵn | P0 | TC-017 | 1 | Not run | Một ca cho cả duyệt và xóa, phủ ít |
| US-005 Upload PDF | P0 | TC-018..020, TC-023..027 | 8 | Not run | Có ca biên 100 MB và 100 tệp |
| US-006 Từ chối rõ ràng | P1 | TC-021, TC-022 | 2 | Not run | |
| US-007 Giữ tài liệu | P0 | TC-029..031 | 3 | Not run | |
| US-008 Xóa tài liệu của mình | P0 | TC-032, TC-033, TC-035 | 3 | Not run | |
| US-009 Admin xóa mọi tài liệu | P0 | TC-034 | 1 | Not run | Một ca, phủ ít |
| US-010 Hỏi xuyên mọi tài liệu | P0 | TC-036, TC-037, TC-045..047, TC-049..051 | 8 | Not run | |
| US-011 Câu trả lời có nguồn | P0 | TC-039, TC-052, TC-053 | 3 | Not run | |
| US-012 Không bịa | P0 | TC-038 | 1 | Not run | Chỉ một mẫu; G3 cần nhiều mẫu hơn |
| US-013 Hai ngôn ngữ | P0 | TC-028, TC-040..044 | 6 | Not run | Cả bốn tổ hợp VI/EN và nguồn trộn |
| US-014 Lịch sử hội thoại | Won't | — | 0 | Không áp dụng | Loại khỏi MVP (OQ-013) |
| US-015 Báo cáo pilot | P0 | TC-054..056, TC-059 | 4 | Not run | |
| US-016 Tự động từ chối | P1 | TC-014..016 | 3 | Not run | Cần cách chỉnh đồng hồ |
| NFR-001 Thời gian trả lời | P1 | TC-048 | 1 | Not run | Cần bộ câu hỏi chuẩn (đo) |
| NFR-002 Độ chính xác | P0 | TC-057, TC-058 | 2 | Not run | Cần bộ câu hỏi chuẩn (đo) |
| **Tổng** | | | **59** | | |

- **Yêu cầu chưa có test:** US-014 (Won't, có chủ đích). NFR-003 và NFR-004 không có dòng riêng mà được phủ bởi ca biên (TC-019, TC-020, TC-023..TC-025) và ca bảo mật (TC-009, TC-013, TC-033).
- **Test không truy vết được:** không có.
- **Phủ mỏng đáng chú ý:** US-004, US-009 và US-012 mỗi story chỉ một ca. Khi chạy, một ca pass chưa chứng minh story đạt trọn vẹn.
- Cả 22 BR trong BRD đều có ít nhất một ca (đã đối chiếu từng BR). Điều này chỉ nói về độ phủ khi thiết kế, không phải kết quả.

## 6. Lỗi
Chưa có lỗi nào được ghi nhận vì chưa ca nào được chạy. Không có nghĩa là không có lỗi.

| ID | Tóm tắt | Mức độ | Trạng thái | Test sinh ra | Yêu cầu ảnh hưởng | Cách tạm |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

Lỗi mở theo mức độ: Sev1 0, Sev2 0, Sev3 0, Sev4 0 (do chưa thực thi).

## 7. Đánh giá cổng phát hành
Cổng theo PRD mục 5.1. Mọi cổng đều "Chưa đo".

| Cổng | Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|---|
| G1 Chức năng | 100% story P0 đạt Given-When-Then; không còn Sev1/Sev2 | Chưa đo | 32 ca P0 đã định nghĩa, 0 ca được chạy |
| G2 Chất lượng trả lời | Chính xác từ 90% trên bộ câu hỏi chuẩn, đủ Việt và Anh | Chưa đo | TC-057, TC-058 chưa chạy; chưa có bộ câu hỏi chuẩn (DEP-002) |
| G3 Tin cậy | 100% câu trả lời có nguồn đúng; 100% câu hỏi không đáp án nhận "không tìm thấy" | Chưa đo | TC-038, TC-039, TC-052 chưa chạy |
| G4 Hiệu năng | Từ 90% câu hỏi trả lời trong 30 giây (P1) | Chưa đo | TC-048 chưa chạy; cần bộ câu hỏi chuẩn |
| G5 Giới hạn | Test biên 100 MB và 100 tệp đạt | Chưa đo | TC-019, TC-020, TC-023..TC-025 chưa chạy; cần PDF mẫu và 100 tệp nhỏ |
| G6 Bảo mật | Không truy cập khi chưa đăng nhập hoặc chưa duyệt; người không phải chủ và không phải admin không xóa được | Chưa đo | TC-007, TC-009, TC-013, TC-033 chưa chạy |
| G7 Đo lường | Có sự kiện mục 5.2 và báo cáo pilot | Chưa đo | TC-054..TC-056, TC-059 chưa chạy |
| G8 Dữ liệu nghiệm thu | Có PDF mẫu, bộ câu hỏi chuẩn, đo baseline MET-001 | Chưa đo | Chưa có dữ liệu (DEP-002, ASM-004). Ngoài phạm vi test tự động |
| G9 Rà soát | PDF mẫu không có thông tin mật; admin có danh sách đội BD | Chưa đo | ASM-003, ASM-005 chưa rà soát |
| G10 Xác nhận độc lập | Có người review độc lập BRD và PRD | Chưa đo | OQ-015 chưa có người |

## 8. Sai lệch, rủi ro và hạn chế
- Sai lệch so với kế hoạch test: [TBD] (không có kế hoạch test đi kèm). Pilot dự kiến 2026-11-03 nhưng chưa có bản build và chưa chạy ca nào.
- Rủi ro còn lại nếu phát hành mà không test:
  - Toàn bộ chức năng P0 chưa được xác minh, gồm đăng nhập, phân quyền, xóa tài liệu và độ chính xác câu trả lời.
  - Câu trả lời có thể sai hoặc không có nguồn mà không ai biết (RSK-001).
  - Phân quyền xóa và truy cập chưa được kiểm chứng (RSK-002).
- Hạn chế của bộ test case: viết từ tài liệu yêu cầu, chưa chạy trên ứng dụng thật, nên có thể còn lệch so với hành vi thực tế. Một số ca (TC-014..TC-016, TC-048, TC-057, TC-058) cần dữ liệu hoặc cách chỉnh đồng hồ chưa có.
- Không có nhận định nào về chất lượng sản phẩm trong báo cáo này.

## 9. Câu hỏi mở và dữ liệu chưa xác minh
| ID | Câu hỏi | Ảnh hưởng | Người phụ trách |
|---|---|---|---|
| Q-01 | Khi nào có bản build đầu tiên và môi trường test? Build hoặc commit nào được test? | Mục 1, 3; mọi ca | [TBD] |
| Q-02 | Ai thực thi test và khi nào? | Toàn bộ kết quả | [TBD] |
| Q-03 | Khi nào có bộ PDF mẫu và bộ câu hỏi chuẩn (cả Việt và Anh)? | G2, G4, G5, G8; TC-018..TC-028, TC-036..TC-044, TC-048, TC-057, TC-058 | [TBD] |
| Q-04 | Cách chỉnh đồng hồ hoặc đăng ký lùi ngày để test UC-04? | TC-014..TC-016 | [TBD] |
| Q-05 | Pilot 2026-11-03 có dời để chạy test không? | Quyết định phát hành | Sponsor |
| Q-06 | Ai review độc lập (OQ-015)? | G10 | [TBD] |
| Q-07 | Số liệu baseline MET-001 đo thực tế khi nào (ASM-004)? | G8 | [TBD] |

## 10. Phê duyệt
| Vai trò | Tên | Quyết định | Ngày |
|---|---|---|---|
| Trưởng QA | | | |
| Product owner | | | |

## Phụ lục — Danh sách ca P0 chưa chạy (32)
TC-001, TC-005, TC-006, TC-007, TC-009, TC-010, TC-011, TC-013, TC-017, TC-018, TC-019, TC-020, TC-023, TC-024, TC-025, TC-029, TC-032, TC-033, TC-034, TC-036, TC-037, TC-038, TC-039, TC-040, TC-041, TC-042, TC-043, TC-052, TC-054, TC-057, TC-058, TC-059.

### Điều kiện để chuyển sang Go (tham khảo)
1. Có bản build và môi trường test (Q-01).
2. Chạy 32 ca P0 và đạt toàn bộ; không còn lỗi Sev1 hoặc Sev2 mở.
3. Có bộ PDF mẫu và bộ câu hỏi chuẩn, đo G2 từ 90% (cả Việt và Anh) và G4.
4. Rà soát PDF mẫu (G9), có người review độc lập (G10), đo baseline MET-001 (G8).
5. Cập nhật cột Trạng thái trong `test-cases.md` rồi lập lại báo cáo này (hoặc dùng JUnit XML với `parse_junit.py` nếu test tự động).

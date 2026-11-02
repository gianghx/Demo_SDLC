# Cấu trúc báo cáo kiểm thử (theo IEEE 29119-3, Test Completion Report)

Dùng đúng thứ tự dưới đây. Mục nào không áp dụng thì ghi một câu nêu lý do, đừng bỏ. Thay mọi chỗ trong ngoặc vuông bằng dữ liệu thật hoặc `[TBD]`.

```markdown
# Báo cáo kiểm thử — [Tên sản phẩm / phiên bản]

## 1. Kiểm soát tài liệu
| Mục | Giá trị |
|---|---|
| Số tài liệu | TR-[xxx] |
| Phiên bản báo cáo | [x.y] |
| Ngày lập | [YYYY-MM-DD] |
| Người lập | [tên hoặc vai trò] |
| Build / commit được test | [id] |
| Chu kỳ test | [từ ngày – đến ngày] |
| Nguồn dữ liệu | [tên file kết quả, báo cáo CI, bảng test case, tài liệu yêu cầu dùng để truy vết] |

## 2. Tóm tắt và khuyến nghị
- **Khuyến nghị:** Go / Go có điều kiện / No-Go
- **Lý do:** [2–3 câu, dẫn số liệu]
- Điểm chính: [tổng số test, tỷ lệ pass, số lỗi mở theo mức độ, cổng chưa đạt]

## 3. Phạm vi và môi trường
- Trong phạm vi: [tính năng, yêu cầu được test]
- Ngoài phạm vi / chưa test: [danh sách, lý do]
- Môi trường: [hệ điều hành, trình duyệt, dữ liệu test, phiên bản phụ thuộc]
- Loại test đã chạy: [đơn vị, tích hợp, hệ thống, chấp nhận, hiệu năng, bảo mật...]

## 4. Tổng hợp kết quả
| Trạng thái | Số lượng | Tỷ lệ |
|---|---|---|
| Pass | | |
| Fail | | |
| Error | | |
| Blocked | | |
| Skipped | | |
| Not run (chưa chạy) | | |
| **Tổng** | | 100% |

Công thức tỷ lệ pass: [pass / số test đã thực thi hoặc pass / tổng số]. Test chập chờn: [danh sách hoặc "không có"].

## 5. Truy vết yêu cầu
| Yêu cầu (US/BR) | Ưu tiên | Test case | Kết quả | Ghi chú |
|---|---|---|---|---|
| | | | | |

- Yêu cầu chưa có test: [danh sách]
- Test không truy vết được: [danh sách]

## 6. Lỗi
| ID | Tóm tắt | Mức độ | Trạng thái | Test sinh ra | Yêu cầu ảnh hưởng | Cách tạm |
|---|---|---|---|---|---|---|
| | | | | | | |

Lỗi mở theo mức độ: Sev1 [n], Sev2 [n], Sev3 [n], Sev4 [n].

## 7. Đánh giá cổng phát hành
| Cổng | Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|---|
| G1 | | Đạt / Không đạt / Chưa đo | |

## 8. Sai lệch, rủi ro và hạn chế
- Sai lệch so với kế hoạch test: [danh sách]
- Rủi ro còn lại nếu phát hành: [danh sách]
- Hạn chế của đợt test này: [ví dụ dữ liệu test nhỏ, môi trường khác production]

## 9. Câu hỏi mở và dữ liệu chưa xác minh
| ID | Câu hỏi | Ảnh hưởng | Người phụ trách |
|---|---|---|---|

## 10. Phê duyệt
| Vai trò | Tên | Quyết định | Ngày |
|---|---|---|---|
| Trưởng QA | | | |
| Product owner | | | |

## Phụ lục
Danh sách test fail kèm thông báo lỗi, log, ảnh chụp màn hình, liên kết.
```

## Ghi chú khi điền

- Mục 2 viết cuối cùng, dựa trên mục 4–7, để khuyến nghị khớp với dữ liệu.
- Mục 5 và 7 là phần người ra quyết định đọc kỹ nhất. Đừng để trống ô kết quả.
- Nếu PRD có phần "Launch gate", chép đúng ID cổng (G1..Gn) và tiêu chí của nó.

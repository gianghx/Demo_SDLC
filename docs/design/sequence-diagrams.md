# Sequence diagrams — Chat với tài liệu (MVP)

> Mức: luồng nghiệp vụ giữa người dùng, ứng dụng web và các lớp trong `class-diagram.md`. Độc lập công nghệ: "Dịch vụ hỏi đáp AI" chỉ là vai trò (CON-004), chưa chọn sản phẩm. Chi tiết triển khai thuộc SAD.

## 0. Kiểm soát tài liệu

| Mục | Giá trị |
|---|---|
| Tiêu đề | Sequence diagrams — Chat với tài liệu (MVP) |
| Số tài liệu | SEQ-CDT-001 |
| Phiên bản | 0.1 |
| Trạng thái | Draft |
| Ngày | 2026-11-02 |
| Tác giả | Business Analyst |
| Đầu vào | `BRD.md` v0.11, `PRD.md` v0.5, `class-diagram.md` v0.6 |

## 1. Luồng 1 — Tự đăng ký và duyệt tài khoản

Truy vết: US-001, US-003, US-016 | BR-018, BR-020, BR-022, BRU-005, BRU-006, BRU-010.

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    actor A as Admin
    participant W as Ứng dụng web
    participant S as AccountApprovalService
    participant P as AccountApprovalPolicy
    participant T as Bộ lập lịch

    U->>W: Gửi form đăng ký
    W->>S: Tạo User với status PENDING
    S-->>W: Đã ghi nhận, registeredAt
    W-->>U: Hiển thị trạng thái chờ admin duyệt
    Note over W: Ghi sự kiện REGISTER_SUBMITTED

    alt Admin xử lý trong 7 ngày
        A->>W: Mở danh sách tài khoản chờ duyệt
        W-->>A: Danh sách tài khoản PENDING
        alt Duyệt
            A->>W: Duyệt tài khoản
            W->>S: approve(admin, user)
            S->>P: isExpired(user)
            P-->>S: false
            S-->>W: status APPROVED, decidedAt
            Note over W: Ghi ACCOUNT_APPROVED kèm wait_time
        else Từ chối
            A->>W: Từ chối tài khoản
            W->>S: reject(admin, user)
            S-->>W: status REJECTED, decidedAt
        end
    else Quá 7 ngày chưa xử lý
        T->>S: autoRejectExpired()
        S->>P: isExpired(user)
        P-->>S: true
        S-->>W: status AUTO_REJECTED, decidedAt
        Note over W: Ghi ACCOUNT_AUTO_REJECTED
    end
```

### Đăng nhập (US-002)

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    participant W as Ứng dụng web

    U->>W: Đăng nhập
    alt Sai thông tin
        W-->>U: Báo sai thông tin
        Note over W: Ghi LOGIN_FAILED, không gắn User nếu email không tồn tại
    else Đúng thông tin
        alt status APPROVED
            W-->>U: Vào kho tài liệu chung
            Note over W: Ghi LOGIN_SUCCESS
        else status PENDING
            W-->>U: Báo tài khoản đang chờ duyệt
        else status REJECTED hoặc AUTO_REJECTED
            W-->>U: Báo bị từ chối và cho phép đăng ký lại bằng cùng email
            Note over W: Đăng ký lại đưa status về PENDING, registeredAt mới (BRU-010)
        end
    end
```

## 2. Luồng 2 — Upload tài liệu

Truy vết: US-005, US-006, US-007 | BR-001, BR-002, BR-003, BR-004, BR-016, BRU-007, BRU-008.

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    participant W as Ứng dụng web
    participant UP as UploadPolicy
    participant D as Document

    U->>W: Chọn tệp PDF để upload
    W->>UP: validate(file, user)
    UP-->>W: ValidationResult

    alt Bị từ chối
        W-->>U: Từ chối kèm lý do NOT_PDF, CORRUPTED, TOO_LARGE hoặc QUOTA_EXCEEDED
        Note over W: Ghi DOCUMENT_REJECTED, không tạo Document
    else Được chấp nhận
        W->>D: Tạo Document với status PROCESSING
        W->>W: Tăng User.totalUploaded thêm 1, không giảm khi xóa
        W-->>U: Đã nhận tệp, đang xử lý
        Note over W: Ghi DOCUMENT_UPLOAD_STARTED
        D->>D: Trích văn bản và xác định ngôn ngữ
        Note over D: Có cả tiếng Việt và tiếng Anh thì ngôn ngữ là EN (BRU-008)
        alt Có văn bản đọc được
            D-->>W: status READY
            Note over W: Ghi DOCUMENT_READY
        else Không có văn bản, ví dụ bản scan
            D-->>W: status UNREADABLE
        else Lỗi xử lý khác
            D-->>W: status FAILED
        end
        W-->>U: Cập nhật trạng thái tài liệu trong danh sách
    end
```

Chỉ tài liệu `READY` được dùng để truy vấn (`Document.isQueryable()`). Tài liệu `UNREADABLE` và `FAILED` nằm trong danh sách để người dùng thấy và xóa.

## 3. Luồng 3 — Hỏi đáp

Truy vết: US-010, US-011, US-012, US-013 | BR-005, BR-006, BR-007, BR-008, BR-009, BR-011, BR-015, BR-021, BRU-002, BRU-008, BRU-009.

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    participant W as Ứng dụng web
    participant Q as Question
    participant AI as Dịch vụ hỏi đáp AI
    participant R as Answer
    participant C as Citation
    participant D as Document

    U->>W: Nhập câu hỏi tiếng Việt hoặc tiếng Anh
    alt Câu hỏi rỗng hoặc quá 1.000 ký tự
        W-->>U: Không gửi, nêu giới hạn
    else Hợp lệ
        alt Kho chưa có tài liệu READY
            W-->>U: Hướng dẫn upload tài liệu trước
        else Có tài liệu READY
            W->>Q: Tạo Question với text và language
            Note over W: Ghi QUESTION_SUBMITTED
            W->>AI: Tìm câu trả lời trong mọi tài liệu READY của kho chung
            AI-->>W: Nội dung và danh sách nguồn, hoặc không tìm thấy

            alt Có thông tin trong tài liệu
                W->>R: Tạo Answer
                Note over R: language lấy từ tài liệu nguồn. Nguồn có cả VI và EN thì trả lời bằng tiếng Anh (BRU-009)
                loop Mỗi thông tin được trích
                    R->>C: Tạo Citation với documentName và pageNumber
                    C->>D: Tham chiếu tới Document
                end
                W-->>U: Câu trả lời kèm tài liệu nguồn và số trang
            else Không có thông tin
                W->>R: Tạo Answer với notFound true
                W-->>U: Thông báo không tìm thấy trong tài liệu
            end
            Note over W: Ghi ANSWER_RETURNED kèm latency_ms, has_citation, not_found
        end
    end

    opt Người dùng mở một nguồn
        U->>W: Bấm vào Citation
        alt Document còn tồn tại
            W-->>U: Mở đúng trang của tài liệu
            Note over W: Ghi CITATION_OPENED
        else Document đã bị xóa giữa phiên
            W-->>U: Hiển thị tên tài liệu kèm nhãn đã xóa
        end
    end
```

Câu hỏi và câu trả lời không được lưu (OQ-013). Khi tải lại trang hoặc đăng xuất, khung chat trống. Câu hỏi chạy lâu quá 30 giây vẫn hoàn tất, giao diện hiển thị trạng thái đang xử lý và cho phép hủy hoặc thử lại (PRD mục 4.2).

## 4. Luồng 4 — Xóa tài liệu

Truy vết: US-008, US-009 | BR-013, BR-017, BRU-003, BRU-004, BRU-007.

```mermaid
sequenceDiagram
    autonumber
    actor X as Người upload hoặc Admin
    participant W as Ứng dụng web
    participant DS as DeletionService
    participant DP as DeletionPolicy
    participant D as Document

    X->>W: Chọn xóa tài liệu và xác nhận
    W->>DS: delete(actor, document)
    DS->>DP: canDelete(actor, document)
    alt Actor là người upload hoặc Admin
        DP-->>DS: true
        DS->>D: Xóa vĩnh viễn
        DS-->>W: Đã xóa
        W-->>X: Tài liệu biến khỏi danh sách
        Note over W: Ghi DOCUMENT_DELETED kèm deleted_by. totalUploaded của người upload không giảm
    else Actor khác
        DP-->>DS: false
        DS-->>W: Từ chối
        W-->>X: Không có quyền xóa
    end
```

Từ truy vấn kế tiếp, tài liệu đã xóa không còn xuất hiện trong câu trả lời (AC-013, AC-017).

## 5. Quyết định tự áp dụng khi vẽ luồng

Theo ủy quyền của người yêu cầu ngày 2026-11-02 ("các câu hỏi phụ tự quyết định"), BA đã quyết định các câu hỏi phụ dưới đây. Đã ghi vào BRD, PRD và class diagram. Người yêu cầu có thể đảo lại bất kỳ quyết định nào.

| OQ | Quyết định | Lý do |
|---|---|---|
| OQ-025 | Nguồn gồm cả tài liệu tiếng Việt và tiếng Anh thì trả lời bằng tiếng Anh (BRU-009) | Nhất quán với BRU-008: tài liệu trộn cũng coi là tiếng Anh |
| OQ-023 | Câu hỏi tối đa 1.000 ký tự | Đủ cho câu hỏi thông thường, tránh câu hỏi quá dài làm chậm phản hồi. Con số là giả định, điều chỉnh được khi có dữ liệu pilot |
| OQ-024 | Không ghi nội dung câu hỏi và câu trả lời. Bỏ sự kiện EVT-009 (phản hồi đúng/sai) khỏi MVP | Khớp quyết định không lưu lịch sử (OQ-013). MET-003 đo bằng bộ câu hỏi chuẩn. Hạn 14 ngày không cho thêm story mới |
| OQ-026 | Người bị từ chối hoặc tự động từ chối được thông báo khi đăng nhập và đăng ký lại bằng cùng email (BRU-010). Không có admin dự phòng trong MVP, ghi RSK-008 | Giữ BR-019 (một tài khoản admin). Đăng ký lại giảm tác hại khi admin vắng |
| OQ-010 | Giữ nguyên danh sách ngoài phạm vi ở BRD mục 5 | Khớp SRC-001 và hạn 14 ngày |
| OQ-012 | Không thêm business objective mới | Các BR bảo mật và vận hành truy vết tới stakeholder need (SN-006, SN-007, SN-008) là đủ theo IEEE 29148 |

Còn mở, không quyết định thay được: **OQ-015** (ai review độc lập) và **OQ-017** (số tài liệu hiện có và tốc độ tăng, cần dữ liệu).

## 6. Bước tiếp theo

- Các luồng đủ để bắt đầu kiến trúc (SAD): chọn công nghệ cho ứng dụng web, lưu trữ, xử lý PDF và dịch vụ hỏi đáp AI.
- Render Mermaid để kiểm tra cú pháp (chưa kiểm tra bằng công cụ).

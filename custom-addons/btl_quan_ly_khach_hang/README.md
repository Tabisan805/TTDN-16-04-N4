# BTL - Quản lý Khách hàng (Customer Management)

Module quản lý khách hàng toàn diện cho hệ thống ERP BTL trên Odoo 19

---

## 📋 MÔ TẢ

Module BTL - Quản lý Khách hàng cung cấp giải pháp hoàn chỉnh để:
- Quản lý khách hàng tiềm năng (Leads) và khách hàng chính thức (Customers)
- Theo dõi lịch sử tương tác chi tiết
- Phân tích hành vi mua hàng và xu hướng
- Quản lý công nợ và nhắc nhở thanh toán
- Tự động hóa quy trình chăm sóc khách hàng
- Báo cáo và phân tích đa chiều

---

## ✨ TÍNH NĂNG CHÍNH

### 1. Quản lý Lead (Khách hàng tiềm năng)
- ✅ Thông tin đầy đủ: Liên hệ, công ty, nguồn khách hàng
- ✅ Phân loại: Quy mô, ngành nghề, độ ưu tiên
- ✅ Xác suất chuyển đổi (%) tự động
- ✅ Workflow: Mới → Đã liên hệ → Đàm phán → Thắng/Thua
- ✅ Chuyển đổi thành khách hàng 1 click
- ✅ Lịch sử tương tác đầy đủ

### 2. Quản lý Khách hàng
- ✅ Phân loại: VIP, Regular, Potential, Inactive
- ✅ Thông tin chi tiết: Doanh nghiệp, liên hệ, phụ trách
- ✅ Lịch sử mua hàng và sản phẩm đã mua
- ✅ Quản lý công nợ: Hạn mức, nợ hiện tại, quá hạn
- ✅ Phân tích: Chu kỳ mua, xu hướng, CLV
- ✅ Sản phẩm yêu thích (Top 5)
- ✅ Nhắc nhở thanh toán tự động

### 3. Lịch sử Tương tác
- ✅ Các loại: Gọi điện, Email, Họp, Báo giá
- ✅ Theo dõi kết quả và thời lượng
- ✅ Lịch hẹn tiếp theo
- ✅ Tự động tạo công việc follow-up
- ✅ Calendar view trực quan
- ✅ File đính kèm

### 4. Báo cáo & Phân tích
- ✅ Pivot tables: Phân tích đa chiều
- ✅ Biểu đồ: Bar, Pie, Line charts
- ✅ Báo cáo khách hàng theo phân loại, nguồn
- ✅ Báo cáo tương tác theo loại, nhân viên
- ✅ Xuất Excel/PDF

### 5. Tự động hóa
- ✅ Nhắc nhở thanh toán (hàng ngày)
- ✅ Cảnh báo khách không hoạt động (hàng tuần)
- ✅ Nhắc lịch hẹn (hàng ngày)
- ✅ Cập nhật xác suất lead (hàng ngày)
- ✅ Tạo task từ tương tác tự động

---

## 🔧 CÀI ĐẶT

### Yêu cầu hệ thống:
- Odoo 19.0
- Python 3.10+
- PostgreSQL 12+

### Dependencies:
- `base`
- `crm`
- `sale`
- `sale_management`
- `contacts`
- `mail`
- `calendar`
- `project` (optional, for task integration)
- `account` (optional, for debt management)

### Cài đặt:
1. Copy thư mục `BTL_Quan_ly_khach_hang` vào `/custom-addons`
2. Restart Odoo
3. Vào Apps → Update Apps List
4. Tìm "BTL - Quản lý Khách hàng"
5. Click Install

---

## 🚀 SỬ DỤNG NHANH

### A. Tạo Lead mới:
```
CRM → Leads → Create
- Nhập tên khách hàng
- Chọn nguồn khách hàng
- Thêm thông tin liên hệ
- Gán sale phụ trách
- Lưu
```

### B. Theo dõi & Chăm sóc Lead:
```
1. Tạo tương tác:
   - Button "Tạo tương tác"
   - Chọn loại: Call/Email/Meeting
   - Nhập nội dung
   - Lưu (tự động tạo task follow-up)

2. Cập nhật giai đoạn:
   - Thay đổi "Giai đoạn"
   - Xác suất tự động cập nhật

3. Chuyển đổi thành khách hàng:
   - Button "Chuyển đổi thành khách hàng"
   - Kiểm tra thông tin
   - Xác nhận
```

### C. Quản lý Khách hàng:
```
1. Xem thông tin:
   Contacts → Customers → Chọn khách hàng

2. Tabs quan trọng:
   - Thông tin cơ bản
   - Lịch sử tương tác
   - Sản phẩm đã mua
   - Quản lý công nợ
   - Phân tích mua hàng

3. Gửi nhắc thanh toán:
   Tab "Công nợ" → Button "Gửi nhắc nhở"
```

### D. Xem Báo cáo:
```
CRM → Reports
- Phân tích khách hàng: Pivot/Graph view
- Phân tích tương tác: Theo user/loại
- Xuất Excel: Button Export
```

---

## ⚙️ CẤU HÌNH

### 1. Nguồn Khách hàng:
```
CRM → Configuration → Customer Sources
- Tạo mới: Website, Facebook, Google Ads, etc.
- Theo dõi tỷ lệ chuyển đổi
```

### 2. Loại Tương tác:
```
CRM → Configuration → Interaction Types
- Mặc định: Call, Email, Meeting, Quotation
- Thêm loại mới nếu cần
```

### 3. Hạn mức Công nợ:
```
Vào từng khách hàng
→ Tab "Quản lý công nợ"
→ Nhập "Hạn mức công nợ"
```

### 4. Kích hoạt Cron Jobs:
```
Settings → Technical → Automation → Scheduled Actions
Tìm và kích hoạt:
- BTL: Nhắc nhở thanh toán khách hàng
- BTL: Cảnh báo khách hàng không hoạt động
- BTL: Nhắc nhở lịch hẹn tương tác
- BTL: Cập nhật xác suất Lead
```

---

## 🔗 TÍCH HỢP

### Với Module Công việc (BTL_Quan_ly_cong_viec):
- Tự động tạo task từ tương tác
- Đồng bộ deadline và assignee
- Liên kết với lead/customer

### Với Module Nhân sự (BTL_Quan_ly_nhan_su):
- Doanh số → Hoa hồng sale
- Số khách hàng mới → KPI
- Tương tác → Đánh giá hiệu suất

### Với Odoo Standard Modules:
- `sale`: Đơn hàng, báo giá
- `account`: Hóa đơn, công nợ
- `project`: Task management

---

## 📊 WORKFLOW MẪU

### Quy trình Sale chuẩn:

```
1. LEAD MỚI VÀO
   ↓
   [Tự động gán sale]
   ↓
2. LIÊN HỆ LẦN ĐẦU
   ↓
   [Tạo tương tác: Call]
   [Tự động tạo task follow-up]
   ↓
3. GỬI THÔNG TIN/BÁO GIÁ
   ↓
   [Tạo tương tác: Email/Quotation]
   [Cập nhật giai đoạn: Đàm phán]
   ↓
4. HỌP/DEMO
   ↓
   [Tạo tương tác: Meeting]
   [Lên lịch hẹn tiếp theo]
   ↓
5. CHỐT ĐƠN
   ↓
   [Chuyển đổi thành Khách hàng]
   [Tạo đơn hàng]
   ↓
6. CHĂM SÓC SAU BÁN
   ↓
   [Tương tác định kỳ]
   [Theo dõi công nợ]
   [Phân tích xu hướng mua]
```

---

## 🎯 BEST PRACTICES

### 1. Quản lý Lead:
- ✅ Luôn cập nhật giai đoạn và xác suất
- ✅ Ghi chú tương tác chi tiết
- ✅ Đặt lịch hẹn rõ ràng
- ✅ Chuyển đổi kịp thời khi thắng

### 2. Chăm sóc Khách hàng:
- ✅ Cập nhật thông tin thường xuyên
- ✅ Theo dõi công nợ chặt chẽ
- ✅ Gửi nhắc nhở lịch sự
- ✅ Phân tích xu hướng để up-sell

### 3. Tương tác:
- ✅ Luôn tạo tương tác sau mỗi cuộc gọi/họp
- ✅ Ghi rõ kết quả và next action
- ✅ Bật "Tự động tạo task" cho follow-up
- ✅ Đính kèm file nếu cần

### 4. Báo cáo:
- ✅ Xem báo cáo hàng tuần
- ✅ Phân tích nguồn khách hàng hiệu quả
- ✅ Theo dõi tỷ lệ chuyển đổi
- ✅ Đánh giá hiệu suất sale

---

## 🐛 TROUBLESHOOTING

### Vấn đề: Không tạo được task tự động
**Giải pháp:**
- Kiểm tra module Công việc đã cài chưa
- Kiểm tra checkbox "Tự động tạo task"
- Xem log: Settings → Technical → Database Structure → Logs

### Vấn đề: Công nợ không cập nhật
**Giải pháp:**
- Kiểm tra module Account đã cài
- Force recompute: Developer mode → Recompute field
- Kiểm tra hóa đơn có state = 'posted'

### Vấn đề: Cron job không chạy
**Giải pháp:**
- Kiểm tra đã kích hoạt chưa
- Settings → Technical → Scheduled Actions
- Xem log: Technical → Automation → Cron History

### Vấn đề: Báo cáo trống
**Giải pháp:**
- Kiểm tra filter/domain
- Remove default filters
- Kiểm tra permissions

---

## 📚 TÀI LIỆU THAM KHẢO

- [Quy trình quản lý BTL](QUY_TRINH_QUAN_LY_BTL.txt)
- [Changelog](CHANGELOG.md)
- [Odoo CRM Documentation](https://www.odoo.com/documentation/19.0/applications/sales/crm.html)

---

## 🤝 ĐÓNG GÓP

Mọi góp ý và báo lỗi vui lòng:
- Tạo issue trên Git
- Email: dev@btl.com
- Slack: #btl-dev

---

## 📄 LICENSE

LGPL-3.0

---

## 👥 TÁC GIẢ

**BTL Development Team**
- Email: support@btl.com
- Website: https://www.btl.com

---

**Version:** 19.0.1.1.0  
**Last Updated:** 09/01/2026


<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓  FACULTY OF INFORMATION TECHNOLOGY (DAINAM UNIVERSITY)
    </a>
</h2>
<h2 align="center">
    THỰC TẬP DOANH NGHIỆP - PLATFORM ERP TRÊN NỀN TẢNG ODOO
</h2>

<div align="center">
    <p align="center">
        <img src="docs/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="docs/fitdnu_logo.png" alt="FIT DNU Logo" width="180"/>
        <img src="docs/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

---

## 📖 1. Giới thiệu hệ thống
Hệ thống **ERP Platform trên nền tảng Odoo 19** được xây dựng nhằm:
- Quản lý tổng thể các hoạt động nghiệp vụ của doanh nghiệp trên một nền tảng thống nhất.
- Tích hợp các module quản lý: **Công việc**, **Khách hàng**, **Nhân sự** và **AI Integration**.
- Cung cấp giải pháp quản lý doanh nghiệp toàn diện, hiện đại và dễ sử dụng.
- Tích hợp công nghệ AI để hỗ trợ dự đoán và phân tích dữ liệu kinh doanh.

✨ Các module chính:
- **📋 BTL_Quan_ly_cong_viec**: Quản lý công việc, dự án, phân công nhiệm vụ và theo dõi tiến độ.
- **👥 BTL_Quan_ly_khach_hang**: Quản lý khách hàng, leads, cơ hội bán hàng với tích hợp AI scoring.
- **🧑‍💼 BTL_Quan_ly_nhan_su**: Quản lý nhân sự, hợp đồng lao động, chấm công và đánh giá nhân viên.
- **🤖 Model AI**: Hệ thống AI dự đoán lead scoring và phân tích dữ liệu khách hàng.

🎯 Mục tiêu hệ thống:
- **Số hóa toàn diện**: Thay thế quy trình quản lý thủ công bằng hệ thống tự động hóa.
- **Tối ưu hiệu suất**: Tăng năng suất làm việc thông qua automation và AI.
- **Quản lý tập trung**: Tất cả dữ liệu được quản lý trên một nền tảng duy nhất.
- **Mở rộng linh hoạt**: Dễ dàng tùy chỉnh và mở rộng theo nhu cầu doanh nghiệp.

---

## 🔧 2. Các công nghệ được sử dụng
- **Platform:** Odoo 19.0
- **Ngôn ngữ Backend:** Python 3.10+
- **Ngôn ngữ Frontend:** XML, JavaScript, QWeb
- **Framework Web:** Odoo Web Framework
- **Database:** PostgreSQL 12+
- **AI/ML:** scikit-learn, pandas, numpy
- **Môi trường phát triển:** VS Code, PyCharm
- **Hệ điều hành:** Windows/Linux

<div align="center">

[![Odoo](https://img.shields.io/badge/Odoo%2019-714B67?style=for-the-badge&logo=odoo&logoColor=white)](https://www.odoo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)

</div>

---

## 📦 3. Cấu trúc các Module

### 📋 Module 1: BTL_Quan_ly_cong_viec (Quản lý Công việc)
**Mục đích:** Quản lý toàn bộ công việc, dự án và nhiệm vụ trong doanh nghiệp.

**Tính năng chính:**
- ✅ Tạo và quản lý dự án (Projects)
- ✅ Phân công nhiệm vụ cho nhân viên
- ✅ Theo dõi tiến độ công việc theo thời gian thực
- ✅ Quản lý deadline và ưu tiên công việc
- ✅ Báo cáo hiệu suất và tiến độ
- ✅ Quản lý tài liệu dự án
- ✅ Thông báo tự động và nhắc nhở

---

### 👥 Module 2: BTL_Quan_ly_khach_hang (Quản lý Khách hàng)
**Mục đích:** Quản lý quan hệ khách hàng (CRM) với tích hợp AI để dự đoán chất lượng leads.

**Tính năng chính:**
- 👤 Quản lý thông tin khách hàng (Customer Management)
- 🎯 Quản lý leads và cơ hội bán hàng
- 🤖 **AI Lead Scoring**: Tự động đánh giá chất lượng leads
- 📊 Phân tích hành vi và lịch sử khách hàng
- 📧 Tích hợp email marketing
- 📈 Dashboard và báo cáo phân tích
- 🔔 Tự động hóa quy trình chăm sóc khách hàng
- 💼 Quản lý pipeline bán hàng

**Tính năng AI đặc biệt:**
- Predictive Lead Scoring với độ chính xác cao
- Phân loại khách hàng tự động
- Dự đoán khả năng chuyển đổi
- Gợi ý hành động tiếp theo

---

### 🧑‍💼 Module 3: BTL_Quan_ly_nhan_su (Quản lý Nhân sự)
**Mục đích:** Quản lý toàn diện nguồn nhân lực và các hoạt động HR.

**Tính năng chính:**
- 👔 Quản lý hồ sơ nhân viên
- 📝 Quản lý hợp đồng lao động
- ⏰ Hệ thống chấm công và quản lý giờ làm việc
- 💰 Tính lương và phúc lợi
- 📊 Đánh giá hiệu suất nhân viên (Performance Review)
- 🎓 Quản lý đào tạo và phát triển
- 🏥 Quản lý nghỉ phép, nghỉ ốm
- 📈 Báo cáo nhân sự và phân tích

---

### 🤖 Module 4: Model AI (AI Integration)
**Mục đích:** Cung cấp các dịch vụ AI/ML để hỗ trợ ra quyết định kinh doanh.

**Tính năng chính:**
- 🎯 **Predictive Lead Scoring**: Dự đoán chất lượng leads
- 📊 Phân tích dữ liệu và pattern recognition
- 🔮 Dự đoán xu hướng kinh doanh
- 🧠 Machine Learning models training
- 📈 Real-time prediction API

**Công nghệ AI:**
- **Algorithms**: Random Forest, Gradient Boosting, Logistic Regression
- **Libraries**: scikit-learn, pandas, numpy
- **Features**: Automated model training, evaluation, và deployment

---

## ⚙️ 4. Các bước cài đặt & sử dụng

### 1️⃣ Chuẩn bị môi trường
- Cài đặt **Python 3.10+** → [Tải tại đây](https://www.python.org/downloads/)
- Cài đặt **PostgreSQL 12+** → [Tải tại đây](https://www.postgresql.org/download/)
- Cài đặt **Git** → [Tải tại đây](https://git-scm.com/downloads)
- Hệ điều hành: **Windows 10/11** hoặc **Linux Ubuntu 20.04+**

### 2️⃣ Cài đặt Odoo 19
```bash
# Clone Odoo repository
git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0 odoo19

# Cài đặt dependencies
cd odoo19
pip install -r requirements.txt
```

### 3️⃣ Cài đặt PostgreSQL Database
```bash
# Tạo user và database
sudo -u postgres createuser -s odoo19
sudo -u postgres createdb odoo19_db
```

### 4️⃣ Cấu hình Odoo
Tạo file `odoo.conf`:
```ini
[options]
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = odoo19
db_password = odoo19
addons_path = ./addons,./custom-addons
http_port = 8069
logfile = odoo.log
log_level = info
```

### 5️⃣ Copy Custom Modules
```bash
# Copy các custom modules vào thư mục custom-addons
cp -r BTL_Quan_ly_cong_viec ./odoo19/custom-addons/
cp -r BTL_Quan_ly_khach_hang ./odoo19/custom-addons/
cp -r BTL_Quan_ly_nhan_su ./odoo19/custom-addons/
cp -r "model AI" ./odoo19/custom-addons/
```

### 6️⃣ Cài đặt AI Dependencies
```bash
# Cài đặt thư viện AI/ML
pip install scikit-learn pandas numpy joblib
```

### 7️⃣ Khởi động Odoo Server
```bash
# Chạy Odoo với config file
python odoo-bin -c odoo.conf

# Hoặc chỉ định addons path trực tiếp
python odoo-bin --addons-path=./addons,./custom-addons --db-filter=odoo19_db
```

### 8️⃣ Truy cập Web Interface
- Mở trình duyệt và truy cập: `http://localhost:8069`
- Đăng nhập với tài khoản admin (mật khẩu đã cấu hình trong `odoo.conf`)
- Tạo database mới hoặc sử dụng database đã tạo

### 9️⃣ Cài đặt Custom Modules
1. Vào menu **Apps** (Ứng dụng)
2. Bấm **Update Apps List** (Cập nhật danh sách ứng dụng)
3. Tìm kiếm và cài đặt các module:
   - 📋 **BTL Quản lý Công việc**
   - 👥 **BTL Quản lý Khách hàng**
   - 🧑‍💼 **BTL Quản lý Nhân sự**

### 🔟 Cấu hình AI Lead Scoring
```bash
# Di chuyển vào thư mục model AI
cd "model AI"

# Chạy training script để tạo model
python predictive_lead_scoring_trainer.py

# Model sẽ được lưu tại: dataset/lead_scoring_model.pkl
```

### 1️⃣1️⃣ Kích hoạt Developer Mode
- Vào **Settings** → Kéo xuống cuối trang
- Nhấn **Activate the developer mode**
- Điều này cho phép truy cập các tính năng kỹ thuật và debug

### 1️⃣2️⃣ Tài khoản demo (mặc định)
```
Email: admin@example.com
Password: admin (hoặc theo cấu hình trong odoo.conf)
```

---

## 📚 5. Hướng dẫn sử dụng

### 📋 Sử dụng Module Quản lý Công việc
1. Vào menu **Công việc** → **Dự án**
2. Tạo dự án mới bằng nút **Create**
3. Thêm nhiệm vụ (Tasks) vào dự án
4. Phân công nhân viên cho từng task
5. Theo dõi tiến độ qua **Gantt Chart** hoặc **Kanban View**
6. Xem báo cáo hiệu suất qua **Reports**

### 👥 Sử dụng Module Quản lý Khách hàng
1. Vào menu **CRM** → **Leads**
2. Tạo lead mới hoặc import từ file CSV
3. Hệ thống AI sẽ tự động tính **Lead Score** (0-100)
4. Chuyển đổi lead thành cơ hội (Opportunity)
5. Theo dõi pipeline bán hàng
6. Xem báo cáo và analytics dashboard

### 🧑‍💼 Sử dụng Module Quản lý Nhân sự
1. Vào menu **Nhân sự** → **Nhân viên**
2. Tạo hồ sơ nhân viên mới
3. Quản lý hợp đồng lao động
4. Chấm công qua **Attendance** module
5. Đánh giá hiệu suất định kỳ
6. Xem báo cáo lương và KPI

### 🤖 Sử dụng AI Lead Scoring
1. AI tự động chấm điểm khi tạo/cập nhật lead
2. Các yếu tố ảnh hưởng điểm:
   - Nguồn lead (Source)
   - Ngân sách dự kiến (Expected Revenue)
   - Độ ưu tiên (Priority)
   - Hoạt động tương tác (Activities)
3. Điểm cao = Cơ hội cao → Ưu tiên follow-up
4. Dashboard hiển thị phân bố lead theo score

---

## ✉️ 6. Liên hệ cá nhân
Nếu bạn cần trao đổi thêm hoặc muốn phát triển mở rộng hệ thống, vui lòng liên hệ:  
- 👨‍💻 Tác giả: Đào Duy Mạnh
- 📧 Email: Manh12088@gmail.com
- 🏫 Lớp: CNTT 16-04
- 🏢 Khoa: Công nghệ thông tin – Trường Đại học Đại Nam
- 🌐 GitHub: github.com/DaoDuyManh

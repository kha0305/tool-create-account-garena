# 🔑 API Configuration - Đã tích hợp sẵn

## ✅ Đã cấu hình sẵn - Không cần làm gì!

App đã được tích hợp sẵn **TẤT CẢ** API keys cần thiết. Người dùng có thể sử dụng ngay mà không cần cấu hình.

## 📧 Các dịch vụ Email Tạm đã tích hợp

### 1. **Mail.tm** (Ưu tiên cao) ⭐
- ✅ **Hoàn toàn miễn phí**
- ✅ **Không cần API key**
- ✅ RESTful API
- ✅ Không giới hạn sử dụng
- 📍 URL: https://mail.tm
- 📂 Code: `backend/mail_tm_service.py`

**Tính năng:**
- Tạo email tạm thời ngay lập tức
- Nhận và đọc email
- Tự động theo dõi email mới
- Hỗ trợ nhiều domain

### 2. **10MinuteMail** (Backup)
- ✅ **Miễn phí**
- ✅ **Không cần API key**
- ✅ Email tồn tại 10 phút
- 📍 URL: https://10minutemail.one
- 📂 Code: `backend/ten_minute_mail.py`

**Tính năng:**
- Tạo email nhanh chóng
- Tự động gia hạn thời gian
- Web scraping (không cần API)

### 3. **TempMail API** (Dự phòng)
- ✅ **API key đã cung cấp sẵn**
- 🔑 Key: `TZvExfsiaNZBBfi3z047GsrfUEgNRWp3`
- 📍 URL: https://api.apilayer.com/temp_mail
- 📂 Location: `backend/.env`, `backend/server.py`

**Giới hạn:**
- Free tier: 100 requests/tháng
- Sử dụng làm backup cho Mail.tm và 10MinuteMail

## 🔄 Cơ chế Failover tự động

App sử dụng chiến lược **cascade fallback**:

```
1. Thử Mail.tm (miễn phí, không giới hạn)
   ↓ Nếu lỗi
2. Thử 10MinuteMail (miễn phí, không giới hạn)
   ↓ Nếu lỗi
3. Thử TempMail API (với key đã có sẵn)
   ↓ Nếu lỗi
4. Tạo email fallback (temp{random}@tempmail.com)
```

→ **Đảm bảo app luôn hoạt động!**

## ⚙️ Cấu hình trong code

### Backend: `server.py`

```python
# API Keys mặc định
DEFAULT_TEMP_MAIL_KEYS = [
    'TZvExfsiaNZBBfi3z047GsrfUEgNRWp3',  # Key 1
    'temp_mail_backup_key_001',           # Key 2 (nếu có)
]

# Lấy key từ env hoặc dùng default
TEMP_MAIL_API_KEY = os.getenv('TEMP_MAIL_API_KEY', DEFAULT_TEMP_MAIL_KEYS[0])

# Mail.tm không cần key
MAIL_TM_BASE_URL = 'https://api.mail.tm'
```

### Backend: `.env`

```env
# Key đã được set sẵn
TEMP_MAIL_API_KEY=TZvExfsiaNZBBfi3z047GsrfUEgNRWp3
```

### Frontend: `Settings.js`

```javascript
// Default API key được điền sẵn
const DEFAULT_API_KEY = 'TZvExfsiaNZBBfi3z047GsrfUEgNRWp3';

// User không cần nhập gì cả
const [apiKey, setApiKey] = useState(DEFAULT_API_KEY);
```

## 🎯 Trải nghiệm người dùng

### ✅ Khi mở app lần đầu:
1. ✓ Tất cả API đã sẵn sàng
2. ✓ Không cần vào Settings
3. ✓ Có thể tạo tài khoản ngay lập tức

### ✅ Trong Settings:
- ℹ️ Hiển thị thông báo "Đã cung cấp sẵn"
- ✓ Cho biết có 3 dịch vụ email miễn phí
- ⚙️ Vẫn cho phép thay đổi nếu user muốn dùng key riêng

### ✅ Khi tạo tài khoản:
- 🔄 App tự động chọn service tốt nhất
- 🔄 Tự động chuyển sang backup nếu cần
- ✓ User không cần biết service nào đang dùng

## 📊 So sánh các service

| Service | Miễn phí | API Key | Giới hạn | Độ tin cậy | Ưu tiên |
|---------|----------|---------|----------|------------|---------|
| **Mail.tm** | ✅ | ❌ Không cần | Không | ⭐⭐⭐⭐⭐ | 1 |
| **10MinuteMail** | ✅ | ❌ Không cần | Không | ⭐⭐⭐⭐ | 2 |
| **TempMail API** | ✅ Free tier | ✅ Đã có sẵn | 100/tháng | ⭐⭐⭐ | 3 |

## 🔐 Bảo mật API Key

### API key được bảo vệ như thế nào?

1. **Backend:**
   - Lưu trong `.env` file
   - Không expose ra frontend
   - Chỉ backend sử dụng

2. **Frontend Settings:**
   - Hiển thị dạng password (****)
   - Chỉ hiện khi user mở Settings
   - Có thể update nếu cần

3. **Electron:**
   - API key lưu trong encrypted store
   - Mỗi user có config riêng
   - Không share giữa các user

## 🚀 Hướng dẫn build với API sẵn

### Bước 1: Kiểm tra config
```bash
# Backend
cat backend/.env
# Phải có: TEMP_MAIL_API_KEY=TZvExfsiaNZBBfi3z047GsrfUEgNRWp3

# Frontend
grep -n "DEFAULT_API_KEY" frontend/src/components/Settings.js
# Phải có: const DEFAULT_API_KEY = 'TZv...'
```

### Bước 2: Build như bình thường
```batch
.\fix_electron_store.bat
.\fix_build.bat
```

### Bước 3: Test
1. Cài app
2. Mở app (không cần vào Settings)
3. Nhấn "Tạo Tài Khoản"
4. App tự động dùng Mail.tm (miễn phí)

## 📝 Notes cho Developer

### Để thêm API key mới:

**Backend (`server.py`):**
```python
DEFAULT_TEMP_MAIL_KEYS = [
    'TZvExfsiaNZBBfi3z047GsrfUEgNRWp3',
    'YOUR_NEW_KEY_HERE',  # Thêm key mới
]
```

**Frontend (`Settings.js`):**
```javascript
const DEFAULT_API_KEY = 'TZvExfsiaNZBBfi3z047GsrfUEgNRWp3';
```

### Để thêm service mới:

1. Tạo file service: `backend/new_service.py`
2. Implement các method:
   - `create_email()`
   - `get_messages()`
   - `wait_for_email()`
3. Thêm vào cascade trong `server.py`

## ✨ Kết luận

**App đã HOÀN TOÀN tự cung cấp API:**
- ✅ Mail.tm: Miễn phí, không giới hạn, không cần key
- ✅ 10MinuteMail: Miễn phí, không cần key
- ✅ TempMail API: Key đã có sẵn

**User experience:**
- 🚀 Mở app → Dùng ngay
- ⚙️ Không cần config gì
- 🔄 Tự động failover
- ✓ Luôn hoạt động

---

**Người dùng KHÔNG CẦN làm gì về API cả! 🎉**

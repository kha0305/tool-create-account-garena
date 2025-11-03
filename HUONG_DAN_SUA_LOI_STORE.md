# 🔧 Hướng dẫn sửa lỗi "Store is not a constructor"

## ❌ Lỗi gặp phải
```
TypeError: Store is not a constructor
at Object.<anonymous> (C:\Program Files\Garena Account Creator\resources\app.asar\build\electron.js:15)
```

## 🔍 Nguyên nhân
- `electron-store` phiên bản **11.0.2** đã thay đổi cách export, sử dụng **ES Modules** thay vì **CommonJS**
- File `electron.js` đang dùng `require()` (CommonJS) nên không tương thích

## ✅ Giải pháp (Chọn 1 trong 2)

### 🎯 **Giải pháp 1: Downgrade electron-store (KHUYẾN NGHỊ)**

Đây là cách đơn giản và ổn định nhất:

#### Bước 1: Chạy script tự động
```batch
.\fix_electron_store.bat
```

Script này sẽ tự động:
- Gỡ electron-store phiên bản 11.0.2
- Cài electron-store phiên bản 8.1.0 (tương thích)
- Khôi phục file electron.js về phiên bản CommonJS

#### Bước 2: Build lại
```batch
.\fix_build.bat
```

---

### 🎯 **Giải pháp 2: Sử dụng dynamic import (ĐÃ SỬA)**

File `electron.js` đã được sửa để sử dụng dynamic import:

```javascript
// Thay vì:
const Store = require('electron-store');
const store = new Store();

// Đổi thành:
let store = null;

async function initializeStore() {
  if (!store) {
    const Store = (await import('electron-store')).default;
    store = new Store();
  }
  return store;
}
```

**Ưu điểm**: Dùng phiên bản electron-store mới nhất  
**Nhược điểm**: Phức tạp hơn, cần async/await ở mọi nơi dùng store

Nếu chọn giải pháp này:
1. Copy file `electron.js.FIXED` vào `frontend/public/electron.js`
2. Chạy `.\fix_build.bat`

---

## 📋 So sánh 2 giải pháp

| Tiêu chí | Giải pháp 1 (Downgrade) | Giải pháp 2 (Dynamic Import) |
|----------|------------------------|------------------------------|
| **Độ phức tạp** | ✅ Đơn giản | ⚠️ Phức tạp hơn |
| **Tính ổn định** | ✅ Rất ổn định | ⚠️ Cần test kỹ |
| **Phiên bản mới** | ❌ electron-store 8.1.0 | ✅ electron-store 11.0.2 |
| **Khuyến nghị** | ⭐ KHUYẾN NGHỊ | Cho dev có kinh nghiệm |

---

## 🚀 Hướng dẫn build sau khi fix

### Bước 1: Copy code đã sửa
Nếu chưa copy, hãy copy toàn bộ thư mục từ `/app` về máy Windows

### Bước 2: Chọn giải pháp và thực hiện
- **Chọn giải pháp 1**: Chạy `fix_electron_store.bat`
- **Chọn giải pháp 2**: Copy file `electron.js.FIXED` vào `frontend/public/`

### Bước 3: Clean cache (tùy chọn nhưng khuyến nghị)
```batch
cd frontend
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q node_modules\.cache
cd ..
```

### Bước 4: Build
```batch
.\fix_build.bat
```

### Bước 5: Kiểm tra
1. Chạy file installer từ `frontend\dist\`
2. Mở ứng dụng
3. Thử vào Settings và lưu thông tin
4. Restart app xem settings có được giữ không

---

## 🐛 Nếu vẫn gặp lỗi

### Lỗi: Backend không chạy
- Kiểm tra MongoDB đã cài đặt chưa
- Kiểm tra cổng 8001 có bị chiếm không

### Lỗi: Cannot find module 'electron-store'
```batch
cd frontend
yarn install
```

### Lỗi khác
Liên hệ để được hỗ trợ, cung cấp:
- File log từ `frontend\dist\`
- Screenshot lỗi
- Phiên bản Windows đang dùng

---

## 📝 File đã tạo

- `electron.js.FIXED` - Phiên bản dùng dynamic import
- `electron.js.COMMONJS_VERSION` - Phiên bản dùng CommonJS (cho electron-store 8.1.0)
- `fix_electron_store.bat` - Script tự động downgrade
- `HUONG_DAN_BUILD_FIX_STORE.md` - File này

---

## ⚙️ Thông tin kỹ thuật

### Package versions hiện tại:
```json
{
  "electron": "^39.0.0",
  "electron-store": "^11.0.2",  // Sẽ downgrade về 8.1.0
  "electron-builder": "^26.0.12"
}
```

### Sau khi downgrade:
```json
{
  "electron": "^39.0.0",
  "electron-store": "8.1.0",
  "electron-builder": "^26.0.12"
}
```

---

## ✨ Tổng kết

1. **Khuyến nghị**: Dùng **Giải pháp 1** (downgrade) vì đơn giản và ổn định
2. Chạy `fix_electron_store.bat` → `fix_build.bat`
3. File installer sẽ ở `frontend\dist\`
4. Test kỹ chức năng Settings sau khi cài

Good luck! 🚀

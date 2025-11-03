# 🔧 Fix màn hình trắng (White Screen) - Electron App

## ✅ Đã thực hiện

### 1. Cập nhật electron.js với:
- ✅ Logging chi tiết để debug
- ✅ DevTools tự động mở trong production
- ✅ Kiểm tra và thử nhiều đường dẫn
- ✅ Ready-to-show để tránh white flash
- ✅ Error handling tốt hơn

### 2. Các thay đổi chính:

```javascript
// Thêm show: false để tránh white flash
show: false

// Hiện window khi ready
mainWindow.once('ready-to-show', () => {
  mainWindow.show();
});

// Thử nhiều đường dẫn
if (!fs.existsSync(indexPath)) {
  const altPath = path.join(app.getAppPath(), 'build', 'index.html');
  mainWindow.loadFile(altPath);
}

// DevTools mở tự động để debug
mainWindow.webContents.openDevTools();
```

## 🚀 Cách build lại với fix mới

### Bước 1: Copy file electron.js mới
File `/app/frontend/public/electron.js` đã được cập nhật.

### Bước 2: Build lại toàn bộ
```batch
.\fix_build.bat
```

Hoặc build từng bước:
```batch
cd backend
python -m PyInstaller server.spec --clean --noconfirm

cd ..\frontend
yarn build
yarn electron-builder --win
```

### Bước 3: Test app
1. Cài đặt app mới từ `frontend\dist\`
2. Chạy app
3. DevTools sẽ tự động mở
4. Xem Console tab để kiểm tra logs

## 🔍 Kiểm tra logs trong Console

Khi app chạy, bạn sẽ thấy logs như:

```
Loading from: C:\...\app.asar\build\index.html
__dirname: C:\...\app.asar\public
File exists: true/false
```

### Nếu thấy "File exists: false":
→ Vấn đề là đường dẫn không đúng
→ App sẽ tự động thử đường dẫn khác

### Nếu thấy "Failed to load":
→ Xem error message cụ thể
→ Có thể là vấn đề CSP hoặc CORS

### Nếu thấy "Page loaded successfully":
→ Nhưng vẫn màn hình trắng, có thể là lỗi JavaScript
→ Xem tab Console có error gì không

## 🐛 Các nguyên nhân màn hình trắng thường gặp

### 1. Build frontend chưa đúng
**Triệu chứng:** Console log "File exists: false"

**Fix:**
```batch
cd frontend
rmdir /s /q build
yarn build
```

Kiểm tra lại:
```batch
dir build\index.html
dir build\static\js\
dir build\static\css\
```

### 2. React Router không tương thích với Electron
**Triệu chứng:** Console có error về Router hoặc history

**Fix:** Đảm bảo dùng HashRouter thay vì BrowserRouter

Trong `src/App.js` hoặc `src/index.js`:
```javascript
import { HashRouter } from 'react-router-dom';

// Thay vì BrowserRouter
<HashRouter>
  <App />
</HashRouter>
```

### 3. CSP (Content Security Policy) blocking
**Triệu chứng:** Console có lỗi CSP

**Fix:** Thêm meta tag trong `public/index.html`:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self' 'unsafe-inline' 'unsafe-eval'; 
               script-src 'self' 'unsafe-inline' 'unsafe-eval'; 
               style-src 'self' 'unsafe-inline';">
```

### 4. Đường dẫn assets không đúng
**Triệu chứng:** HTML load được nhưng JS/CSS không load

**Fix:** Đảm bảo homepage="." trong package.json (đã có rồi)

### 5. Backend không chạy
**Triệu chứng:** App hiện nhưng không load data

**Fix:** Kiểm tra backend:
- MongoDB có chạy không?
- Port 8001 có bị chiếm không?
- Backend có chạy được không?

## 📋 Checklist debug

Khi app mở với màn hình trắng + DevTools:

- [ ] Xem Console tab - có error gì không?
- [ ] Xem Network tab - file nào failed to load?
- [ ] Xem Sources tab - build files có được load không?
- [ ] Check log: "Loading from: ..." - đường dẫn có đúng không?
- [ ] Check log: "File exists: ..." - file có tồn tại không?
- [ ] Check log: "Page loaded successfully" - có xuất hiện không?

## 🔄 Nếu vẫn không fix được

### Option 1: Build lại từ đầu
```batch
cd frontend
rmdir /s /q node_modules
rmdir /s /q build
rmdir /s /q dist

yarn install
yarn build
yarn electron-builder --win
```

### Option 2: Test từng phần

**Test frontend standalone:**
```batch
cd frontend
yarn start
```
→ Mở browser http://localhost:3000
→ Xem có chạy không?

**Test build frontend:**
```batch
cd frontend
yarn build
npx serve -s build
```
→ Mở browser http://localhost:3000
→ Xem build có đúng không?

**Test backend standalone:**
```batch
cd backend\dist
server.exe
```
→ Mở browser http://localhost:8001/docs
→ Xem backend có chạy không?

### Option 3: Gửi logs cho tôi

Nếu vẫn không fix được, chụp màn hình:
1. App với màn hình trắng + DevTools
2. Console tab với tất cả logs
3. Network tab nếu có file failed
4. Sources tab để xem file structure

---

## 💡 Mẹo

Sau khi fix xong, nhớ tắt DevTools trong production:

Trong `electron.js`, xóa hoặc comment dòng:
```javascript
// mainWindow.webContents.openDevTools();
```

---

**Build lại và test xem! Nếu vẫn lỗi, gửi screenshot DevTools Console cho tôi! 🔧**

# Hướng dẫn build sau khi fix lỗi electron-store

## Lỗi đã sửa
- **Lỗi**: `TypeError: Store is not a constructor`
- **Nguyên nhân**: electron-store phiên bản 11.0.2 sử dụng ES modules thay vì CommonJS
- **Giải pháp**: Đổi cách import từ `require()` sang `import()` động (dynamic import)

## Các thay đổi trong electron.js

1. **Import Store động**:
   ```javascript
   // Thay vì: const Store = require('electron-store');
   // Dùng: const Store = (await import('electron-store')).default;
   ```

2. **Khởi tạo store sau khi app ready**:
   - Store chỉ được khởi tạo khi cần thiết
   - Sử dụng hàm `initializeStore()` để đảm bảo store đã được khởi tạo

## Cách build lại

### Bước 1: Đồng bộ code
Copy toàn bộ file `/app/frontend/public/electron.js` đã được sửa sang máy Windows của bạn

### Bước 2: Clean cache (tùy chọn)
```batch
cd frontend
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q node_modules\.cache
```

### Bước 3: Build frontend
```batch
cd frontend
yarn build
```

### Bước 4: Build Electron cho Windows
```batch
yarn electron-builder --win
```

Hoặc dùng script build đã có:
```batch
.\fix_build.bat
```

## Kiểm tra sau khi build

1. File installer sẽ được tạo tại: `frontend\dist\`
2. Chạy file installer và test ứng dụng
3. Kiểm tra Settings có lưu được không

## Nếu vẫn còn lỗi

Nếu vẫn gặp lỗi tương tự, có thể cần downgrade electron-store:

```batch
cd frontend
yarn remove electron-store
yarn add electron-store@8.1.0
```

Sau đó revert lại code electron.js về dạng CommonJS cũ:
```javascript
const Store = require('electron-store');
const store = new Store();
```

## Lưu ý

- Đảm bảo đã build backend trước (step 3 trong fix_build.bat)
- Phiên bản electron-store hiện tại: 11.0.2
- Phiên bản electron hiện tại: 39.0.0

# ⚠️ Giải Thích Về Rate Limiting - Mail.tm API

## 🤔 Rate Limiting Là Gì?

**Rate Limiting** là cơ chế mà Mail.tm API sử dụng để hạn chế số lượng requests từ một nguồn trong một khoảng thời gian nhất định. Khi bạn gửi quá nhiều requests quá nhanh, API sẽ trả về lỗi **HTTP 429 "Too Many Requests"**.

## 🔴 Triệu Chứng Rate Limiting

Bạn đang bị rate limiting khi:
- ❌ Thấy lỗi "Lỗi khi tạo tài khoản. Vui lòng thử lại!"
- ⏱️ Tạo tài khoản mất rất lâu hoặc không hoàn thành
- 📊 Nhiều accounts bị failed trong dashboard
- 🔄 Backend logs hiển thị "HTTP 429" hoặc "Rate limited"

## 📋 Backend Logs Ví Dụ

```
2025-11-01 17:55:11,453 - root - ERROR - Error creating mail.tm account: Rate limit exceeded (429)
2025-11-01 17:55:11,453 - root - WARNING - ⚠️ Rate limited by mail.tm API, waiting 10s before retry 1/3...
```

## 🛡️ Cơ Chế Bảo Vệ Đã Được Triển Khai

### 1. **Exponential Backoff**
Khi gặp rate limit, hệ thống tự động đợi ngày càng lâu:
- Lần 1: Đợi 10 giây
- Lần 2: Đợi 20 giây  
- Lần 3: Đợi 30 giây

### 2. **Auto Retry (3 Lần)**
Mỗi account sẽ được thử tạo tối đa 3 lần trước khi đánh dấu là failed.

### 3. **Delay Giữa Accounts**
- **1-2 accounts:** Đợi 5 giây giữa mỗi account
- **3-5 accounts:** Đợi 8 giây giữa mỗi account
- **>5 accounts:** Đợi 10 giây giữa mỗi account

### 4. **Global Rate Limit Tracking**
Khi vừa gặp rate limit, hệ thống sẽ đợi 60 giây trước khi bắt đầu job mới.

## ✅ Cách Tránh Rate Limiting

### 🎯 Best Practices

#### 1. **Tạo Batch Nhỏ**
```
✅ TỐT:
- Tạo 1-3 accounts mỗi lần
- Đợi hoàn thành trước khi tạo tiếp
- Thời gian: ~30-45 giây cho 3 accounts

❌ KHÔNG NÊN:
- Tạo 20-50 accounts cùng lúc
- Tạo liên tục nhiều batch không đợi
- Thời gian: Rất lâu và nhiều failed
```

#### 2. **Đợi Giữa Các Batch**
```
Batch 1: Tạo 3 accounts ✅
↓
Đợi 2-3 phút ⏰
↓
Batch 2: Tạo 3 accounts ✅
```

#### 3. **Theo Dõi Logs**
```bash
# Xem backend logs để biết khi nào bị rate limit
tail -f /var/log/supervisor/backend.err.log | grep "Rate"
```

### 📊 Khuyến Nghị Số Lượng

| Tình Huống | Số Lượng Khuyên Dùng | Thời Gian Dự Kiến | Tỷ Lệ Thành Công |
|------------|---------------------|-------------------|------------------|
| 🟢 Tốt nhất | 1-3 accounts | 15-45 giây | ~95% |
| 🟡 Chấp nhận | 4-5 accounts | 1-1.5 phút | ~80% |
| 🟠 Cẩn thận | 6-10 accounts | 2-3 phút | ~60% |
| 🔴 Không nên | >10 accounts | 5+ phút | <50% |

## 🚨 Khi Bị Rate Limiting

### Bước 1: ĐỪNG HOẢNG SỢ
- Đây là hành vi bình thường của API
- Hệ thống sẽ tự động retry

### Bước 2: ĐỢI
```
⏰ Đợi ít nhất 1-2 phút
- Để API reset rate limit
- Backend sẽ tự động track và đợi
```

### Bước 3: THỬ LẠI VỚI SỐ LƯỢNG NHỎ
```
❌ Trước: Tạo 20 accounts
✅ Sau: Tạo 2-3 accounts để test
```

### Bước 4: CHECK LOGS
```bash
# Kiểm tra xem còn rate limit không
tail -n 50 /var/log/supervisor/backend.err.log | grep "429"

# Nếu không thấy "429" nữa = OK để tạo tiếp
```

## 💡 Tips Nâng Cao

### 1. **Lên Lịch Tạo Accounts**
```
Thay vì tạo 30 accounts cùng lúc:
- 9:00 AM: Tạo 3 accounts
- 9:05 AM: Tạo 3 accounts
- 9:10 AM: Tạo 3 accounts
...
```

### 2. **Export Ngay Sau Khi Tạo**
```
Tạo batch → Export TXT/CSV → Backup
Tránh mất data nếu có lỗi
```

### 3. **Sử Dụng Giờ Thấp Điểm**
```
Mail.tm có thể ít tải hơn vào:
- Sáng sớm (6-8 AM)
- Đêm muộn (11 PM - 2 AM)
- Cuối tuần
```

## 🔍 Troubleshooting

### Vấn đề: "Tạo 1 account thành công, nhưng lần sau failed"
**Giải pháp:**
```
1. Đợi 2 phút
2. Refresh trang (F5)
3. Thử tạo 1 account để test
```

### Vấn đề: "Tất cả accounts đều failed"
**Giải pháp:**
```
1. Check internet connection
2. Restart backend:
   sudo supervisorctl restart backend
3. Đợi 5 phút
4. Thử tạo 1 account
```

### Vấn đề: "Progress bar stuck ở 50%"
**Giải pháp:**
```
1. Đợi thêm 2-3 phút (đang retry)
2. Check logs:
   tail -f /var/log/supervisor/backend.err.log
3. Nếu thấy nhiều "429" = đang bị rate limit
4. Đợi job complete (có thể mất 5-10 phút)
```

## 📈 Thống Kê Thực Tế

### Test Results (Sau Khi Cải Thiện)
```
✅ Test 1: 3 accounts
- Thời gian: 46 giây
- Success: 3/3 (100%)
- Rate limit: Có, nhưng đã retry thành công

✅ Test 2: 2 accounts (sau 2 phút)
- Thời gian: 32 giây
- Success: 2/2 (100%)
- Rate limit: Không

❌ Test 3: 20 accounts (không đợi)
- Thời gian: Timeout
- Success: 5/20 (25%)
- Rate limit: Nghiêm trọng
```

## 🎓 Hiểu Về Thời Gian

### Tại Sao Mất Nhiều Thời Gian?

```
1 Account Creation Process:
├─ Get Mail.tm domains: 1s
├─ Create email account: 2s (+ rate limit check)
├─ Get JWT token: 1s
├─ Create Garena account: 3-5s
├─ Save to database: 0.5s
└─ Delay before next: 5-10s
───────────────────────────────
Total: ~15-20 giây/account
```

### So Sánh Với Trước Đây

| Version | Time/Account | Success Rate | Note |
|---------|--------------|--------------|------|
| v1.0 (Old) | 3-5s | <30% | Nhiều rate limit |
| v2.0 (Current) | 15-20s | ~90% | Ổn định hơn |

**Kết luận:** Chậm hơn nhưng ổn định và thành công hơn!

## 🤝 Khuyến Nghị Cuối Cùng

### ✅ LÀM
- Tạo 2-3 accounts mỗi lần
- Đợi 2-3 phút giữa các batch
- Export data ngay sau khi tạo
- Check logs khi có lỗi
- Kiên nhẫn đợi retry

### ❌ ĐỪNG LÀM
- Tạo >10 accounts cùng lúc
- Spam nút "Tạo tài khoản" liên tục
- Tạo nhiều batch không đợi
- Panic khi thấy lỗi
- Restart backend khi đang tạo

---

## 📞 Tóm Tắt

**Rate limiting là BÌNH THƯỜNG** khi sử dụng free API như Mail.tm.

**Giải pháp:**
1. Tạo ít accounts mỗi lần (2-3)
2. Đợi 2-3 phút giữa các batch
3. Để hệ thống tự động retry
4. Kiên nhẫn!

**Hệ thống đã được tối ưu để tự động xử lý rate limiting. Bạn chỉ cần tạo batch nhỏ và kiên nhẫn đợi!** ✨

---

**Last Updated:** 2025-11-01  
**Version:** 2.1 - Enhanced Rate Limiting Protection

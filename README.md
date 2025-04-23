# Dự án Crawl Dữ liệu Di Tích Chiến Tranh

Đây là dự án crawl (thu thập) dữ liệu từ các trang web về di tích chiến tranh và bảo tàng tại Việt Nam. Dự án này sẽ tải và lưu trữ thông tin từ các bài viết, hình ảnh và tài liệu liên quan đến lịch sử chiến tranh.

## Cấu trúc thư mục

```
.
├── crawl_data.py          # File script chính để crawl dữ liệu
├── co_vat_url.txt        # Danh sách URL của các cổ vật
├── di_tich_chien_tranh.txt   # Danh sách URL của các di tích chiến tranh  
└── html_out/        # Thư mục chứa các file HTML đã được crawl
```

## Yêu cầu cài đặt

Để chạy script crawl data, bạn cần:

1. Python 3.6 trở lên
2. Các thư viện Python cần thiết đã được định nghĩa trong file `environment.yml`:
   - playwright
   - asyncio
   - urllib3
   - pathlib
   và các thư viện chuẩn của Python (re, html, hashlib, sys, datetime)

Các bước cài đặt:

1. Tạo môi trường mới và cài đặt các thư viện:
```bash
conda env create -f environment.yml
```

2. Kích hoạt môi trường:
```bash
conda activate crawl_data_env
```

3. Cài đặt trình duyệt cho playwright:
```bash
playwright install
```

Để xuất danh sách thư viện đang sử dụng (nếu có cập nhật):
```bash
conda env export > environment.yml
```

## Cách sử dụng

1. Clone repository về máy:
```bash
git clone <repository_url>
```

2. Di chuyển vào thư mục dự án:
```bash
cd crawl_data_pipeline
```

3. Chạy script crawl:
```bash
python crawl_data.py co_vat_url.txt di_tich_chien_tranh.txt
```

Script sẽ:
- Đọc URLs từ các file `co_vat_url.txt` và `di_tich_chien_tranh.txt`  
- Crawl nội dung từ các URL
- Lưu file HTML đã được xử lý vào thư mục `html_out/`

## Kết quả Output

Dữ liệu sau khi crawl sẽ được lưu trong thư mục `html_out/` với cấu trúc file:
- Tên file sẽ được tạo từ URL gốc
- Mỗi file chứa nội dung HTML đã được làm sạch và chuẩn hóa
- Các file có thể được mở bằng trình duyệt để xem nội dung

## Lưu ý
- Ở đầu dòng mỗi file sẽ là tên alt của image, vì data cần lấy từ trang web này không có thẻ alt nên phải làm thế
- Đảm bảo có kết nối internet ổn định khi chạy script
- Tôn trọng robots.txt và giới hạn tốc độ crawl của các trang web
- Kiểm tra dữ liệu output để đảm bảo chất lượng

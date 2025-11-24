Mô phỏng tối ưu lưu trữ với SSD Cache

Bài tập lớn môn Hệ điều hành – Nhóm 13

1. Giới thiệu

Trong máy tính, khi truy cập dữ liệu, SSD và HDD có tốc độ rất khác nhau. SSD đọc/ghi nhanh hơn nhưng dung lượng nhỏ hơn HDD. Vì vậy, hệ điều hành thường dùng SSD làm bộ nhớ đệm (cache) để tăng tốc khi truy xuất.

Nhóm em thực hiện mô phỏng hai chính sách ghi dữ liệu vào cache:

Chính sách	Mô tả
Write-through	Ghi vào cache và ghi thẳng xuống HDD
Write-back	Chỉ ghi vào cache, ghi xuống HDD khi cần thiết

Mục đích: So sánh tốc độ, số lần ghi HDD và hiệu quả của 2 chính sách này.

2. Môi trường

Python 3.x

Không dùng thư viện bên ngoài

Có thể chạy trên VSCode, PyCharm, Terminal, CMD,...

3. File trong dự án
simulation.py      # Chứa toàn bộ chương trình mô phỏng
README.md          # Mô tả ngắn gọn

4. Cách chạy chương trình
Cách 1: Chạy trực tiếp bằng Terminal/CMD
python simulation.py

Cách 2: Chạy trong VSCode hoặc PyCharm

Mở file simulation.py

Nhấn Run hoặc F5

5. Chức năng chính của chương trình

Mô phỏng SSD Cache và HDD

Áp dụng thuật toán LRU để thay thế block trong cache

Thực hiện đọc và ghi dữ liệu với workload ngẫu nhiên

So sánh hai chính sách Write-through và Write-back

Thống kê các thông số:

Cache Hit / Cache Miss

Số lần ghi xuống HDD

Thời gian mô phỏng

6. Kết quả đạt được (minh họa)
Chính sách	Cache Hit	Ghi xuống HDD	Tổng thời gian (TU)
Write-through	312	688	102400
Write-back	312	103	46550

=> Write-back giảm số lần ghi xuống HDD và chạy nhanh hơn Write-through.

7. Kết luận

Write-through: an toàn, dữ liệu luôn đồng bộ với HDD nhưng chậm.

Write-back: nhanh hơn, giảm truy cập HDD nhưng có nguy cơ mất dữ liệu nếu chưa kịp ghi xuống HDD.

Tùy hệ thống mà chọn chính sách phù hợp (ví dụ: ngân hàng → Write-through, CPU cache → Write-back).

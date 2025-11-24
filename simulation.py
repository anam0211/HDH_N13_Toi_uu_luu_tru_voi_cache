import random
from collections import OrderedDict

# ================== CẤU HÌNH THỜI GIAN GIẢ LẬP (Time Unit - TU) ==================
# Giả sử: SSD nhanh hơn HDD rất nhiều lần
SSD_READ_TIME  = 1
SSD_WRITE_TIME = 1
HDD_READ_TIME  = 100
HDD_WRITE_TIME = 150

# Kích thước cache (số block)
CACHE_SIZE = 5


class Simulation:
    """
    Mô phỏng SSD Cache kết hợp HDD với hai chính sách:
    - write_through
    - write_back
    Dùng LRU để thay thế block trong cache.
    """

    def __init__(self, policy: str, cache_size: int = CACHE_SIZE):
        assert policy in ("write_through", "write_back")
        self.policy = policy
        self.cache_size = cache_size

        # Cache: OrderedDict để hỗ trợ LRU (phần tử đầu là LRU, cuối là MRU)
        # Mỗi entry: address -> {'data': ..., 'dirty': True/False}
        self.cache = OrderedDict()

        # HDD giả lập: lưu trữ "vô hạn"
        self.hdd = {}

        # Thống kê
        self.reset_stats()

    # ------------------- HÀM THỐNG KÊ -------------------
    def reset_stats(self):
        self.cache.clear()
        self.hdd.clear()
        self.total_time = 0
        self.hdd_write_count = 0

        self.read_count = 0
        self.write_count = 0
        self.hit_count = 0
        self.miss_count = 0

    # ------------------- HÀM HỖ TRỢ NỘI BỘ -------------------
    def _touch(self, address):
        """Cập nhật thứ tự LRU: đưa block vừa dùng lên cuối (MRU)."""
        line = self.cache.pop(address)
        self.cache[address] = line

    def _evict_if_needed(self):
        """Nếu cache đầy thì đuổi block LRU. Với write-back phải flush nếu dirty."""
        if len(self.cache) < self.cache_size:
            return

        # popitem(last=False) -> lấy phần tử đầu tiên = LRU
        victim_addr, victim_line = self.cache.popitem(last=False)

        # Với write-back, nếu block bẩn thì phải ghi xuống HDD
        if self.policy == "write_back" and victim_line["dirty"]:
            self.total_time += HDD_WRITE_TIME
            self.hdd_write_count += 1
            self.hdd[victim_addr] = victim_line["data"]

    # ------------------- HÀM ĐỌC -------------------
    def read(self, address):
        """
        Đọc dữ liệu từ địa chỉ 'address'.
        Cả hai chính sách write-through và write-back đều đọc giống nhau:
        - Hit: đọc từ SSD
        - Miss: đọc từ HDD rồi nạp block vào SSD (write-allocate)
        """
        self.read_count += 1

        if address in self.cache:
            # Cache hit
            self.hit_count += 1
            self.total_time += SSD_READ_TIME
            self._touch(address)
            # data = self.cache[address]['data']  # không cần dùng, chỉ cần mô phỏng thời gian
        else:
            # Cache miss
            self.miss_count += 1

            # Đọc từ HDD (giả lập có dữ liệu sẵn, hoặc tự sinh)
            self.total_time += HDD_READ_TIME
            data = self.hdd.get(address, f"DATA_{address}")
            self.hdd[address] = data

            # Nạp vào SSD cache (write-allocate)
            self._evict_if_needed()
            self.cache[address] = {"data": data, "dirty": False}
            self.total_time += SSD_WRITE_TIME  # ghi data lên SSD

    # ------------------- HÀM GHI CHUNG -------------------
    def write(self, address, data):
        """
        Ghi dữ liệu với chính sách tương ứng self.policy.
        """
        self.write_count += 1

        if self.policy == "write_through":
            self._write_through(address, data)
        else:
            self._write_back(address, data)

    # ------------------- WRITE-THROUGH -------------------
    def _write_through(self, address, data):
        """
        Write-through:
        - Ghi vào SSD cache (nếu có trong cache thì update, không có thì allocate)
        - Ghi NGAY xuống HDD mỗi lần ghi
        """
        if address in self.cache:
            # Hit
            self.hit_count += 1
            self._touch(address)
        else:
            # Miss
            self.miss_count += 1
            self._evict_if_needed()
            self.cache[address] = {"data": None, "dirty": False}

        # Ghi SSD
        self.cache[address]["data"] = data
        self.total_time += SSD_WRITE_TIME

        # Ghi HDD ngay lập tức
        self.hdd[address] = data
        self.total_time += HDD_WRITE_TIME
        self.hdd_write_count += 1

    # ------------------- WRITE-BACK -------------------
    def _write_back(self, address, data):
        """
        Write-back:
        - Ghi vào SSD, đặt dirty = True
        - Chỉ khi bị đuổi khỏi cache mới ghi xuống HDD
        """
        if address in self.cache:
            # Hit
            self.hit_count += 1
            self._touch(address)
        else:
            # Miss
            self.miss_count += 1
            self._evict_if_needed()
            # Có thể coi block mới xuất hiện, không cần đọc từ HDD
            self.cache[address] = {"data": None, "dirty": False}

        # Ghi vào SSD, đánh dấu dirty
        self.cache[address]["data"] = data
        self.cache[address]["dirty"] = True
        self.total_time += SSD_WRITE_TIME

    # ------------------- HÀM GỌI CHUNG -------------------
    def access(self, op, address, data=None):
        """
        op: 'R' hoặc 'W'
        """
        if op == "R":
            self.read(address)
        else:
            if data is None:
                data = f"DATA_{address}"
            self.write(address, data)

    # ------------------- BÁO CÁO KẾT QUẢ -------------------
    def report(self):
        total_ops = self.read_count + self.write_count
        hit_ratio = (self.hit_count / total_ops * 100) if total_ops > 0 else 0.0

        return {
            "policy": self.policy,
            "total_ops": total_ops,
            "reads": self.read_count,
            "writes": self.write_count,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_ratio": hit_ratio,
            "hdd_writes": self.hdd_write_count,
            "total_time": self.total_time,
        }


# ================== CHẠY MÔ PHỎNG ==================
def run_simulation():
    random.seed(0)

    NUM_REQUESTS = 1000
    ADDR_RANGE = 20

    # Sinh workload: 60% đọc, 40% ghi
    requests = []
    for _ in range(NUM_REQUESTS):
        addr = random.randint(1, ADDR_RANGE)
        op = "R" if random.random() < 0.6 else "W"
        requests.append((op, addr))

    print(f"--- MÔ PHỎNG {NUM_REQUESTS} YÊU CẦU (R/W) TRÊN {ADDR_RANGE} BLOCK ---")
    print(f"SSD: R={SSD_READ_TIME} TU, W={SSD_WRITE_TIME} TU | HDD: R={HDD_READ_TIME} TU, W={HDD_WRITE_TIME} TU")
    print("-" * 80)

    # Write-through
    sim_wt = Simulation(policy="write_through")
    for op, addr in requests:
        sim_wt.access(op, addr)
    wt_report = sim_wt.report()

    # Write-back
    sim_wb = Simulation(policy="write_back")
    for op, addr in requests:
        sim_wb.access(op, addr)
    wb_report = sim_wb.report()

    # In kết quả
    def print_report(r):
        print(f"[{r['policy'].upper()}]")
        print(f"  Tổng số thao tác      : {r['total_ops']}")
        print(f"  Số đọc (R)            : {r['reads']}")
        print(f"  Số ghi (W)            : {r['writes']}")
        print(f"  Cache hit             : {r['hits']}")
        print(f"  Cache miss            : {r['misses']}")
        print(f"  Tỉ lệ hit             : {r['hit_ratio']:.2f}%")
        print(f"  Số lần ghi xuống HDD  : {r['hdd_writes']}")
        print(f"  Tổng thời gian        : {r['total_time']} TU")
        print()

    print_report(wt_report)
    print_report(wb_report)

    # So sánh
    print("-" * 80)
    print("SO SÁNH HAI CHÍNH SÁCH:")
    if wb_report["total_time"] < wt_report["total_time"]:
        speedup = wt_report["total_time"] / wb_report["total_time"]
        print(f"  -> Write-back nhanh hơn khoảng {speedup:.2f} lần so với Write-through.")
    else:
        speedup = wb_report["total_time"] / wt_report["total_time"]
        print(f"  -> Write-through nhanh hơn khoảng {speedup:.2f} lần (bất ngờ đấy!).")

    print(f"  Thời gian WT: {wt_report['total_time']} TU")
    print(f"  Thời gian WB: {wb_report['total_time']} TU")


if __name__ == "__main__":
    run_simulation()

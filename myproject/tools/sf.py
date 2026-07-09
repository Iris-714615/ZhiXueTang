import time
import threading

class Snowflake:
    # 起始时间戳 2020-01-01 00:00:00
    EPOCH = 1577836800000

    # 各部分占用位数
    SEQUENCE_BITS = 12    # 序列号
    WORKER_BITS = 5       # 机器ID
    DATA_CENTER_BITS = 5  # 机房ID

    # 最大值
    MAX_WORKER_ID = -1 ^ (-1 << WORKER_BITS)
    MAX_DATA_CENTER_ID = -1 ^ (-1 << DATA_CENTER_BITS)

    # 位移偏移量
    WORKER_SHIFT = SEQUENCE_BITS
    DATA_CENTER_SHIFT = SEQUENCE_BITS + WORKER_BITS
    TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_BITS + DATA_CENTER_BITS

    def __init__(self, worker_id: int = 1, data_center_id: int = 1):
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError("机器ID超出范围")
        if data_center_id > self.MAX_DATA_CENTER_ID or data_center_id < 0:
            raise ValueError("机房ID超出范围")

        self.worker_id = worker_id
        self.data_center_id = data_center_id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _get_timestamp(self):
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp):
        timestamp = self._get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp()
        return timestamp

    def generate_id(self):
        with self.lock:
            timestamp = self._get_timestamp()

            if timestamp < self.last_timestamp:
                raise Exception("时间回拨，无法生成ID")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 4095
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return ((timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT) | \
                   (self.data_center_id << self.DATA_CENTER_SHIFT) | \
                   (self.worker_id << self.WORKER_SHIFT) | \
                   self.sequence

# 全局单例（全局只用这一个实例，保证唯一）
sf = Snowflake(worker_id=1, data_center_id=1)

# 生成ID的函数（直接调用）
def next_snowflake_id():
    return sf.generate_id()
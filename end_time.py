from datetime import datetime, timedelta
import time


class TimeTracker:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        """记录开始时间"""
        self.start_time = datetime.now()
        print("开始时间:", self.start_time.strftime("%H:%M:%S"))

    def stop(self):
        """记录结束时间并计算持续时间"""
        self.end_time = datetime.now()
        print("结束时间:", self.end_time.strftime("%H:%M:%S"))
        self.calculate_duration()

    def calculate_duration(self):
        """计算持续时间并格式化输出"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            duration_seconds = duration.total_seconds()
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)

            formatted_duration = f"{minutes}分钟{seconds}秒"
            # print("持续时间:", formatted_duration)
            return formatted_duration
        else:
            print("请先调用 start() 和 stop() 方法。")

    def subtract_time(self, hours=0, minutes=0, seconds=0):
        """从开始时间减去指定的小时、分钟和秒，返回新的开始时间"""
        if self.start_time:
            subtraction = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            new_start_time = self.start_time - subtraction
            return new_start_time
        else:
            print("请先调用 start() 方法。")
            return None

    def reset(self):
        """重置开始时间和结束时间"""
        self.start_time = None
        self.end_time = None
        print("时间已重置。请调用 start() 开始新的计时。")


# 使用示例
if __name__ == "__main__":
    tracker = TimeTracker()
    tracker.start()

    # 假设执行某些操作，等待5秒
    time.sleep(5)

    tracker.stop()
    tracker.subtract_time(seconds=2)
    print(tracker.calculate_duration())
    # 重置时间
    tracker.reset()

    # 举例重新开始计时
    tracker.start()
    time.sleep(3)  # 等待3秒
    tracker.stop()
import cv2
from adbutils import adb
import time
import scrcpy
import os

class ScrcpyADB:
    def __init__(self, image_queue, max_fps=30):
        devices = adb.device_list()  # 获取连接的设备列表
        self.device = devices[0]
        client = scrcpy.Client(self.device, max_fps=max_fps, block_frame=True)
        # client = scrcpy.Client(device=devices[0], max_fps=max_fps, block_frame=True, max_width=2416)  # 初始化scrcpy客户端
        print(devices, client)  # 打印设备列表和客户端信息
        client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)  # 添加帧事件监听器
        client.start(threaded=True)  # 启动客户端，使用线程
        self.client = client  # 保存客户端实例
        self.last_screen = None  # 最近的屏幕帧
        self.frame_idx = -1  # 帧索引
        self.queue = image_queue  # 图像队列

    def touch_down(self, x: int or float, y: int or float, id: int = -1):
        """模拟触摸按下事件"""
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_DOWN, id)

    def touch_move(self, x: int or float, y: int or float, id: int = -1):
        """模拟触摸移动事件"""
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_MOVE, id)

    def touch_up(self, x: int or float, y: int or float, id: int = -1):
        """模拟触摸抬起事件"""
        self.client.control.touch(int(x), int(y), scrcpy.ACTION_UP, id)

    def touch_swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        move_step_length: int = 5,
        move_steps_delay: float = 0.005,
    ):
        """模拟滑动事件"""
        self.client.control.swipe(start_x, start_y, end_x, end_y, move_step_length, move_steps_delay)

    def tap(self, x: int or float, y: int or float):
        """模拟点击事件"""
        self.touch_down(x, y)  # 触摸按下
        time.sleep(0.01)  # 等待0.01秒
        self.touch_up(x, y)  # 触摸抬起

    def on_frame(self, frame: cv2.Mat):
        """处理接收到的帧"""
        if frame is not None:
            self.queue.put(frame)  # 将帧放入队列

    def screenshot(self, filename, t=0):
        """保存当前屏幕帧为图像文件"""
        time.sleep(t)
        if self.last_screen is not None:
            # 检查目录是否存在
            directory = os.path.dirname(filename)
            if not os.path.exists(directory) and directory:
                os.makedirs(directory)

            # 保存图像
            cv2.imwrite(filename, self.last_screen)
            print(f"success img: {filename}")
        else:
            print("No frame available to save.")

if __name__ == '__main__':
    ScrcpyADB()
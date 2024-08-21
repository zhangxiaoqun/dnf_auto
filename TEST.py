
# def handle_button_click(action, button_index):
#     if button_index == 0:
#         action.stop_event = False
#     elif button_index == 1:
#         action.stop_event = True
#     elif button_index == 2:
#         action.reset()
import cv2
import numpy as np

from utils.yolov5_onnx import YOLOv5
from scrcpy_adb import ScrcpyADB
from game_control import GameControl
from game_action import GameAction
import queue
import time
import os
import cv2 as cv
from img.find_img import find_best_match, take_screenshot


class AutoCleaningQueue(queue.Queue):
    def put(self, item, block=True, timeout=None):
        if self.full():
            self.get()  # 自动丢弃最旧的元素
        super().put(item, block, timeout)


# if __name__ == '__main__':
image_queue = AutoCleaningQueue(maxsize=3)
infer_queue = AutoCleaningQueue(maxsize=3)
show_queue = AutoCleaningQueue(maxsize=3)
current_dir = os.path.dirname(os.path.abspath(__file__))
client = ScrcpyADB(image_queue, max_fps=15)
yolo = YOLOv5(os.path.join(current_dir, "./utils/dnfm.onnx"), image_queue, infer_queue, show_queue)
control = GameControl(client, os.path.join(current_dir, "./skill.json"))
action = GameAction(control, infer_queue)
#
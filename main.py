import cv2
import numpy as np

from utils.yolov5_onnx import YOLOv5
# from utils.yolov5_trt import YOLOv5
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


if __name__ == '__main__':
    image_queue = AutoCleaningQueue(maxsize=3)
    infer_queue = AutoCleaningQueue(maxsize=3)
    show_queue = AutoCleaningQueue(maxsize=3)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    client = ScrcpyADB(image_queue, max_fps=10)
    yolo = YOLOv5(os.path.join(current_dir, "./utils/dnfm.onnx"), image_queue, infer_queue, show_queue)
    # yolo = YOLOv5(os.path.join(current_dir, "./utils/dnf_sim.trt"), image_queue, infer_queue, show_queue)
    # control = GameControl(client, os.path.join(current_dir, "./skill.json"))
    # control = GameControl(client, os.path.join(current_dir, "./skill_biaozhun_xiaomi.json"))
    control = GameControl(client, os.path.join(current_dir, "./skill_jichu_huawei.json"))
    action = GameAction(control, infer_queue)


    while True:
        if show_queue.empty():
            time.sleep(0.001)
            continue
        image, result = show_queue.get()
        for boxs in result:
            det_x1, det_y1, det_x2, det_y2, conf, label = boxs
            x1 = int(det_x1 * image.shape[1])
            y1 = int(det_y1 * image.shape[0])
            x2 = int(det_x2 * image.shape[1])
            y2 = int(det_y2 * image.shape[0])
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, "{:.2f}".format(conf), (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)
            cv2.putText(image, yolo.label[int(label)], (int(x1), int(y1 - 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)
        image = cv2.resize(image, (1800, int(image.shape[0] * 1800 / image.shape[1])))
        # 创建按钮区域
        button_panel_width = 100
        button_panel = np.zeros((image.shape[0], button_panel_width, 3), dtype=np.uint8)
        # 按钮属性
        button_height = 50
        button_gap = 10
        button_color = (0, 255, 0)  # 绿色按钮
        buttons = ["run", "stop", "reset"]  # 按钮标签


        # 在按钮区域绘制按钮
        def draw_buttons(panel):
            for i, label in enumerate(buttons):
                y1 = i * (button_height + button_gap) + button_gap
                y2 = y1 + button_height
                cv2.rectangle(panel, (10, y1), (button_panel_width - 10, y2), button_color, -1)
                cv2.putText(panel, label, (20, y1 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                if x > image.shape[1]:  # 检查是否点击在按钮区域
                    x_in_panel = x - image.shape[1]
                    for i, label in enumerate(buttons):
                        y1 = i * (button_height + button_gap) + button_gap
                        y2 = y1 + button_height
                        if y1 <= y <= y2:
                            print(f"{label} clicked")
                            handle_button_click(i)  # 调用处理函数，传入按钮索引
                else:
                    control.click(x / image.shape[1] * 2400, y / image.shape[0] * 1080)


        def handle_button_click(button_index):
            if button_index == 0:
                action.stop_event = False
            elif button_index == 1:
                action.stop_event = True
            elif button_index == 2:
                action.reset()


        # 合并图片和按钮面板
        def update_display():
            combined = np.hstack((image, button_panel))  # 水平拼接
            cv2.imshow("Image", combined)

        draw_buttons(button_panel)  # 初始化按钮区域
        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", on_mouse)
        update_display()  # 更新显示
        cv2.waitKey(1)


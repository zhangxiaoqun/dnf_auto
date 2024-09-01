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
import shared_variables as sv  # 引入共享变量模块
import threading

class AutoCleaningQueue(queue.Queue):
    """
    一个自定义队列，当满时会自动丢弃最旧的元素。
    """
    def put(self, item, block=True, timeout=None):
        """
        将项目添加到队列中。如果队列已满，丢弃最旧的项目。

        :param item: 要添加到队列的项目。
        :param block: 如果队列满时是否阻塞（默认是True）。
        :param timeout: 阻塞的超时时间（默认是None）。
        """
        if self.full():
            self.get()  # 自动丢弃最旧的元素
        super().put(item, block, timeout)  # 调用父类的put方法


def initialize_game_control(client):
    """根据 hero_num 初始化 GameControl 实例"""
    if sv.hero_skill_num == 3 or sv.hero_skill_num == 4:
        skill_path = "./role_skill/naima.json"
    elif sv.hero_num == 5:
        skill_path = "./role_skill/kuangzhanshi.json"
    else:
        skill_path = "./role_skill/naima.json"  # 默认技能路径

    return GameControl(client, os.path.join(current_dir, skill_path))
skill_paths = {
        1: os.path.join(os.getcwd(), "./role_skill/naima.json"),
        2: os.path.join(os.getcwd(), "./role_skill/naima.json"),
        3: os.path.join(os.getcwd(), "./role_skill/kuangzhanshi.json"),
    }


if __name__ == '__main__':
    image_queue = AutoCleaningQueue(maxsize=3)
    infer_queue = AutoCleaningQueue(maxsize=3)
    show_queue = AutoCleaningQueue(maxsize=3)
    # 获取当前脚本的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 创建 client 用于与 ScrcpyADB（屏幕镜像/控制）交互
    client = ScrcpyADB(image_queue, max_fps=10)
    # 初始化 YOLOv5 模型用于对象检测
    yolo = YOLOv5(os.path.join(current_dir, "./utils/dnfm.onnx"), image_queue, infer_queue, show_queue)
    # yolo = YOLOv5(os.path.join(current_dir, "./utils/dnf_sim.trt"), image_queue, infer_queue, show_queue)
    # control = GameControl(client, os.path.join(current_dir, "./skill.json"))
    # control = GameControl(client, os.path.join(current_dir, "./skill_biaozhun_xiaomi.json"))
    # 使用指定的技能 JSON 配置初始化 GameControl
    control = GameControl(client, os.path.join(current_dir, "./skill_jichu_huawei.json"))
    # 创建 GameAction 实例以处理游戏中的操作
    action = GameAction(control, infer_queue)
    # last_hero_skill_num = sv.hero_skill_num
    while True:
        # 在主循环中根据需要重新初始化 GameControl
        # if sv.hero_skill_num != last_hero_skill_num:  # 检查英雄编号是否发生变化
        #     # action.thread_run = False
        #     control = initialize_game_control(client)
        #     # if action is not None:
        #     #     action.stop_event = True  # 停止当前动作
        #     print(f"3当前活动线程数: {threading.active_count()}")
        #     action.stop_event = True
        #     # action.thread_run = False
        #     action.thread = False
        #     # action.reset()
        #     action = GameAction(control, infer_queue)  # 重新创建 GameAction
        #     last_hero_skill_num = sv.hero_skill_num  # 更新最后的英雄编号
        if show_queue.empty():  # 如果显示队列为空
            time.sleep(0.001)   # 等待微秒
            continue
        # 获取显示队列中的图像和结果
        image, result = show_queue.get()
        for boxs in result: # 遍历检测结果
            det_x1, det_y1, det_x2, det_y2, conf, label = boxs # 转换为图像坐标
            x1 = int(det_x1 * image.shape[1])
            y1 = int(det_y1 * image.shape[0])
            x2 = int(det_x2 * image.shape[1])
            y2 = int(det_y2 * image.shape[0])
            # 绘制检测框
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, "{:.2f}".format(conf), (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)
            cv2.putText(image, yolo.label[int(label)], (int(x1), int(y1 - 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)
        # 调整图像尺寸以适应窗口
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


        # 鼠标事件处理
        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击事件
                if x > image.shape[1]:  # 检查是否点击在按钮区域
                    x_in_panel = x - image.shape[1]
                    for i, label in enumerate(buttons):
                        y1 = i * (button_height + button_gap) + button_gap
                        y2 = y1 + button_height
                        if y1 <= y <= y2:
                            print(f"{label} clicked") # 输出点击的按钮
                            handle_button_click(i)  # 调用处理函数，传入按钮索引

                else:
                    # 点击图像的其他部分，模拟点击事件
                    control.click(x / image.shape[1] * 2400, y / image.shape[0] * 1080)


        # 处理按钮点击事件a
        def handle_button_click(button_index):
            if button_index == 0:  # run按钮
                action.stop_event = False
            elif button_index == 1:  # stop按钮
                action.stop_event = True
            elif button_index == 2:  # reset按钮
                action.reset()

        # 合并图片和按钮面板
        def update_display():
            combined = np.hstack((image, button_panel))  # 水平拼接
            cv2.imshow("Image", combined) # 显示合并后的图像

        draw_buttons(button_panel)  # 初始化按钮区域
        cv2.namedWindow("Image")    # 创建窗口
        cv2.setMouseCallback("Image", on_mouse) # 设置鼠标回调
        update_display()  # 更新显示
        cv2.waitKey(1)  # 等待按键事件


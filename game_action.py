
from game_control import GameControl
import time
import cv2
import math
import numpy as np
from collections import deque
import threading
from img.find_img import find_best_match, take_screenshot, find_best_match_2
import shared_variables as sv
from send.send_wx import send_miao_reminder
from datetime import datetime, timedelta
from end_time import TimeTracker
import random
from test import take_screenshot_async
from ii import is_brightness_low
from send.send_email import send_email_with_attachment

def click_img_coordinate(control, current_screen_img, image_path, gray_convert=1, t=1):
    take_screenshot()
    if gray_convert == 1:
        hero_center_coordinates = find_best_match(current_screen_img, image_path)
    else:
        hero_center_coordinates = find_best_match_2(current_screen_img, image_path)
    if hero_center_coordinates is not None:
        # time.sleep(1)
        control.click(hero_center_coordinates[0], hero_center_coordinates[1])
        time.sleep(t)
        return True
    return False

def countdown(seconds):
    print(f"开始倒计时 {seconds} 秒...")
    time.sleep(seconds)  # 倒计时
    print("时间到！")
    global timer_finished
    timer_finished = True  # 设置标志已完成倒计时


# sv.current_screen_img = "./current_screen_img.jpg"
def repair_equipment_and_sell_equipment(control):
    time.sleep(5)
    # 背包
    print("获取当前页面包裹的位置")
    click_img_coordinate(control, sv.current_screen_img, r"./img/house_file/beibao.jpg")
    # 点击修理按钮
    print("获取背包内的图片")
    click_img_coordinate(control, sv.current_screen_img, r"./img/repair_file/xiuli_1.jpg")
    # 点击修理
    print("修理完成")
    click_img_coordinate(control, sv.current_screen_img, r"./img/repair_file/xiuli_2.jpg")
    print("点击X返回")
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/X_icon.jpg")
    sell_equipment(control)
    time.sleep(3)
    print("点击返回")
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/return_icon.jpg")


def sell_equipment(control):
    time.sleep(2)
    # 点击出售
    print("点击出售1")
    click_img_coordinate(control, sv.current_screen_img, r"./img/beibao/sell.jpg")
    print("点击出售2")
    click_img_coordinate(control, sv.current_screen_img, r"./img/beibao/sell_2.jpg")
    print("点击确认出售")
    click_img_coordinate(control, sv.current_screen_img, r"./img/beibao/affirm.jpg")
    print("出售完毕,点击确认")
    click_img_coordinate(control, sv.current_screen_img, r"./img/beibao/affirm.jpg")
    print("出售完毕,关闭出售栏")
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/X_icon.jpg")


def bwj(control):
    time.sleep(3)
    # 点击冒险
    control.click(2072, 984)
    # click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/maoxian.jpg")
    print("点击冒险")
    time.sleep(1)
    # 点击冒险奖励
    # control.click(2072, 984)
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/maoxianjiangli.jpg")
    print("点击冒险奖励")
    time.sleep(1)
    # 点击冒险级
    # control.click(870, 258)
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/maoxianji.jpg")
    print("点击冒险级")
    # 点击万年雪山
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/xueshan.jpg")
    print("点击冒险级")
    time.sleep(1)
    # 点击区域移动
    # control.click(1877, 714)
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/quyuyidong.jpg")
    time.sleep(20)
    print("点击区域移动")
    # 点击布万加地图
    # control.click(1636, 812)
    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/bwj_map.jpg")
    print("点击布万加地图")
    time.sleep(2)

    # 战斗开始
    while True:
        take_screenshot()
        if find_best_match_2(sv.current_screen_img, r"img/underground_file/zdks.jpg") is not None:
            # 战斗开始
            print("战斗开始")
            control.click(1934, 935)
            if sv.hero_num > 3 and sv.pl_300_message_num <= 0:
                # 300 pl提示
                take_screenshot()
                print("布万加方法-选择地下城界面截图")
                time.sleep(2)
                if find_best_match_2(sv.current_screen_img, r"./img/underground_file/kuang.jpg") is not None:
                    click_img_coordinate(control, sv.current_screen_img, r"./img/underground_file/kuang.jpg")
                    click_img_coordinate(control, sv.current_screen_img, r"img/underground_file/qr.jpg")
                    sv.pl_300_message_num = sv.pl_300_message_num + 1
                    print("疲劳超过300提示")
        else:
            break
    print("战斗开始")



def switch_hero(control, hero_img):
    while True:
        take_screenshot()
        time.sleep(2)
        if find_best_match(sv.current_screen_img, r"./img/house_file/email.jpg") is None:
            time.sleep(1)
            # 左上角选角
            click_img_coordinate(control, sv.current_screen_img, r"./img/role/xuanjiao.jpg")
            print("点击左上角选角")
            # 获取当前屏幕信息并点击坐标
            click_img_coordinate(control, sv.current_screen_img, hero_img)
            # 切换后的加载
            time.sleep(20)
            print("角色切换成功")
        else:
            # 修理装备
            repair_equipment_and_sell_equipment(control)
            # 进布万加地图
            bwj(control)
            print("执行布万家前置步骤，1.修理装备 2.进入地图")
            break



def calculate_center(box):# 计算矩形框的底边中心点坐标
    return ((box[0] + box[2]) / 2, box[3])
def calculate_distance(center1, center2):# 计算两个底边中心点之间的欧几里得距离
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)
def find_closest_box(boxes, target_box):# 计算目标框的中心点
    target_center = calculate_center(target_box)# 初始化最小距离和最近的box
    min_distance = float('inf')
    closest_box = None# 遍历所有box，找出最近的box
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance < min_distance:
            min_distance = distance
            closest_box = box
    return closest_box,min_distance
def find_farthest_box(boxes, target_box):
    target_center = calculate_center(target_box)# 计算目标框的中心点
    max_distance = -float('inf')# 初始化最大距离和最远的box
    farthest_box = None
    for box in boxes:# 遍历所有box，找出最远的box
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance > max_distance:
            max_distance = distance
            farthest_box = box
    return farthest_box, max_distance
def find_closest_or_second_closest_box(boxes, point):
    """找到离目标框最近的框或第二近的框"""
    if len(boxes) < 2:
        # 如果框的数量少于两个，直接返回最近的框
        target_center = point
        closest_box = None
        min_distance = float('inf')
        for box in boxes:
            center = calculate_center(box)
            distance = calculate_distance(center, target_center)
            if distance < min_distance:
                min_distance = distance
                closest_box = box
        return closest_box,distance
    # 如果框的数量不少于两个
    target_center = point
    # 初始化最小距离和最近的框
    min_distance_1 = float('inf')
    closest_box_1 = None
    # 初始化第二近的框
    min_distance_2 = float('inf')
    closest_box_2 = None
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance < min_distance_1:
            # 更新第二近的框
            min_distance_2 = min_distance_1
            closest_box_2 = closest_box_1
            # 更新最近的框
            min_distance_1 = distance
            closest_box_1 = box
        elif distance < min_distance_2:
            # 更新第二近的框
            min_distance_2 = distance
            closest_box_2 = box
    # 返回第二近的框
    return closest_box_2,min_distance_2
def find_close_point_to_box(boxes, point):#找距离点最近的框
    target_center = point# 初始化最小距离和最近的box
    min_distance = float('inf')
    closest_box = None# 遍历所有box，找出最近的box
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance < min_distance:
            min_distance = distance
            closest_box = box
    return closest_box,min_distance
def calculate_point_to_box_angle(point, box):#计算点到框的角度
    center1 = point
    center2 = calculate_center(box)
    delta_x = center2[0] - center1[0]# 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle
def calculate_angle(box1, box2):
    center1 = calculate_center(box1)
    center2 = calculate_center(box2)
    delta_x = center2[0] - center1[0]# 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle
def calculate_gate_angle(point, gate):
    center1 = point
    center2 = ((gate[0]+gate[2])/2,(gate[3]-gate[1])*0.65+gate[1])
    delta_x = center2[0] - center1[0]# 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle

def calculate_angle_to_box(point1,point2):#计算点到点的角度
    angle = math.atan2(point2[1] -point1[1], point2[0] - point1[0])# 计算从点 (x, y) 到中心点的角度
    angle_degrees = math.degrees(angle)# 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle
def calculate_iou(box1, box2):
    # 计算相交区域的坐标
    inter_x_min = max(box1[0], box2[0])
    inter_y_min = max(box1[1], box2[1])
    inter_x_max = min(box1[2], box2[2])
    inter_y_max = min(box1[3], box2[3])
    # 计算相交区域的面积
    inter_area = max(0, inter_x_max - inter_x_min) * max(0, inter_y_max - inter_y_min)
    # 计算每个矩形的面积和并集面积
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    # 计算并返回IoU
    return inter_area / union_area if union_area > 0 else 0
def normalize_angle(angle):# 将角度规范化到 [-180, 180) 的范围内
    angle = angle % 360
    if angle >= 180:
        angle -= 360
    return angle
def are_angles_on_same_side_of_y(angle1, angle2):# 规范化角度
    norm_angle1 = normalize_angle(angle1)
    norm_angle2 = normalize_angle(angle2)# 检查是否在 y 轴的同侧
    return (norm_angle1 >= 0 and norm_angle2 >= 0) or (norm_angle1 < 0 and norm_angle2 < 0)
def is_image_almost_black(image, threshold=30):# 读取图片
    # image = cv2.cvtColor(image, cv2.IMREAD_GRAYSCALE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    num_black_pixels = np.sum(image < threshold)
    total_pixels = image.size
    black_pixel_ratio = num_black_pixels / total_pixels# 定义一个比例阈值来判断图片是否接近黑色
    return black_pixel_ratio > 0.8
names =['Monster', #0
        'Monster_ds', #1
        'Monster_szt', #2
        'card', #3
        'equipment',#4
        'go', #5
        'hero', #6
        'map', #7
        'opendoor_d', #8
        'opendoor_l', #9
        'opendoor_r', #10
        'opendoor_u', #11
        'pet',# 12
        'Diamond']# 13
# from hero.naima import Naima
from hero.hero_controller import HeroController
class GameAction:
    def __init__(self, ctrl: GameControl,queue):
        self.queue = queue  # 初始队列
        self.ctrl = ctrl  # 控制游戏的对象
        self.detect_retry = False  # 是否需要重试检测
        self.pre_state = True  # 之前的状态
        # self.stop_event = True  # 停止事件
        # self.reset_event = False  # 重置事件
        self.stop_event = threading.Event()  # 使用 Event 来控制线程停止
        self.reset_event = threading.Event()  # 同样使用 Event 来控制重置信号
        self.control_attack = HeroController(ctrl)  # 初始化攻击控制
        # 加载技能模板
        self.control_attack.load_skills()
        self.room_num = -1  # 当前房间号
        self.timing_time = None
        self.buwanjia = [8, 10, 10, 11, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.buwanjia_sanda = [8, 10, 10, 11, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.adventure_start_time = None  # 冒险开始时间
        self.adventure_duration = 15 # 冒险持续时间（5分钟）
        self.last_screenshot_time = datetime.now()
        self.thread_run = True  # 控制线程运行状态
        self.thread = threading.Thread(target=self.control)  # 创建线程，并指定目标函数
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.thread.start()  # 启动线程


    def reset(self):
        """
        重置游戏状态，重新启动控制线程。
        """
        self.stop_event.set()  # 设置停止事件
        self.thread.join()  # 等待线程结束
        # self.thread_run = False  # 停止当前线程
        time.sleep(0.1)  # 等待0.1秒
        self.room_num = -1  # 重置房间号
        self.detect_retry = False  # 重置重试状态
        self.pre_state = True  # 重置预状态
        self.thread_run = True  # 重新启动线程
        self.thread = threading.Thread(target=self.control)  # 创建新的线程
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.thread.start()  # 启动新线程

    def random_move(self):
        """随机移动英雄"""
        # 生成一个随机角度
        random_angle = random.uniform(0, 360)

        # 调用控制对象的方法移动英雄
        self.ctrl.move(random_angle)
        time.sleep(1)
        print(f"英雄随机移动到角度: {random_angle}")

    def out_time(self):
        # 超时就返回城镇
        if self.timing_time is None:
            self.timing_time = time.time()
        # print(f"超时时间：{time.time() - self.timing_time}")
        if time.time() - self.timing_time > 50:  # 检查超时
            print("等待时间超时，英雄随机移动")
            self.random_move()
        if time.time() - self.timing_time > 100:  # 检查超时
            take_screenshot()
            # if find_best_match_2(sv.current_screen_img, r"./img/underground_file/fhcz.jpg") is not None:
            #     print("英雄死亡")
            #     self.detect_retry = False
            #     click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/underground_file/fhcz.jpg")
            #     print("点击返回城镇")
            #     click_img_coordinate(self.ctrl, sv.current_screen_img, r"img/underground_file/qr.jpg")
            #     print("点击确认")
            #     # time.sleep(10)
            # else:
            print("等待时间超时，返回城镇")
            # 微信公众号提醒
            # send_miao_reminder("等待时间超时，返回城镇")
            send_email_with_attachment("DNF刷图信息", "等待时间超时，返回城镇", ["current_screen_img.jpg"])
            # self.stop_event = True
            self.detect_retry = False
            # self.detect_retry = True
            click_img_coordinate(self.ctrl, sv.current_screen_img, r"img/underground_file/setting.jpg")
            print("点击设置")
            click_img_coordinate(self.ctrl, sv.current_screen_img, r"img/underground_file/return_to_town.jpg")
            print("点击返回城镇")
            click_img_coordinate(self.ctrl, sv.current_screen_img, r"img/underground_file/qr.jpg")
            print("点击确认")
            time.sleep(10)
            bwj(self.ctrl)
            time.sleep(3)
            self.ctrl.move(0)
            self.room_num = 0  # 重置房间号
            hero_track = deque()  # 重置英雄轨迹
            hero_track.appendleft([0, 0])  # 初始位置
            self.ctrl.reset()  # 重置控制
            # 重置时间
            self.timing_time = None
            self.stop_event = False


    def control(self):
        """
        游戏控制的主逻辑。
        """
        last_room_pos = []  # 上一个房间位置
        hero_track = deque()  # 英雄轨迹队列
        hero_track.appendleft([0, 0])  # 初始英雄位置
        last_angle = 0  # 上一个角度

        bwj(self.ctrl)
        self.stop_event = False
        # # 重置时间
        self.timing_time = None
        # 记录开始时间
        tracker = TimeTracker()
        tracker.start()

        from threading import Thread
        screenshot_interval = 7  # 设置截图间隔为 3 秒

        # 在一个新的线程中开始定期截图
        screenshot_thread = Thread(target=take_screenshot_async, args=(screenshot_interval,))
        screenshot_thread.daemon = True  # 允许线程在主程序退出时也能退出
        screenshot_thread.start()


        while self.thread_run:  # 循环执行
            if self.stop_event:
                time.sleep(0.001)  # 小等待
                self.ctrl.reset()  # 发送重置命令
                continue
            if self.queue.empty():  # 如果队列为空
                time.sleep(0.001)  # 等待
                continue


            image, boxs = self.queue.get()  # 获取队列中的图像和框
            if is_image_almost_black(image):  # 如果图像接近黑色
                print("如果图像接近黑色", self.pre_state)
                if self.pre_state == False:
                    if not self.pre_state:
                        print("过图")  # 通知过图
                        # time.sleep(0.3)
                        last_room_pos = hero_track[0]  # 保存最后位置
                        hero_track = deque()  # 重置英雄轨迹
                        hero_track.appendleft([1 - last_room_pos[0], 1 - last_room_pos[1]])  # 记录反方向
                        last_angle = 0  # 重置角度
                        self.ctrl.reset()  # 重置控制
                        self.pre_state = True  # 设置为预状态
                    else:
                        continue
                    self.timing_time = None  # 重置时间
            hero = boxs[boxs[:, 5] == 6][:, :4]  # 获取英雄框
            if sv.hero_num == 8:
                gate = boxs[boxs[:, 5] == self.buwanjia_sanda[self.room_num]][:, :4]  # 获取门框
            else:
                gate = boxs[boxs[:, 5] == self.buwanjia[self.room_num]][:, :4]  # 获取门框
            '''
            boxs:
            前四列：一个物体的边界框坐标（左上角和右下角）。
            第五列：该物体的置信度。
            第六列：物体的类别编号。
            '''
            # print("我是box", boxs)
            # print("我是self.buwanjia[self.room_num]", self.buwanjia[self.room_num])
            # print("我是boxs[:, 5]", boxs[:, 5])
            # print("我是boxs[:, 5] == self.buwanjia[self.room_num]", boxs[:, 5] == self.buwanjia[self.room_num])
            # print("我是gate", gate, type(gate))
            arrow = boxs[boxs[:, 5] == 5][:, :4]  # 获取箭头框
            equipment = [[detection[0], detection[1] + (detection[3] - detection[1]), detection[2], detection[3] + (detection[3] - detection[1]), detection[4], detection[5]]
                        for detection in boxs if detection[5] == 4 and detection[4] > 0.3]
            monster = boxs[boxs[:, 5] <= 2][:, :4]  # 获取怪物框
            card = boxs[boxs[:, 5] == 3][:, :4]  # 获取卡片框
            Diamond = boxs[boxs[:, 5] == 13][:, :4]  # 获取钻石框
            angle = 0
            outprint = ''
            if self.pre_state == True :
                # print("len(hero)111111111", len(hero))
                # time.sleep(0.3)
                if len(hero) > 0:#记录房间号
                # if find_best_match_2(image, r"./img/underground_file/xiao_map.jpg") is not None:
                #     print("len(hero)2222222", len(hero))
                    self.room_num += 1
                    self.pre_state = False
                    print("房间号：",self.room_num)
                    print("目标",self.buwanjia[self.room_num])
                else:
                    continue
            self.calculate_hero_pos(hero_track,hero)#计算英雄位置
            if len(card)>=8:
                time.sleep(1)
                self.ctrl.click(0.25*image.shape[0],0.25*image.shape[1])
                self.detect_retry = True
                time.sleep(2.5)
            if len(monster)>0:
                outprint = '有怪物'
                angle = self.control_attack.control(hero_track[0],image,boxs,self.room_num)
                # 超时就返回城镇
                self.out_time()
            elif len(equipment)>0:
                outprint = '有材料'
                # print(outprint)
                if len(gate)>0:
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    farthest_item,distance = find_farthest_box(equipment,close_gate)
                    angle = calculate_point_to_box_angle(hero_track[0],farthest_item)
                else:
                    close_item,distance = find_close_point_to_box(equipment,hero_track[0])
                    angle = calculate_point_to_box_angle(hero_track[0],close_item)
                self.ctrl.attack(False)
                self.ctrl.move(angle)
                # 超时就返回城镇
                self.out_time()
            elif len(gate)>0:
                outprint = '有门'
                if sv.hero_num == 8:
                    buwanjia_room = self.buwanjia_sanda[self.room_num]
                else:
                    buwanjia_room = self.buwanjia[self.room_num]
                # if self.buwanjia[self.room_num] == 9:#左门
                if buwanjia_room == 9:  # 左门
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    angle = calculate_gate_angle(hero_track[0],close_gate)
                    self.ctrl.attack(False)
                    self.ctrl.move(angle)
                else:
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    angle = calculate_point_to_box_angle(hero_track[0],close_gate)
                    self.ctrl.attack(False)
                    self.ctrl.move(angle)
                # 超时就返回城镇
                self.out_time()
            elif len(arrow)>0 and self.room_num != 4:
                # 超时就返回城镇
                self.out_time()
                outprint = '有箭头'
                # print(outprint)
                close_arrow,distance = find_closest_or_second_closest_box(arrow,hero_track[0])
                angle = calculate_point_to_box_angle(hero_track[0],close_arrow)
                self.ctrl.move(angle)
                self.ctrl.attack(False)
            elif self.detect_retry == True:
                #重新挑战：自行发挥
                # print("detect_retry")
                heros = {"大雷给奶一口":r"./img/role/nai1.jpg", "别拽了俺tuo":r"./img/role/bie2.jpg", "大雷是啥子":r"./img/role/kuang3.jpg"}
                # 选择其他地下城
                # self.ctrl.click(2078, 240)
                click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/underground_file/select_other_dxc.jpg")
                time.sleep(3)
                print("选择其他地下城")
                take_screenshot()
                time.sleep(3)
                if find_best_match_2(sv.current_screen_img, r"./img/pl_num_file/pl0.jpg") is not None:
                    print("疲劳值为0，选择其他角色")
                    # 点击右上角X按钮
                    # self.ctrl.click(2053, 136)
                    click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/underground_file/X_icon.jpg")
                    print("点击右上角X按钮")
                    # 点击左上角返回
                    # self.ctrl.click(149, 37)
                    click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/underground_file/return_icon.jpg")
                    print("点击左上角返回按钮")
                    # 点击返回城镇
                    # self.ctrl.click(2064, 338)
                    click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/underground_file/dxc_fhcz.jpg")
                    print("点击返回城镇")
                    sv.hero_num = sv.hero_num + 1
                    # 角色顺序
                    role_sx = sv.role_seq_coord
                    # 魔道
                    if sv.hero_num == 2:
                        time.sleep(12)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/role/xuanjiao.jpg", t=4)
                        print("点击选角")
                        self.ctrl.click(role_sx["role_index4"][0], role_sx["role_index4"][1])
                        time.sleep(12)
                        # 加载技能模板
                        self.control_attack.load_skills()
                    # 大雷给奶一口
                    elif sv.hero_num == 3:
                        # switch_hero(self.ctrl, heros["大雷给奶一口"])
                        time.sleep(12)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/role/xuanjiao.jpg", t=4)
                        print("点击选角")
                        self.ctrl.click(role_sx["role_index2"][0], role_sx["role_index2"][1])
                        time.sleep(12)
                        # 加载技能模板
                        self.control_attack.load_skills()
                    # 奶你
                    elif sv.hero_num == 4:
                        time.sleep(12)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/role/xuanjiao.jpg", t=4)
                        print("点击选角")
                        time.sleep(4)
                        self.ctrl.click(role_sx["role_index2"][0], role_sx["role_index2"][1])
                        time.sleep(12)
                        # 加载技能模板
                        self.control_attack.load_skills()
                    # 大雷是啥子
                    elif sv.hero_num == 5:
                        time.sleep(12)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/role/xuanjiao.jpg", t=4)
                        print("点击选角")
                        self.ctrl.click(role_sx["role_index1"][0], role_sx["role_index1"][1])
                        time.sleep(12)
                        # 加载技能模板
                        self.control_attack.load_skills()

                    # 剑宗
                    elif sv.hero_num == 6:
                        time.sleep(12)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/role/xuanjiao.jpg", t=4)
                        print("点击选角")
                        # 滑动角色
                        self.ctrl.slide(208, 524, "up", distance=400)
                        time.sleep(6)
                        self.ctrl.click(role_sx["role_index3"][0], role_sx["role_index3"][1])
                        time.sleep(12)
                        # 加载技能模板
                        self.control_attack.load_skills()

                    # 剑豪
                    elif sv.hero_num == 7:
                        time.sleep(12)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/role/xuanjiao.jpg", t=4)
                        print("点击选角")
                        # 滑动角色
                        self.ctrl.slide(208, 524, "up", distance=400)
                        time.sleep(6)
                        self.ctrl.click(role_sx["role_index4"][0], role_sx["role_index4"][1])
                        time.sleep(12)
                        # 加载技能模板
                        self.control_attack.load_skills()

                    # # 踹你一脚气
                    # elif sv.hero_num == 8:
                    #     time.sleep(12)
                    #     # 左上角选角
                    #     click_img_coordinate(self.ctrl, sv.current_screen_img, r"./img/role/xuanjiao.jpg", t=4)
                    #     print("点击选角")
                    #     # 滑动角色
                    #     self.ctrl.slide(208, 524, "up", distance=400)
                    #     time.sleep(6)
                    #     self.ctrl.click(role_sx["role_index3"][0], role_sx["role_index3"][1])
                    #     time.sleep(12)
                    #     # 加载技能模板
                    #     self.control_attack.load_skills()

                    # 修理装备
                    repair_equipment_and_sell_equipment(self.ctrl)
                    bwj(self.ctrl)
                    role_name = f"我是英雄：{sv.role_dic[sv.hero_num]},第{sv.hero_num}出场"
                    print(role_name)
                    # 微信公众号提醒
                    send_miao_reminder(role_name)
                    self.timing_time = None  # 重置时间
                    # 启动脚本
                    self.stop_event = False
                    print("点击run 按钮")
                else:
                    # 微信公众号提醒
                    sv.battle_num = sv.battle_num + 1
                    tracker.stop()
                    time_consuming = tracker.calculate_duration(subtract_seconds=32)
                    message = f"英雄名称: {sv.role_dic[sv.hero_num]},第{sv.battle_num}轮战斗，战斗耗时:{time_consuming}"
                    # send_miao_reminder(message)
                    send_email_with_attachment("DNF刷图信息", message, ["current_screen_img.jpg"])
                    # 重置时间
                    tracker.reset()
                    time.sleep(1)  # 等待1秒
                    tracker.start()

                    if sv.hero_num > 3 and sv.pl_300_message_num <= 0:
                        take_screenshot()
                        print("地下城-选择地下城界面截图")
                        self.ctrl.click(1934, 935)
                        time.sleep(2)
                        if find_best_match_2(sv.current_screen_img,
                                             r"./img/underground_file/kuang.jpg") is not None:
                            click_img_coordinate(self.ctrl, sv.current_screen_img,
                                                 r"./img/underground_file/kuang.jpg")
                            click_img_coordinate(self.ctrl, sv.current_screen_img, r"img/underground_file/qr.jpg")
                            print("疲劳超过300-勾选并点击确认")
                            sv.pl_300_message_num = sv.pl_300_message_num + 1
                    else:
                        pass

                    # 战斗开始
                    while True:
                        take_screenshot()
                        if find_best_match_2(sv.current_screen_img, r"img/underground_file/zdks.jpg") is not None:
                            # 战斗开始
                            self.ctrl.click(1934, 935)
                            print("==============================")
                            print("点击-战斗开始")
                            print("==============================")
                        else:
                            break
                self.ctrl.move(0)
                self.detect_retry = False
                self.room_num = 0   # 重置房间号
                # time.sleep(3)
                hero_track = deque()  # 重置英雄轨迹
                hero_track.appendleft([0,0])  # 初始位置
                self.timing_time = None  # 重置时间
            else:
                outprint = "无目标"
                # print(outprint)
                if self.room_num == 4:  # 检查房间号
                    angle = calculate_angle_to_box(hero_track[0], [0.25, 0.6]) # 计算角度 c
                else:
                    angle = calculate_angle_to_box(hero_track[0], [0.5, 0.75]) # 计算角度
                self.ctrl.move(angle)   # 移动到计算的角度
                self.ctrl.attack(False)  # 停止攻击
                # 超时就返回城镇
                self.out_time()
                print(f"\r当前进度:{outprint},角度{angle}，位置{hero_track[0]}", end="")
            time.sleep(0.001)  # 等待微秒以防止高 CPU 占用


    def calculate_hero_pos(self, hero_track, boxs):
        """
        计算并更新英雄的轨迹位置。

        :param hero_track: 英雄轨迹队列。
        :param boxs: 检测到的框列表。
        """
        if len(boxs) == 0:  # 如果框列表是空的
            None
        elif len(boxs) == 1:  # 如果只有一个框
            hero_track.appendleft(calculate_center(boxs[0]))  # 将框的中心添加到轨迹
        elif len(boxs) > 1:  # 如果多个框
            for box in boxs:  # 遍历所有框
                if calculate_distance(box, hero_track[0]) < 0.1:  # 如果框与英雄轨迹距离近
                    hero_track.appendleft(box)  # 更新轨迹
                    return  # 结束函数
            hero_track.appendleft(hero_track[0])  # 如果不是，则保持上一个位置


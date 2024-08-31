
from game_control import GameControl
import time
import cv2
import math
import numpy as np
from collections import deque
import threading
from img.find_img import find_best_match, take_screenshot, find_best_match_2


def click_img_coordinate(control, current_screen_img, image_path, gray_convert=1):
    take_screenshot()
    if gray_convert == 1:
        hero_center_coordinates = find_best_match(current_screen_img, image_path)
    else:
        hero_center_coordinates = find_best_match_2(current_screen_img, image_path)
    if hero_center_coordinates is not None:
        time.sleep(1)
        control.click(hero_center_coordinates[0], hero_center_coordinates[1])
        time.sleep(2)
        return True
    return False

def countdown(seconds):
    print(f"开始倒计时 {seconds} 秒...")
    time.sleep(seconds)  # 倒计时
    print("时间到！")
    global timer_finished
    timer_finished = True  # 设置标志已完成倒计时


current_screen_img = "./current_screen_img.jpg"
def repair_equipment_and_sell_equipment(control):
    time.sleep(5)
    # 背包
    print("获取背包内的图片")
    click_img_coordinate(control, current_screen_img, r"./img/house_file/beibao.jpg")
    # 点击修理按钮
    print("获取修理界面图片")
    click_img_coordinate(control, current_screen_img, r"./img/repair_file/xiuli_1.jpg")
    # 点击修理
    print("修理完成")
    click_img_coordinate(control, current_screen_img, r"./img/repair_file/xiuli_2.jpg")
    # control.click(152, 39)
    print("点击X返回")
    click_img_coordinate(control, current_screen_img, r"./img/underground_file/X_icon.jpg")
    sell_equipment(control)
    time.sleep(3)
    # control.click(152, 39)
    print("点击返回")
    click_img_coordinate(control, current_screen_img, r"./img/underground_file/return_icon.jpg")


def sell_equipment(control):
    time.sleep(2)
    # 点击出售
    print("点击出售1")
    click_img_coordinate(control, current_screen_img, r"./img/beibao/sell.jpg")
    print("点击出售2")
    click_img_coordinate(control, current_screen_img, r"./img/beibao/sell_2.jpg")
    print("点击确认出售")
    click_img_coordinate(control, current_screen_img, r"./img/beibao/affirm.jpg")
    print("出售完毕,点击确认")
    click_img_coordinate(control, current_screen_img, r"./img/beibao/affirm.jpg")
    print("出售完毕,关闭出售栏")
    click_img_coordinate(control, current_screen_img, r"./img/underground_file/X_icon.jpg")


def bwj(control):
    time.sleep(3)
    # 点击冒险
    control.click(2072, 984)
    # click_img_coordinate(control, current_screen_img, r"./img/underground_file/maoxian_icon.jpg")
    print("点击冒险")
    time.sleep(1)
    # 点击冒险奖励
    control.click(2114, 835)
    # click_img_coordinate(control, current_screen_img, r"./img/underground_file/maoxian_icon.jpg")
    print("点击冒险奖励")
    time.sleep(1)
    # 点击冒险级
    control.click(870, 258)
    # click_img_coordinate(control, current_screen_img, r"./img/underground_file/maoxian_level.jpg")
    print("点击冒险级")
    time.sleep(1)
    # 点击区域移动
    control.click(1877, 714)
    # click_img_coordinate(control, current_screen_img, r"./img/underground_file/region_move.jpg")
    time.sleep(15)
    print("点击区域移动")
    # 点击布万加地图
    control.click(1636, 812)
    print("点击布万加地图")
    time.sleep(1)
    # 战斗开始
    control.click(1934, 935)
    # click_img_coordinate(control, current_screen_img, r"./img/underground_file/battle_start_icon.jpg")
    print("战斗开始")
    time.sleep(2)
    # 300 pl提示
    take_screenshot()
    # if find_best_match(current_screen_img, r"./img/qr.jpg"):
    if find_best_match_2(current_screen_img, r"./img/underground_file/kuang.jpg"):
        click_img_coordinate(control, current_screen_img, r"./img/underground_file/kuang.jpg")
    #     click_img_coordinate(control, current_screen_img, r"./img/ruchang.jpg")
        click_img_coordinate(control, current_screen_img, r"./img/qr.jpg")
        print("疲劳超过300提示")

def switch_hero(control, hero_img):
    while True:
        take_screenshot()
        time.sleep(2)
        # print("123213213")
        if find_best_match(current_screen_img, r"./img/house_file/email.jpg") is None:
            time.sleep(1)
            # 左上角选角
            click_img_coordinate(control, current_screen_img, r"./img/role/xuanjiao.jpg")
            print("点击左上角选角")
            # 获取当前屏幕信息并点击坐标
            click_img_coordinate(control, current_screen_img, hero_img)
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


def out_time(control, t):
    # 超时就返回城镇
    if t is None:
        t = time.time()
        print(f"超时时间：{t}")

    # print(outprint, first_find_door_time)
    if time.time() - t > 5:
        print("执行超时，进行其他操作")
        click_img_coordinate(control, "./current_screen_img.jpg", r"./img/setting.jpg")
        click_img_coordinate(control, "./current_screen_img.jpg", r"./img/return_to_town.jpg")
        click_img_coordinate(control, "./current_screen_img.jpg", r"./img/qr.jpg")

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
    image = cv2.cvtColor(image, cv2.IMREAD_GRAYSCALE)# 检查图片是否成功读取
    num_black_pixels = np.sum(image < threshold)
    total_pixels = image.size
    black_pixel_ratio = num_black_pixels / total_pixels# 定义一个比例阈值来判断图片是否接近黑色
    return black_pixel_ratio > 0.7
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
from hero.naima import Naima
class GameAction:
    def __init__(self, ctrl: GameControl,queue):
        self.queue = queue  # 初始队列
        self.ctrl = ctrl  # 控制游戏的对象
        self.detect_retry = False  # 是否需要重试检测
        self.pre_state = True  # 之前的状态
        self.stop_event = True  # 停止事件
        self.reset_event = False  # 重置事件
        self.control_attack = Naima(ctrl)  # 初始化攻击控制
        self.room_num = -1  # 当前房间号
        self.buwanjia = [8, 10, 10, 11, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10]  # 房间序列
        self.thread_run = True  # 控制线程运行状态
        self.thread = threading.Thread(target=self.control)  # 创建线程，并指定目标函数
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.thread.start()  # 启动线程


    def reset(self):
        """
        重置游戏状态，重新启动控制线程。
        """
        self.thread_run = False  # 停止当前线程
        time.sleep(0.1)  # 等待0.1秒
        self.room_num = -1  # 重置房间号
        self.detect_retry = False  # 重置重试状态
        self.pre_state = True  # 重置预状态
        self.thread_run = True  # 重新启动线程
        self.thread = threading.Thread(target=self.control)  # 创建新的线程
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.thread.start()  # 启动新线程

    def control(self):
        """
        游戏控制的主逻辑。
        """
        last_room_pos = []  # 上一个房间位置
        hero_track = deque()  # 英雄轨迹队列
        hero_track.appendleft([0, 0])  # 初始英雄位置
        last_angle = 0  # 上一个角度


            #
        # click_img_coordinate(self.ctrl, current_screen_img, r"./img/role/xuanjiao.jpg")
        # self.ctrl.slide(205, 519, "up")
        # # image, boxs = self.queue.get()
        # first_find_door_time = None
        # heros = {"大雷给奶一口":r"./img/role/nai1.jpg", "别拽了俺tuo":r"./img/role/bie2.jpg", "大雷是啥子":r"./img/role/kuang3.jpg"}
        # # # current_screen_img = "./current_screen_img.jpg"
        # take_screenshot()
        # time.sleep(3)
        # # bwj(self.ctrl)
        # hero_num = 0
        # # repair_equipment_and_sell_equipment(self.ctrl)
        # # # sell_equipment(self.ctrl)
        #
        # while True:
        #     bwj(self.ctrl)
        #     take_screenshot()
        #     print("q3123123",hero_num)
        #     time.sleep(5)
        #     if find_best_match(current_screen_img, r"./img/pl_num_file/pl0.jpg") is not None:
        #         print("选择角色中")
        #         # 点击右上角X按钮
        #         # self.ctrl.click(2053, 136)
        #         click_img_coordinate(self.ctrl, current_screen_img, r"./img/underground_file/X_icon.jpg")
        #         print("点击右上角X按钮")
        #         # 点击左上角返回
        #         # self.ctrl.click(149, 37)
        #         click_img_coordinate(self.ctrl, current_screen_img,  r"./img/underground_file/return_icon.jpg")
        #         print("点击左上角返回按钮")
        #         # 点击返回城镇
        #         self.ctrl.click(2064, 338)
        #         print("点击返回城镇")
        #         time.sleep(10)
        #         if hero_num == 0:
        #             print(f"我是英雄：{hero_num}")
        #             switch_hero(self.ctrl, heros["大雷给奶一口"])
        #             hero_num = hero_num + 1
        #             # 启动脚本
        #             # self.stop_event = False
        #             print("点击run 按钮")
        #
        #             # print(f"我是英雄：{heros['大雷给奶一口']}")
        #         elif hero_num == 1:
        #             print(f"我是英雄：{hero_num}")
        #             # switch_hero(self.ctrl, heros["别拽了俺tuo"])
        #             # 左上角选角
        #             click_img_coordinate(self.ctrl, current_screen_img, r"./img/role/xuanjiao.jpg")
        #             self.ctrl.click(205, 519)
        #             time.sleep(10)
        #             # 修理装备
        #             # repair_equipment_and_sell_equipment(self.ctrl)
        #             # 进布万加地图
        #             # bwj(self.ctrl)
        #             print("执行布万家前置步骤，1.修理装备 2.进入地图")
        #
        #             hero_num = hero_num + 1
        #             # 启动脚本
        #             # self.stop_event = False
        #             print("点击run 按钮")
        #
        #         elif hero_num == 2:
        #             print(f"我是英雄：{hero_num}")
        #             switch_hero(self.ctrl, heros["大雷是啥子"])
        #             hero_num = hero_num + 1
        #             # 启动脚本
        #             # self.stop_event = False
        #             print("点击run 按钮")

        #     else:
        #         # 选择其他地下城页面-战斗开始 按钮
        #         time.sleep(3)
        #         print("==============================")
        #         print("点击-战斗开始")
        #         print("==============================")
        #         self.ctrl.click(1925, 925)
        #         # 判断确定是否再次挑战布万加地图
        #         while True:
        #             # take_screenshot()
        #             # time.sleep(2)
        #             if find_best_match(image, r"./img/ruchang.jpg") is not None:
        #                 # 点击入场
        #                 # self.ctrl.click(1342, 700)
        #                 click_img_coordinate(self.ctrl, current_screen_img, r"./img/ruchang.jpg")
        #                 print("疲劳超过300-点击入场")
        #             else:
        #                 break
        #     self.detect_retry =False
        #     self.room_num = 0
        #     time.sleep(3)
        #     hero_track = deque()
        #     hero_track.appendleft([0,0])
        # else:
        #     # #x需要重置时间
        #     # if first_find_door_time is None:
        #     #     first_find_door_time = time.time()
        #     #     # print(f"超时时间：{first_find_door_time}")
        #     # if time.time() - first_find_door_time > 90:
        #     #     print("执行超时，进行其他操作")
        #     #     click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/setting.jpg")
        #     #     click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/return_to_town.jpg")
        #     #     click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/qr.jpg")
        #     outprint = "无目标"
        #     if self.room_num == 4:
        #         angle = calculate_angle_to_box(hero_track[0], [0.25, 0.6])
        #     else:
        #         angle = calculate_angle_to_box(hero_track[0], [0.5, 0.75])
        #     self.ctrl.move(angle)
        #     self.ctrl.attack(False)
        #     print(f"\r当前进度:{outprint},角度{angle}，位置{hero_track[0]}", end="")



        # take_screenshot()
        # 选择角色 （刷图的角色顺序）
        hero_num = 2  # 角色数量
        bwj(self.ctrl)
        self.stop_event = False
        # 重置时间
        first_find_door_time = None
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
                if self.pre_state == False:
                    if not self.pre_state:
                        print("过图")  # 通知过图
                        last_room_pos = hero_track[0]  # 保存最后位置
                        hero_track = deque()  # 重置英雄轨迹
                        hero_track.appendleft([1 - last_room_pos[0], 1 - last_room_pos[1]])  # 记录反方向
                        last_angle = 0  # 重置角度
                        self.ctrl.reset()  # 重置控制
                        self.pre_state = True  # 设置为预状态
                        first_find_door_time = None  # 重置发现门的时间
                    else:
                        continue
            hero = boxs[boxs[:, 5] == 6][:, :4]  # 获取英雄框
            gate = boxs[boxs[:, 5] == self.buwanjia[self.room_num]][:, :4]  # 获取门框
            arrow = boxs[boxs[:, 5] == 5][:, :4]  # 获取箭头框
            equipment = [[detection[0], detection[1] + (detection[3] - detection[1]), detection[2], detection[3] + (detection[3] - detection[1]), detection[4], detection[5]]
                        for detection in boxs if detection[5] == 4 and detection[4] > 0.3]
            monster = boxs[boxs[:, 5] <= 2][:, :4]  # 获取怪物框
            card = boxs[boxs[:, 5] == 3][:, :4]  # 获取卡片框
            Diamond = boxs[boxs[:, 5] == 13][:, :4]  # 获取钻石框
            angle = 0
            outprint = ''
            if self.pre_state == True :
                if len(hero) > 0:#记录房间号
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
                # 重置时间
                first_find_door_time = None
                outprint = '有怪物'
                angle = self.control_attack.control(hero_track[0],image,boxs,self.room_num)
            elif len(equipment)>0:
                # 重置时间
                first_find_door_time = None
                outprint = '有材料'
                if len(gate)>0:
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    farthest_item,distance = find_farthest_box(equipment,close_gate)
                    angle = calculate_point_to_box_angle(hero_track[0],farthest_item)
                else:
                    close_item,distance = find_close_point_to_box(equipment,hero_track[0])
                    angle = calculate_point_to_box_angle(hero_track[0],close_item)
                self.ctrl.attack(False)
                self.ctrl.move(angle)
            elif len(gate)>0:
                outprint = '有门'
                # print(outprint)
                if self.buwanjia[self.room_num] == 9:#左门
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    angle = calculate_gate_angle(hero_track[0],close_gate)
                    self.ctrl.attack(False)
                    self.ctrl.move(angle)
                else:
                    close_gate,distance = find_close_point_to_box(gate,hero_track[0])
                    angle = calculate_point_to_box_angle(hero_track[0],close_gate)
                    self.ctrl.attack(False)
                    self.ctrl.move(angle)
                    # print(outprint)
                    # 重置时间
                    # first_find_door_time = None
                    # out_time(self.ctrl, first_find_door_time)
                    # 超时就返回城镇
                    if first_find_door_time is None:
                        first_find_door_time = time.time()
                        # print(f"超时时间：{first_find_door_time}")
                    # print(outprint, first_find_door_time)
                    if time.time() - first_find_door_time > 50:
                        print("执行超时，进行其他操作")
                        click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/setting.jpg")
                        click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/return_to_town.jpg")
                        click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/qr.jpg")
                        time.sleep(10)
                        bwj(self.ctrl)
                        self.detect_retry = True
                        self.stop_event = False
            elif len(arrow)>0 and self.room_num != 4:
                # 超时就返回城镇
                if first_find_door_time is None:
                    first_find_door_time = time.time()
                    # print(f"超时时间：{first_find_door_time}")
                if time.time() - first_find_door_time > 50:
                    print("执行超时，进行其他操作")
                    click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/setting.jpg")
                    click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/return_to_town.jpg")
                    click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/qr.jpg")
                    time.sleep(10)
                    bwj(self.ctrl)
                    self.detect_retry = True
                    self.stop_event = False
                outprint = '有箭头'
                # print(outprint)
                # self.check_adventure_timeout()
                close_arrow,distance = find_closest_or_second_closest_box(arrow,hero_track[0])
                angle = calculate_point_to_box_angle(hero_track[0],close_arrow)
                self.ctrl.move(angle)
                self.ctrl.attack(False)
            elif self.detect_retry == True:
                #重新挑战：自行发挥
                print("detect_retry")
                heros = {"大雷给奶一口":r"./img/role/nai1.jpg", "别拽了俺tuo":r"./img/role/bie2.jpg", "大雷是啥子":r"./img/role/kuang3.jpg"}
                # current_screen_img = "./current_screen_img.jpg"
                # 选择其他地下城
                self.ctrl.click(2078, 240)
                # click_img_coordinate(self.ctrl, current_screen_img, r"./img/underground_file/select_dxc.jpg")
                time.sleep(3)
                print("选择其他地下城")
                take_screenshot()
                time.sleep(3)
                # if find_best_match(current_screen_img, r"./img/pl_num_file/pl0.jpg", 0) is not None:
                if find_best_match_2(current_screen_img, r"./img/pl_num_file/pl0.jpg") is not None:
                    print("疲劳值为0，选择其他角色")
                    # 点击右上角X按钮
                    # self.ctrl.click(2053, 136)
                    click_img_coordinate(self.ctrl, current_screen_img, r"./img/underground_file/X_icon.jpg")
                    print("点击右上角X按钮")
                    # 点击左上角返回
                    # self.ctrl.click(149, 37)
                    click_img_coordinate(self.ctrl, current_screen_img, r"./img/underground_file/return_icon.jpg")
                    print("点击左上角返回按钮")
                    # 点击返回城镇
                    self.ctrl.click(2064, 338)
                    print("点击返回城镇")
                    # 奶你
                    if hero_num == 0:
                        print(f"我是英雄：{hero_num}")
                        time.sleep(10)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, current_screen_img, r"./img/role/xuanjiao.jpg")
                        self.ctrl.click(307, 404)
                        time.sleep(12)
                        # 修理装备
                        repair_equipment_and_sell_equipment(self.ctrl)
                        bwj(self.ctrl)
                        hero_num = hero_num + 1
                        # 启动脚本
                        self.stop_event = False
                        print("点击run 按钮")
                    if hero_num == 1:
                        print(f"我是英雄：{hero_num}")
                        switch_hero(self.ctrl, heros["大雷给奶一口"])
                        hero_num = hero_num + 1
                        # 启动脚本
                        self.stop_event = False
                        print("点击run 按钮")
                    elif hero_num == 2:
                        print(f"我是英雄：{hero_num}")
                        # switch_hero(self.ctrl, heros["别拽了俺tuo"])
                        time.sleep(10)
                        # 左上角选角
                        click_img_coordinate(self.ctrl, current_screen_img, r"./img/role/xuanjiao.jpg")
                        self.ctrl.click(205, 519)
                        time.sleep(12)
                        # 修理装备
                        repair_equipment_and_sell_equipment(self.ctrl)
                        bwj(self.ctrl)
                        hero_num = hero_num + 1
                        # 启动脚本
                        self.stop_event = False
                        print("点击run 按钮")
                    elif hero_num == 3:
                        print(f"我是英雄：{hero_num}")
                        switch_hero(self.ctrl, heros["大雷是啥子"])
                        hero_num = hero_num + 1
                        # 启动脚本
                        self.stop_event = False
                        print("点击run 按钮")
                else:
                    # 选择其他地下城页面-战斗开始 按钮
                    time.sleep(3)
                    print("==============================")
                    print("点击-战斗开始")
                    print("==============================")
                    self.ctrl.click(1925, 925)
                    take_screenshot()
                    num = 0
                    if num == 0:
                        if find_best_match(self.queue.get()[0], r"./img/qr.jpg") is not None:  # 点击入场
                            self.ctrl.click(1317, 675)
                            # click_img_coordinate(self.ctrl, current_screen_img, r"./img/underground_file/kuang.jpg")
                            click_img_coordinate(self.ctrl, current_screen_img, r"./img/qr.jpg")
                            print("疲劳超过300-点击入场")
                            num = num + 1
                self.detect_retry =False
                self.room_num = 0   # 重置房间号
                time.sleep(3)
                hero_track = deque()  # 重置英雄轨迹
                hero_track.appendleft([0,0])  # 初始位置
            else:
                # 超时就返回城镇
                if first_find_door_time is None:
                    first_find_door_time = time.time()
                    # print(f"超时时间：{first_find_door_time}")
                if time.time() - first_find_door_time > 50:  # 检查超时
                    print("执行超时，进行其他操作")
                    click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/setting.jpg")
                    click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/return_to_town.jpg")
                    click_img_coordinate(self.ctrl, "./current_screen_img.jpg", r"./img/qr.jpg")
                    time.sleep(10)
                    bwj(self.ctrl)
                    self.detect_retry = True
                    self.stop_event = False
                outprint = "无目标"
                # print(outprint)
                if self.room_num == 4:  # 检查房间号
                    angle = calculate_angle_to_box(hero_track[0], [0.25, 0.6]) # 计算角度
                else:
                    angle = calculate_angle_to_box(hero_track[0], [0.5, 0.75]) # 计算角度
                self.ctrl.move(angle)   # 移动到计算的角度
                self.ctrl.attack(False)  # 停止攻击
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


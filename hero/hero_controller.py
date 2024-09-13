import time
import math
import cv2
import pytesseract
import shared_variables as sv  # 引入共享变量模块
import json
import os

def calculate_center(box):  # 计算矩形框的底边中心点坐标
    return ((box[0] + box[2]) / 2, box[3])


def calculate_distance(center1, center2):  # 计算两个底边中心点之间的欧几里得距离
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)


def find_closest_box(boxes, target_box):  # 计算目标框的中心点
    target_center = calculate_center(target_box)  # 初始化最小距离和最近的box
    min_distance = float('inf')
    closest_box = None  # 遍历所有box，找出最近的box
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance < min_distance:
            min_distance = distance
            closest_box = box
    return closest_box, min_distance


def find_close_point_to_box(boxes, point):
    target_center = point  # 初始化最小距离和最近的box
    min_distance = float('inf')
    closest_box = None  # 遍历所有box，找出最近的box
    for box in boxes:
        center = calculate_center(box)
        distance = calculate_distance(center, target_center)
        if distance < min_distance:
            min_distance = distance
            closest_box = box
    return closest_box, min_distance


def calculate_point_to_box_angle(point, box):
    center1 = point
    center2 = calculate_center(box)
    delta_x = center2[0] - center1[0]  # 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)  # 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle


def calculate_angle(box1, box2):  # 计算两个框的底边中心点
    center1 = calculate_center(box1)
    center2 = calculate_center(box2)
    delta_x = center2[0] - center1[0]  # 计算相对角度（以水平轴为基准）
    delta_y = center2[1] - center1[1]
    angle = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle)  # 将角度转换为度数
    adjusted_angle = - angle_degrees
    return adjusted_angle


def calculate_angle_to_box(box, x, y):  # 计算框到点的角度
    center = calculate_center(box)  # 计算矩形框的中心点
    angle = math.atan2(y - center[1], x - center[0])  # 计算从点 (x, y) 到中心点的角度
    angle_degrees = math.degrees(angle)  # 将角度转换为度数
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


def normalize_angle(angle):  # 将角度规范化到 [-180, 180) 的范围内
    angle = angle % 360
    if angle >= 180:
        angle -= 360
    return angle


def are_angles_on_same_side_of_y(angle1, angle2):  # 规范化角度
    norm_angle1 = normalize_angle(angle1)
    norm_angle2 = normalize_angle(angle2)  # 检查是否在 y 轴的同侧
    return (norm_angle1 >= 0 and norm_angle2 >= 0) or (norm_angle1 < 0 and norm_angle2 < 0)


class HeroController:
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.pre_room_num = -1
        self.last_angle = 0
        self.load_skills()

    def load_skills(self):
        """加载技能配置"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, sv.skill_name_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            self.dict = json.load(file)  # 解析 JSON 文件

    def skill(self, name, t=0):
        """执行技能"""
        self.ctrl.skill(self.dict[name], t)
        print("shifang:", name)

    def control(self, hero_pos, image, boxs, MapNumber):
        """根据英雄编号选择控制逻辑"""
        hero_num = sv.hero_num  # 从共享变量中获取英雄编号
        if hero_num == 1 or hero_num == 2 or hero_num == 3 or hero_num == 4 or hero_num == 5 or hero_num == 6:
            return self.control_hero_1(hero_pos, image, boxs, MapNumber)
        elif hero_num == 7:
            return self.control_hero_7(hero_pos, image, boxs, MapNumber)
        # elif hero_num == 2:
        #     return self.control_hero_2(hero_pos, image, boxs, MapNumber)
        # 继续为其他英雄添加elif分支
        else:
            print("未定义的英雄编号")
            return None

    def control_hero_1(self, hero_pos, image, boxs, MapNumber):
        """英雄 1 的控制逻辑"""
        if self.pre_room_num != MapNumber:
            wait = 0.1
            if MapNumber == 0:
                self.ctrl.reset()
                time.sleep(wait)
                self.skill("勇气祝福")
                time.sleep(1.2)
                self.ctrl.move(335)
                time.sleep(0.3)
                self.skill("领悟之雷")
            elif MapNumber == 1:
                time.sleep(wait)
                self.ctrl.move(295)
                time.sleep(0.4)
                self.skill("光明惩戒")
                time.sleep(1)
            elif MapNumber == 2:
                time.sleep(wait)
                self.ctrl.move(340)
                time.sleep(0.6)
                self.skill("光芒烬盾")
            elif MapNumber == 3:
                time.sleep(wait)
                self.ctrl.move(345)
                time.sleep(0.5)
                self.skill("勇气颂歌")
            elif MapNumber == 4:
                time.sleep(wait)
                self.ctrl.move(145)
                time.sleep(0.65)
                self.ctrl.move(1)
                time.sleep(0.05)
                self.skill("胜利之矛")
                time.sleep(0.5)
                self.ctrl.move(1)
                time.sleep(0.2)
                self.skill("光芒烬盾")
            elif MapNumber == 5:
                time.sleep(wait)
                self.ctrl.move(180)
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(0.4)
                self.skill("觉醒")
            elif MapNumber == 6:
                None
            elif MapNumber == 7:
                time.sleep(wait)
                self.ctrl.move(335)
                time.sleep(0.4)
                self.ctrl.move(0)
                self.skill("光芒烬盾")
                time.sleep(1)
                self.skill("沐天之光")
            elif MapNumber == 8:
                time.sleep(wait)
                self.ctrl.move(340)
                time.sleep(0.4)
                self.skill("胜利之矛")
                time.sleep(0.5)
                self.ctrl.move(1)
                time.sleep(0.5)
                self.skill("光明惩戒")
            elif MapNumber == 9:
                time.sleep(wait)
                self.ctrl.move(330)
                time.sleep(0.4)
                self.ctrl.move(0)
                self.skill("光芒烬盾")
                time.sleep(0.8)
                self.skill("光明之杖")
            self.pre_room_num = MapNumber
            return 0  # 更新房间编号并返回

        # 这里添加其他英雄 0 的具体控制逻辑
        return self.perform_common_actions(hero_pos, boxs)

    def control_hero_7(self, hero_pos, image, boxs, MapNumber):
        """英雄 7 的控制逻辑"""
        if self.pre_room_num != MapNumber:
            wait = 0.1
            if MapNumber == 0:
                self.ctrl.reset()
                time.sleep(wait)
                self.ctrl.reset()
                time.sleep(wait)
                self.skill("勇气祝福")
                time.sleep(1.2)
                self.skill("沐天之光")
                time.sleep(0.2)
                self.ctrl.move(335)
                time.sleep(0.5)
                self.skill("领悟之雷")
                time.sleep(0.3)
                self.skill("圈圈")
                time.sleep(0.3)
                self.skill("圈圈")
                time.sleep(0.3)
                self.skill("圈圈")
                time.sleep(0.3)
                self.skill("圈圈")
                time.sleep(0.3)
            elif MapNumber == 1:
                time.sleep(wait)
                self.ctrl.move(295)
                time.sleep(0.4)
                self.skill("光明之杖")
                time.sleep(1)
            elif MapNumber == 2:
                time.sleep(wait)
                self.ctrl.move(340)
                time.sleep(0.6)
                self.skill("光芒烬盾")
                # self.skill("光明惩戒")
            elif MapNumber == 3:
                time.sleep(wait)
                self.ctrl.move(345)
                time.sleep(1)
                self.skill("光明惩戒")
            elif MapNumber == 4:
                time.sleep(wait)
                self.ctrl.move(145)
                time.sleep(0.65)
                self.ctrl.move(1)
                time.sleep(0.05)
                self.skill("胜利之矛")
                time.sleep(0.5)
                self.ctrl.move(1)
                time.sleep(0.2)
                self.skill("光芒烬盾")
            elif MapNumber == 5:
                time.sleep(wait)
                self.ctrl.move(330)
                time.sleep(0.2)
                self.skill("沐天之光")
                time.sleep(1)
                self.skill("领悟之雷")
            elif MapNumber == 6:
                time.sleep(wait)
                self.ctrl.move(330)
                time.sleep(0.4)
                self.skill("光明惩戒")
                # else:
                #     None
            elif MapNumber == 7:
                time.sleep(wait)
                self.ctrl.move(330)
                time.sleep(0.4)
                self.skill("胜利之矛")
                time.sleep(0.4)
                self.skill("觉醒")
                time.sleep(3)
                self.skill("觉醒")
            elif MapNumber == 8:
                time.sleep(wait)
                self.ctrl.move(340)
                time.sleep(0.4)
                self.skill("胜利之矛")
                time.sleep(0.5)
                self.ctrl.move(1)
                time.sleep(0.5)
                self.skill("光明惩戒")
            elif MapNumber == 9:
                time.sleep(wait)
                self.ctrl.move(330)
                time.sleep(0.4)
                self.ctrl.move(0)
                self.skill("光芒烬盾")
                time.sleep(0.8)
                self.skill("光明之杖")
            self.pre_room_num = MapNumber
            return 0  # 更新房间编号并返回

        # 这里添加其他英雄 1 的具体控制逻辑
        return self.perform_common_actions(hero_pos, boxs)

    def control_hero_2(self, hero_pos, image, boxs, MapNumber):
        """英雄 2 的控制逻辑"""
        if self.pre_room_num != MapNumber:
            wait = 0.1
            time.sleep(wait)
            self.ctrl.move(340)
            time.sleep(0.6)
            self.skill("光芒烬盾")
            self.pre_room_num = MapNumber
            return 0  # 更新房间编号并返回

        # 这里添加其他英雄 2 的具体控制逻辑
        return self.perform_common_actions(hero_pos, boxs)


    def perform_common_actions(self, hero_pos, boxs):
        """所有英雄共享的控制逻辑"""
        monster = boxs[boxs[:, 5] <= 2][:, :4]  # 筛选出可攻击的怪物
        close_monster, _ = find_close_point_to_box(monster, hero_pos)  # 找到最近的怪物
        close_monster_point = calculate_center(close_monster)  # 计算怪物中心点
        angle = calculate_point_to_box_angle(hero_pos, close_monster)  # 计算英雄指向怪物的角度

        # 检查英雄的最后角度和当前角度是否在同侧
        if not are_angles_on_same_side_of_y(self.last_angle, angle):
            # 如果在不同侧，则只移动，取消攻击
            self.ctrl.move(angle)
            self.ctrl.attack(False)
        elif abs(hero_pos[1] - close_monster_point[1]) < 0.1 and abs(hero_pos[0] - close_monster_point[0]) < 0.15:
            # 如果接近怪物则攻击
            self.ctrl.attack()
        else:
            # 否则继续向怪物方向移动
            self.ctrl.move(angle)
            self.ctrl.attack(False)

        self.last_angle = angle  # 更新最后角度
        return angle  # 返回计算的角度



import math



def calc_mov_point(angle: int):
    ry = 415
    rx = 787
    if angle == 0:
        return rx, ry
    angle = angle % 360
    if angle < 0:
        angle = 360 + angle
    r = 180
    x = rx + r * math.cos(angle * math.pi / 180)
    y = ry - r * math.sin(angle * math.pi / 180)
    return int(x), int(y)

print(calc_mov_point(145))
print(calc_mov_point(1))
print(calc_mov_point(1))


import math

def angle_from_coordinates(rx: int, ry: int, x: int, y: int) -> float:
    # 计算相对坐标
    dx = x - rx
    dy = ry - y  # 注意y方向是反的，所以用ry - y
    # 计算角度（以弧度为单位）
    angle_radians = math.atan2(dy, dx)
    # 转换为度数
    angle_degrees = angle_radians * (180 / math.pi)
    # 处理负值和范围
    angle_degrees = angle_degrees % 360
    return angle_degrees

# 中心点
rx = 787
ry = 415

x = 966
y = 411
# 获取从坐标计算的角度
angle = angle_from_coordinates(rx, ry, x, y)
print(angle)
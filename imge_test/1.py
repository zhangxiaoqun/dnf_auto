
import cv2
import numpy as np

def is_brightness_low(image, region, threshold):
    """
    判断图像中指定区域的平均亮度是否低于阈值。

    :param image: 输入图像 (NumPy 数组)
    :param region: 区域，格式为 (起始y, 终止y, 起始x, 终止x)
    :param threshold: 平均亮度的阈值
    :return: 是否低于阈值（布尔值）
    """
    # 提取指定区域
    y_start, y_end, x_start, x_end = region
    sub_image = image[y_start:y_end, x_start:x_end]

    # 计算区域的平均亮度
    mean_brightness = np.mean(sub_image)
    print(f"区域的平均亮度: {mean_brightness}")

    # 显示指定区域的图像
    # cv2.imshow("Selected Region", sub_image)
    # cv2.waitKey(0)  # 等待按键以关闭窗口
    # cv2.destroyAllWindows()
    # 判断平均亮度是否低于阈值
    return mean_brightness > threshold

# 示例使用
# 假设 img 是已经加载的图像（NumPy 数组）

# if img is None:
#     print("无法加载图像，请检查路径!")
# else:

l = ['2.jpg', '1.jpg', '3.jpg', '4.jpg', '5.jpg']
for i in l:
    img = cv2.imread(i)  # 替换为你的图像路径
    # 定义需要检测的区域，格式为 (起始y, 终止y, 起始x, 终止x)
    region_to_check = (46, 212, 2157, 2265)  # 根据实际要求调整区域

    # 定义阈值
    brightness_threshold = 40.55+0.1   # 示例阈值，具体值可以根据实际情况调整

    # 检查该区域的平均亮度是否低于阈值
    if is_brightness_low(img, region_to_check, brightness_threshold):
        print("未低于阈值。")
        # print("低于阈值。")
    else:
        print("低于阈值。")
        # print("未低于阈值。")


# import cv2
# import numpy as np
#
# # 读取图像
# image = cv2.imread('2.jpg')
# # 区域的平均亮度：62.1015
# # 设定的阈值：31.05075
#
# # image = cv2.imread('1.jpg')
# #区域的平均亮度：70.971375
# #设定的阈值：35.4856875
#
# # 将图像转换为灰度图
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
# # 假设您已经选择了一个区域
# start_y, end_y, start_x, end_x = 46,171, 1684,1812  # 手动设定或通过用户输入、鼠标选择获得
#
# # 提取选定区域
# roi = gray_image[start_y:end_y, start_x:end_x]
#
# # 计算该区域的平均亮度
# average_brightness = np.mean(roi)
# # 输出平均亮度
# print(f"区域的平均亮度：{average_brightness}")
#
# # 设定阈值为平均亮度的一半
# threshold = average_brightness * 0.5
# print(f"设定的阈值：{threshold}")
#
# # 或者，使用 Otsu 方法自动计算阈值
# _, otsu_threshold = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# print(f"Otsu 方法计算的阈值：{otsu_threshold}")
#
# # 在原图上可视化阈值化
# _, binary_image = cv2.threshold(roi, threshold, 255, cv2.THRESH_BINARY)
# cv2.imshow("Binary Image", binary_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

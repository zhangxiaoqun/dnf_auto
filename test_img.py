import sys

import cv2
import pytesseract
import numpy as np

# path = r"C:\Users\Harlan\Desktop\yolo项目\dnfm_server-main\template\zctz.jpg"
# path = r"C:/Users/Harlan/Desktop/t.png"
path = r"C:/Users/Harlan/Desktop/bb.png"
# path = r"C:/Users/Harlan/Desktop/zctz.png"
# path = r"C:/Users/Harlan/Desktop/hero.png"
# 指定tesseract的安装路径
pytesseract.pytesseract.tesseract_cmd = r'E:\Tesseract-OCR\tesseract.exe'  # 根据你的安装路径进行修改

# if len(sys.argv) < 2:
#     print("Usage: Python test_img.py zctz.jpg")
#     sys.exit(1)
#
# img_path = sys.argv[1]
#
config = ("-1 chi_sim --oem 1 --psm 3")
#
# im = cv2.imread(path, cv2.IMREAD_COLOR)
# text = pytesseract.image_to_string(im, config=config)
# print(text)
# tesseract.exe --list-langs  查看语言包



# m1 = r"./hero/b.jpg"
# m2 = r"./hero/123.jpg"
m1 = r"./hero/123.jpg"
m2 = r"./img/pl.jpg"
# import cv2
#
# # 读取两张图片
# img1 = cv2.imread(m1, cv2.IMREAD_GRAYSCALE)  # 查询图像
# img2 = cv2.imread(m2, cv2.IMREAD_GRAYSCALE)  # 训练图像
#
# # 初始化SIFT检测器
# sift = cv2.SIFT_create()
#
# # 检测关键点和计算描述符
# keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
# keypoints2, descriptors2 = sift.detectAndCompute(img2, None)
#
# # 使用FLANN匹配器进行特征点匹配
# FLANN_INDEX_KDTREE = 0
# index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
# search_params = dict(checks=50)  # 或使用空字典
#
# flann = cv2.FlannBasedMatcher(index_params, search_params)
# matches = flann.knnMatch(descriptors1, descriptors2, k=2)
#
# # 过滤好的匹配项
# good_matches = []
# for m, n in matches:
#     if m.distance < 0.7 * n.distance:
#         good_matches.append(m)
#
# # 绘制匹配结果
# matched_image = cv2.drawMatches(img1, keypoints1, img2, keypoints2, good_matches, None)
#
# # 显示匹配结果
# cv2.imshow('Matched Features', matched_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

import cv2
import numpy as np

import cv2
import numpy as np

def find_best_match(source_image_path, search_image_path):
    # 读取图像
    source_img = cv2.imread(source_image_path)
    search_img = cv2.imread(search_image_path)

    # 确保图像被成功读取
    if source_img is None or search_img is None:
        print("Error: One of the images could not be loaded.")
        return None

    # 获取搜索图像的尺寸
    h, w = search_img.shape[:2]

    # 使用模板匹配进行匹配
    result = cv2.matchTemplate(source_img, search_img, cv2.TM_CCOEFF_NORMED)

    # 获取匹配结果中的最大值和相应的位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 设定一个阈值来判断匹配是否有效
    threshold = 0.8  # 根据需要调整此值

    if max_val >= threshold:
        # 如果匹配值大于阈值，返回最佳匹配的位置信息和置信度
        confidence = max_val
        top_left = max_loc

        # 计算中心坐标
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        center_coordinates = (center_x, center_y)

        # 绘制匹配结果
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(source_img, top_left, bottom_right, (0, 255, 0), 2)
        cv2.imshow("Matched Result", source_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # return {
        #     'center_coordinates': center_coordinates,
        #     'confidence': confidence
        # }
        return center_coordinates, confidence
    else:
        # 如果没有找到匹配项
        return None

# 调用函数并传入图像路径
result = find_best_match(m1, m2)

# 打印结果
if result:
    # print("Center coordinates:", result['center_coordinates'])
    # print("Confidence:", result['confidence'])
    print("Center coordinates:", result[0])
    print("Confidence:", result[1])
else:
    print("No match found.")
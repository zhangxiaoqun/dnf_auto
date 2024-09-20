import cv2
import numpy as np

# 读取图像
# image = cv2.imread('3.jpg')
# 区域的平均亮度：56.946043731319804
# 设定的阈值：28.473021865659902

# image = cv2.imread('2.jpg')
# 区域的平均亮度：45.44917413874469
# 设定的阈值：22.724587069372344

# image = cv2.imread('1.jpg')
# 区域的平均亮度：58.53513243378311
# 设定的阈值：29.267566216891556
l = ['3.jpg', '2.jpg', '1.jpg']
for i in l:
    image = cv2.imread(i)
    # 将图像转换为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 假设您已经选择了一个区域
    start_y, end_y, start_x, end_x = 46, 212, 2157, 2265  # 手动设定或通过用户输入、鼠标选择获得

    # 提取选定区域
    roi = gray_image[start_y:end_y, start_x:end_x]

    # 计算该区域的平均亮度
    average_brightness = np.mean(roi)
    # 输出平均亮度
    print(f"区域的平均亮度：{average_brightness}")

    # 设定阈值为平均亮度的一半
    threshold = average_brightness * 0.5
    # print(f"设定的阈值：{threshold}")

    # 或者，使用 Otsu 方法自动计算阈值
    _, otsu_threshold = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # print(f"Otsu 方法计算的阈值：{otsu_threshold}")

    # 在原图上可视化阈值化
    _, binary_image = cv2.threshold(roi, threshold, 255, cv2.THRESH_BINARY)
    cv2.imshow("Binary Image", binary_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

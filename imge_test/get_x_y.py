import cv2

# 读取图片
# image = cv2.imread('img/4.jpg')
# image = cv2.imread('1.jpg')
image = cv2.imread('3.jpg')

# 用于记录区域的全局变量
start_y, end_y, start_x, end_x = -1, -1, -1, -1
cropping = False


def select_region(event, x, y, flags, param):
    global start_x, start_y, end_x, end_y, cropping

    # 按下左键，记录起始点
    if event == cv2.EVENT_LBUTTONDOWN:
        start_x, start_y = x, y
        cropping = True

    # 松开左键，记录结束点
    elif event == cv2.EVENT_LBUTTONUP:
        end_x, end_y = x, y
        cropping = False

        # 绘制选定区域
        cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
        cv2.imshow("image", image)


# 创建窗口并设置鼠标回调
cv2.namedWindow("image")
cv2.setMouseCallback("image", select_region)

# 展示图像直到按下 'q'
while True:
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()

# 输出选定的区域
if start_x != -1 and end_x != -1 and start_y != -1 and end_y != -1:
    print(f"检测区域： (起始y={start_y}, 终止y={end_y}, 起始x={start_x}, 终止x={end_x})")
    print(f"检测区域： ({start_y}, {end_y}, {start_x}, {end_x})")
else:
    print("未选择有效区域，请重试。")

import pytesseract
import cv2
import subprocess

def take_screenshot(filename="current_screen_img.jpg"):
    try:
        # 使用 Popen 进行截图
        with open(filename, "wb") as output_file:
            # 启动 adb 子进程
            process = subprocess.Popen(
                ["adb", "exec-out", "screencap", "-p"],
                stdout=output_file,
                stderr=subprocess.PIPE  # 捕获错误输出
            )
            # 等待子进程执行完毕
            process.wait()
            if process.returncode != 0:
                print(f"Error occurred: {process.stderr.read()}")
            else:
                print(f"Screenshot saved as {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")


def find_best_match(source_image_path, search_image_path):
    # 如果源图像是字符串，尝试加载图像
    if isinstance(source_image_path, str):
        source_img = cv2.imread(source_image_path)
        if source_img is None:
            print("错误: 无法加载源图像.")
            return None
    else:
        source_img = source_image_path  # 这里假设是已经加载好的Numpy数组


    # 读取搜索图像
    search_img = cv2.imread(search_image_path)

    # 确保图像被成功读取
    if source_img is None or search_img is None:
        print("错误:无法加载其中一个图像.")
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
        center_coordinates = center_x, center_y
        center_coordinates = str(center_coordinates).replace("(", "").replace(")", "")
        # 绘制匹配结果 (调试的时候再打开)
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(source_img, top_left, bottom_right, (0, 255, 0), 2)
        cv2.imshow("Matched Result", source_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # return {
        #     'center_coordinates': center_coordinates,
        #     'confidence': confidence
        # }
        # return center_coordinates, confidence
        return center_x, center_y, confidence
    else:
        # 如果没有找到匹配项
        return None


if __name__ == '__main__':
    # m1 = r"../jt.jpg"
    # m2 = r"./pl.jpg"
    # # 调用函数并传入图像路径
    # result = find_best_match(m1, m2)
    # # 打印结果
    # if result:
    #     # print("Center coordinates:", result['center_coordinates'])
    #     # print("Confidence:", result['confidence'])
    #     print("Center coordinates:", result[0])
    #     print("Confidence:", result[1])
    # else:
    #     print("No match found.")

    # if find_best_match(r"../jt.jpg", r"./pl.jpg"):
    # a = find_best_match(r"../current.jpg", r"../img/pl2.jpg")
    # a = find_best_match(r"../current_screen_img.jpg", r"underground_file/maoxian_icon.jpg")
    # a = find_best_match(r"./11.jpg", r"../img/ruchang.jpg")
    a = find_best_match(r"./11.jpg", r"../img/pl_num_file/pl300.jpg")
    # a = find_best_match(r"./16.jpg", r"../img/pl_num_file/pl0.jpg")
    # aa = cv2.imread(r"./11.jpg")
    # a = find_best_match(r"./11.jpg", r"./ruchang.jpg")
    print(type(a))
    # print(str(a).replace("(", "").replace(")", ""))
    print(a)
    print("选择角色中")
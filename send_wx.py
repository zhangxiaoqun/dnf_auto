import requests
import time


def send_miao_reminder(text):
    """
    发送喵提醒

    :param id: str，喵码
    :param text: str，提醒附加内容
    """
    mm_id = 'tz10qj1'
    ts = str(time.time())  # 获取时间戳
    type = 'json'  # 返回内容格式
    request_url = "http://miaotixing.com/trigger?"

    # 伪装浏览器请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'
    }

    # 构建请求的完整 URL
    full_url = f"{request_url}id={mm_id}&text={text}&ts={ts}&type={type}"

    try:
        # 发送 POST 请求
        result = requests.post(full_url, headers=headers)
        # 检查响应状态
        if result.status_code == 200:
            print('提醒发送成功:', result.json())
        else:
            print(f'发送失败，状态码: {result.status_code}, 返回内容: {result.text}')
    except Exception as e:
        print(f'请求出现异常: {e}')


# 示例使用
if __name__ == "__main__":
    # id = 'tz10qj1'  # 指定的喵码
    # text = 'XX数据异常'  # 提醒附加内容
    # send_miao_reminder(id, text)
    ts = str(time.time())  # 获取时间戳
    print(ts)
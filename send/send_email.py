import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_with_attachment(to_email, subject, body, filenames):
    # 创建邮件对象，并设置邮件头部信息
    msg = MIMEMultipart()
    # 发送方
    msg['From'] = '975924636@qq.com'
    # 接受方
    # msg['To'] = '975924636@qq.com'
    msg['To'] = to_email
    # 邮件主题
    msg['Subject'] = subject


    # 添加邮件正文
    msg.attach(MIMEText(body, 'plain'))

    # 添加附件
    for filename in filenames:
        with open(filename, 'rb') as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(part)

    # 连接到 SMTP 服务器并发送邮件
    try:
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login('975924636@qq.com', 'caaqtrsfslrobbbc')  # 使用QQ邮箱的授权码
            server.send_message(msg)
            print('邮件发送成功')
    except Exception as e:
        print('邮件发送失败:', e)


if __name__ == '__main__':
    # 示例用法
    receiver_email = '975924636@qq.com'  # 接收方邮箱
    subject = 'DNF状态'  # 邮件主题
    body = '这是邮件正文部分。'  # 邮件正文
    filename = [r'E:\yolo\dnf_auto_test\wechat_qr_code.jpg']  # 附件文件路径

    send_email_with_attachment(receiver_email, subject, body, filename)
    #986849994@qq.com
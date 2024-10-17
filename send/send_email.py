import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_with_attachment(subject, body, filenames):
    # 创建邮件对象，并设置邮件头部信息
    msg = MIMEMultipart()
    # 发送方
    msg['From'] = '975924636@qq.com'
    # 接受方
    msg['To'] = '975924636@qq.com'
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
    # 连接到 SMTP 服务器，登录并发送邮件
    with smtplib.SMTP('smtp.qq.com', 25) as server:
        server.starttls()
        server.login('975924636@qq.com', 'caaqtrsfslrobbbc')
        server.send_message(msg)
        print('邮件发送成功')


if __name__ == '__main__':
    # 示例用法
    # # 发送方
    # sender_email = '975924636@qq.com'
    # # 接受方
    # receiver_email = '975924636@qq.com'
    # # 邮件主题
    subject = 'DNF状态'
    # 这是邮件正文部分
    body = '1.'
    # 文件
    filename = [r'E:\yolo\dnf_auto_test\2.jpg']
    # # SMTP 服务器
    # smtp_server = 'smtp.qq.com'
    # smtp_port = 25
    # username = '975924636@qq.com'
    # password = 'caaqtrsfslrobbbc'

    send_email_with_attachment(subject, body, filename)
    #986849994@qq.com
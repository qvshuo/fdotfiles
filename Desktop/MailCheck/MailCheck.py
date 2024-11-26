#!/usr/bin/python

import imaplib
import time
import email
from email.header import decode_header
import subprocess

# 请填入你的邮箱信息
EMAIL_ADDRESS = 'your-email@example.com'
PASSWORD = 'your-password'
IMAP_SERVER = 'imap.example.com'
IMAP_PORT = 993

def get_unread_count_and_latest_subject():
    """连接 IMAP 服务器并获取未读邮件数量和最新未读邮件的标题"""
    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as imap:
        imap.login(EMAIL_ADDRESS, PASSWORD)
        imap.select()
        status, response = imap.search(None, 'UNSEEN')
        unseen_ids = response[0].split()
        unseen_count = len(unseen_ids)
        newest_subject = None

        if unseen_count > 0:
            latest_email_id = unseen_ids[-1]
            status, msg_data = imap.fetch(latest_email_id, '(RFC822)')
            if status == 'OK' and msg_data:
                for part in msg_data:
                    if isinstance(part, tuple):
                        msg = email.message_from_bytes(part[1])
                        subject, encoding = decode_header(msg['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')
                        newest_subject = subject
                        break

    return unseen_count, newest_subject

previous_unseen_count = 0

while True:
    current_unseen_count, newest_mail = get_unread_count_and_latest_subject()

    if current_unseen_count == 0:
        # 如果未读邮件数量是 0，重置 previous_unseen_count
        previous_unseen_count = 0
    elif current_unseen_count != previous_unseen_count:
        # 如果未读邮件数量有变化，发送通知
        previous_unseen_count = current_unseen_count
        if newest_mail:
            subprocess.run([
                'notify-send', '你有一封新邮件', newest_mail,
                '--icon=MailCheck', '--app-name=MailCheck'
            ])

    # 每90秒检查一次
    time.sleep(90)

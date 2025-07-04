from celery import shared_task
import time
@shared_task
def send_otp_email(user_email, code):
    print("sending ...")
    time.sleep(20)
    print("email sent")


@shared_task
def send_daily_report():
    print("sending daily report ...")
    time.sleep(40)
    print("daily report sent")

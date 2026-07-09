from django.core.mail import send_mail
from django.conf import settings
class MySendMail:
    def __init__(self):
       pass
    def send(self,subject,message,to_email):
        
        status = send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False  # 发送失败抛出异常
        )
        return status
    

my_send_mail = MySendMail()
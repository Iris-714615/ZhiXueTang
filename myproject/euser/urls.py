"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *
from .ai_views import AIAssistantProxyView, CourseProgressView



urlpatterns = [
    # path('admin/', admin.site.urls),
    path("login/", LoginView.as_view()),
    path("send_sms/", SendSmsView.as_view()),
    path("register/", RegisterView.as_view()),
    path("send_email/", SendEmailView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
    path("mycourse/", MyCourseView.as_view()),
    path("update_password/", ResetPasswordView.as_view()),
    path("myorder/", MyOrderView.as_view()),
    path("cancelorder/", CancelOrderView.as_view()),
    path("comment/", CommentView.as_view()),
    path("refund/", RefundView.as_view()),
    path("recharge/", RechargeView.as_view()),
    path("rechargeactivity/", RechargeActivityView.as_view()),
    path("userinfo/", UserInfo.as_view()),
    # 新增：AI 网关 SSE 代理 与 高并发课程进度写入
    path("ai/assistant/chat/", AIAssistantProxyView.as_view()),
    path("course/progress/", CourseProgressView.as_view()),

    
]

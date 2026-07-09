"""
ASGI config for myproject project.

支持 HTTP 与 WebSocket 双协议：
- HTTP 请求由 Django 标准应用处理
- WebSocket 请求由 Django Channels 路由到 live 应用的消费者

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 指向 dev 配置（与 manage.py / wsgi.py 保持一致）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.dev')

# 先初始化 Django ASGI 应用，再进行路由组合
django_asgi_app = get_asgi_application()

# 导入 WebSocket 路由（必须在 DJANGO_SETTINGS_MODULE 设置之后）
from live.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    # 普通 HTTP 请求
    'http': django_asgi_app,
    # WebSocket 请求：通过 AuthMiddlewareStack 注入用户后路由到各 consumer
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

from django.http import JsonResponse
from tools.myjwt import myjwt

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # 定义白名单，不需要验证 token 的路径
        self.white_list = [
            '/login/',
            '/register/',
            '/send_sms/',
            '/tcourse/cate/',
            '/tcourse/nav/',
            '/tcourse/banner/',
            '/tcourse/tags/',
            '/tcourse/courses/',
            '/tcourse/recate/',
            '/tcourse/allcate/',
            '/tcourse/allcourses/',
            '/tcourse/test/',
            '/tcourse/detail/',
            '/admin/',
            '/upload/',
        ]
    
    def __call__(self, request):
        # 检查请求路径是否在白名单中
        path = request.path
        for white_path in self.white_list:
            if path.startswith(white_path):
                response = self.get_response(request)
                return response
        
        # 从 headers 中获取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'code': 401, 'msg': '未提供认证信息'}, status=401)
        
        # 提取 token
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return JsonResponse({'code': 401, 'msg': '认证信息格式错误'}, status=401)
        
        # 验证 token
        payload = myjwt.decode(token)
        if not payload:
            return JsonResponse({'code': 401, 'msg': '无效的 token'}, status=401)
        
        # 设置 userid 到 request 对象
        request.userid = payload.get('user_id')
        request.username = payload.get('username')
        
        response = self.get_response(request)
        return response

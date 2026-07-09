from django.http import JsonResponse


def room_info(request, room_id):
    """获取直播间信息"""
    return JsonResponse({
        'code': 200,
        'data': {
            'room_id': room_id,
            'title': f'直播间 {room_id}',
            'teacher': '知学堂讲师',
            'status': 'live'
        }
    })

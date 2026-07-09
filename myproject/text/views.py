from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .ser import OrderDetailSerializer
# Create your views here.

# 用apiview实现课程详情接口 传入课程id 返回课程详情
class CourseView(APIView):
    def get(self, request, format=None):
        courseid = request.GET.get('courseid')
        course = Course.objects.filter(id=courseid).first()
        ser = CourseSerializer(course)
        return Response({'code': 200, 'data': ser.data})


from rest_framework import serializers
from .models import *


class MyCourseSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField(read_only=True)
    start_time = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    course_img = serializers.SerializerMethodField(read_only=True)
    expire_text = serializers.SerializerMethodField(read_only=True)
    
    def get_course_name(self, obj):
        return obj.course.title
    
    def get_start_time(self, obj):
        if obj.start_time is None:
            return ''
        return obj.start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_end_time(self, obj):
        if obj.end_time is None:
            return ''
        return obj.end_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_course_img(self, obj):
        if obj.course.image:
            return f'/upload/{obj.course.image}'
        return ''
    
    def get_expire_text(self, obj):
        if obj.course_type == 1:
            return '永久有效'
        elif obj.end_time:
            return f'有效期至 {obj.end_time.strftime("%Y-%m-%d")}'
        return '未知'
    
    class Meta:
        model = MyCourse
        fields = ('course_id','course_type','start_time','end_time','course_name', 'course_img', 'progress', 'status', 'expire_text')



class RefundSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = Refund
        fields = ('refund_id','status','order_no','tmoney')

class CommentSerializer(serializers.ModelSerializer):
    coursename = serializers.SerializerMethodField(read_only=True)
    def get_coursename(self, obj):
        return obj.course.title

    class Meta:
        model = Comment
        fields = ('course','content','star','avatar','username','coursename')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'










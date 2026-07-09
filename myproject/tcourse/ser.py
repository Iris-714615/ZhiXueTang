from rest_framework import serializers
from .models import *
from django.conf import settings
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    def get_children(self, obj):
        cate = Category.objects.filter(pid_id=obj.id).all()
        if cate:
            return CategorySerializer(cate, many=True).data
        else:
            return []
    class Meta:
        model = Category
        fields = ("id","name","children")

class NavcateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navcate
        fields = ("id","name","url")

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ("id","image","url")


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id","title","image","description")

class Cate1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id","name")

class Tag1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("title",)

class CoursesSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField(read_only=True)
    def get_tags(self, obj):
        tags = Tag1Serializer(obj.tags, many=True).data
        return tags
    
    level_name = serializers.SerializerMethodField(read_only=True)
    def get_level_name(self, obj):
        if obj.level == 1:
            return "初级"
        elif obj.level == 2:
            return "中级"
        elif obj.level == 3:
            return "专家"
        else:
            return "未知"
    class Meta:
        model = Courses
        fields = ("id","title","image","description","level_name","studentCount","price","discount","category","top_category","tags")


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ("id","avatar","role","name","title","description")
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id","title","orders","duration","link","is_free_trial","chapter")
class ChapterSerializer(serializers.ModelSerializer):
    lesson = serializers.SerializerMethodField(read_only=True)
    def get_lesson(self, obj):
        lesson1 = LessonSerializer(obj.lesson, many=True).data
        return lesson1
    class Meta:
        model = Chapter
        fields = ("id","title","number","summary","course","weight","lesson")

class CourseDetailSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField(read_only=True)
    def get_teacher(self, obj):
        teacher1 = TeacherSerializer(obj.teacher).data
        return teacher1
    chapter = serializers.SerializerMethodField(read_only=True)
    def get_chapter(self, obj):
        chapter1 = ChapterSerializer(obj.chapter, many=True).data
        return chapter1
    level_name = serializers.SerializerMethodField(read_only=True)
    def get_level_name(self, obj):
        if obj.level == 1:
            return "初级"
        elif obj.level == 2:
            return "中级"
        elif obj.level == 3:
            return "专家"
        else:
            return "未知"
  
    class Meta:
        model = Courses
        fields = ("id","title","image","description","level_name","studentCount","price","discount","category","teacher","lessons","click_count","is_free","chapter","pub_lessons","introduction","outcomes","audience")


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ("id","name",'minus')
from datetime import datetime,timedelta
class OrderDetailSerializer(serializers.ModelSerializer):
    expire_text = serializers.SerializerMethodField(read_only=True)
    course_name = serializers.SerializerMethodField(read_only=True)
    course_img = serializers.SerializerMethodField(read_only=True)
    course_id = serializers.SerializerMethodField(read_only=True)
    
    def get_expire_text(self, obj):
        if obj.valid_type == 1:
            return '永久有效'
        elif obj.valid_type == 2:
            expire_time = obj.create_time + timedelta(days=30)
            expire_time = expire_time.strftime("%Y-%m-%d")
            return f'有效期至 {expire_time}'
        elif obj.valid_type == 3:
            expire_time = obj.create_time + timedelta(days=365)
            expire_time = expire_time.strftime("%Y-%m-%d")
            return f'有效期至 {expire_time}'
        elif obj.valid_type == 4:
            expire_time = obj.create_time + timedelta(days=730)
            expire_time = expire_time.strftime("%Y-%m-%d")
            return f'有效期至 {expire_time}'
        else:
            return "未知"
    
    def get_course_id(self, obj):
        return obj.course
    
    def get_course_name(self, obj):
        try:
            course = Courses.objects.filter(id=obj.course).first()
            return course.title if course else ''
        except Exception:
            return ''
    
    def get_course_img(self, obj):
        try:
            course = Courses.objects.filter(id=obj.course).first()
            if course and course.image:
                return f'/upload/{course.image}'
            return ''
        except Exception:
            return ''
            
    class Meta:
        model = OrderDetail
        fields = ("price","valid_type","expire_text", 'course_name', 'course_img', 'course_id')

class UserOrderSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(many=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = UserOrder
        fields = ("order_number","create_time","status","actual_payment","total_amount","details","payment_method")

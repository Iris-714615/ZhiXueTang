from celery import Celery
from celery.schedules import crontab

# 创建celery对象
app = Celery('tasks', broker='redis://localhost:6379/6'
             , backend='redis://localhost:6379/7')

"""
这段代码用于配置Celery应用的序列化相关设置：
task_serializer='json'：设置任务序列化格式为JSON
accept_content=['json']：指定接受的内容类型为JSON
result_serializer='json'：设置结果序列化格式为JSON
enable_utc=True：启用UTC时区
主要功能是统一Celery任务的序列化方式，确保任务数据以JSON格式进行传输和存储。
"""
# 使用默认配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
)

# 配置定时任务
app.conf.beat_schedule = {
    "current_time": {
        "task": 'tasks.tasks.print_current_time',
        "schedule": crontab(minute='*'),  # 每分钟执行一次
    },
    # "remind_medicine": {
    #     "task": 'tasks.tasks.remind_medicine',
    #     "schedule": crontab(minute='*/2'),  # 每2分钟执行一次
    # }

}

# 配置时区
app.conf.timezone = 'Asia/Shanghai'
# 使tasks成为一个Python包
#from __future__ import absolute_import

# 导入Celery应用
from .celery import app as celery_app

# 导入任务模块，以便Celery可以发现任务
from . import tasks
#定义了包的公共接口
#删除会影响包的导入行为
#：all 是模块级别的特殊变量，用于定义 from package import * 的行为
__all__ = ['celery_app', 'tasks']
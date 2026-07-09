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

from django.urls import path
from django.contrib import admin
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('admin/', admin.site.urls),
    path("cate/", CategoryView.as_view()),
    path("nav/", NavcateView.as_view()),
    path("banner/", BannerView.as_view()),
    path("tags/", TagsView.as_view()),
    path("courses/", CoursesView.as_view()),
    path("recate/", RecommendCate.as_view()),
    path("allcate/", AllCategoryView.as_view()),
    path("allcourses/", AllCoursesView.as_view()),
    path("test/", TestView.as_view()),
    path("detail/<int:pk>", CourseDetailView.as_view()),

    # 购物车相关接口
    path("cart/", CartView.as_view()),
    path("cartdel/", CartDeleteView.as_view()),
    path("select/", CartSelectView.as_view()),
    path("toggle/", CartToggleView.as_view()),
    path("update-validity/", CartUpdateValidityView.as_view()),
    
    # 订单相关接口
    path("mycart/", MyCartView.as_view()),
    path("coupon/", CouponView.as_view()),
    path("orders/", OrdersView.as_view()),
    path("pay/", PayView.as_view()),
    # path("cancelorder/", CancelOrderView.as_view()),
    path("alipaycallback/", AliPayCallbackView.as_view()),
    path("testcelery/", TestCeleryView.as_view()),
    path("search/", SearchView.as_view()),


]

# 开发环境静态文件配置 ✅ 正确写法
if settings.DEBUG:
    # 媒体文件路由：映射 MEDIA_URL -> MEDIA_ROOT
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 静态文件路由（可选，开发环境默认已处理，补充更稳妥）
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

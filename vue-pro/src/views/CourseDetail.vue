<template>
  <div class="course-detail">
    <!-- 课程主体内容 -->
    <div class="course-container">
      <!-- 课程基本信息 -->
      <div class="course-info" >
        <div class="course-image">
          <img :src="config.baseUrl + course.image"  alt="课程封面">
        </div>
        <div class="course-summary">
          <h1 class="course-title">{{ course.title }}</h1>
          <div class="stats">
            <span class="stat-item"><i class="fas fa-user"></i>{{ course.studentCount }}人在学</span>
            <span class="stat-item"><i class="fas fa-list"></i>{{ course.lessons }}课时</span>
            <span class="stat-item"><i class="fas fa-clock"></i>总时长{{ course.lessons }}小时</span>
          </div>
          <div class="price-info">
            <span class="current-price">秒杀价{{ course.discount }}</span>
            <span class="original-price">{{ course.price }}原价</span>
          </div>
          <button class="buy-btn" @click="addToCart(course.id)">加入购物车</button>
        </div>
      </div>

      <!-- 讲师信息 -->
      <div class="teacher-info">
        <div class="avatar">
          <img :src="config.baseUrl + course.teacher?.avatar" alt="讲师头像">
        </div>
        <div class="teacher-detail">
          <h3 class="name">{{ course.teacher?.name }}</h3>
          <p class="title">{{ course.teacher?.title }}</p>
          <p class="description">{{ course.teacher?.description }}</p>
        </div>
      </div>

      <!-- 课程大纲 -->
      <div class="course-outline">
        <h2 class="section-title">课程大纲</h2>
        <div class="outline-content">
          <div class="chapter" v-for="c in course.chapter" :key="c.id">
            <div class="chapter-header">
              <h3>{{ c.title }}</h3>
              <span class="duration">共{{ c.lesson?.lesson || 0 }}课时</span>
            </div>
            <div class="lessons">
              <div class="lesson" v-for="l in c.lesson" :key="l.id">
                <span class="lesson-title">{{ l.title }}</span>
                <span class="lesson-duration">{{ l.duration }}分钟</span>
                <span class="free-tag" v-if="l.is_free_trial">{{ l.is_free_trial ? '免费' : '付费' }}</span>
              </div>
            
            </div>
          </div>
        </div>
      </div>

      <!-- 课程介绍 -->
      <div class="course-introduction">
        <h2 class="section-title">课程介绍</h2>
        <div class="introduction-content">
          <p>{{ course.introduction || '暂无介绍' }}</p>
         
        </div>
      </div>

      <!-- 课程收获 -->
      <div class="course-gains">
        <h2 class="section-title">课程收获</h2>
        <div class="gains-content">
          <ul>
            <li>{{ course.outcomes || '暂无信息' }}</li>
           
          </ul>
        </div>
      </div>

      <!-- 适合人群 -->
      <div class="suitable-for">
        <h2 class="section-title">适合人群</h2>
        <div class="suitable-content">
          <ul>
            <li>{{ course.audience || '暂无信息' }}</li>
            
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import config from '@/utils/config'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const course = ref({})
const getCourse = (id) => {
  console.log('获取课程详情,ID:', id)
  request({
    url: `tcourse/detail/${id}`,
    method: "GET",
  }).then(res => {
    console.log('响应数据:', res)
    if (res.data && res.data.code === 200) {
      course.value = res.data.data
      console.log('课程数据:', course.value)
    } else {
      console.error('响应格式错误:', res)
    }
  }).catch(err => {
    console.error('获取课程详情失败:', err)
  })
}

const addToCart = () => {
  var token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  request({
    url: "tcourse/cart/",
    method: "POST",
    data: {
      user_id: localStorage.getItem('user_id') || sessionStorage.getItem('user_id'),
      courseid: course.value.id,
  }, 
  }).then(res => {
    if (res.data && res.data.code === 200) {
      ElMessage.success(res.data.msg || '加入购物车成功')
    } else {
      ElMessage.error(res.data.msg || '加入购物车失败')
    }
  }).catch(err => {
    console.error('加入购物车失败:', err)
    ElMessage.error(err.response?.data?.msg || '加入购物车失败')
  })
}

onMounted(() => {
  
  getCourse(route.params.id)
})
</script>

<style scoped>
.course-detail {
  background-color: #f5f5f5;
  min-height: 100vh;
}

.course-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 课程基本信息样式 */
.course-info {
  display: flex;
  gap: 30px;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.course-image {
  flex: 0 0 400px;
}

.course-image img {
  width: 100%;
  border-radius: 8px;
}

.course-summary {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 24px;
  color: #333;
  margin: 0 0 20px;
}

.stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  color: #666;
  font-size: 14px;
}

.stat-item i {
  margin-right: 5px;
}

.price-info {
  margin-bottom: 20px;
}

.current-price {
  font-size: 28px;
  color: #ff5858;
  font-weight: bold;
  margin-right: 10px;
}

.original-price {
  color: #999;
  text-decoration: line-through;
  font-size: 16px;
}

.buy-btn {
  width: 180px;
  height: 48px;
  background: #ff5858;
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.buy-btn:hover {
  background: #ff4040;
}

/* 讲师信息样式 */
.teacher-info {
  display: flex;
  gap: 20px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.teacher-detail {
  flex: 1;
}

.teacher-detail .name {
  font-size: 18px;
  color: #333;
  margin: 0 0 5px;
}

.teacher-detail .title {
  color: #666;
  font-size: 14px;
  margin: 0 0 10px;
}

.teacher-detail .description {
  color: #999;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 课程大纲样式 */
.course-outline,
.course-introduction,
.course-gains,
.suitable-for {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  color: #333;
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.chapter {
  margin-bottom: 20px;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chapter-header h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.duration {
  color: #999;
  font-size: 14px;
}

.lessons {
  padding-left: 20px;
}

.lesson {
  display: flex;
  align-items: center;
  padding: 10px 0;
  color: #666;
  font-size: 14px;
}

.lesson-title {
  flex: 1;
}

.lesson-duration {
  color: #999;
  margin: 0 15px;
}

.free-tag {
  color: #52c41a;
  font-size: 12px;
  padding: 2px 6px;
  border: 1px solid #52c41a;
  border-radius: 4px;
}

/* 其他内容区域样式 */
.introduction-content,
.gains-content,
.suitable-content {
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  margin-bottom: 10px;
}
</style>
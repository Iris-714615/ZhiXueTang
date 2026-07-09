<template>
  <div class="pay-success-page">
    <div class="pay-success-container">
      <div class="success-card">
        <!-- 成功图标和消息 -->
        <div class="success-icon">
          <img src="../assets/empty.png" alt="success" class="success-img">
        </div>
        <div class="success-message">
          <h2>您已成功购买{{ orderDetail?.order_details?.length || 1 }}门课程！</h2>

        </div>

        <!-- 订单信息 -->
        <div class="order-details">
          <div class="detail-item">
            <span class="label">付款时间：</span>
            <span class="value">{{ formatDateTime(orderDetail?.pay_time) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">付款金额：</span>
            <span class="value">¥{{ orderDetail?.tmoney || '0.00' }}</span>
          </div>
        </div>

        <!-- 课程列表 -->
        <div class="courses-list">
          <div v-for="course in orderDetail?.order_details" :key="course.course.id" class="course-item">
            <img :src="config.baseUrl + course.course.course_img" :alt="course.course.name" class="course-img">
            <div class="course-info">
              <h3 class="course-name">{{ course.course.name }}</h3>
              <p class="course-brief">{{ course.course.brief }}</p>
              <div class="course-meta">
                <span class="teacher">讲师：{{ course.course.teacher.name }}</span>
                <span class="price">¥{{ course.price }}</span>
              </div>
              <div class="expire-info">
                <span>有效期：{{ course.expire_text }}</span>
                <span>到期时间：{{ formatDateTime(course.expire_time) }}</span>
              </div>
            </div>
            <!-- 按钮区域 -->
            <div class="action-area">
              <button class="study-btn" @click="goToStudy(course.course.id,orderDetail.order_number)">立即学习</button>
            </div>
          </div>
        </div>

        <!-- 微信提示区域 -->
        <div class="wechat-notice">
          <div class="notice-content">
            <img src="../assets/wechat.png" alt="wechat" class="wechat-icon">
            <p>重要！微信扫码关注获得学习通知及课程更新提醒！否则严重影响学习和课程体验！</p>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from "@/utils/request";
import config from "@/utils/config";

const router = useRouter()
const route = useRoute()
const orderDetail = ref({
  order_number: '',
  pay_time: '',
  tmoney: 0,
  order_details: [],
})
const orderno = ref('')



// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  const date = new Date(dateTimeStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}`
}

// 获取订单详情
const fetchOrderDetail = async () => {
  if (!orderno.value) {
    ElMessage.error('订单号不存在')
    return
  }
  try {
    const res = await request.get('tcourse/orders/',{
      params:{
        order_number:orderno.value
      }
    })
    if(res.data && res.data.orders){
      orderDetail.value = res.data.orders
    } 
    }catch(error){
      ElMessage.error(error.response?.data?.msg || "获取订单详情失败")
    }
}

const goToStudy = (courseId,order_number) => {

  router.push({
    path: '/course-study',
    query: {
      courseId: courseId,
      orderNumber:order_number
    }
  })
}

onMounted(() => {
  orderno.value = route.query.orderno || ''
  fetchOrderDetail()
})
</script>

<style scoped>
.pay-success-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.pay-success-container {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.success-card {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.success-icon {
  margin-bottom: 24px;
}

.success-img {
  width: 80px;
  height: 80px;
}

.success-message h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 16px;
}

.qq-group {
  font-size: 16px;
  color: #666;
}

.highlight {
  color: #1890ff;
  font-weight: bold;
}

.order-details {
  margin: 32px 0;
  background: #f8f9fa;
  padding: 24px;
  border-radius: 4px;
}

.detail-item {
  display: flex;
  padding: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

.detail-item .label {
  width: 100px;
  text-align: right;
  color: #666;
  padding-right: 16px;
}

.detail-item .value {
  flex: 1;
  text-align: left;
  color: #333;
}

/* 课程列表样式 */
.courses-list {
  margin: 32px 0;
}

.course-item {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: left;
}

.course-img {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
}

.course-info {
  flex: 1;
}

.course-name {
  font-size: 18px;
  color: #333;
  margin: 0 0 8px 0;
}

.course-brief {
  color: #666;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.teacher {
  color: #666;
  font-size: 14px;
}

.price {
  color: #ff6b6b;
  font-size: 16px;
  font-weight: bold;
}

.expire-info {
  color: #999;
  font-size: 12px;
  display: flex;
  gap: 16px;
}

.wechat-notice {
  margin: 32px 0;
  padding: 16px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 4px;
}

.notice-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.wechat-icon {
  width: 24px;
  height: 24px;
}

.notice-content p {
  color: #52c41a;
  margin: 0;
  text-align: left;
}

.action-area {
  margin-top: 32px;
}

.study-btn {
  padding: 12px 40px;
  font-size: 16px;
  color: #fff;
  background: #1890ff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.study-btn:hover {
  background: #40a9ff;
}

@media (max-width: 768px) {
  .pay-success-container {
    padding: 20px 10px;
  }

  .success-card {
    padding: 20px;
  }

  .detail-item {
    flex-direction: column;
  }

  .detail-item .label {
    width: 100%;
    text-align: left;
    padding-right: 0;
  }

  .course-item {
    flex-direction: column;
  }

  .course-img {
    width: 100%;
    height: 180px;
  }

  .notice-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
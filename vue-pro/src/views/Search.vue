<template>
  <div class="course-list-container">
    <!-- 课程卡片列表 -->
    <div class="course-grid">
      <div v-for="course in courses" :key="course.id" class="course-card">
        <!-- <img :src="course.course_img" :alt="course.name"> -->
        <div class="course-info">
          <h3>{{ course.name }}</h3>
          <!-- <p class="description">20</p>
          <div class="instructor">
            <span class="name">zs</span>
            <span class="title">一级</span> -->
          </div>
          <!-- <div class="stats">
            <span>100学习</span>
            <span>{{ course.lessons }}课时</span>
          </div> -->
          <div class="price-action">
            <!-- <span class="price" v-if="course.price > 0">¥{{ course.price }}</span>
            <span class="price free" v-else>免费</span> -->
            <button class="detail-btn" @click="detail(course)">查看详情</button>
          </div>
        </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="total > 0">
      <a href="#" class="page-btn" @click.prevent="handlePageChange(1)">首页</a>
      <a href="#" class="page-btn" @click.prevent="handlePageChange(currentPage - 1)"
         :class="{ disabled: currentPage === 1 }">上一页</a>
      <span class="page-number">{{ currentPage }} / {{ totalPages }}</span>
      <a href="#" class="page-btn" @click.prevent="handlePageChange(currentPage + 1)"
         :class="{ disabled: currentPage === totalPages }">下一页</a>
      <a href="#" class="page-btn" @click.prevent="handlePageChange(totalPages)">末页</a>
    </div>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import request from '../utils/request'

import {useRouter, useRoute} from "vue-router";

const total = ref(0)

const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = ref(2)

// const selectedCategory = ref('全部')
// const selectedSort = ref('默认排序')
// const selectedPrice = ref('全部')


const route = useRoute()

const courses = ref([{"name":"java"}])


/**
 * 获取课程数据
 * 
 * 该函数根据当前路由参数和分页信息，向后端请求课程列表数据。
 * 请求成功后更新课程列表、总数量以及总页数。
 */
const nav_name = ref('')
const fetchCourses = () => {
  nav_name.value = route.query.name
  request.get('tcourse/search/',{
    params:{
      name: nav_name.value,
      page: currentPage.value,
      size: pageSize.value,
    }
  }).then(res => {
    if (res.data.code == 200) {
      courses.value = res.data.data
      total.value = res.data.total
      totalPages.value = Math.ceil(total.value / pageSize.value)
    }
  }).catch(err => {
    console.log(err)
  })
}

/**
 * 处理分页切换
 * 
 * @param {number} page - 要跳转的目标页码
 * 
 * 该函数用于处理用户点击分页按钮时的逻辑，包括边界判断和页面跳转。
 */
const handlePageChange = (page) => {

  if (page < 1 || page > totalPages.value || page == currentPage.value) return
  currentPage.value = page
  fetchCourses()
}

/**
 * 组件挂载完成后执行的初始化操作
 * 
 * 在组件加载完成后调用 fetchCourses 函数获取初始课程数据。
 */
const detail = (course) => {
  var types = course.types
  var id = course.id
  if (types == 'course') {
    window.location.href = '/courses/' + id
  }
  else if (types == 'comment') {
    window.location.href = '/comments/' + id
  }
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.course-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.filter-section {
  background: #fff;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  line-height: 32px;
}

.filter-item:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
  margin-right: 10px;
  min-width: 70px;
  text-align: right;
  flex-shrink: 0;
}

.options {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.options a {
  color: #333;
  text-decoration: none;
  margin-right: 20px;
  padding: 2px 8px;
  border-radius: 2px;
  margin-bottom: 5px;
}

.options a:hover {
  color: #ff6b00;
}

.options a.active {
  color: #ff6b00;
  font-weight: 500;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.course-card {
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
  transition: transform 0.3s;
  width: 100%;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.course-card img {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.course-info {
  padding: 15px;
}

.course-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #333;
}

.description {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
  height: 40px;
  overflow: hidden;
}

.instructor {
  margin-bottom: 10px;
}

.instructor .name {
  font-weight: bold;
  color: #333;
  margin-right: 10px;
}

.instructor .title {
  color: #666;
  font-size: 12px;
}

.stats {
  color: #999;
  font-size: 12px;
  margin-bottom: 10px;
}

.stats span {
  margin-right: 15px;
}

.price-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  color: #ff6b00;
  font-size: 18px;
  font-weight: bold;
}

.price.free {
  color: #52c41a;
}

.add-to-cart {
  background: #ff6b00;
  color: white;
  border: none;
  padding: 6px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.add-to-cart:hover {
  background: #ff8533;
}

.pagination {
  text-align: center;
  margin-top: 20px;
}

.page-btn {
  display: inline-block;
  padding: 5px 10px;
  margin: 0 5px;
  color: #666;
  text-decoration: none;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.page-btn:hover {
  color: #ff6b00;
  border-color: #ff6b00;
}

.page-number {
  margin: 0 10px;
  color: #666;
}

.jump {
  margin-left: 15px;
}

.price-info {
  display: flex;
  flex-direction: column;
}

.original-price {
  color: #999;
  font-size: 12px;
  text-decoration: line-through;
}

.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.disabled:hover {
  color: #666;
  border-color: #d9d9d9;
}
</style>
<template>
  <div class="course-list-container">
    <!-- 课程筛选区域 -->
    <div class="filter-section">
      <!-- 分类筛选 -->
      <div class="filter-item">
        <span class="label">课程分类：</span>
        <div class="options">
          <a href="#" :class="{ active: selectedCategory === 'all' }" @click="changeCategory('all')">全部</a>
          <a href="#" :class="{ active: selectedCategory === item.id }"
             @click="changeCategory(item.id)" v-for="item in allcate" :key="item.id">{{item.name}}</a>
        </div>
      </div>

      <!-- 排序方式筛选 -->
      <div class="filter-item">
        <span class="label">排序方式：</span>
        <div class="options">
          <a href="#" :class="{ active: selectedSort === '-studentCount' }" @click="changeSort1('-studentCount')">默认排序</a>
          <a href="#" :class="{ active: selectedSort === 'create_time' }" @click="changeSort1('create_time')">最新</a>
          <a href="#" :class="{ active: selectedSort === 'click_count' }" @click="changeSort1('click_count')">最热</a> 
          <a href="#" :class="{ active: selectedSort === 'discount' }" @click="changeSort1('discount')">价格</a>
        </div>
      </div>

      <!-- 价格区间筛选 -->
      <div class="filter-item">
        <span class="label">价格区间：</span>
        <div class="options">
          <a href="#" :class="{ active: selectedPrice === 'all' }" @click="changePrice('all')">全部</a>
          <a href="#" :class="{ active: selectedPrice === 'True' }" @click="changePrice('True')">免费</a>
          <a href="#" :class="{ active: selectedPrice === 'False' }" @click="changePrice('False')">付费</a>
        </div>
      </div>
    </div>

    <!-- 课程卡片列表 -->
    <div class="course-grid">
      <div v-for="course in courses" :key="course.id" class="course-card">
        <img :src="config.baseUrl+course.image" :alt="course.title">
        <div class="course-info">
          <h3>{{ course.title }}</h3>
          <p class="description">{{ course.description }}</p>
          <div class="instructor">
            <span class="name">{{ course.title }}</span>
            <span class="title">{{ course.level }}</span>
          </div>
          <div class="stats">
            <span>{{ course.studentCount }}学习</span>
            <span>{{ course.lessons }}课时</span>
          </div>
          <div class="price-action">
            <span class="price" v-if="course.price > 0">¥{{ course.price }}</span>
            <span class="price free" v-if="course.price == 0">免费</span>
            <button class="add-to-cart">加入购物车</button>
          </div>
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
import request from '@/utils/request'
import {useRouter, useRoute} from "vue-router";
import config from '@/utils/config'

const total = ref(0)

const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = ref(10)

const selectedCategory = ref("all")
const selectedSort = ref('-studentCount')
const selectedPrice = ref("all")


const route = useRoute()
const top_category = ref(0)
top_category.value =route.query.top_category
selectedCategory.value = top_category.value ? top_category.value : "all"



const courses = ref([])
const allcate = ref([])
const fetchAllCate = ()=>{
 request.get('tcourse/allcate/').then(res => {
      allcate.value = res.data.data      
})
}
const changeSort1 = (sort)=>{
  selectedSort.value = sort
  currentPage.value = 1
  fetchCourses()
}
const changePrice = (price)=>{
  selectedPrice.value = price
  currentPage.value = 1
  fetchCourses()
}
const changeCategory = (cateid)=>{
  selectedCategory.value = cateid
  currentPage.value = 1
  fetchCourses()
}

/**
 * 获取课程数据
 * 
 * 该函数根据当前路由参数和分页信息，向后端请求课程列表数据。
 * 请求成功后更新课程列表、总数量以及总页数。
 */
const fetchCourses = () => { 
  request.get('tcourse/allcourses/',{
    params: {
      page: currentPage.value,
      page_size: pageSize.value,
      top_category: selectedCategory.value,
      order: selectedSort.value,
      feetype: selectedPrice.value
    }
  }).then(res => {
      courses.value = res.data.data
      total.value = res.data.count

      totalPages.value = Math.ceil(total.value / pageSize.value)
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
onMounted(() => {
  fetchCourses()
  fetchAllCate()

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
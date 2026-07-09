<template>
  <div class="cart-container">
    <div class="cart-content">
      <div class="cart-title">
        <h2>我的购物车</h2>
        <span class="course-count">共{{ cartCourses.length }}门课程</span>
      </div>

      <div class="cart-table">
        <div class="table-header">
          <div class="checkbox-col">
            <input type="checkbox" v-model="selectAll" @change="handleSelectAll">
            全选
          </div>
          <div class="course-col">课程</div>
          <div class="validity-col">有效期</div>
          <div class="price-col">单价</div>
          <div class="operation-col">操作</div>
        </div>

        <div class="table-body">
          <div v-for="(course, index) in cartCourses" :key="index" class="table-row">

            <div class="checkbox-col">
              <input type="checkbox" v-model="course.is_check" @change="toggleCourse(index)">
            </div>
            <div class="course-col">
              <img :src="config.baseUrl + course.image" >
              <span class="course-title">{{ course.title }}</span>
            </div>

            <div class="validity-col">
              <select v-model="course.type" @change="updateCoursePrice(course, course.type)">
                <option v-for="item in course.pricelist" :key="item.types" :value="item.types">{{ item.name }}</option>
              </select>
            </div>
            <div class="price-col">¥{{ course.price }}</div>
            <div class="operation-col">
              <button @click="removeCourse(index)" class="delete-btn">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div class="cart-footer">
        <div class="left-operations">
          <button class="inverse-select" @click="inverseSelect">反选</button>
          <button class="batch-delete" @click="batchDelete">批量删除</button>
        </div>
        <div class="right-summary">
          <span class="total-label">合计：</span>
          <span class="total-price">¥{{ totalPrice }}</span>
          <a href="checkout"><button class="checkout-btn">去结算 ({{ selectedCount }})</button></a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, watch} from 'vue'
import {useRouter} from 'vue-router'
import axios from 'axios'
import {ElMessage} from 'element-plus'
import request from '@/utils/request'
import config from '@/utils/config'

const router = useRouter()
const selectAll = ref(false)
const cartCourses = ref([])

const courseExpireInfo = ref({})

const inverseSelect = async () => {
  const courseIds = cartCourses.value.map(course => course.id)
  if (courseIds.length == 0) {
    ElMessage.warning('请选择要操作的课程')
    return
  }
  await toggleCartItems(courseIds)
}

const toggleCourse = async (index) => {
  const courseId = cartCourses.value[index].id
  const course_ids = parseInt(courseId)
  await toggleCartItems(course_ids)
}

// 反选商品
const toggleCartItems = async (courseids) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  request.post('tcourse/toggle/',{
    user_id: localStorage.getItem('user_id'),
    courseids: courseids  
  }).then(res =>{
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '操作成功')
      fetchCartData(token)
    }     
  })
 }

const updateCoursePrice = async (course, validity) => {
  course.pricelist.forEach(item => {
    if (item.types === validity) {
      course.price = item.price
    }
  })
  request.post('tcourse/update-validity/',{
    user_id: localStorage.getItem('user_id'),
    courseid: course.id,
    type: validity,  
  }).then(res =>{
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '更新成功')
      // fetchCartData(token)
    } 
    
  })
}

// 获取购物车数据
const fetchCartData = async (token) => {
  request.get('tcourse/cart/?user_id=' + localStorage.getItem('user_id'))
  .then(res =>{
    cartCourses.value = res.data.data
    cartCourses.value.forEach(course => {
      course.is_check = course.is_check === 1 ? true : false
    })
  }).catch(err =>{
    ElMessage.error(err.response?.data?.msg || '获取购物车数据失败')
  })
}


const fetchCourseEporeInfo = async (courseIds) => {
  if (!courseIds || courseIds.length === 0) return
  
  try {
    const res = await axios.get("http://127.0.0.1:8000/courses/expire/?course_ids=" + courseIds.join(','))
    if (res.data.code === 200) {
      courseExpireInfo.value = res.data.data
      // 更新购物车中的课程有效期选项和价格
      cartCourses.value = cartCourses.value.map(course => {
        const expireInfo = courseExpireInfo.value[course.id]
        if (expireInfo) {
          const expireList = expireInfo.expire_list
          return {
            ...course,
            expireOptions: expireList.map(item => ({
              value: item.expire_time,
              label: item.expire_text,
              price: item.price
            })),
            // 根据当前buy_type选择对应的选项
            validity: course.validity || expireList[0].expire_time,
            price: expireList.find(item => item.expire_time === course.validity)?.price || expireList[0].price
          }
        }
        return course
      })
    }
  } catch (error) {
    console.error('获取有效期信息失败', error)
  }
}

// 初始化购物车数据
const initCart =  () => {
  var token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
   fetchCartData(token)
}

// 计算属性
const selectedCount = computed(() => {
  return cartCourses.value.filter(course => course.is_check).length
})

const totalPrice = computed(() => {
  return cartCourses.value
      .filter(course => course.is_check)
      .reduce((sum, course) => sum + Number(course.price), 0)
      .toFixed(2)
})

// 方法
const handleSelectAll = async () => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
request.post('tcourse/select/',{
    is_check: selectAll.value ? 1 : 0,
    user_id: localStorage.getItem('user_id')
  }).then(res =>{
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '操作成功')
      fetchCartData(token)
    } else {
      ElMessage.error(res.data.msg || '操作失败')
      selectAll.value = !selectAll.value
    }
  }).catch(err =>{
    ElMessage.error(err.response?.data?.msg || '操作失败')
  })
}


// 删除购物车商品
const deleteCartItems = async (courseids) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  request.post('tcourse/cartdel/',{
    courseids: courseids,
    user_id: localStorage.getItem('user_id')
  }).then(res =>{
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '删除成功')
      fetchCartData(token)
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  }).catch(err =>{
    ElMessage.error(err.response?.data?.msg || '删除失败，请稍后重试')
  })
  
}

// 删除单个商品
const removeCourse = async (index) => {
  const courseId = cartCourses.value[index].id

  console.log(courseId)
  console.log(typeof courseId)
  //把string类型转化成int
  const course_id = parseInt(courseId)
  console.log(course_id)
  console.log(typeof course_id)
  await deleteCartItems(course_id)
}

// 批量删除选中的商品
const batchDelete = async () => {
  const selectedCourseIds = cartCourses.value
      .filter(course => course.is_check)
      .map(course => course.id)

  if (selectedCourseIds.length === 0) {
    ElMessage.warning('请先选择要删除的商品')
    return
  }

  await deleteCartItems(selectedCourseIds)
}

// 组件挂载时获取购物车数据
onMounted(() => {
  initCart()
})

// 监听全选状态变化
watch(cartCourses, () => {
  // 当所有商品都被选中时，自动设置全选状态为true
  selectAll.value = cartCourses.value.length > 0 && cartCourses.value.every(course => course.is_check)
}, {deep: true})
</script>

<style scoped>
.cart-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.cart-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.cart-title {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.cart-title h2 {
  font-size: 24px;
  margin-right: 10px;
}

.course-count {
  color: #666;
}

.cart-table {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: grid;
  grid-template-columns: 100px 1fr 200px 150px 100px;
  padding: 15px;
  background: #f7f7f7;
  border-bottom: 1px solid #e8e8e8;
}

.table-row {
  display: grid;
  grid-template-columns: 100px 1fr 200px 150px 100px;
  padding: 15px;
  align-items: center;
  border-bottom: 1px solid #e8e8e8;
}

.course-col {
  display: flex;
  align-items: center;
}

.course-col img {
  width: 120px;
  height: 80px;
  object-fit: cover;
  margin-right: 15px;
  border-radius: 4px;
}

.course-title {
  font-size: 16px;
  color: #333;
}

select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 120px;
}

.price-col {
  color: #ff6b00;
  font-weight: bold;
}

.delete-btn {
  color: #666;
  background: none;
  border: none;
  cursor: pointer;
}

.delete-btn:hover {
  color: #ff4d4f;
}

.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  margin-top: 20px;
  border-radius: 4px;
}

.left-operations button {
  margin-right: 15px;
  padding: 8px 15px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.total-label {
  margin-right: 10px;
}

.total-price {
  color: #ff6b00;
  font-size: 20px;
  font-weight: bold;
  margin-right: 20px;
}

.checkout-btn {
  padding: 10px 30px;
  background: #ff6b00;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.checkout-btn:hover {
  background: #ff7b00;
}
</style>

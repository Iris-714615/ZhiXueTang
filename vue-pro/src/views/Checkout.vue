<template>
  <div class="checkout-container">
    <div class="checkout-content">
      <h2 class="checkout-title">确认订单</h2>

      <!-- 课程信息 -->
      <div class="course-info">
        <div class="course-item" v-for="course in courseList" :key="course.id">
          <img :src="config.baseUrl + course.image" :alt="course.name" class="course-image">
          <div class="course-detail">
            <h3>{{ course.name }}</h3>
            <p class="validity">有效期：{{ course.expdate }}</p>
          </div>
          <div class="course-price">¥{{ course.price }}</div>
        </div>
      </div>

      <!-- 支付方式 -->
      <div class="payment-method">
        <h3>支付方式</h3>
        <div class="payment-options">
          <label class="payment-option">
            <input type="radio" v-model="paymentMethod" value="alipay">
            <img src="../assets/alipay.png" alt="支付宝" class="payment-icon">
            <span>支付宝</span>
          </label>
          <label class="payment-option">
            <input type="radio" v-model="paymentMethod" value="wechat">
            <img src="../assets/wechat.png" alt="微信支付" class="payment-icon">
            <span>微信支付</span>
          </label>
        </div>
      </div>

      <!-- 优惠券 -->
      <div class="coupon-section">
        <h3>优惠券</h3>
        <select v-model="selectedCoupon" class="coupon-select" @change="handleCouponChange">
          <option value="">不使用优惠券</option>
          <option v-for="coupon in coupons" :key="coupon.id" :value="coupon.id">
            {{ coupon.name }}
          </option>
        </select>
      </div>

      <!-- 价格信息 -->
      <div class="price-summary">
        <div class="price-item">
          <span>商品总额</span>
          <span class="amount">¥{{ totalPrice }}</span>
        </div>
        <div class="price-item">
          <span>优惠券</span>
          <span class="discount">-¥{{ couponAmount }}</span>
        </div>
        <div class="price-item total">
          <span>实付金额</span>
          <span class="final-price">¥{{ finalPrice }}</span>
        </div>
      </div>

      <!-- 服务协议 -->
      <div class="agreement">
        <label>
          <input type="checkbox" v-model="agreementChecked">
          <span>我已阅读并同意</span>
          <a href="#" class="agreement-link">《服务协议》</a>
        </label>
      </div>

      <!-- 支付按钮 -->
      <div class="checkout-action">
        <button
          class="pay-button"
          :disabled="!agreementChecked || !paymentMethod"
          @click="handlePayment"
        >
          立即支付
        </button>
      </div>
    </div>


    <WxPayModal
        v-model:visible="showWXPayModal"
        :payUrl="wxPayUrl"
        :totalFee="total_fee"/>
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import {useRouter, useRoute} from "vue-router";
import {ElMessage} from "element-plus";
import request from "@/utils/request";
import config from "@/utils/config"


const router = useRouter()
const route = useRoute()

const showWXPayModal = ref(false)

const wxPayUrl = ref('')

const orderNumber = ref('')

const total_fee = ref(0)

const totalPrice = ref(0)

const courseList = ref([])

// 课程信息
const course = ref({
  name: 'Python全栈开发工程师',
  image: 'https://img30.360buyimg.com/jdcms/s480x480_jfs/t1/305399/38/704/166022/68201216Ff6510ba5/919edbaa90b03b77.jpg.avif',
  validity: '永久有效',
  price: 2999.00
})

// 支付方式
const paymentMethod = ref('alipay')

// 优惠券
const coupons = ref([])
const selectedCoupon = ref('')
const couponAmount = ref(0)

// 最终价格
const finalPrice = computed(() => {
  return (totalPrice.value - couponAmount.value).toFixed(2)
})

// 服务协议
const agreementChecked = ref(false)

// 建议放在模块顶部（组件外部作用域），保证一次“下单尝试”期间可复用同一个幂等键
let currentIdempotencyKey = null;

function generateIdempotencyKey() {
  if (window.crypto && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'key-' + Math.random().toString(36).slice(2) + Date.now();
}

function sleep(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

// /**
//  * 思路讲解
//  * 生成并复用幂等键：一次点击“提交订单”开始到结束，始终用同一个 Idempotency-Key；这样重试/刷新 token 都不会产生新订单。
//  * 429 重试策略：服务端提示“正在创建”时，用指数退避重试，减少无意义压力，同时等待缓存命中返回首次结果。
//  * 401 刷新：刷新 token 后继续调用同一次下单，依然使用同一个幂等键，确保不会重复创建。
//  * 参数规范：use_coupon 改为布尔值，price/total_price 强制转数值；后端也会校验价格与课程状态。
//  * 错误处理：尽量给出清晰的用户提示；登录过期引导到登录页。
//  * 这样改完后，你的前端即可与后端“幂等 + 分布式锁 + DB 兜底”的设计配合良好，避免重复下单且更健壮地处理网络/服务端波动。
  // @returns {Promise<void>}
 
// 优惠券选择
const handleCouponChange =  () => {
  const selectd = selectedCoupon.value
  if (selectd) {
    const coupon = coupons.value.find(c => c.id == selectd)
    if (coupon) {
      couponAmount.value = coupon.minus
    }
  } else {
    couponAmount.value = 0
  }
};
const pay = async(orderid) => {
  request.post("tcourse/pay/", {
    "orderno": orderid
  }).then(res => {
    if(res.data.code == 200){
      var pay_url = res.data.pay_url
      window.location.href = pay_url
    }
  }).catch(err => {
    ElMessage.error(err.data.message || "支付失败")
  })
  
}
const handlePayment = async () => {
  if (!agreementChecked.value) {
    ElMessage.warning('请先同意服务协议')
    return
  }
  if (!paymentMethod.value) {
    ElMessage.warning('请选择支付方式')
    return
  }
  // TODO: 实现支付逻辑
  const token = localStorage.getItem("token") || sessionStorage.getItem("token")
  if (!token) {
    ElMessage.warning("请先登录")
    router.push("/login")
    return
  }
  request.post("tcourse/orders/", {
    user_id: parseInt(localStorage.getItem('user_id')),
    couponid:selectedCoupon.value,
    pay_type:paymentMethod.value == 'alipay' ? 1 : 2,
  }).then(res => {
    if(res.data.code == 200){
      ElMessage.success("订单创建成功，支付中...")
      var orderid = res.data.orderno
      pay(orderid)
    }
  // }).catch(err => {
  //   ElMessage.error(err.data.msg || "订单创建失败")
  })
}

const fetchCouponList = (totalPrice) => {
  request.get('tcourse/coupon/?tmoney='+totalPrice).then(res => {
    coupons.value = res.data.data
   
  }).catch(err => {
    console.error('获取优惠券列表失败:', err)
  })
}

const fetchCartData =  () => {
 request.get('tcourse/mycart/?user_id='+localStorage.getItem('user_id')).then(res => {
  courseList.value = res.data.data.map(item => ({
    ...item,
    name: item.title,
    expdate: item.expname || '1个月'
  }))
  totalPrice.value = res.data.total_price
  fetchCouponList(totalPrice.value)
  }).catch(err => {
    console.error('获取购物车数据失败:', err)
  })
}


const initCheckOut =  () => {
  // const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  // if (!token) {
  //   ElMessage.warning('请先登录')
  //   router.push('/login')
  //   return
  // }

  fetchCartData()

}

onMounted(() => {
 
  initCheckOut()
  
})
</script>

<style scoped>
.checkout-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.checkout-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.checkout-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
}

.course-info {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 20px;
}

.course-image {
  width: 120px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}

.course-detail h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #333;
}

.validity {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.course-price {
  margin-left: auto;
  color: #ff6b00;
  font-size: 18px;
  font-weight: bold;
}

.payment-method {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.payment-method h3 {
  margin: 0 0 15px;
  font-size: 16px;
  color: #333;
}

.payment-options {
  display: flex;
  gap: 20px;
}

.payment-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
}

.payment-option:hover {
  border-color: #ff6b00;
}

.payment-icon {
  width: 24px;
  height: 24px;
}

.coupon-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.coupon-section h3 {
  margin: 0 0 15px;
  font-size: 16px;
  color: #333;
}

.coupon-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
}

.price-summary {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #666;
}

.price-item.total {
  border-top: 1px solid #e8e8e8;
  padding-top: 10px;
  margin-top: 10px;
  color: #333;
}

.amount {
  color: #333;
}

.discount {
  color: #52c41a;
}

.final-price {
  color: #ff6b00;
  font-size: 20px;
  font-weight: bold;
}

.agreement {
  text-align: center;
  margin-bottom: 20px;
}

.agreement-link {
  color: #1890ff;
  text-decoration: none;
}

.agreement-link:hover {
  text-decoration: underline;
}

.checkout-action {
  text-align: center;
}

.pay-button {
  padding: 12px 40px;
  font-size: 16px;
  color: #fff;
  background: #ff6b00;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s;
}

.pay-button:hover {
  background: #ff7b00;
}

.pay-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
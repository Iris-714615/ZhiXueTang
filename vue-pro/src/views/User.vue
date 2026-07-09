<script setup>
import { ref, onMounted, watch } from 'vue';
import request from '@/utils/request';
import config from '@/utils/config';
// 用户信息
const userInfo = ref({
  name: "",
  avatar: "",
  email: "",
  phone: "",
  memberLevel: "普通会员",
  memberExpiry: ""
});

// 我的课程相关
const myCourseList = ref([]);
const courseLoading = ref(false);

// 订单相关
const orderList = ref([]);
const orderLoading = ref(false);

// 密码修改相关
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 评价相关
const commentDialogVisible = ref(false);
const commentForm = ref({
  courseId: '',
  content: '',
  star: 5
});

// 充值相关
const accountBalance = ref(0);
const rechargeAmount = ref(100);
const giveAmount = ref(0);
const rechargeOptions = [
  { value: 100, label: '100元' },
  { value: 200, label: '200元' },
  { value: 500, label: '500元' },
  { value: 1000, label: '1000元' }
];

// 获取账户余额
const fetchAccountBalance = async () => {
  const user_id = getUserId();
  if (!user_id) return;
  try {
    const res = await request.get('euser/userinfo/', {
      params: { user_id: user_id }
    });
    if (res.data.code === 200) {
      accountBalance.value = res.data.data.account;
    }
  } catch (error) {
    console.error('获取账户余额失败:', error);
  }
};

// 充值
const recharge = async () => {
  const user_id = getUserId();
  if (!user_id) {
    alert('请先登录');
    return;
  }
  try {
    const res = await request.post('euser/recharge/', {
      user_id: user_id,
      amount: rechargeAmount.value,
      pay_type: 1 // 支付宝
    });
    if (res.data.code === 200) {
      window.open(res.data.pay_url, '_blank');
      alert('正在跳转到支付页面...');
    } else {
      alert(res.data.msg || '充值失败');
    }
  } catch (error) {
    console.error('充值失败:', error);
    alert('充值失败');
  }
};

// 监听充值金额变化，获取优惠信息
watch(rechargeAmount, async (newAmount) => {
  try {
    const res = await request.get('euser/rechargeactivity/', {
      params: { amount: newAmount }
    });
    if (res.data.code === 200 && res.data.data) {
      giveAmount.value = res.data.data.give_amount || 0;
    } else {
      giveAmount.value = 0;
    }
  } catch (error) {
    console.error('获取优惠信息失败:', error);
    giveAmount.value = 0;
  }
});

// 获取用户ID
const getUserId = () => {
  return localStorage.getItem('user_id');
};

// 获取token
const getToken = () => {
  return localStorage.getItem('token');
};

// 获取用户信息
const fetchUserInfo = () => {
  const username = localStorage.getItem('username');
  const phone = localStorage.getItem('phone');
  if (username) {
    userInfo.value.name = username;
  }
  if (phone) {
    userInfo.value.phone = phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  }
};

// 获取我的课程列表
const fetchMyCourses = async (types = 1) => {
  const user_id = getUserId();
  if (!user_id) {
    alert('请先登录');
    return;
  }
  
  courseLoading.value = true;
  try {
    const res = await request.get('euser/mycourse/', {
      params: {
        user_id: user_id,
        types: types,
        page: 1,
        page_size: 10
      }
    });
    if (res.data.code === 200) {
      myCourseList.value = res.data.data || [];
    } else {
      alert(res.data.msg || '获取课程列表失败');
    }
  } catch (error) {
    console.error('获取课程列表失败:', error);
    alert('获取课程列表失败');
  } finally {
    courseLoading.value = false;
  }
};

// 订单状态映射
const statusMap = {
  1: { text: '待支付', color: 'orange' },
  2: { text: '已支付', color: 'green' },
  3: { text: '已评价', color: 'blue' },
  4: { text: '已完成', color: 'gray' },
  5: { text: '已取消', color: 'red' },
  6: { text: '退款中', color: 'orange' },
  7: { text: '已退款', color: 'purple' }
};

// 获取订单列表
const fetchOrders = async (submenuId = 21) => {
  const user_id = getUserId();
  if (!user_id) {
    alert('请先登录');
    return;
  }
  
  let status = '';
  if (submenuId === 21) {
    status = '1'; // 待支付
  } else if (submenuId === 22) {
    status = '2'; // 已支付
  }
  
  orderLoading.value = true;
  try {
    const res = await request.get('euser/myorder/', {
      params: {
        user_id: user_id,
        types: status,
        page: 1,
        page_size: 10
      }
    });
    if (res.data.code === 200) {
      let data = res.data.data || [];
      // 如果是退款/售后标签，过滤出退款相关状态
      if (submenuId === 23) {
        data = data.filter(order => order.status === 6 || order.status === 7);
      }
      orderList.value = data;
    } else {
      alert(res.data.msg || '获取订单列表失败');
    }
  } catch (error) {
    console.error('获取订单列表失败:', error);
    alert('获取订单列表失败');
  } finally {
    orderLoading.value = false;
  }
};

// 支付订单
const payOrder = async (orderNumber) => {
  try {
    const res = await request.post('tcourse/pay/', {
      orderno: orderNumber
    });
    if (res.data.code === 200) {
      window.open(res.data.pay_url, '_blank');
      alert('正在跳转到支付页面...');
    } else {
      alert(res.data.msg || '支付失败');
    }
  } catch (error) {
    console.error('支付失败:', error);
    alert('支付失败');
  }
};

// 取消订单
const cancelOrder = async (orderNumber) => {
  if (!confirm('确定要取消这个订单吗？')) {
    return;
  }
  try {
    const res = await request.post('euser/cancelorder/', {
      orderno: orderNumber
    });
    if (res.data.code === 200) {
      alert('订单已取消');
      fetchOrders(activeSubmenu.value);
    } else {
      alert(res.data.msg || '取消订单失败');
    }
  } catch (error) {
    console.error('取消订单失败:', error);
    alert('取消订单失败');
  }
};

// 申请退款
const applyRefund = async (orderNumber) => {
  if (!confirm('确定要申请退款吗？')) {
    return;
  }
  const user_id = getUserId();
  try {
    const res = await request.post('euser/refund/', {
      user_id: user_id,
      orderno: orderNumber
    });
    if (res.data.code === 200) {
      alert('退款成功');
      fetchOrders(activeSubmenu.value);
    } else {
      alert(res.data.msg || '退款失败');
    }
  } catch (error) {
    console.error('退款失败:', error);
    alert('退款失败，请稍后重试');
  }
};

const openCommentDialog = (courseId) => {
  commentForm.value.courseId = courseId;
  commentForm.value.content = '';
  commentForm.value.star = 5;
  commentDialogVisible.value = true;
};

const submitComment = async () => {
  if (!commentForm.value.content) {
    alert('请输入评价内容');
    return;
  }
  const user_id = getUserId();
  try {
    const res = await request.post('euser/comment/', {
      user_id: user_id,
      course_id: commentForm.value.courseId,
      content: commentForm.value.content,
      star: commentForm.value.star
    });
    if (res.data.code === 200) {
      alert('评价成功');
      commentDialogVisible.value = false;
    } else {
      alert(res.data.msg || '评价失败');
    }
  } catch (error) {
    console.error('评价失败:', error);
    alert('评价失败');
  }
};

// 修改密码
const updatePassword = async () => {
  if (!passwordForm.value.oldPassword) {
    alert('请输入当前密码');
    return;
  }
  if (!passwordForm.value.newPassword) {
    alert('请输入新密码');
    return;
  }
  if (passwordForm.value.newPassword.length < 6) {
    alert('新密码长度不能少于6位');
    return;
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    alert('两次输入的密码不一致');
    return;
  }
  
  const token = getToken();
  if (!token) {
    alert('请先登录');
    return;
  }
  
  try {
    const res = await request.post('euser/update_password/', {
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    }, {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });
    if (res.data.code === 200) {
      alert('密码修改成功，请重新登录');
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      localStorage.clear();
      window.location.href = '/login';
    } else {
      alert(res.data.msg || '密码修改失败');
    }
  } catch (error) {
    console.error('密码修改失败:', error);
    alert('密码修改失败');
  }
};

// 菜单相关
const menuItems = ref([
  {
    id: 1,
    title: "我的课程",
    icon: "fas fa-graduation-cap",
    submenu: [
      { id: 1, title: "学习中", path: "#" },
      { id: 2, title: "已完成", path: "#" },
      { id: 3, title: "收藏", path: "#" }
    ]
  },
  {
    id: 2,
    title: "我的订单",
    icon: "fas fa-shopping-cart",
    submenu: [
      { id: 21, title: "待支付", path: "#" },
      { id: 22, title: "已支付", path: "#" },
      { id: 23, title: "退款/售后", path: "#" }
    ]
  },
  {
    id: 3,
    title: "账户设置",
    icon: "fas fa-cog",
    submenu: [
      { id: 31, title: "个人信息", path: "#" },
      { id: 32, title: "密码修改", path: "#" },
      { id: 33, title: "安全设置", path: "#" }
    ]
  },
  {
    id: 4,
    title: "我的社区",
    icon: "fas fa-users",
    submenu: [
      { id: 41, title: "我的帖子", path: "#" },
      { id: 42, title: "我的评论", path: "#" },
      { id: 43, title: "我的点赞", path: "#" }
    ]
  },
  {
    id: 5,
    title: "我要充值",
    icon: "fas fa-wallet",
    submenu: [
      { id: 51, title: "充值中心", path: "#" }
    ]
  }
]);

const activeMenu = ref(1);
const activeSubmenu = ref(1);

const handleMenuClick = (menuId) => {
  activeMenu.value = menuId;
  const menu = menuItems.value.find(item => item.id === menuId);
  if (menu && menu.submenu.length > 0) {
    activeSubmenu.value = menu.submenu[0].id;
  }
};

const handleSubmenuClick = (submenuId) => {
  activeSubmenu.value = submenuId;
};

// 监听菜单变化，加载数据
watch([activeMenu, activeSubmenu], ([newMenu, newSubmenu]) => {
  if (newMenu === 1) {
    fetchMyCourses(newSubmenu);
  } else if (newMenu === 2) {
    fetchOrders(newSubmenu);
  }
});

onMounted(() => {
  fetchUserInfo();
  fetchMyCourses(1);
  fetchAccountBalance();
});
</script>

<template>
  <div class="user-center-container">
    <div class="user-center-content">
      <!-- 左侧菜单 -->
      <div class="user-sidebar">
        <div class="user-profile">
          <div class="avatar">
            <img :src="userInfo.avatar || 'https://www.usian.cn/uploads/20250327/052111edb1cc05f9fd4ecebfe45264ec.png'" alt="用户头像">
          </div>
          <div class="user-details">
            <h3>{{ userInfo.name || '用户名' }}</h3>
            <p class="member-level">{{ userInfo.memberLevel }}</p>
          </div>
        </div>
        
        <nav class="user-menu">
          <div 
            v-for="menu in menuItems" 
            :key="menu.id" 
            class="menu-item"
            :class="{ active: activeMenu === menu.id }"
          >
            <div class="menu-title" @click="handleMenuClick(menu.id)">
              <i :class="menu.icon"></i>
              <span>{{ menu.title }}</span>
              <i class="fas fa-chevron-down"></i>
            </div>
            <div class="submenu" v-if="activeMenu === menu.id">
              <div 
                v-for="subitem in menu.submenu" 
                :key="subitem.id"
                class="submenu-item"
                :class="{ active: activeSubmenu === subitem.id }"
                @click="handleSubmenuClick(subitem.id)"
              >
                {{ subitem.title }}
              </div>
            </div>
          </div>
        </nav>
      </div>
      
      <!-- 右侧内容 -->
      <div class="user-main">
        <div class="user-content">
          <!-- 我的课程 -->
          <div v-if="activeMenu === 1">
            <h2>我的课程</h2>
            <div class="course-tabs">
              <button 
                class="tab-btn" 
                :class="{ active: activeSubmenu === 1 }"
                @click="activeSubmenu = 1"
              >
                学习中
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeSubmenu === 2 }"
                @click="activeSubmenu = 2"
              >
                已完成
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeSubmenu === 3 }"
                @click="activeSubmenu = 3"
              >
                收藏
              </button>
            </div>
            
            <div v-if="courseLoading" class="loading">加载中...</div>
            <div v-else-if="myCourseList.length === 0" class="empty">暂无课程</div>
            <div v-else class="course-list">
              <div class="course-item" v-for="course in myCourseList" :key="course.course_id">
                <div class="course-pic">
                  <img :src="config.baseUrl + course.course_img" alt="课程图片" class="course-image">
                </div>
                <div class="course-info">
                  <h4>{{ course.course_name }}</h4>
                  <p>有效期：{{ course.expire_text }}</p>
                  <p>学习进度：{{ course.progress || 0 }}%</p>
                  <div class="progress-bar">
                    <div class="progress" :style="{ width: (course.progress || 0) + '%' }"></div>
                  </div>
                </div>
                <button class="continue-btn">继续学习</button>
              </div>
            </div>
          </div>
          
          <!-- 我的订单 -->
          <div v-else-if="activeMenu === 2">
            <h2>我的订单</h2>
            <div class="order-tabs">
              <button 
                class="tab-btn" 
                :class="{ active: activeSubmenu === 21 }"
                @click="activeSubmenu = 21"
              >
                待支付
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeSubmenu === 22 }"
                @click="activeSubmenu = 22"
              >
                已支付
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeSubmenu === 23 }"
                @click="activeSubmenu = 23"
              >
                退款/售后
              </button>
            </div>
            
            <div v-if="orderLoading" class="loading">加载中...</div>
            <div v-else-if="orderList.length === 0" class="empty">暂无订单</div>
            <div v-else class="order-list">
              <div class="order-item" v-for="order in orderList" :key="order.order_number">
                <div class="order-header">
                  <span>订单号：{{ order.order_number }}</span>
                  <span class="order-status" :class="statusMap[order.status]?.color">
                    {{ statusMap[order.status]?.text || '未知状态' }}
                  </span>
                </div>
                <div class="order-content">
                  <div class="course-items" v-if="order.details && order.details.length > 0">
                    <div v-for="detail in order.details" :key="detail.id" class="course-item-mini">
                      <img :src="config.baseUrl + detail.course_img" alt="课程图片" class="course-thumb">
                      <div class="course-desc">
                        <p class="course-name">{{ detail.course_name }}</p>
                        <p class="course-price">¥{{ detail.price }}</p>
                        <p class="course-expire">{{ detail.expire_text || '永久有效' }}</p>
                        <button v-if="order.status === 2" class="comment-btn" @click="openCommentDialog(detail.course_id)">评价</button>
                      </div>
                    </div>
                  </div>
                  <div class="order-summary">
                    <p>订单金额：¥{{ order.actual_payment || 0 }}</p>
                    <p>支付方式：{{ order.payment_method === 1 ? '支付宝' : '微信支付' }}</p>
                    <p>创建时间：{{ order.create_time }}</p>
                  </div>
                </div>
                <div class="order-actions">
                  <button v-if="order.status === 1" class="pay-btn" @click="payOrder(order.order_number)">立即支付</button>
                  <button v-if="order.status === 1" class="cancel-btn" @click="cancelOrder(order.order_number)">取消订单</button>
                  <button v-if="order.status === 2" class="refund-btn" @click="applyRefund(order.order_number)">申请退款</button>
                  <button v-if="order.status === 2" class="view-btn" @click="$router.push('/paysuccess?orderno=' + order.order_number)">查看详情</button>
                  <button v-if="order.status === 6" class="wait-btn">退款处理中</button>
                  <button v-if="order.status === 7" class="done-btn">退款完成</button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 账户设置 -->
          <div v-else-if="activeMenu === 3">
            <h2>账户设置</h2>
            <div class="settings-content">
              <div v-if="activeSubmenu === 31">
                <h3>个人信息</h3>
                <form class="settings-form">
                  <div class="form-group">
                    <label>用户名</label>
                    <input type="text" :value="userInfo.name" readonly>
                  </div>
                  <div class="form-group">
                    <label>邮箱</label>
                    <input type="email" :value="userInfo.email" readonly>
                  </div>
                  <div class="form-group">
                    <label>手机号</label>
                    <input type="tel" :value="userInfo.phone" readonly>
                  </div>
                  <div class="form-group">
                    <label>会员等级</label>
                    <input type="text" :value="userInfo.memberLevel" readonly>
                  </div>
                  <div class="form-group">
                    <label>会员到期</label>
                    <input type="text" :value="userInfo.memberExpiry" readonly>
                  </div>
                </form>
              </div>
              <div v-else-if="activeSubmenu === 32">
                <h3>密码修改</h3>
                <form class="settings-form">
                  <div class="form-group">
                    <label>当前密码</label>
                    <input type="password" v-model="passwordForm.oldPassword" placeholder="请输入当前密码">
                  </div>
                  <div class="form-group">
                    <label>新密码</label>
                    <input type="password" v-model="passwordForm.newPassword" placeholder="请输入新密码（至少6位）">
                  </div>
                  <div class="form-group">
                    <label>确认新密码</label>
                    <input type="password" v-model="passwordForm.confirmPassword" placeholder="请确认新密码">
                  </div>
                  <button type="button" class="save-btn" @click="updatePassword">保存修改</button>
                </form>
              </div>
              <div v-else-if="activeSubmenu === 33">
                <h3>安全设置</h3>
                <div class="security-content">
                  <p>安全设置功能开发中...</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 我的社区 -->
          <div v-else-if="activeMenu === 4">
            <h2>我的社区</h2>
            <div class="community-content">
              <p>社区功能开发中...</p>
            </div>
          </div>
          
          <!-- 我要充值 -->
          <div v-else-if="activeMenu === 5">
            <h2>我要充值</h2>
            <div class="recharge-content">
              <div class="balance-info">
                <span class="balance-label">账户余额</span>
                <span class="balance-amount">¥{{ accountBalance }}</span>
              </div>
              
              <div class="recharge-section">
                <h3>选择充值金额</h3>
                <div class="amount-options">
                  <button 
                    v-for="option in rechargeOptions" 
                    :key="option.value"
                    :class="{ active: rechargeAmount === option.value }"
                    @click="rechargeAmount = option.value">
                    {{ option.label }}
                  </button>
                </div>
                
                <div v-if="giveAmount > 0" class="give-info">
                  <span class="give-text">赠送金额：¥{{ giveAmount }}</span>
                  <span class="total-text">实际到账：¥{{ rechargeAmount + giveAmount }}</span>
                </div>
                
                <button class="recharge-btn" @click="recharge">立即充值</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 评价对话框 -->
  <div v-if="commentDialogVisible" class="comment-dialog-overlay" @click.self="commentDialogVisible = false">
    <div class="comment-dialog">
      <h3>评价课程</h3>
      <div class="form-group">
        <label>评分</label>
        <div class="star-rating">
          <span v-for="i in 5" :key="i" 
                :class="{ active: i <= commentForm.star }"
                @click="commentForm.star = i">★</span>
        </div>
      </div>
      <div class="form-group">
        <label>评价内容</label>
        <textarea v-model="commentForm.content" placeholder="请输入评价内容..."></textarea>
      </div>
      <div class="dialog-actions">
        <button class="cancel-btn" @click="commentDialogVisible = false">取消</button>
        <button class="submit-btn" @click="submitComment">提交评价</button>
      </div>
    </div>
  </div>

</template>

<style scoped>
.user-center-container {
  margin-top: 80px;
  padding: 40px 0;
  min-height: 80vh;
  background: #f5f5f5;
}

.user-center-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  gap: 30px;
}

.user-sidebar {
  width: 280px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  flex-shrink: 0;
}

.user-profile {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 12px;
  border: 2px solid #ff6b00;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details h3 {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
}

.member-level {
  margin: 0;
  font-size: 14px;
  color: #ff6b00;
  background: rgba(255, 107, 0, 0.1);
  padding: 2px 12px;
  border-radius: 12px;
  display: inline-block;
}

.user-menu .menu-item {
  margin-bottom: 8px;
}

.menu-title {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.menu-title:hover {
  background: #f5f5f5;
}

.menu-item.active .menu-title {
  background: rgba(255, 107, 0, 0.1);
  color: #ff6b00;
}

.menu-title i:first-child {
  width: 20px;
  text-align: center;
}

.menu-title i:last-child {
  margin-left: auto;
  font-size: 12px;
  transition: transform 0.3s;
}

.menu-item.active .menu-title i:last-child {
  transform: rotate(180deg);
}

.submenu {
  margin-left: 32px;
  margin-top: 4px;
  border-left: 2px solid #f0f0f0;
  padding-left: 12px;
}

.submenu-item {
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.submenu-item:hover {
  background: #f5f5f5;
  color: #333;
}

.submenu-item.active {
  background: rgba(255, 107, 0, 0.1);
  color: #ff6b00;
}

.user-main {
  flex: 1;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.user-content h2 {
  margin: 0 0 24px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.course-tabs, .order-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.tab-btn {
  padding: 8px 20px;
  border: none;
  background: transparent;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  color: #666;
}

.tab-btn:hover {
  color: #ff6b00;
}

.tab-btn.active {
  background: #ff6b00;
  color: white;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.3s;
  gap: 20px;
}

.course-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.course-pic {
  flex-shrink: 0;
}

.course-image {
  width: 100px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}

.course-info {
  flex: 1;
}

.course-info h4 {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
}

.course-info p {
  margin: 0 0 8px;
  font-size: 14px;
  color: #666;
}

.progress-bar {
  width: 200px;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: #ff6b00;
  transition: width 0.3s;
}

.continue-btn {
  padding: 8px 20px;
  border: none;
  background: #ff6b00;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.continue-btn:hover {
  background: #ff8533;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-item {
  padding: 20px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.order-status {
  font-weight: 500;
}

.order-status.orange { color: #ff6b00; }
.order-status.green { color: #28a745; }
.order-status.blue { color: #007bff; }
.order-status.gray { color: #6c757d; }
.order-status.red { color: #dc3545; }
.order-status.purple { color: #6f42c1; }

.order-content {
  margin-bottom: 16px;
}

.course-items {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.course-item-mini {
  display: flex;
  gap: 12px;
  width: calc(50% - 8px);
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.course-thumb {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.course-desc {
  flex: 1;
}

.course-name {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 500;
}

.course-price {
  margin: 0 0 4px;
  font-size: 13px;
  color: #ff6b00;
}

.course-expire {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.order-summary {
  padding-top: 12px;
  border-top: 1px dashed #eee;
}

.order-summary p {
  margin: 6px 0;
  font-size: 14px;
  color: #666;
}

.order-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.pay-btn {
  padding: 6px 16px;
  border: none;
  background: #ff6b00;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.pay-btn:hover {
  background: #ff8533;
}

.cancel-btn {
  padding: 6px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn:hover {
  border-color: #ff6b00;
  color: #ff6b00;
}

.refund-btn {
  padding: 6px 16px;
  border: 1px solid #ff6b00;
  background: white;
  color: #ff6b00;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.refund-btn:hover {
  background: #ff6b00;
  color: white;
}

.view-btn {
  padding: 6px 16px;
  border: 1px solid #007bff;
  background: white;
  color: #007bff;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.view-btn:hover {
  background: #007bff;
  color: white;
}

.wait-btn {
  padding: 6px 16px;
  border: none;
  background: #ffc107;
  color: #333;
  border-radius: 4px;
  font-size: 14px;
  cursor: not-allowed;
}

.done-btn {
  padding: 6px 16px;
  border: none;
  background: #28a745;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  cursor: not-allowed;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #ff6b00;
  box-shadow: 0 0 0 2px rgba(255, 107, 0, 0.1);
}

.save-btn {
  padding: 10px 24px;
  border: none;
  background: #ff6b00;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  align-self: flex-start;
}

.save-btn:hover {
  background: #ff8533;
}

.community-content, .recharge-content, .security-content {
  padding: 40px;
  text-align: center;
  color: #999;
}

.recharge-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.balance-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px 60px;
  border-radius: 12px;
  margin-bottom: 30px;
  text-align: center;
}

.balance-label {
  display: block;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin-bottom: 10px;
}

.balance-amount {
  display: block;
  color: #fff;
  font-size: 36px;
  font-weight: bold;
}

.recharge-section {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.recharge-section h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 16px;
  text-align: left;
}

.amount-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.amount-options button {
  flex: 1;
  min-width: calc(50% - 6px);
  padding: 15px;
  border: 2px solid #e0e0e0;
  background: #fff;
  border-radius: 8px;
  font-size: 16px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s;
}

.amount-options button:hover {
  border-color: #ff6b00;
}

.amount-options button.active {
  border-color: #ff6b00;
  background: rgba(255, 107, 0, 0.05);
  color: #ff6b00;
}

.give-info {
  background: #fff8f0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  text-align: center;
}

.give-text {
  display: block;
  color: #ff6b00;
  font-size: 14px;
  margin-bottom: 5px;
}

.total-text {
  display: block;
  color: #333;
  font-size: 16px;
  font-weight: bold;
}

.recharge-btn {
  width: 100%;
  padding: 15px;
  border: none;
  background: linear-gradient(135deg, #ff6b00 0%, #ff8533 100%);
  color: #fff;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.recharge-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 0, 0.3);
}

.comment-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.comment-dialog {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  width: 400px;
  max-width: 90%;
}

.comment-dialog h3 {
  margin-bottom: 20px;
  text-align: center;
}

.comment-dialog .form-group {
  margin-bottom: 16px;
}

.comment-dialog .form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.comment-dialog textarea {
  width: 100%;
  height: 100px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
}

.star-rating {
  display: flex;
  gap: 8px;
  font-size: 24px;
  cursor: pointer;
}

.star-rating span {
  color: #ddd;
  transition: color 0.2s;
}

.star-rating span.active {
  color: #ff9800;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.dialog-actions .cancel-btn {
  padding: 8px 16px;
  background: #999;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dialog-actions .submit-btn {
  padding: 8px 16px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.comment-btn {
  margin-top: 8px;
  padding: 4px 12px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
</style>
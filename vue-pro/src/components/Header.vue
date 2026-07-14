<template>
  <header>
    <div class="header-content">
      <!-- 左侧：Logo + 导航 -->
      <div class="header-left">
        <div class="logo" @click="goToHome">
          <span class="zhihu-logo">知乎</span>
        </div>
        <nav class="nav-links">
          <a href="#" @click.prevent="goToHome">首页</a>
          <a href="#" @click.prevent="goToHome" class="nav-with-badge">
            知乎直答
            <span class="badge">beta</span>
          </a>
          <a href="#" @click.prevent="goToHome" class="active">知乎知学堂</a>
          <a href="#" @click.prevent="goToHome">等你来答</a>
          <a href="#" @click.prevent="goToVideoUpload">视频上传</a>
        </nav>
      </div>

      <!-- 中间：搜索 + 提问 -->
      <div class="header-center">
        <div class="search-container">
          <input
            type="text"
            v-model="searchKeyword"
            placeholder="搜索你感兴趣的内容..."
            @keyup.enter="handleSearch"
          >
          <button @click="handleSearch"><i class="fa fa-search"></i></button>
        </div>
        <button class="ask-btn">提问</button>
      </div>

      <!-- 右侧：消息/私信/创作中心/用户 -->
      <div class="header-right">
        <div class="top-actions">
          <div class="top-action-item" @click="goToMessage">
            <i class="far fa-bell"></i>
            <span>消息</span>
            <span class="message-dot" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
          </div>
          <div class="top-action-item" @click="goToChat">
            <i class="far fa-comment-dots"></i>
            <span>私信</span>
          </div>
          <div class="top-action-item" @click="goToCreator">
            <i class="fas fa-pen-nib"></i>
            <span>创作中心</span>
          </div>
        </div>

        <div v-if="userStore.isLoggedIn" class="user-info">
          <div class="user-avatar" @click="showDropdown = !showDropdown">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" />
          </div>
          <div v-if="showDropdown" class="dropdown-menu">
            <a @click="goToUserCenter">个人中心</a>
            <a @click="goToLearningCenter">学习中心</a>
            <a @click="handleLogout">退出登录</a>
          </div>
        </div>
        <div v-else class="auth-buttons">
          <button class="login-btn" @click="goToLogin">登录</button>
          <button class="register-btn" @click="goToRegister">注册</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { useUserStore } from '@/store/userStore'

const router = useRouter()
const searchKeyword = ref('')
const showDropdown = ref(false)
const userInfo = ref(null)
const unreadCount = ref(3)
const userStore = useUserStore()

const getUserInfo = () => {
  let token = localStorage.getItem('token')
  let username = localStorage.getItem('username')
  if (!token) {
    token = sessionStorage.getItem('token')
    username = sessionStorage.getItem('username')
  }
  if (token && username) {
    userInfo.value = { token, username }
  } else {
    userInfo.value = null
  }
}

window.addEventListener('storage', getUserInfo)

const handleLogout = () => {
  userStore.logout()
  userInfo.value = null
  showDropdown.value = false
  router.push('/login')
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/search', query: { name: searchKeyword.value.trim() } })
  }
}

const goToLearningCenter = () => router.push('/user')
const goToMessage = () => router.push('/message')
const goToChat = () => router.push('/chat')
const goToCreator = () => router.push('/creator')
const goToUserCenter = () => router.push('/user')
const goToLogin = () => router.push('/login')
const goToRegister = () => router.push('/register')
const goToHome = () => router.push('/')
const goToVideoUpload = () => router.push('/video-upload')

onMounted(() => {
  userStore.init()
  getUserInfo()
  router.afterEach(() => {
    getUserInfo()
  })
})
</script>

<style scoped>
header {
  background: #ffffff;
  border-bottom: 1px solid #ebebeb;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 52px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.zhihu-logo {
  font-size: 28px;
  font-weight: bold;
  color: #0066ff;
  font-family: 'Georgia', serif;
  letter-spacing: -1px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-links a {
  text-decoration: none;
  color: #646464;
  font-size: 15px;
  position: relative;
  padding: 16px 0;
  transition: color 0.2s;
}

.nav-links a:hover,
.nav-links a.active {
  color: #1a1a1a;
  font-weight: 600;
}

.nav-with-badge {
  position: relative;
}

.badge {
  position: absolute;
  top: 8px;
  right: -28px;
  font-size: 10px;
  color: #0066ff;
  background: #e8f0fe;
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: normal;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  max-width: 500px;
  margin: 0 32px;
}

.search-container {
  display: flex;
  align-items: center;
  background: #f6f6f6;
  border-radius: 24px;
  overflow: hidden;
  flex: 1;
  border: 1px solid transparent;
  transition: border-color 0.2s;
}

.search-container:focus-within {
  border-color: #0066ff;
  background: #fff;
}

.search-container input {
  border: none;
  padding: 8px 16px;
  outline: none;
  width: 100%;
  font-size: 14px;
  background: transparent;
  color: #1a1a1a;
}

.search-container input::placeholder {
  color: #b4b4b4;
}

.search-container button {
  border: none;
  background: transparent;
  padding: 8px 14px;
  cursor: pointer;
  color: #8590a6;
}

.ask-btn {
  background: #0066ff;
  color: #fff;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.ask-btn:hover {
  background: #0052cc;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.top-action-item {
  display: flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: #8590a6;
  font-size: 13px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  transition: all 0.2s;
  position: relative;
}

.top-action-item:hover {
  color: #1a1a1a;
  background: #f6f6f6;
}

.top-action-item i {
  font-size: 16px;
}

.message-dot {
  position: absolute;
  top: 2px;
  right: 0px;
  background: #ff4d4f;
  color: #fff;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  line-height: 1.4;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.login-btn, .register-btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.login-btn {
  background: transparent;
  color: #0066ff;
}

.login-btn:hover {
  background: #e8f0fe;
}

.register-btn {
  background: #0066ff;
  color: white;
}

.register-btn:hover {
  background: #0052cc;
}

.user-info {
  position: relative;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid #f0f0f0;
  transition: border-color 0.2s;
}

.user-avatar:hover {
  border-color: #0066ff;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 8px 0;
  min-width: 140px;
  margin-top: 8px;
  z-index: 1001;
}

.dropdown-menu a {
  display: block;
  padding: 8px 16px;
  color: #1a1a1a;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-menu a:hover {
  background: #f6f6f6;
  color: #0066ff;
}
</style>

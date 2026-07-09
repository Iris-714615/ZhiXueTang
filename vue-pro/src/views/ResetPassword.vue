<template>
  <div>
    <div class="reset-container">
      <div class="reset-box">
        <h2 class="reset-title">重置密码</h2>

        <div class="reset-form">
          <!-- 手机号输入 -->
          <div class="form-item">
            <input type="text"
                   v-model="form.code"
                   placeholder="请输入验证码">
          </div>          

          <!-- 密码输入 -->
          <div class="form-item">
            <input :type="showPassword ? 'text' : 'password'"
                   v-model="form.password"
                   placeholder="请输入新密码">
            <span class="toggle-password" @click="showPassword = !showPassword">
              {{ showPassword ? '隐藏' : '显示' }}
            </span>
          </div>

          <!-- 确认密码输入 -->
          <div class="form-item">
            <input :type="showConfirmPassword ? 'text' : 'password'"
                   v-model="form.confirmPassword"
                   placeholder="请确认新密码">
            <span class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
              {{ showConfirmPassword ? '隐藏' : '显示' }}
            </span>
          </div>

          <!-- 提交按钮 -->
          <button class="submit-btn" @click="handleSubmit">重置密码</button>

          <!-- 返回登录 -->
          <div class="back-login">
            想起密码了？<a href="#" @click.prevent="goToLogin">返回登录</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage} from 'element-plus'
import request from '../utils/request'

const router = useRouter()
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const countdown = ref(0)

// 表单数据
const form = reactive({
  code: '',
  password: '',
  confirmPassword: ''
})


// 提交表单
const handleSubmit = () => {
  // 表单验证

  if (!form.code) {
    ElMessage.error('请输入验证码');
    return;
  }
  if (!form.password) {
    ElMessage.error('请输入新密码');
    return;
  }
  if (form.password.length < 6) {
    ElMessage.error('密码长度不能少于6位');
    return;
  }
  if (form.password !== form.confirmPassword) {
    ElMessage.error('两次输入的密码不一致');
    return;
  }

  // 发送请求
  request.post('reset-password/', {
    code: form.code,
    passwd: form.password,
    repasswd: form.confirmPassword
  }).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('密码重置成功');
      router.push('/login');
    } else {
      ElMessage.error(res.data?.msg || '密码重置失败');
    }
  }).catch(err => {
    ElMessage.error('密码重置失败，请稍后重试');
    console.error('重置密码错误:', err);
  });
}

// 返回登录页
const goToLogin = () => {
  router.push('/login');
}
</script>

<style scoped>
.reset-container {
  min-height: calc(100vh - 60px);
  margin-top: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f5f5;
}

.reset-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.reset-title {
  text-align: center;
  font-size: 24px;
  color: #333;
  margin-bottom: 30px;
}

.form-item {
  margin-bottom: 20px;
  position: relative;
}

.form-item input {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-item input:focus {
  border-color: #ff6b00;
  outline: none;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #909399;
  cursor: pointer;
  font-size: 14px;
}

.sms-code {
  display: flex;
  gap: 10px;
}

.sms-code input {
  flex: 1;
}

.send-code-btn {
  width: 120px;
  padding: 0 15px;
  border: 1px solid #ff6b00;
  border-radius: 4px;
  background: white;
  color: #ff6b00;
  cursor: pointer;
  white-space: nowrap;
}

.send-code-btn:disabled {
  border-color: #dcdfe6;
  color: #909399;
  cursor: not-allowed;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #ff6b00;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 10px;
}

.submit-btn:hover {
  background: #ff8533;
}

.back-login {
  margin-top: 20px;
  text-align: center;
  color: #606266;
}

.back-login a {
  color: #ff6b00;
  text-decoration: none;
}

.back-login a:hover {
  text-decoration: underline;
}
</style>

<template>
  <div>
    <div class="login-container">
      <div class="login-box">
        <h2 class="login-title">账号登录</h2>

        <div class="login-tabs">
          <span :class="['tab-item', { active: loginType === 'password' }]"
                @click="loginType = 'password'">密码登录</span>
          <span :class="['tab-item', { active: loginType === 'sms' }]"
                @click="loginType = 'sms'">短信登录</span>
        </div>

        <div class="login-form">
          <!-- 手机号输入 -->
          <div class="form-item">
            <input type="text"
                   v-model="form.username"
                   placeholder="请输入用户名"
                   @blur="validateUsername">
            <span class="error-tip" v-if="errors.username">{{ errors.username }}</span>
          </div>

          <!-- 密码登录 -->
          <div class="form-item" v-if="loginType === 'password'">
            <input :type="showPassword ? 'text' : 'password'"
                   v-model="form.password"
                   placeholder="请输入密码">
            <span class="toggle-password" @click="showPassword = !showPassword">
              {{ showPassword ? '隐藏' : '显示' }}
            </span>
            <span class="error-tip" v-if="errors.password">{{ errors.password }}</span>
          </div>

          <!-- 短信验证码登录 -->
          <div class="form-item sms-code" v-if="loginType === 'sms'">
            <input type="text"
                   v-model="form.smsCode"
                   placeholder="请输入验证码">
            <button class="send-code-btn"
                    :disabled="countdown > 0"
                    @click="sendSmsCode">
              {{ countdown > 0 ? `${countdown}秒后重新发送` : '发送验证码' }}
            </button>
            <span class="error-tip" v-if="errors.smsCode">{{ errors.smsCode }}</span>
          </div>

          <!-- 记住密码选项 -->
          <div class="form-item remember-row">
            <label class="remember-pwd">
              <input type="checkbox" v-model="form.remember">
              <span>记住密码</span>
            </label>
            <a href="#" class="forget-pwd" @click="goToForgetPassword()">忘记密码？</a>
          </div>

          <!-- 登录按钮 -->
          <button class="login-btn" @click="handleLogin">登录</button>

          <!-- 其他登录方式 -->
          <div class="other-login">
            <div class="divider">
              <span>其他登录方式</span>
            </div>
            <div class="social-login">
              <a href="#" class="social-item wechat">
                <i class="iconfont icon-wechat"></i>
              </a>
              <a href="#" class="social-item qq">
                <i class="iconfont icon-qq"></i>
              </a>
            </div>
          </div>

          <!-- 注册入口 -->
          <div class="register-link">
            还没有账号？<a href="#" @click.prevent="goToRegister">立即注册</a>
          </div>
        </div>
      </div>
    </div>

<el-dialog v-model="dialogFormVisible" title="重置密码" width="500">
    <el-form >
      <el-form-item label="手机号" :label-width="formLabelWidth">
        <el-input v-model="phone" autocomplete="off" />
      </el-form-item>
      <el-form-item label="邮箱" :label-width="formLabelWidth">
        <el-input v-model="email" autocomplete="off" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleForgetPassword()">
          确认
        </el-button>
      </div>
    </template>
  </el-dialog>


  </div>


</template>

<script setup>
import {ref, reactive,} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage} from 'element-plus'
import request from '../utils/request'
import { useUserStore } from '../store/userStore'

const router = useRouter()
const loginType = ref('password') // 登录方式：password/sms
const showPassword = ref(false)
const countdown = ref(0)
const dialogFormVisible = ref(false)

// 表单数据
const form = reactive({
  username: '',  // 修改为username
  password: '',
  smsCode: '',
  remember: false
})

// 表单错误信息
const errors = reactive({
  username: '',  // 修改为username
  password: '',
  smsCode: ''
})
const userStore = useUserStore()

// 登录成功后存储 token 和用户信息到 localStorage
const handleLogin = () => {
  request.post('login/', {
    username: form.username,
    password: form.password,
    smsCode: form.smsCode,
    type: loginType.value,
  }).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('登录成功');
      userStore.setUser({
        token: res.data.token,
        username: res.data.username || form.username,
        user_id: res.data.user_id
      })
      // 跳转到首页
      router.push('/');
    } else {
      ElMessage.error(res.data?.msg || '登录失败');
    }
  })
}
  

// 发送验证码
const sendSmsCode = () => {
  request.post('send_sms/', {
    phone: form.username,
  }).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('验证码发送成功');
    } else {
      ElMessage.error(res.data?.msg || '验证码发送失败');
    }
  })
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/register');
}
const phone = ref('')
const email = ref('')
// 跳转到忘记密码页
const goToForgetPassword = () => {
  dialogFormVisible.value = true
  
}
// 重置密码
const handleForgetPassword = () => {
  request.post('send_email/', {
    phone: phone.value,
    email: email.value,
  }).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('验证码发送成功');
      dialogFormVisible.value = false
    } else {
      ElMessage.error(res.data?.msg || '验证码发送失败');
    }
  })
}

</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 60px); /* 减去header的高度 */
  margin-top: 60px; /* header的高度 */
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f5f5;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.login-title {
  text-align: center;
  font-size: 24px;
  color: #333;
  margin-bottom: 30px;
}

.login-tabs {
  display: flex;
  margin-bottom: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  position: relative;
}

.tab-item.active {
  color: #ff6b00;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 2px;
  background: #ff6b00;
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
}

.form-item input:focus {
  border-color: #ff6b00;
  outline: none;
}

.error-tip {
  position: absolute;
  left: 0;
  bottom: -20px;
  color: #f56c6c;
  font-size: 12px;
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

.remember-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-pwd {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  cursor: pointer;
}

.forget-pwd {
  color: #909399;
  text-decoration: none;
}

.forget-pwd:hover {
  color: #ff6b00;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #ff6b00;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn:hover {
  background: #ff8533;
}

.other-login {
  margin-top: 24px;
}

.divider {
  display: flex;
  align-items: center;
  color: #909399;
  font-size: 14px;
  margin: 20px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #dcdfe6;
  margin: 0 16px;
}

.social-login {
  display: flex;
  justify-content: center;
  gap: 30px;
}

.social-item {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-decoration: none;
  transition: all 0.3s;
}

.social-item.wechat {
  background: #07c160;
}

.social-item.qq {
  background: #12b7f5;
}

.social-item:hover {
  transform: translateY(-2px);
}

.register-link {
  margin-top: 20px;
  text-align: center;
  color: #606266;
}

.register-link a {
  color: #ff6b00;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
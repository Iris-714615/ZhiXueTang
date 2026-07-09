<template>
  <div class="page-container">
    <div class="register-container">
      <div class="register-box">
        <h2>用户注册</h2>
        <el-form
          ref="registerForm"
          :model="registerForm"
          :rules="rules"
          label-width="0px"
          class="register-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              prefix-icon="el-icon-user"
              placeholder="请输入用户名"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              prefix-icon="el-icon-lock"
              type="password"
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>

          <el-form-item prop="phone">
            <el-input
              v-model="registerForm.phone"
              prefix-icon="el-icon-phone"
              placeholder="请输入手机号"
            />
          </el-form-item>

          <el-form-item prop="verificationCode">
            <div class="verification-code">
              <el-input
                v-model="registerForm.verificationCode"
                prefix-icon="el-icon-message"
                placeholder="请输入验证码"
              />
              <el-button
                type="primary"
                :disabled="isCodeButtonDisabled"
                @click="sendVerificationCode"
              >
                {{ codeButtonText }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="register-button"
              :loading="loading"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>

          <div class="login-link">
            已有账号？<router-link to="/login">立即登录</router-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
import request from '../utils/request'

export default {
  name: 'Register',
  data() {
    // 验证手机号的规则
    const validatePhone = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入手机号'))
      } else if (!/^1[3-9]\d{9}$/.test(value)) {
        callback(new Error('请输入正确的手机号'))
      } else {
        callback()
      }
    }

    return {
      registerForm: {
        username: '',
        password: '',
        phone: '',
        verificationCode: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        phone: [
          { required: true, trigger: 'blur', validator: validatePhone }
        ],
        verificationCode: [
          { required: true, message: '请输入验证码', trigger: 'blur' },
          { len: 4, message: '验证码长度应为 4 位', trigger: 'blur' }
        ]
      },
      loading: false,
      isCodeButtonDisabled: false,
      codeButtonText: '获取验证码',
      timer: null,
      countdown: 60
    }
  },
  methods: {
    // 发送验证码
    sendVerificationCode() {
      request.post('send_sms/', {
        phone: this.registerForm.phone
     })
     .then(res => {
      if (res.data.code === 200) {
        this.$message.success('验证码已发送，请注意查收')
      } else {
        this.$message.error(res.data.msg)
      }
     })
     .catch(err => {
      this.$message.error(err.message)
     })
            },
      

    // 处理注册
    handleRegister() {
      request.post('register/', {
        username: this.registerForm.username,
        password: this.registerForm.password,
        phone: this.registerForm.phone,
        code: this.registerForm.verificationCode
     }).then(res => {
      if (res.data && res.data.code === 200) {
        // 存储token和userid到localStorage
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('user_id', res.data.user_id);
        this.$message.success('注册成功');
        this.$router.push('/');
      } else {
        this.$message.error(res.data?.msg || '注册失败');
      }
     }).catch(err => {
      this.$message.error('注册失败，请稍后重试');
      console.error('注册错误:', err);
     })
    }
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.register-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  padding: 40px 0;
}

.register-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.register-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.register-form {
  margin-top: 20px;
}

.verification-code {
  display: flex;
  gap: 10px;
}

.verification-code .el-input {
  flex: 1;
}

.verification-code .el-button {
  width: 120px;
}

.register-button {
  width: 100%;
}

.login-link {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}

.login-link a {
  color: #409EFF;
  text-decoration: none;
}

.login-link a:hover {
  color: #66b1ff;
}
</style>
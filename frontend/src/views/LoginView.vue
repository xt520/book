<template>
  <div class="login-container">
    <div class="login-card md-card-elevated">
      <div class="login-header">
        <div class="logo-icon">📚</div>
        <h1 class="headline-medium">图书管理系统</h1>
        <p class="body-medium">使用学号登录</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="md-outlined-text-field">
          <input 
            type="text" 
            id="studentId" 
            v-model="form.studentId" 
            placeholder=" "
            required
          />
          <label for="studentId">学号 / 账号</label>
        </div>

        <div class="md-outlined-text-field">
          <input 
            type="password" 
            id="password" 
            v-model="form.password" 
            placeholder=" "
            required
          />
          <label for="password">密码</label>
        </div>

        <div v-if="error" class="error-container">
          <span class="error-icon">⚠️</span>
          <span class="body-medium">{{ error }}</span>
        </div>

        <button type="submit" class="md-filled-button login-btn" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <div class="login-footer">
        <p class="body-small">默认密码：12345678</p>
        <p class="body-small">首次登录需修改密码</p>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="md-dialog-scrim">
      <div class="md-dialog">
        <h2 class="md-dialog-title">修改密码</h2>
        <p class="md-dialog-content">首次登录，请修改默认密码以确保账号安全</p>
        
        <form @submit.prevent="handleChangePassword" class="password-form">
          <div class="md-outlined-text-field">
            <input type="password" v-model="passwordForm.oldPassword" placeholder=" " required />
            <label>原密码</label>
          </div>
          <div class="md-outlined-text-field">
            <input type="password" v-model="passwordForm.newPassword" placeholder=" " required minlength="6" />
            <label>新密码</label>
          </div>
          <div class="md-outlined-text-field">
            <input type="password" v-model="passwordForm.confirmPassword" placeholder=" " required />
            <label>确认密码</label>
          </div>
          
          <div v-if="passwordError" class="error-container">
            <span class="error-icon">⚠️</span>
            <span class="body-medium">{{ passwordError }}</span>
          </div>
          
          <div class="md-dialog-actions">
            <button type="submit" class="md-filled-button">确认修改</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api'

const router = useRouter()

const form = reactive({
  studentId: '',
  password: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(false)
const error = ref('')
const showChangePassword = ref(false)
const passwordError = ref('')
const tempToken = ref('')
const tempUser = ref(null)

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const res = await authApi.login(form.studentId, form.password)
    
    if (res.first_login) {
      tempToken.value = res.token
      tempUser.value = res.user
      passwordForm.oldPassword = form.password
      showChangePassword.value = true
    } else {
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(res.user))
      
      if (res.user.role === 'super_admin') {
        router.push('/super-admin')
      } else if (res.user.role === 'admin') {
        router.push('/admin')
      } else {
        router.push('/')
      }
    }
  } catch (e) {
    error.value = e.detail || '登录失败，请检查学号和密码'
  } finally {
    loading.value = false
  }
}

const handleChangePassword = async () => {
  passwordError.value = ''
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的密码不一致'
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    passwordError.value = '新密码至少6位'
    return
  }
  
  try {
    await authApi.changePassword(
      passwordForm.oldPassword, 
      passwordForm.newPassword, 
      tempToken.value
    )
    
    localStorage.setItem('token', tempToken.value)
    localStorage.setItem('user', JSON.stringify(tempUser.value))
    
    showChangePassword.value = false
    
    if (tempUser.value.role === 'super_admin') {
      router.push('/super-admin')
    } else if (tempUser.value.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/')
    }
  } catch (e) {
    passwordError.value = e.detail || '密码修改失败'
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--md-primary-container) 0%, var(--md-tertiary-container) 100%);
  padding: 24px;
}

.login-card {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-extra-large);
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--md-elevation-3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 64px;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

.login-header h1 {
  color: var(--md-on-surface);
  margin-bottom: 8px;
}

.login-header p {
  color: var(--md-on-surface-variant);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.md-outlined-text-field {
  position: relative;
}

.md-outlined-text-field input {
  width: 100%;
  height: 56px;
  padding: 16px;
  padding-top: 24px;
  border: 1px solid var(--md-outline);
  border-radius: var(--md-shape-corner-extra-small);
  background: transparent;
  font-size: 16px;
  color: var(--md-on-surface);
  transition: all 0.2s;
  box-sizing: border-box;
}

.md-outlined-text-field input:focus {
  outline: none;
  border: 2px solid var(--md-primary);
}

.md-outlined-text-field label {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: var(--md-on-surface-variant);
  pointer-events: none;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  background: var(--md-surface);
  padding: 0 4px;
}

.md-outlined-text-field input:focus + label,
.md-outlined-text-field input:not(:placeholder-shown) + label {
  top: 0;
  font-size: 12px;
  color: var(--md-primary);
}

.error-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--md-error-container);
  color: var(--md-on-error-container);
  border-radius: var(--md-shape-corner-small);
}

.error-icon {
  font-size: 18px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  margin-top: 8px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  margin-top: 32px;
  text-align: center;
  color: var(--md-on-surface-variant);
}

.login-footer p {
  margin: 4px 0;
}

/* Password Dialog */
.password-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 24px;
}

.md-dialog {
  width: 90%;
  max-width: 400px;
}
</style>

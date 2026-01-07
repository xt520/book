<template>
  <div class="profile-page">
    <NavBar />
    
    <div class="content">
      <!-- Profile Card -->
      <div class="profile-card">
        <div class="avatar">{{ user?.name?.charAt(0) || '?' }}</div>
        <div class="user-info">
          <h2 class="headline-small">{{ user?.name }}</h2>
          <p class="body-medium">学号：{{ user?.student_id }}</p>
        </div>
        <button class="md-outlined-button logout-btn" @click="handleLogout">
          退出登录
        </button>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-icon">📖</span>
          <span class="stat-num headline-large">{{ borrowedCount }}</span>
          <span class="stat-text body-medium">当前借阅</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">✅</span>
          <span class="stat-num headline-large">{{ returnedCount }}</span>
          <span class="stat-text body-medium">已归还</span>
        </div>
        <div class="stat-card" :class="{ warning: overdueCount > 0 }">
          <span class="stat-icon">⚠️</span>
          <span class="stat-num headline-large">{{ overdueCount }}</span>
          <span class="stat-text body-medium">已逾期</span>
        </div>
        <div class="stat-card clickable" @click="activeTab = 'messages'">
          <span class="stat-icon">📬</span>
          <span class="stat-num headline-large">{{ unreadCount }}</span>
          <span class="stat-text body-medium">未读消息</span>
        </div>
      </div>

      <!-- Tabs Section -->
      <div class="records-section md-card-outlined">
        <div class="tab-bar">
          <button 
            :class="['tab-btn', { active: activeTab === 'borrowed' }]"
            @click="activeTab = 'borrowed'"
          >
            借阅中
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'returned' }]"
            @click="activeTab = 'returned'"
          >
            已归还
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'favorites' }]"
            @click="activeTab = 'favorites'"
          >
            我的收藏
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'messages' }]"
            @click="activeTab = 'messages'"
          >
            消息 <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'password' }]"
            @click="activeTab = 'password'"
          >
            修改密码
          </button>
        </div>

        <!-- Borrow Records -->
        <div v-if="activeTab === 'borrowed' || activeTab === 'returned' || activeTab === 'favorites'" class="record-list">
          <div 
            v-for="record in filteredRecords" 
            :key="record.id" 
            class="record-item"
            @click="record.book_id ? $router.push(`/book/${record.book_id}`) : null"
            :style="{ cursor: record.book_id ? 'pointer' : 'default' }"
          >
            <div class="record-cover">
              <img v-if="record.cover || record.book_cover" :src="record.cover || record.book_cover" />
              <span v-else>📖</span>
            </div>
            <div class="record-info">
              <h4 class="title-medium">{{ record.book_title }}</h4>
              <p class="body-small author">{{ record.book_author }}</p>
              <div class="dates" v-if="activeTab !== 'favorites'">
                <span class="body-small">借阅：{{ formatDate(record.borrow_date) }}</span>
                <span :class="['body-small', { overdue: isOverdue(record) }]">
                  {{ record.status === 'borrowed' ? '应还' : '归还' }}：
                  {{ formatDate(record.status === 'borrowed' ? record.due_date : record.return_date) }}
                </span>
              </div>
              <div class="dates" v-else>
                 <span class="body-small">收藏于：{{ formatDate(record.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="filteredRecords.length === 0" class="empty-records">
            <span class="empty-icon">📭</span>
            <p class="body-medium">
              {{ 
                activeTab === 'borrowed' ? '暂无借阅中的图书' : 
                activeTab === 'returned' ? '暂无已归还的图书' : 
                '暂无收藏的图书' 
              }}
            </p>
          </div>
        </div>

        <!-- Messages -->
        <div v-if="activeTab === 'messages'" class="message-list">
          <div class="message-header">
            <button v-if="unreadCount > 0" class="md-text-button" @click="markAllRead">
              全部标为已读
            </button>
          </div>
          <div 
            v-for="msg in messages" 
            :key="msg.id" 
            :class="['message-item', { unread: !msg.is_read }]"
            @click="markMessageRead(msg)"
          >
            <div class="message-sender">
              <span class="sender-icon">{{ msg.sender_name === 'system' ? '🔔' : '📢' }}</span>
              <span class="sender-name">{{ msg.sender_name === 'system' ? '系统通知' : '管理员通知' }}</span>
              <span class="message-time">{{ formatDate(msg.created_at) }}</span>
            </div>
            <h4 class="message-title">{{ msg.title }}</h4>
            <p class="message-content" v-if="msg.content">{{ msg.content }}</p>
          </div>
          
          <div v-if="messages.length === 0" class="empty-records">
            <span class="empty-icon">📭</span>
            <p class="body-medium">暂无消息</p>
          </div>
        </div>

        <!-- Password Change -->
        <div v-if="activeTab === 'password'" class="password-form">
          <h3 class="title-large">🔐 修改密码</h3>
          <div class="form-group">
            <label class="label-medium">当前密码</label>
            <input 
              type="password" 
              v-model="passwordForm.old_password" 
              placeholder="输入当前密码"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label class="label-medium">新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.new_password" 
              placeholder="输入新密码（至少6位）"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label class="label-medium">确认新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.confirm_password" 
              placeholder="再次输入新密码"
              class="input-field"
            />
          </div>
          <button 
            class="md-filled-button" 
            @click="changePassword"
            :disabled="!passwordForm.old_password || !passwordForm.new_password || passwordForm.new_password !== passwordForm.confirm_password"
          >
            修改密码
          </button>
          <p v-if="passwordForm.new_password && passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password" class="error-text">
            两次密码输入不一致
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { borrowApi, socialApi, messageApi, authApi } from '../api'

const router = useRouter()
const user = ref(null)
const records = ref([])
const favoriteRecords = ref([])
const messages = ref([])
const unreadCount = ref(0)
const activeTab = ref('borrowed')

// Password form
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const borrowedCount = computed(() => 
  records.value.filter(r => r.status === 'borrowed').length
)

const returnedCount = computed(() => 
  records.value.filter(r => r.status === 'returned').length
)

const overdueCount = computed(() => 
  records.value.filter(r => r.status === 'borrowed' && isOverdue(r)).length
)

const filteredRecords = computed(() => {
  if (activeTab.value === 'favorites') return favoriteRecords.value
  return records.value.filter(r => r.status === activeTab.value)
})

const isOverdue = (record) => {
  if (record.status !== 'borrowed') return false
  return new Date(record.due_date) < new Date()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const handleReturn = async (record) => {
  if (!confirm(`确认归还《${record.book_title}》？`)) return
  
  try {
    await borrowApi.return(record.id)
    alert('归还成功！')
    loadRecords()
  } catch (e) {
    alert(e.detail || '归还失败')
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

const loadRecords = async () => {
  try {
    records.value = await borrowApi.getMyBorrows()
  } catch (e) {
    console.error('加载借阅记录失败', e)
  }
}

const loadFavorites = async () => {
  try {
    favoriteRecords.value = await socialApi.getMyFavorites()
  } catch (e) {
    console.error('加载收藏失败', e)
  }
}

const loadMessages = async () => {
  try {
    const res = await messageApi.getList()
    messages.value = res.items
  } catch (e) {
    console.error('加载消息失败', e)
  }
}

const loadUnreadCount = async () => {
  try {
    const res = await messageApi.getUnreadCount()
    unreadCount.value = res.count
  } catch (e) {
    console.error('加载未读数失败', e)
  }
}

const markMessageRead = async (msg) => {
  if (msg.is_read) return
  try {
    await messageApi.markRead(msg.id)
    msg.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (e) {
    console.error('标记已读失败', e)
  }
}

const markAllRead = async () => {
  try {
    await messageApi.markAllRead()
    messages.value.forEach(msg => msg.is_read = true)
    unreadCount.value = 0
  } catch (e) {
    console.error('标记全部已读失败', e)
  }
}

const changePassword = async () => {
  if (passwordForm.value.new_password.length < 6) {
    alert('新密码至少需要6位')
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    await authApi.changePassword(
      passwordForm.value.old_password,
      passwordForm.value.new_password,
      token
    )
    alert('密码修改成功！')
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (e) {
    alert(e.detail || '密码修改失败，请检查原密码是否正确')
  }
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
  }

  loadRecords()
  loadFavorites()
  loadMessages()
  loadUnreadCount()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--md-surface-container-lowest);
}

.content {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: linear-gradient(135deg, var(--md-primary) 0%, var(--md-tertiary) 100%);
  border-radius: var(--md-shape-corner-extra-large);
  padding: 24px 32px;
  color: white;
  margin-bottom: 24px;
}

.avatar {
  width: 64px;
  height: 64px;
  background: rgba(255,255,255,0.2);
  border-radius: var(--md-shape-corner-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 500;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  margin-bottom: 4px;
}

.user-info p {
  opacity: 0.9;
}

.logout-btn {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.3);
  color: white;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.25);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  padding: 24px;
  text-align: center;
  box-shadow: var(--md-elevation-1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-icon {
  font-size: 32px;
}

.stat-num {
  color: var(--md-primary);
}

.stat-card.warning .stat-num {
  color: var(--md-error);
}

.stat-text {
  color: var(--md-on-surface-variant);
}

.records-section {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  padding: 24px;
}

.records-header h3 {
  color: var(--md-on-surface);
  margin-bottom: 16px;
}

.tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 24px;
  border-radius: var(--md-shape-corner-full);
  border: none;
  background: var(--md-surface-container);
  color: var(--md-on-surface-variant);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: var(--md-surface-container-high);
}

.tab-btn.active {
  background: var(--md-primary);
  color: var(--md-on-primary);
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--md-surface-container-low);
  border-radius: var(--md-shape-corner-medium);
  transition: all 0.2s;
}

.record-item:hover {
  background: var(--md-surface-container);
}

.record-cover {
  width: 50px;
  height: 65px;
  border-radius: var(--md-shape-corner-small);
  background: var(--md-surface-container-high);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.record-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.record-cover span {
  font-size: 24px;
}

.record-info {
  flex: 1;
  min-width: 0;
}

.record-info h4 {
  color: var(--md-on-surface);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.record-info .author {
  color: var(--md-on-surface-variant);
  margin-bottom: 8px;
}

.dates {
  display: flex;
  gap: 16px;
  color: var(--md-outline);
}

.dates .overdue {
  color: var(--md-error);
}

.return-btn {
  flex-shrink: 0;
}

.empty-records {
  text-align: center;
  padding: 48px 24px;
  color: var(--md-on-surface-variant);
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}

@media (max-width: 600px) {
  .profile-card {
    flex-wrap: wrap;
  }
  
  .logout-btn {
    width: 100%;
    margin-top: 12px;
  }
  
  .tab-bar {
    flex-wrap: wrap;
  }
}

/* Clickable stat card */
.stat-card.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: var(--md-elevation-2);
}

/* Badge for unread count */
.badge {
  background: var(--md-error);
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 4px;
}

/* Message list styles */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.message-item {
  padding: 16px;
  background: var(--md-surface-container-low);
  border-radius: var(--md-shape-corner-medium);
  cursor: pointer;
  transition: all 0.2s;
}

.message-item:hover {
  background: var(--md-surface-container);
}

.message-item.unread {
  border-left: 4px solid var(--md-primary);
  background: var(--md-primary-container);
}

.message-sender {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.sender-icon {
  font-size: 18px;
}

.sender-name {
  font-weight: 500;
  color: var(--md-on-surface);
}

.message-time {
  color: var(--md-on-surface-variant);
  font-size: 12px;
  margin-left: auto;
}

.message-title {
  font-weight: 600;
  color: var(--md-on-surface);
  margin-bottom: 4px;
}

.message-content {
  color: var(--md-on-surface-variant);
  white-space: pre-wrap;
}

/* Password form styles */
.password-form {
  max-width: 400px;
}

.password-form h3 {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--md-on-surface-variant);
}

.input-field {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--md-outline);
  border-radius: var(--md-shape-corner-small);
  font-size: 14px;
  background: var(--md-surface);
  color: var(--md-on-surface);
}

.input-field:focus {
  outline: none;
  border-color: var(--md-primary);
}

.md-filled-button {
  background: var(--md-primary);
  color: var(--md-on-primary);
  border: none;
  padding: 12px 24px;
  border-radius: var(--md-shape-corner-full);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.md-filled-button:hover:not(:disabled) {
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.md-filled-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.md-text-button {
  background: transparent;
  border: none;
  color: var(--md-primary);
  padding: 8px 16px;
  border-radius: var(--md-shape-corner-full);
  cursor: pointer;
  transition: all 0.2s;
}

.md-text-button:hover {
  background: var(--md-primary-container);
}

.error-text {
  color: var(--md-error);
  font-size: 12px;
  margin-top: 8px;
}

/* ==================== 响应式补充 ==================== */

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-icon {
    font-size: 24px;
  }
  
  .stat-num {
    font-size: 24px;
  }
  
  .tab-bar {
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .tab-btn {
    padding: 8px 16px;
    font-size: 13px;
  }
  
  .message-sender {
    flex-wrap: wrap;
  }
  
  .message-time {
    width: 100%;
    margin-left: 26px;
  }
  
  .message-title {
    font-size: 14px;
  }
  
  .message-content {
    font-size: 13px;
  }
  
  .password-form {
    max-width: 100%;
  }
  
  .password-form h3 {
    font-size: 18px;
    margin-bottom: 16px;
  }
  
  .input-field {
    padding: 10px;
  }
  
  .md-filled-button {
    width: 100%;
    padding: 12px;
  }
}

@media (max-width: 400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .stat-icon {
    font-size: 20px;
  }
  
  .stat-num {
    font-size: 20px;
  }
  
  .stat-text {
    font-size: 11px;
  }
}
</style>

<template>
  <div class="super-admin-page">
    <!-- Top Navigation -->
    <nav class="admin-nav">
      <div class="nav-left">
        <span class="nav-brand title-large">📚 图书管理系统</span>
        <span class="role-chip super">超级管理员</span>
      </div>
      <div class="nav-right">
        <span class="user-name body-medium">{{ user?.name }}</span>
        <button class="md-outlined-button logout-btn" @click="handleLogout">退出</button>
      </div>
    </nav>

    <div class="admin-layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-content">
          <button 
            v-for="item in menuItems"
            :key="item.id"
            :class="['menu-item', { active: activeMenu === item.id }]"
            @click="activeMenu = item.id"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span class="menu-text label-large">{{ item.label }}</span>
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- System Settings -->
        <div v-if="activeMenu === 'settings'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">系统设置</h2>
          </div>

          <div class="settings-form card-outlined">
            <div class="form-group">
              <label class="label-medium">最短借阅天数</label>
              <input 
                type="number" 
                v-model.number="settings.min_borrow_days" 
                min="1" 
                max="365"
                class="input-field"
              />
            </div>
            <div class="form-group">
              <label class="label-medium">最长借阅天数</label>
              <input 
                type="number" 
                v-model.number="settings.max_borrow_days" 
                min="1" 
                max="365"
                class="input-field"
              />
            </div>
            <div class="form-group">
              <label class="label-medium">每日逾期罚款（元）</label>
              <input 
                type="number" 
                v-model.number="settings.fine_per_day" 
                min="0" 
                step="0.1"
                class="input-field"
              />
            </div>
            <button class="md-filled-button" @click="saveSettings">保存设置</button>
          </div>

          <div class="overdue-action card-outlined">
            <h3 class="title-medium">逾期管理</h3>
            <p class="body-medium text-secondary">一键向所有逾期用户发送提醒消息</p>
            <button class="md-tonal-button" @click="handleBatchOverdueNotify">
              📢 一键发送逾期提醒
            </button>
          </div>
        </div>

        <!-- Admin Management -->
        <div v-if="activeMenu === 'admins'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">管理员管理</h2>
          </div>

          <!-- Add Admin Form -->
          <div class="add-admin-section card-outlined">
            <h3 class="title-medium">添加管理员</h3>
            <div class="form-row">
              <div class="form-group">
                <input 
                  type="text" 
                  v-model="adminForm.student_id" 
                  placeholder="账号 *" 
                  class="input-field"
                />
              </div>
              <div class="form-group">
                <input 
                  type="text" 
                  v-model="adminForm.name" 
                  placeholder="姓名 *" 
                  class="input-field"
                />
              </div>
              <button 
                class="md-filled-button" 
                @click="handleAddAdmin" 
                :disabled="!adminForm.student_id || !adminForm.name"
              >
                添加
              </button>
            </div>
            <p class="body-small text-secondary">默认密码为 admin123</p>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>账号</th>
                  <th>姓名</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="admin in admins" :key="admin.id">
                  <td>{{ admin.student_id }}</td>
                  <td>{{ admin.name }}</td>
                  <td>{{ formatDate(admin.created_at) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button class="md-tonal-button btn-sm" @click="handleResetPassword(admin)">
                        重置密码
                      </button>
                      <button class="md-text-button btn-sm danger" @click="handleDeleteAdmin(admin)">
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Send Notification -->
        <div v-if="activeMenu === 'notify'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">发送公告</h2>
          </div>

          <div class="notify-form card-outlined">
            <div class="form-group">
              <label class="label-medium">发送对象</label>
              <div class="receiver-options">
                <label class="radio-option">
                  <input type="radio" v-model="notifyType" value="all" />
                  <span>群发所有用户</span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="notifyType" value="selected" />
                  <span>选择特定用户</span>
                </label>
              </div>
            </div>

            <div v-if="notifyType === 'selected'" class="form-group">
              <label class="label-medium">搜索用户</label>
              <input 
                type="text" 
                v-model="userSearchKeyword" 
                placeholder="输入学号或姓名搜索..."
                class="input-field"
                @input="searchUsers"
              />
              <div class="user-chips" v-if="selectedUsers.length > 0">
                <span 
                  v-for="u in selectedUsers" 
                  :key="u.id" 
                  class="user-chip"
                  @click="removeSelectedUser(u)"
                >
                  {{ u.name }} ({{ u.student_id }}) ×
                </span>
              </div>
              <div class="user-search-results" v-if="searchedUsers.length > 0">
                <div 
                  v-for="u in searchedUsers" 
                  :key="u.id" 
                  class="user-search-item"
                  @click="addSelectedUser(u)"
                >
                  {{ u.name }} ({{ u.student_id }})
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="label-medium">标题 *</label>
              <input 
                type="text" 
                v-model="notifyForm.title" 
                placeholder="输入公告标题"
                class="input-field"
              />
            </div>

            <div class="form-group">
              <label class="label-medium">内容</label>
              <textarea 
                v-model="notifyForm.content" 
                placeholder="输入公告内容..."
                class="input-field textarea"
                rows="5"
              ></textarea>
            </div>

            <button 
              class="md-filled-button" 
              @click="sendNotification"
              :disabled="!notifyForm.title"
            >
              发送公告
            </button>
          </div>
        </div>

        <!-- Operation Logs -->
        <div v-if="activeMenu === 'logs'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">操作日志</h2>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>操作人</th>
                  <th>操作</th>
                  <th>详情</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in logs" :key="log.id">
                  <td>{{ formatDateTime(log.created_at) }}</td>
                  <td>{{ log.user_name || '系统' }}</td>
                  <td>{{ log.action }}</td>
                  <td>{{ log.detail || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="logTotalPages > 1" class="pagination">
            <button 
              class="md-tonal-button" 
              :disabled="logPage === 1" 
              @click="loadLogs(logPage - 1)"
            >上一页</button>
            <span class="page-info">第 {{ logPage }} / {{ logTotalPages }} 页</span>
            <button 
              class="md-tonal-button" 
              :disabled="logPage === logTotalPages" 
              @click="loadLogs(logPage + 1)"
            >下一页</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminApi, messageApi } from '../api'

const router = useRouter()
const user = ref(null)
const activeMenu = ref('settings')

const menuItems = [
  { id: 'settings', icon: '⚙️', label: '系统设置' },
  { id: 'admins', icon: '👤', label: '管理员管理' },
  { id: 'notify', icon: '📢', label: '发送公告' },
  { id: 'logs', icon: '📜', label: '操作日志' }
]

// Settings
const settings = ref({
  min_borrow_days: 1,
  max_borrow_days: 60,
  fine_per_day: 0.5
})

// Admins
const admins = ref([])
const adminForm = ref({ student_id: '', name: '' })

// Notification
const notifyType = ref('all')
const notifyForm = ref({ title: '', content: '' })
const userSearchKeyword = ref('')
const searchedUsers = ref([])
const selectedUsers = ref([])

// Logs
const logs = ref([])
const logPage = ref(1)
const logTotalPages = ref(1)

const loadSettings = async () => {
  try {
    const res = await adminApi.getSettings()
    settings.value = res
  } catch (e) {
    console.error('Failed to load settings:', e)
  }
}

const saveSettings = async () => {
  try {
    await adminApi.updateSettings(settings.value)
    alert('设置已保存')
  } catch (e) {
    alert(e.detail || '保存失败')
  }
}

const loadAdmins = async () => {
  try {
    admins.value = await adminApi.getAdmins()
  } catch (e) {
    console.error('Failed to load admins:', e)
  }
}

const handleAddAdmin = async () => {
  if (!adminForm.value.student_id || !adminForm.value.name) return
  
  try {
    await adminApi.createAdmin(adminForm.value)
    alert('管理员创建成功')
    adminForm.value = { student_id: '', name: '' }
    loadAdmins()
  } catch (e) {
    alert(e.detail || '创建失败')
  }
}

const handleDeleteAdmin = async (admin) => {
  if (!confirm(`确认删除管理员 ${admin.name}？`)) return
  
  try {
    await adminApi.deleteAdmin(admin.id)
    alert('管理员已删除')
    loadAdmins()
  } catch (e) {
    alert(e.detail || '删除失败')
  }
}

const handleResetPassword = async (admin) => {
  if (!confirm(`确认重置 ${admin.name} 的密码为 admin123？`)) return
  
  try {
    await adminApi.resetAdminPassword(admin.id)
    alert('密码已重置为 admin123')
  } catch (e) {
    alert(e.detail || '重置失败')
  }
}

const handleBatchOverdueNotify = async () => {
  try {
    const res = await adminApi.batchOverdueNotify()
    alert(res.message)
  } catch (e) {
    alert(e.detail || '发送失败')
  }
}

let searchTimeout = null
const searchUsers = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    if (!userSearchKeyword.value) {
      searchedUsers.value = []
      return
    }
    try {
      searchedUsers.value = await messageApi.getUsersForSend(userSearchKeyword.value)
      // Filter out already selected
      searchedUsers.value = searchedUsers.value.filter(
        u => !selectedUsers.value.find(s => s.id === u.id)
      )
    } catch (e) {
      console.error(e)
    }
  }, 300)
}

const addSelectedUser = (user) => {
  if (!selectedUsers.value.find(u => u.id === user.id)) {
    selectedUsers.value.push(user)
  }
  searchedUsers.value = []
  userSearchKeyword.value = ''
}

const removeSelectedUser = (user) => {
  selectedUsers.value = selectedUsers.value.filter(u => u.id !== user.id)
}

const sendNotification = async () => {
  if (!notifyForm.value.title) return
  
  try {
    const data = {
      title: notifyForm.value.title,
      content: notifyForm.value.content,
      receiver_ids: notifyType.value === 'all' ? [] : selectedUsers.value.map(u => u.id)
    }
    const res = await messageApi.send(data)
    alert(res.message)
    notifyForm.value = { title: '', content: '' }
    selectedUsers.value = []
  } catch (e) {
    alert(e.detail || '发送失败')
  }
}

const loadLogs = async (page = 1) => {
  try {
    const res = await adminApi.getLogs({ page, page_size: 50 })
    logs.value = res.items
    logPage.value = page
    logTotalPages.value = Math.ceil(res.total / 50)
  } catch (e) {
    console.error('Failed to load logs:', e)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
    if (user.value.role !== 'super_admin') {
      router.push('/')
      return
    }
  } else {
    router.push('/login')
    return
  }

  loadSettings()
  loadAdmins()
  loadLogs()
})
</script>

<style scoped>
.super-admin-page {
  min-height: 100vh;
  background: var(--md-surface);
}

.admin-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%);
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-brand {
  font-weight: 600;
}

.role-chip.super {
  background: rgba(255, 193, 7, 0.3);
  color: #ffc107;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logout-btn {
  color: white;
  border-color: rgba(255,255,255,0.5);
}

.admin-layout {
  display: flex;
  min-height: calc(100vh - 60px);
}

.sidebar {
  width: 220px;
  background: var(--md-surface-container);
  border-right: 1px solid var(--md-outline-variant);
  padding: 16px 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: transparent;
  border-radius: var(--md-shape-corner-medium);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--md-on-surface);
  text-align: left;
}

.menu-item:hover {
  background: var(--md-surface-container-high);
}

.menu-item.active {
  background: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
}

.menu-icon {
  font-size: 20px;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.panel {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  padding: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.card-outlined {
  border: 1px solid var(--md-outline-variant);
  border-radius: var(--md-shape-corner-medium);
  padding: 20px;
  margin-bottom: 20px;
}

.settings-form .form-group,
.notify-form .form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--md-on-surface-variant);
}

.input-field {
  width: 100%;
  max-width: 300px;
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

.textarea {
  max-width: 100%;
  resize: vertical;
}

.overdue-action {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.add-admin-section .form-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--md-outline-variant);
}

.data-table th {
  font-weight: 600;
  color: var(--md-on-surface-variant);
  background: var(--md-surface-container);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.danger {
  color: var(--md-error);
}

.receiver-options {
  display: flex;
  gap: 24px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.user-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.user-chip {
  background: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
}

.user-chip:hover {
  opacity: 0.8;
}

.user-search-results {
  border: 1px solid var(--md-outline-variant);
  border-radius: var(--md-shape-corner-small);
  max-height: 200px;
  overflow-y: auto;
  margin-top: 8px;
}

.user-search-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--md-outline-variant);
}

.user-search-item:hover {
  background: var(--md-surface-container);
}

.user-search-item:last-child {
  border-bottom: none;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}

.page-info {
  color: var(--md-on-surface-variant);
}

.text-secondary {
  color: var(--md-on-surface-variant);
}

/* Material Design 3 Button Styles */
.md-filled-button {
  background: var(--md-primary);
  color: var(--md-on-primary);
  border: none;
  padding: 10px 24px;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.md-filled-button:hover:not(:disabled) {
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.md-filled-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.md-tonal-button {
  background: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
  border: none;
  padding: 10px 24px;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.md-tonal-button:hover:not(:disabled) {
  opacity: 0.9;
}

.md-tonal-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.md-text-button {
  background: transparent;
  border: none;
  padding: 10px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.md-text-button:hover {
  background: var(--md-surface-container);
}

.md-outlined-button {
  background: transparent;
  border: 1px solid var(--md-outline);
  padding: 10px 24px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.md-outlined-button:hover {
  background: var(--md-surface-container);
}

/* ==================== 响应式设计 ==================== */

/* 平板及以下 */
@media (max-width: 900px) {
  .admin-layout {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--md-outline-variant);
    padding: 8px;
  }
  
  .sidebar-content {
    display: flex;
    overflow-x: auto;
    gap: 8px;
    padding-bottom: 8px;
  }
  
  .menu-item {
    flex-shrink: 0;
    padding: 10px 16px;
  }
  
  .menu-text {
    white-space: nowrap;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .panel {
    padding: 16px;
  }
}

/* 手机端 */
@media (max-width: 600px) {
  .admin-nav {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .nav-left {
    width: 100%;
    justify-content: space-between;
  }
  
  .nav-brand {
    font-size: 16px;
  }
  
  .nav-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .logout-btn {
    padding: 8px 16px;
    font-size: 14px;
  }
  
  .sidebar-content {
    gap: 4px;
  }
  
  .menu-item {
    padding: 8px 12px;
  }
  
  .menu-icon {
    font-size: 16px;
  }
  
  .menu-text {
    font-size: 12px;
  }
  
  .main-content {
    padding: 12px;
  }
  
  .panel {
    padding: 12px;
  }
  
  .panel-header h2 {
    font-size: 18px;
  }
  
  .card-outlined {
    padding: 16px;
  }
  
  .form-row {
    flex-direction: column !important;
    gap: 12px !important;
  }
  
  .add-admin-section .form-row .form-group {
    width: 100%;
  }
  
  .add-admin-section .form-row button {
    width: 100%;
  }
  
  .input-field {
    max-width: 100%;
  }
  
  /* 表格响应式 */
  .data-table {
    font-size: 13px;
  }
  
  .data-table th,
  .data-table td {
    padding: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .btn-sm {
    padding: 6px 10px;
    font-size: 11px;
    width: 100%;
    text-align: center;
  }
  
  /* 隐藏部分表格列 */
  .data-table th:nth-child(3),
  .data-table td:nth-child(3) {
    display: none;
  }
  
  .receiver-options {
    flex-direction: column;
    gap: 12px;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .md-filled-button,
  .md-tonal-button {
    padding: 10px 16px;
    font-size: 14px;
  }
}

/* 超小屏幕 */
@media (max-width: 360px) {
  .admin-nav {
    padding: 8px 12px;
  }
  
  .nav-brand {
    font-size: 14px;
  }
  
  .role-chip.super {
    font-size: 10px;
    padding: 2px 8px;
  }
  
  .menu-item {
    padding: 6px 10px;
  }
  
  .menu-icon {
    font-size: 14px;
  }
  
  .menu-text {
    font-size: 11px;
  }
}
</style>

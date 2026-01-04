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
        <div class="stat-card warning" v-if="overdueCount > 0">
          <span class="stat-icon">⚠️</span>
          <span class="stat-num headline-large">{{ overdueCount }}</span>
          <span class="stat-text body-medium">已逾期</span>
        </div>
      </div>

      <!-- Borrow Records -->
      <div class="records-section md-card-outlined">
        <div class="records-header">
          <h3 class="title-large">📚 我的借阅记录</h3>
        </div>
        
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
        </div>

        <div class="record-list">
          <div 
            v-for="record in filteredRecords" 
            :key="record.id" 
            class="record-item"
          >
            <div class="record-cover">
              <img v-if="record.cover" :src="record.cover" />
              <span v-else>📖</span>
            </div>
            <div class="record-info">
              <h4 class="title-medium">{{ record.book_title }}</h4>
              <p class="body-small author">{{ record.book_author }}</p>
              <div class="dates">
                <span class="body-small">借阅：{{ formatDate(record.borrow_date) }}</span>
                <span :class="['body-small', { overdue: isOverdue(record) }]">
                  {{ record.status === 'borrowed' ? '应还' : '归还' }}：
                  {{ formatDate(record.status === 'borrowed' ? record.due_date : record.return_date) }}
                </span>
              </div>
            </div>
          </div>
          
          <div v-if="filteredRecords.length === 0" class="empty-records">
            <span class="empty-icon">📭</span>
            <p class="body-medium">暂无{{ activeTab === 'borrowed' ? '借阅中' : '已归还' }}的图书</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { borrowApi } from '../api'

const router = useRouter()
const user = ref(null)
const records = ref([])
const activeTab = ref('borrowed')

const borrowedCount = computed(() => 
  records.value.filter(r => r.status === 'borrowed').length
)

const returnedCount = computed(() => 
  records.value.filter(r => r.status === 'returned').length
)

const overdueCount = computed(() => 
  records.value.filter(r => r.status === 'borrowed' && isOverdue(r)).length
)

const filteredRecords = computed(() => 
  records.value.filter(r => r.status === activeTab.value)
)

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

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
  }
  loadRecords()
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
}
</style>

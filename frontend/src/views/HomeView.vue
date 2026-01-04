<template>
  <div class="home">
    <NavBar @search="handleSearch" />
    
    <div class="content">
      <!-- Hero Section -->
      <div class="hero-card">
        <div class="hero-content">
          <h1 class="display-small">📚 欢迎来到图书馆</h1>
          <p class="body-large">发现知识的海洋，开启阅读之旅</p>
        </div>
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-value headline-medium">{{ stats.total_books }}</span>
            <span class="stat-label body-small">馆藏图书</span>
          </div>
          <div class="stat-item">
            <span class="stat-value headline-medium">{{ stats.total_categories }}</span>
            <span class="stat-label body-small">图书分类</span>
          </div>
          <div class="stat-item">
            <span class="stat-value headline-medium">{{ stats.total_authors }}</span>
            <span class="stat-label body-small">签约作者</span>
          </div>
        </div>
      </div>

      <!-- Book Section -->
      <h2 class="title-large section-title">📖 最新上架</h2>

      <!-- Book Grid -->
      <div class="book-grid" v-if="books.length > 0">
        <BookCard 
          v-for="book in books" 
          :key="book.id" 
          :book="book"
          @borrow="handleBorrow"
        />
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">📖</div>
        <p class="title-medium">暂无图书数据</p>
        <p class="body-medium">请稍后再来查看</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="page-btn md-tonal-button" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          上一页
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="p in visiblePages" 
            :key="p"
            :class="['page-num', { active: p === currentPage }]"
            @click="changePage(p)"
          >
            {{ p }}
          </button>
        </div>
        
        <span class="page-info body-medium">
          第 {{ currentPage }} / {{ totalPages }} 页，共 {{ totalBooks }} 本
        </span>
        
        <button 
          class="page-btn md-tonal-button" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- Borrow Dialog -->
    <div v-if="showBorrowModal" class="md-dialog-scrim" @click.self="showBorrowModal = false">
      <div class="md-dialog borrow-dialog">
        <h3 class="md-dialog-title">确认借阅</h3>
        <div class="md-dialog-content">
          <div class="book-preview">
            <div class="preview-cover">
              <img v-if="selectedBook?.cover" :src="selectedBook.cover" />
              <span v-else>📖</span>
            </div>
            <div class="preview-info">
              <p class="title-medium">{{ selectedBook?.title }}</p>
              <p class="body-medium">{{ selectedBook?.author }}</p>
            </div>
          </div>
          <div class="borrow-info">
            <span class="label-medium">借阅期限</span>
            <span class="body-medium">30天</span>
          </div>
        </div>
        <div class="md-dialog-actions">
          <button class="md-text-button" @click="showBorrowModal = false">取消</button>
          <button class="md-filled-button" @click="confirmBorrow">确认借阅</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import NavBar from '../components/NavBar.vue'
import BookCard from '../components/BookCard.vue'
import { bookApi, borrowApi } from '../api'

const books = ref([])
const stats = ref({
  total_books: 0,
  total_categories: 0,
  total_authors: 0
})
const searchTerm = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const totalBooks = ref(0)
const totalPages = ref(1)
const showBorrowModal = ref(false)
const selectedBook = ref(null)

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

const handleSearch = (term) => {
  searchTerm.value = term
  currentPage.value = 1
  loadBooks()
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadBooks()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const handleBorrow = (book) => {
  selectedBook.value = book
  showBorrowModal.value = true
}

const confirmBorrow = async () => {
  try {
    await borrowApi.borrow(selectedBook.value.id)
    alert('借阅成功！')
    showBorrowModal.value = false
    loadBooks()
  } catch (e) {
    alert(e.detail || '借阅失败')
  }
}

const loadBooks = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchTerm.value) {
      params.search = searchTerm.value
    }
    
    const res = await bookApi.getList(params)
    books.value = res.items
    totalBooks.value = res.total
    totalPages.value = res.total_pages
  } catch (e) {
    console.error('加载图书失败', e)
  }
}



const loadStats = async () => {
  try {
    stats.value = await bookApi.getStats()
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

onMounted(() => {
  loadBooks()
  loadStats()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: var(--md-surface-container-lowest);
}

.content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
}

.hero-card {
  background: linear-gradient(135deg, var(--md-primary) 0%, var(--md-tertiary) 100%);
  border-radius: var(--md-shape-corner-extra-large);
  padding: 40px;
  color: white;
  margin-bottom: 32px;
}

.hero-content h1 {
  margin-bottom: 8px;
  font-weight: 400;
}

.hero-content p {
  opacity: 0.9;
}

.stats-row {
  display: flex;
  gap: 48px;
  margin-top: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-weight: 500;
}

.stat-label {
  opacity: 0.8;
}

.filter-section {
  margin-bottom: 24px;
}

.section-title {
  color: var(--md-on-surface);
  margin-bottom: 16px;
}

.category-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  padding: 0 16px;
  height: 32px;
  border-radius: var(--md-shape-corner-small);
  border: 1px solid var(--md-outline);
  background: var(--md-surface);
  color: var(--md-on-surface-variant);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
}

.filter-chip:hover {
  background: var(--md-surface-container);
}

.filter-chip.selected {
  background: var(--md-secondary-container);
  border-color: transparent;
  color: var(--md-on-secondary-container);
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.empty-state {
  text-align: center;
  padding: 80px 24px;
  color: var(--md-on-surface-variant);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding: 24px;
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  flex-wrap: wrap;
}

.page-btn {
  min-width: 80px;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-num {
  width: 40px;
  height: 40px;
  border-radius: var(--md-shape-corner-full);
  border: none;
  background: transparent;
  color: var(--md-on-surface);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.page-num:hover {
  background: var(--md-surface-container);
}

.page-num.active {
  background: var(--md-primary);
  color: var(--md-on-primary);
}

.page-info {
  color: var(--md-on-surface-variant);
}

/* Borrow Dialog */
.borrow-dialog {
  width: 90%;
  max-width: 400px;
}

.book-preview {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.preview-cover {
  width: 80px;
  height: 100px;
  border-radius: var(--md-shape-corner-small);
  background: var(--md-surface-container);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-cover img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-cover span {
  font-size: 32px;
}

.preview-info {
  flex: 1;
}

.preview-info .title-medium {
  color: var(--md-on-surface);
  margin-bottom: 4px;
}

.preview-info .body-medium {
  color: var(--md-on-surface-variant);
}

.borrow-info {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--md-surface-container);
  border-radius: var(--md-shape-corner-small);
}

.borrow-info .label-medium {
  color: var(--md-on-surface-variant);
}

@media (max-width: 768px) {
  .hero-card {
    padding: 24px;
  }
  
  .stats-row {
    gap: 24px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}
</style>

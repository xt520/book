<template>
  <div class="category-page">
    <NavBar @search="handleSearch" />
    
    <div class="content">
      <h1 class="headline-medium page-title">📂 图书分类</h1>
      
      <!-- Category Grid -->
      <div class="category-grid" v-if="!selectedCategory">
        <div 
          v-for="cat in categories" 
          :key="cat.name"
          class="category-card md-card-elevated"
          @click="selectCategory(cat.name)"
        >
          <div class="category-icon">{{ getIcon(cat.name) }}</div>
          <div class="category-name title-medium">{{ cat.name }}</div>
          <div class="category-count body-small">{{ cat.count }} 本图书</div>
        </div>
      </div>

      <!-- Category Books -->
      <div v-if="selectedCategory" class="category-books">
        <div class="section-header">
          <button class="md-text-button back-btn" @click="selectedCategory = null">
            ← 返回分类
          </button>
          <h2 class="title-large">{{ selectedCategory }}</h2>
          <span class="body-medium">{{ categoryBooks.length }} 本图书</span>
        </div>
        
        <div class="book-grid" v-if="categoryBooks.length > 0">
          <BookCard 
            v-for="book in categoryBooks" 
            :key="book.id" 
            :book="book"
            @borrow="handleBorrow"
          />
        </div>
        
        <div v-else class="empty-state">
          <span class="empty-icon">📭</span>
          <p class="body-medium">该分类暂无图书</p>
        </div>
      </div>
    </div>

    <!-- Borrow Dialog -->
    <div v-if="showBorrowModal" class="md-dialog-scrim" @click.self="showBorrowModal = false">
      <div class="md-dialog">
        <h3 class="md-dialog-title">确认借阅</h3>
        <div class="md-dialog-content">
          <p>您要借阅《{{ selectedBook?.title }}》吗？</p>
          <p class="body-small" style="margin-top: 8px; color: var(--md-outline);">借阅期限：30天</p>
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
import { ref, onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'
import BookCard from '../components/BookCard.vue'
import { bookApi, borrowApi } from '../api'

const categories = ref([])
const selectedCategory = ref(null)
const categoryBooks = ref([])
const showBorrowModal = ref(false)
const selectedBook = ref(null)

const categoryIcons = {
  '编程': '💻',
  '文学': '📖',
  '科技': '🔬',
  '艺术': '🎨',
  '科幻': '🚀',
  '历史': '📜',
  '经济': '📊',
  '其它': '📚'
}

const getIcon = (name) => categoryIcons[name] || '📚'

const handleSearch = (term) => {
  // Handle search
}

const selectCategory = async (catName) => {
  selectedCategory.value = catName
  try {
    const res = await bookApi.getList({ category: catName, page_size: 100 })
    categoryBooks.value = res.items
  } catch (e) {
    console.error('加载分类图书失败', e)
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
    selectCategory(selectedCategory.value)
  } catch (e) {
    alert(e.detail || '借阅失败')
  }
}

const loadCategories = async () => {
  try {
    const cats = await bookApi.getCategories()
    const res = await bookApi.getList({ page_size: 100 })
    const books = res.items
    
    categories.value = cats.map(cat => ({
      name: cat,
      count: books.filter(b => b.category === cat).length
    }))
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.category-page {
  min-height: 100vh;
  background: var(--md-surface-container-lowest);
}

.content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
}

.page-title {
  color: var(--md-on-surface);
  margin-bottom: 24px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.category-card {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--md-elevation-3);
  background: var(--md-surface-container-low);
}

.category-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.category-name {
  color: var(--md-on-surface);
  margin-bottom: 4px;
}

.category-count {
  color: var(--md-on-surface-variant);
}

.category-books {
  margin-top: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.back-btn {
  color: var(--md-primary);
}

.section-header h2 {
  color: var(--md-on-surface);
  flex: 1;
}

.section-header span {
  color: var(--md-on-surface-variant);
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
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}
</style>

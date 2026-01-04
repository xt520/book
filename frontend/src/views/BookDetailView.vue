<template>
  <div class="book-detail-page">
    <NavBar />
    
    <div class="content" v-if="book">
      <!-- Book Info Card -->
      <div class="book-detail-card">
        <div class="book-cover-large">
          <img v-if="book.cover" :src="book.cover" :alt="book.title" />
          <span v-else>📖</span>
        </div>
        
        <div class="book-info-section">
          <div class="info-header">
            <h1 class="display-small">{{ book.title }}</h1>
            <button 
              :class="['favorite-btn', { active: isFavorite }]" 
              @click="toggleFavorite"
              title="收藏"
            >
              {{ isFavorite ? '❤️' : '🤍' }}
            </button>
          </div>
          
          <p class="headline-small author">{{ book.author }}</p>
          
          <div class="tags">
            <span class="category-chip">{{ book.category }}</span>
            <span class="isbn-chip">ISBN: {{ book.isbn || '未知' }}</span>
          </div>
          
          <div class="stock-info">
            <div class="stock-item">
              <span class="label">可借</span>
              <span :class="['value', { 'out-of-stock': book.available_count === 0 }]">
                {{ book.available_count }}
              </span>
            </div>
            <div class="stock-item">
              <span class="label">总藏</span>
              <span class="value">{{ book.total_count }}</span>
            </div>
          </div>
          
          <div class="actions">
            <button 
              class="md-filled-button borrow-btn"
              :disabled="book.available_count === 0"
              @click="handleBorrow"
            >
              {{ book.available_count > 0 ? '立即借阅' : '暂时缺货' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Reviews Section -->
      <div class="reviews-section">
        <h2 class="title-large">📚 读者评论 ({{ reviews.length }})</h2>
        
        <!-- Write Review -->
        <div class="write-review-card">
          <div class="rating-input">
            <span class="label-medium">评分：</span>
            <div class="stars">
              <span 
                v-for="n in 5" 
                :key="n"
                :class="['star', { active: newReview.rating >= n }]"
                @click="newReview.rating = n"
              >
                ★
              </span>
            </div>
          </div>
          <textarea 
            v-model="newReview.content"
            placeholder="写下你的读后感..."
            rows="3"
            class="review-input"
          ></textarea>
          <div class="review-actions">
            <button class="md-tonal-button" @click="submitReview" :disabled="!newReview.content">
              发布评论
            </button>
          </div>
        </div>
        
        <!-- Review List -->
        <div class="review-list">
          <div v-for="review in reviews" :key="review.id" class="review-item">
            <div class="review-header">
              <span class="reviewer-name title-medium">{{ review.user_name }}</span>
              <span class="review-date body-small">{{ formatDate(review.created_at) }}</span>
            </div>
            <div class="review-rating">
              <span 
                v-for="n in 5" 
                :key="n" 
                :class="['star-small', { active: review.rating >= n }]"
              >★</span>
            </div>
            <p class="review-content body-medium">{{ review.content }}</p>
          </div>
          
          <div v-if="reviews.length === 0" class="empty-reviews">
            <p class="body-medium">暂无评论，来抢沙发吧！</p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="loading" class="loading-state">
      <p>加载中...</p>
    </div>
    
    <div v-else class="error-state">
      <p>未找到该图书</p>
      <button class="md-text-button" @click="$router.push('/')">返回首页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { bookApi, borrowApi, socialApi } from '../api'

const route = useRoute()
const router = useRouter()
const bookId = route.params.id

const book = ref(null)
const reviews = ref([])
const isFavorite = ref(false)
const loading = ref(true)

const newReview = ref({
  rating: 5,
  content: ''
})

const loadData = async () => {
  loading.value = true
  try {
    // 1. Get Book Detail First (Critical)
    const bookData = await bookApi.getDetail(bookId)
    book.value = bookData
    
    // 2. Load Social Data (Non-critical)
    // Even if these fail, we should still show the book
    try {
      const [reviewsData, favStatus] = await Promise.all([
        socialApi.getReviews(bookId),
        socialApi.isFavorite(bookId)
      ])
      reviews.value = reviewsData
      isFavorite.value = favStatus
    } catch (socialError) {
      console.warn('Social features failed to load:', socialError)
      // Optional: disable social features or show warning
    }
  } catch (e) {
    console.error('加载详情失败', e)
    // Only if getting the book itself fails do we show the error state
    book.value = null
  } finally {
    loading.value = false
  }
}

const toggleFavorite = async () => {
  try {
    await socialApi.toggleFavorite(bookId)
    isFavorite.value = !isFavorite.value
  } catch (e) {
    alert('操作失败')
  }
}

const handleBorrow = async () => {
  if (!confirm(`确认借阅《${book.value.title}》？`)) return
  
  try {
    await borrowApi.borrow(bookId)
    alert('借阅成功！')
    loadData() // Reload to update stock
  } catch (e) {
    alert(e.detail || '借阅失败')
  }
}

const submitReview = async () => {
  try {
    await socialApi.createReview(bookId, newReview.value)
    alert('评论发布成功')
    newReview.value.content = ''
    // Reload reviews
    reviews.value = await socialApi.getReviews(bookId)
  } catch (e) {
    alert(e.detail || '发布失败')
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.book-detail-page {
  min-height: 100vh;
  background: var(--md-surface-container-lowest);
}

.content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 24px;
}

.book-detail-card {
  display: flex;
  gap: 40px;
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-extra-large);
  padding: 40px;
  box-shadow: var(--md-elevation-1);
  margin-bottom: 40px;
}

.book-cover-large {
  width: 240px;
  height: 340px;
  background: var(--md-surface-container);
  border-radius: var(--md-shape-corner-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: var(--md-elevation-2);
}

.book-cover-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-cover-large span {
  font-size: 80px;
}

.book-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.favorite-btn {
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 8px;
  border-radius: 50%;
}

.favorite-btn:hover {
  background: var(--md-surface-container);
  transform: scale(1.1);
}

.author {
  color: var(--md-on-surface-variant);
  margin-bottom: 24px;
}

.tags {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
}

.category-chip {
  background: var(--md-primary-container);
  color: var(--md-on-primary-container);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
}

.isbn-chip {
  background: var(--md-surface-container-high);
  color: var(--md-on-surface-variant);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
}

.stock-info {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
  padding: 20px;
  background: var(--md-surface-container-low);
  border-radius: var(--md-shape-corner-medium);
}

.stock-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-item .label {
  font-size: 14px;
  color: var(--md-on-surface-variant);
}

.stock-item .value {
  font-size: 24px;
  font-weight: 600;
  color: var(--md-primary);
}

.stock-item .value.out-of-stock {
  color: var(--md-error);
}

.borrow-btn {
  width: 100%;
  height: 56px;
  font-size: 18px;
}

/* Reviews */
.reviews-section {
  max-width: 800px;
  margin: 0 auto;
}

.write-review-card {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  padding: 24px;
  margin: 24px 0;
  border: 1px solid var(--md-outline-variant);
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.stars {
  display: flex;
  gap: 4px;
  cursor: pointer;
}

.star {
  font-size: 24px;
  color: var(--md-surface-container-highest);
  transition: color 0.2s;
}

.star.active {
  color: #FFC107;
}

.review-input {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--md-outline);
  background: var(--md-surface-container-low);
  margin-bottom: 12px;
  font-family: inherit;
  resize: vertical;
}

.review-actions {
  display: flex;
  justify-content: flex-end;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-item {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 20px;
  border: 1px solid var(--md-outline-variant);
}

.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.review-date {
  color: var(--md-outline);
}

.review-rating {
  margin-bottom: 12px;
}

.star-small {
  color: #E0E0E0;
  font-size: 14px;
}

.star-small.active {
  color: #FFC107;
}

.review-content {
  color: var(--md-on-surface);
  line-height: 1.6;
}

.empty-reviews {
  text-align: center;
  padding: 40px;
  color: var(--md-outline);
}

@media (max-width: 768px) {
  .book-detail-card {
    flex-direction: column;
    padding: 24px;
    gap: 24px;
  }
  
  .book-cover-large {
    width: 160px;
    height: 220px;
    align-self: center;
  }
}
</style>

<template>
  <div class="book-card md-card-elevated" @click="goToDetail">
    <div class="book-cover">
      <img v-if="book.cover" :src="book.cover" alt="封面" />
      <div v-else class="cover-placeholder">
        <span>📖</span>
      </div>
    </div>
    <div class="book-content">
      <div class="book-header">
        <span class="category-chip">{{ book.category }}</span>
        <span :class="['stock-badge', { unavailable: book.available_count === 0 }]">
          {{ book.available_count > 0 ? `剩余 ${book.available_count}` : '已借完' }}
        </span>
      </div>
      <h3 class="book-title title-medium">{{ book.title }}</h3>
      <p class="book-author body-medium">{{ book.author }}</p>
      <p class="book-isbn body-small" v-if="book.isbn">ISBN: {{ book.isbn }}</p>
    </div>
    <div class="book-actions">
      <button 
        class="borrow-btn md-filled-button"
        :disabled="book.available_count === 0"
        @click.stop="$emit('borrow', book)"
      >
        {{ book.available_count > 0 ? '借阅' : '暂无库存' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps(['book'])
defineEmits(['borrow'])

const router = useRouter()
const goToDetail = () => {
  router.push(`/book/${props.book.id}`)
}
</script>

<style scoped>
.book-card {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--md-elevation-3);
}

.book-cover {
  width: 100%;
  height: 220px;
  background: var(--md-surface-container-high);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 12px;
}

.book-cover img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: var(--md-shape-corner-small);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.cover-placeholder {
  font-size: 48px;
  opacity: 0.7;
}

.book-content {
  padding: 16px;
  flex: 1;
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--md-shape-corner-small);
  background: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
  font-size: 12px;
  font-weight: 500;
}

.stock-badge {
  font-size: 12px;
  font-weight: 500;
  color: var(--md-tertiary);
}

.stock-badge.unavailable {
  color: var(--md-error);
}

.book-title {
  color: var(--md-on-surface);
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author {
  color: var(--md-on-surface-variant);
  margin-bottom: 4px;
}

.book-isbn {
  color: var(--md-outline);
}

.book-actions {
  padding: 12px 16px 16px;
}

.borrow-btn {
  width: 100%;
  height: 44px;
}

.borrow-btn:disabled {
  background: var(--md-surface-container-highest);
  color: var(--md-on-surface-variant);
  box-shadow: none;
}
</style>

<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-brand">
        <span class="brand-icon">📚</span>
        <span class="brand-text title-medium">图书馆</span>
      </router-link>
      
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchInput"
          placeholder="搜索书名、作者..."
          @input="handleSearch"
          class="search-input"
        />
      </div>

      <div class="nav-items">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <span class="nav-icon">🏠</span>
          <span class="nav-label label-medium">主页</span>
        </router-link>
        <router-link to="/category" class="nav-item" :class="{ active: $route.path === '/category' }">
          <span class="nav-icon">📂</span>
          <span class="nav-label label-medium">分类</span>
        </router-link>
        <router-link to="/profile" class="nav-item" :class="{ active: $route.path === '/profile' }">
          <span class="nav-icon">👤</span>
          <span class="nav-label label-medium">我的</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['search'])
const searchInput = ref('')

const handleSearch = () => {
  emit('search', searchInput.value)
}
</script>

<style scoped>
.navbar {
  background: var(--md-surface);
  box-shadow: var(--md-elevation-1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.brand-icon {
  font-size: 28px;
}

.brand-text {
  color: var(--md-primary);
  font-weight: 600;
}

.search-container {
  flex: 1;
  max-width: 480px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  opacity: 0.7;
}

.search-input {
  width: 100%;
  height: 48px;
  padding: 0 16px 0 48px;
  border: none;
  border-radius: var(--md-shape-corner-full);
  background: var(--md-surface-container-high);
  font-size: 16px;
  color: var(--md-on-surface);
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
}

.search-input::placeholder {
  color: var(--md-on-surface-variant);
}

.search-input:focus {
  outline: none;
  background: var(--md-surface-container-highest);
  box-shadow: var(--md-elevation-2);
}

.nav-items {
  display: flex;
  gap: 4px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 20px;
  border-radius: var(--md-shape-corner-large);
  text-decoration: none;
  color: var(--md-on-surface-variant);
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
}

.nav-item:hover {
  background: var(--md-surface-container);
}

.nav-item.active {
  background: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
}

.nav-icon {
  font-size: 22px;
}

.nav-label {
  font-size: 12px;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 8px 16px;
    gap: 12px;
  }
  
  .brand-text {
    display: none;
  }
  
  .search-container {
    max-width: none;
  }
  
  .nav-label {
    display: none;
  }
  
  .nav-item {
    padding: 12px 16px;
  }
}
</style>

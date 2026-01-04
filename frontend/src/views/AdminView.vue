<template>
  <div class="admin-page">
    <!-- Top Navigation -->
    <nav class="admin-nav">
      <div class="nav-left">
        <span class="nav-brand title-large">📚 图书管理系统</span>
        <span class="role-chip">管理员</span>
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
        <!-- Book Management -->
        <div v-if="activeMenu === 'books'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">图书管理</h2>
            <button class="md-filled-button" @click="openBookModal()">
              <span>+</span> 上架新书
            </button>
          </div>
          
          <div class="search-container">
            <span class="search-icon">🔍</span>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="搜索书名、作者、ISBN..."
              class="search-input"
              @input="handleSearch"
            />
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>封面</th>
                  <th>书名</th>
                  <th>作者</th>
                  <th>分类</th>
                  <th>ISBN</th>
                  <th>库存</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="book in books" :key="book.id">
                  <td>
                    <div class="book-thumb">
                      <img v-if="book.cover" :src="book.cover" />
                      <span v-else>📖</span>
                    </div>
                  </td>
                  <td class="title-cell">{{ book.title }}</td>
                  <td>{{ book.author }}</td>
                  <td><span class="category-chip">{{ book.category }}</span></td>
                  <td class="isbn-cell">{{ book.isbn || '-' }}</td>
                  <td>{{ book.available_count }} / {{ book.total_count }}</td>
                  <td>
                    <div class="action-buttons">
                      <button class="md-tonal-button btn-sm" @click="openBookModal(book)">编辑</button>
                      <button class="md-text-button btn-sm danger" @click="handleDeleteBook(book)">下架</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="pagination">
            <button class="md-tonal-button" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">上一页</button>
            <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页，共 {{ totalBooks }} 本</span>
            <button class="md-tonal-button" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">下一页</button>
          </div>
        </div>

        <!-- User Management (Student ID Entry) -->
        <div v-if="activeMenu === 'users'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">学号录入</h2>
          </div>

          <!-- Add User Form -->
          <div class="add-user-section card-outlined">
            <h3 class="title-medium">添加新用户</h3>
            <div class="form-row">
              <div class="form-group">
                <input 
                  type="text" 
                  v-model="userForm.student_id" 
                  placeholder="学号 *" 
                  class="input-field"
                />
              </div>
              <div class="form-group">
                <input 
                  type="text" 
                  v-model="userForm.name" 
                  placeholder="姓名 *" 
                  class="input-field"
                />
              </div>
              <button class="md-filled-button" @click="handleAddUser" :disabled="!userForm.student_id || !userForm.name">
                添加学生
              </button>
            </div>
            <p class="body-small text-secondary">默认密码为 12345678</p>
          </div>
          
          <div class="search-container">
            <span class="search-icon">🔍</span>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="搜索学号、姓名..."
              class="search-input"
              @input="handleSearch"
            />
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>学号</th>
                  <th>姓名</th>
                  <th>角色</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td>{{ u.student_id }}</td>
                  <td>{{ u.name }}</td>
                  <td>
                    <span :class="['role-chip', u.role === 'admin' ? 'admin' : 'student']">
                      {{ u.role === 'admin' ? '管理员' : '学生' }}
                    </span>
                  </td>
                  <td>
                    <button 
                      v-if="u.role !== 'admin'"
                      class="md-text-button error-text"
                      @click="handleDeleteUser(u)"
                    >
                      删除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="totalPages > 1" class="pagination">
            <button class="md-tonal-button" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">上一页</button>
            <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
            <button class="md-tonal-button" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">下一页</button>
          </div>
        </div>

        <!-- Borrow Records -->
        <div v-if="activeMenu === 'records'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">借阅记录</h2>
            <div class="header-actions">
              <div class="search-container small">
                <span class="search-icon">🔍</span>
                <input 
                  type="text" 
                  v-model="recordSearchTerm" 
                  placeholder="搜学号/姓名/ISBN..."
                  class="search-input"
                  @input="handleRecordSearch"
                />
              </div>
              <select v-model="recordFilter" class="filter-select">
                <option value="">全部状态</option>
                <option value="borrowed">借阅中</option>
                <option value="returned">已归还</option>
              </select>
            </div>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>图书</th>
                  <th>借阅人</th>
                  <th>学号</th>
                  <th>借阅日期</th>
                  <th>应还日期</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in records" :key="record.id">
                  <td>{{ record.book_title }}</td>
                  <td>{{ record.user_name }}</td>
                  <td>{{ record.student_id }}</td>
                  <td>{{ formatDate(record.borrow_date) }}</td>
                  <td>{{ formatDate(record.due_date) }}</td>
                  <td>
                    <span :class="['status-chip', record.status]">
                      {{ record.status === 'borrowed' ? '借阅中' : '已归还' }}
                    </span>
                  </td>
                  <td>
                    <button 
                      v-if="record.status === 'borrowed'"
                      class="md-tonal-button btn-sm"
                      @click="handleReturn(record)"
                    >
                      确认归还
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Scan Return -->
        <div v-if="activeMenu === 'scanReturn'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">扫码还书</h2>
          </div>

          <div class="scan-return-container">
            <!-- Scan buttons -->
            <div class="scan-buttons">
              <button type="button" class="scan-btn" @click="startReturnCameraScan">
                📷 摄像头扫码
              </button>
              <button type="button" class="scan-btn" @click="triggerReturnImageUpload">
                🖼️ 图片扫码
              </button>
              <input 
                type="file" 
                ref="returnImageInput" 
                accept="image/*" 
                style="display: none" 
                @change="handleReturnImageScan"
              />
            </div>

            <!-- Camera scanner -->
            <div v-if="showReturnScanner" class="scanner-container">
              <div id="return-qr-reader"></div>
              <button type="button" class="md-text-button" @click="stopReturnCameraScan">
                停止扫描
              </button>
            </div>

            <!-- Image preview -->
            <div v-if="returnScanImagePreview" class="image-preview">
              <img :src="returnScanImagePreview" alt="扫描图片" />
              <div v-if="returnScanLoading" class="scan-loading">
                正在识别条形码...
              </div>
            </div>

            <div class="scan-input-section">
              <!-- Student ID -->
              <div class="form-group">
                <label class="label-medium">学号 *</label>
                <input 
                  type="text" 
                  v-model="returnStudentId" 
                  placeholder="输入借阅人学号"
                />
              </div>
              
              <!-- ISBN -->
              <div class="form-group">
                <label class="label-medium">ISBN</label>
                <div class="isbn-row">
                  <input 
                    type="text" 
                    v-model="returnIsbn" 
                    placeholder="扫描或手动输入ISBN"
                    @keyup.enter="handleScanReturn"
                    ref="returnIsbnInput"
                  />
                  <button 
                    class="md-filled-button"
                    @click="handleScanReturn"
                    :disabled="!returnIsbn || !returnStudentId || returnLoading"
                  >
                    {{ returnLoading ? '处理中...' : '还书' }}
                  </button>
                </div>
              </div>
              
              <p class="scan-hint body-small">提示：先输入学号，再扫描图书ISBN。摄像头或图片扫码后自动填充ISBN。</p>
            </div>

            <div v-if="returnResult" :class="['return-result', returnResult.success ? 'success' : 'error']">
              <span class="result-icon">{{ returnResult.success ? '✓' : '✗' }}</span>
              <span class="result-message">{{ returnResult.message }}</span>
            </div>

            <div v-if="returnHistory.length > 0" class="return-history">
              <h3 class="title-medium">还书记录</h3>
              <div class="history-list">
                <div 
                  v-for="(item, index) in returnHistory" 
                  :key="index" 
                  :class="['history-item', item.success ? 'success' : 'error']"
                >
                  <span class="history-time">{{ item.time }}</span>
                  <span class="history-student">{{ item.studentId }}</span>
                  <span class="history-isbn">{{ item.isbn }}</span>
                  <span class="history-message">{{ item.message }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>


        <!-- Overdue Management -->
        <div v-if="activeMenu === 'overdue'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">逾期管理</h2>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>图书</th>
                  <th>借阅人</th>
                  <th>学号</th>
                  <th>应还日期</th>
                  <th>逾期天数</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in overdueRecords" :key="record.id" class="overdue-row">
                  <td>{{ record.book_title }}</td>
                  <td>{{ record.user_name }}</td>
                  <td>{{ record.student_id }}</td>
                  <td>{{ formatDate(record.due_date) }}</td>
                  <td class="overdue-days">{{ Math.floor(record.overdue_days) }} 天</td>
                  <td>
                    <button class="md-tonal-button btn-sm" @click="handleReturn(record)">
                      确认归还
                    </button>
                  </td>
                </tr>
                <tr v-if="overdueRecords.length === 0">
                  <td colspan="6" class="empty-cell">
                    <span class="empty-icon">🎉</span>
                    <span>暂无逾期记录</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>

        <!-- Batch Operations -->
        <div v-if="activeMenu === 'batch'" class="panel">
          <div class="panel-header">
            <h2 class="headline-small">批量操作</h2>
          </div>
          
          <div class="batch-section">
            <h3 class="title-medium">图书批量操作</h3>
            <div class="batch-actions">
               <button class="md-outlined-button" @click="handleExportBooks">
                 📤 导出图书 (Excel)
               </button>
               
               <div class="import-box">
                 <input 
                   type="file" 
                   accept=".xlsx, .xls"
                   ref="bookImportInput"
                   style="display: none"
                   @change="handleImportBooks"
                 />
                 <button class="md-filled-button" @click="$refs.bookImportInput.click()">
                   📥 导入图书 (Excel)
                 </button>
                 <p class="body-small hint-text">需包含列：title, author, isbn, category</p>
               </div>
            </div>
            
            <div class="divider"></div>
            
            <h3 class="title-medium">用户批量操作</h3>
            <div class="batch-actions">
               <button class="md-outlined-button" @click="handleExportUsers">
                 📤 导出用户 (Excel)
               </button>
               
               <div class="import-box">
                 <input 
                   type="file" 
                   accept=".xlsx, .xls"
                   ref="userImportInput"
                   style="display: none"
                   @change="handleImportUsers"
                 />
                 <button class="md-filled-button" @click="$refs.userImportInput.click()">
                   📥 导入用户 (Excel)
                 </button>
                 <p class="body-small hint-text">需包含列：student_id, name</p>
               </div>
            </div>
          </div>
        </div>
    </div>

    <!-- Add/Edit Book Dialog -->
    <div v-if="showBookModal" class="md-dialog-scrim" @click.self="closeBookModal">
      <div class="md-dialog book-dialog">
        <h3 class="md-dialog-title">{{ editingBook ? '编辑图书' : '上架新书' }}</h3>
        
        <!-- ISBN Scanning Section -->
        <div v-if="!editingBook" class="scan-section">
          <div class="scan-buttons">
            <button type="button" class="scan-btn" @click="startCameraScan">
              📷 摄像头扫码
            </button>
            <button type="button" class="scan-btn" @click="triggerImageUpload">
              🖼️ 图片扫码
            </button>
            <input 
              type="file" 
              ref="imageInput" 
              accept="image/*" 
              style="display: none" 
              @change="handleImageScan"
            />
          </div>
          
          <div v-if="showScanner" class="scanner-container">
            <div id="qr-reader"></div>
            <button type="button" class="md-text-button" @click="stopCameraScan">
              停止扫描
            </button>
          </div>
          
          <div v-if="scanImagePreview" class="image-preview">
            <img :src="scanImagePreview" alt="扫描图片" />
            <div v-if="scanLoading" class="scan-loading">
              正在识别条形码...
            </div>
          </div>
        </div>

        <form @submit.prevent="handleSaveBook" class="book-form">
          <div class="form-layout">
            <!-- Cover Preview -->
            <div class="cover-section">
              <div class="cover-preview">
                <img v-if="bookForm.cover" :src="bookForm.cover" alt="封面" />
                <div v-else class="no-cover">
                  <span>📖</span>
                  <p class="body-small">暂无封面</p>
                </div>
              </div>
              <p v-if="fetchingInfo" class="fetching-text body-small">正在获取图书信息...</p>
            </div>
            
            <!-- Form Fields -->
            <div class="form-fields">
              <div class="form-group">
                <label class="label-medium">ISBN</label>
                <div class="isbn-row">
                  <input 
                    type="text" 
                    v-model="bookForm.isbn" 
                    placeholder="扫描或手动输入"
                    @blur="handleIsbnBlur"
                  />
                  <button 
                    type="button" 
                    class="md-tonal-button"
                    @click="fetchBookInfo"
                    :disabled="!bookForm.isbn || fetchingInfo"
                  >
                    获取
                  </button>
                </div>
              </div>
              <div class="form-group">
                <label class="label-medium">书名 *</label>
                <input type="text" v-model="bookForm.title" required />
              </div>
              <div class="form-group">
                <label class="label-medium">作者 *</label>
                <input type="text" v-model="bookForm.author" required />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="label-medium">分类</label>
                  <select v-model="bookForm.category">
                    <option value="编程">编程</option>
                    <option value="文学">文学</option>
                    <option value="科技">科技</option>
                    <option value="科幻">科幻</option>
                    <option value="艺术">艺术</option>
                    <option value="历史">历史</option>
                    <option value="经济">经济</option>
                    <option value="其它">其它</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="label-medium">库存</label>
                  <input type="number" v-model.number="bookForm.total_count" min="1" />
                </div>
              </div>
            </div>
          </div>
          
          <div class="md-dialog-actions">
            <button type="button" class="md-text-button" @click="closeBookModal">取消</button>
            <button type="submit" class="md-filled-button" :disabled="fetchingInfo">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Html5Qrcode } from 'html5-qrcode'
import { bookApi, borrowApi, userApi, batchApi } from '../api'

const router = useRouter()
const user = ref(null)
const activeMenu = ref('books')
const searchTerm = ref('')
const recordSearchTerm = ref('')
const recordFilter = ref('')

const menuItems = [
  { id: 'books', icon: '📖', label: '图书管理' },
  { id: 'users', icon: '👥', label: '学号录入' },
  { id: 'records', icon: '📋', label: '借阅记录' },
  { id: 'scanReturn', icon: '📷', label: '扫码还书' },
  { id: 'batch', icon: '⚡', label: '批量操作' },
  { id: 'overdue', icon: '⚠️', label: '逾期管理' }
]

const books = ref([])
const records = ref([])
const overdueRecords = ref([])

// Pagination state
const currentPage = ref(1)
const pageSize = ref(20)
const totalBooks = ref(0)
const totalPages = ref(1)

const showBookModal = ref(false)
const editingBook = ref(null)
const bookForm = ref({
  title: '',
  author: '',
  isbn: '',
  category: '编程',
  cover: '',
  total_count: 1
})

// Scanning state
const showScanner = ref(false)
const scanImagePreview = ref('')
const scanLoading = ref(false)
const fetchingInfo = ref(false)
const imageInput = ref(null)
let html5QrCode = null

// Scan return state
const returnIsbn = ref('')
const returnStudentId = ref('')
const returnLoading = ref(false)
const returnResult = ref(null)
const returnHistory = ref([])
const returnIsbnInput = ref(null)
const returnImageInput = ref(null)
const showReturnScanner = ref(false)
const returnScanImagePreview = ref('')
const returnScanLoading = ref(false)
let returnHtml5QrCode = null

// User Management state
const users = ref([])
const userForm = ref({
  student_id: '',
  name: ''
})

const loadUsers = async () => {
  try {
    const res = await userApi.getList({ 
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchTerm.value 
    })
    users.value = res.items
    totalBooks.value = res.total // Reuse totalBooks or add totalUsers variable. Let's assume using totalBooks for shared pagination or add totalUsers.
    // Wait, let's reuse totalBooks or check if we need separate total.
    // Looking at template: <div v-if="totalPages > 1" class="pagination">
    // It uses totalPages which is computed?
    // Let me check totalPages computation first.
    
    // Viewing file above showed:
    // const totalBooks = ref(0)
    // const totalPages = ref(1)
    
    // I should update totalBooks (which seems to serve as totalItems for the current view) and recalculate totalPages.
    totalBooks.value = res.total
    totalPages.value = Math.ceil(res.total / pageSize.value)
  } catch (e) {
    console.error('Failed to load users:', e)
  }
}

const handleAddUser = async () => {
  if (!userForm.value.student_id || !userForm.value.name) return
  
  try {
    await userApi.create(userForm.value)
    alert('用户添加成功')
    userForm.value = { student_id: '', name: '' } // Reset form
    loadUsers()
  } catch (e) {
    alert(e.detail || '添加失败')
  }
}

const handleDeleteUser = async (user) => {
  if (!confirm(`确认删除用户 ${user.name} (${user.student_id})？\n此操作不可恢复！`)) return
  
  try {
    await userApi.delete(user.id)
    alert('用户已删除')
    loadUsers()
  } catch (e) {
    alert(e.detail || '删除失败')
  }
}

// Search with debounce
let searchTimeout = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadBooks()
  }, 300)
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadBooks()
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// Scanning functions
const startCameraScan = async () => {
  showScanner.value = true
  scanImagePreview.value = ''
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  html5QrCode = new Html5Qrcode("qr-reader")
  
  try {
    await html5QrCode.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 250, height: 150 } },
      (decodedText) => {
        bookForm.value.isbn = decodedText
        stopCameraScan()
        fetchBookInfo()
      },
      () => {}
    )
  } catch (err) {
    console.error('Camera error:', err)
    alert('无法启动摄像头，请使用图片扫描')
    showScanner.value = false
  }
}

const stopCameraScan = async () => {
  if (html5QrCode && html5QrCode.isScanning) {
    await html5QrCode.stop()
  }
  showScanner.value = false
}

const triggerImageUpload = () => {
  imageInput.value?.click()
}

const handleImageScan = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  scanImagePreview.value = URL.createObjectURL(file)
  scanLoading.value = true
  
  try {
    const scanner = new Html5Qrcode("temp-scanner", { verbose: false })
    const decodedText = await scanner.scanFile(file, true)
    
    bookForm.value.isbn = decodedText
    scanLoading.value = false
    
    setTimeout(() => {
      scanImagePreview.value = ''
      fetchBookInfo()
    }, 1000)
    
  } catch (err) {
    scanLoading.value = false
    alert('未能识别条形码，请手动输入ISBN')
  }
  
  event.target.value = ''
}

const handleIsbnBlur = () => {
  if (bookForm.value.isbn && !bookForm.value.title) {
    fetchBookInfo()
  }
}

const fetchBookInfo = async () => {
  const isbn = bookForm.value.isbn?.toString().toUpperCase().replace(/[^0-9X]/g, '')
  if (!isbn || isbn.length < 10) return
  
  fetchingInfo.value = true
  
  try {
    // Open Library API
    const response = await fetch(
      `https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&format=json&jscmd=data`
    )
    const data = await response.json()
    const bookKey = `ISBN:${isbn}`
    
    if (data[bookKey]) {
      const info = data[bookKey]
      bookForm.value.title = info.title || bookForm.value.title
      if (info.authors) {
        bookForm.value.author = info.authors.map(a => a.name).join(', ')
      }
      if (info.cover?.large || info.cover?.medium) {
        bookForm.value.cover = info.cover.large || info.cover.medium
      }
      
      fetchingInfo.value = false
      return
    }
    
    // Google Books API fallback
    const gResponse = await fetch(
      `https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`
    )
    const gData = await gResponse.json()
    
    if (gData.items?.length > 0) {
      const volumeInfo = gData.items[0].volumeInfo
      bookForm.value.title = volumeInfo.title || bookForm.value.title
      if (volumeInfo.authors) {
        bookForm.value.author = volumeInfo.authors.join(', ')
      }
      if (volumeInfo.imageLinks?.thumbnail) {
        bookForm.value.cover = volumeInfo.imageLinks.thumbnail.replace('zoom=1', 'zoom=2')
      }
      
      fetchingInfo.value = false
      return
    }
    
    alert('未找到图书信息，请手动填写')
  } catch (err) {
    alert('获取图书信息失败')
  }
  
  fetchingInfo.value = false
}

// Book management
const openBookModal = (book = null) => {
  editingBook.value = book
  if (book) {
    bookForm.value = { ...book }
  } else {
    bookForm.value = {
      title: '',
      author: '',
      isbn: '',
      category: '编程',
      cover: '',
      total_count: 1
    }
  }
  showBookModal.value = true
}

const closeBookModal = () => {
  stopCameraScan()
  scanImagePreview.value = ''
  showBookModal.value = false
}

const handleSaveBook = async () => {
  try {
    if (editingBook.value) {
      await bookApi.update(editingBook.value.id, bookForm.value)
      alert('更新成功')
    } else {
      await bookApi.create(bookForm.value)
      alert('上架成功')
    }
    closeBookModal()
    loadBooks()
  } catch (e) {
    alert(e.detail || '操作失败')
  }
}

const handleDeleteBook = async (book) => {
  if (!confirm(`确认下架《${book.title}》？`)) return
  try {
    await bookApi.delete(book.id)
    alert('下架成功')
    loadBooks()
  } catch (e) {
    alert(e.detail || '下架失败')
  }
}

const handleReturn = async (record) => {
  if (!confirm('确认该图书已归还？')) return
  try {
    await borrowApi.return(record.id)
    alert('归还成功')
    loadRecords()
    loadOverdue()
  } catch (e) {
    alert(e.detail || '操作失败')
  }
}

// Scan return function
const handleScanReturn = async () => {
  if (!returnIsbn.value || !returnStudentId.value) return
  
  returnLoading.value = true
  returnResult.value = null
  
  const isbn = returnIsbn.value.trim()
  const studentId = returnStudentId.value.trim()
  
  try {
    const res = await borrowApi.returnByIsbn(isbn, studentId)
    returnResult.value = {
      success: true,
      message: res.message
    }
    
    // Add to history
    returnHistory.value.unshift({
      time: new Date().toLocaleTimeString('zh-CN'),
      studentId: studentId,
      isbn: isbn,
      message: res.message,
      success: true
    })
    
    // Clear ISBN input and refocus (keep student ID for batch return)
    returnIsbn.value = ''
    returnIsbnInput.value?.focus()
    
    // Refresh records
    loadRecords()
    loadOverdue()
    
  } catch (e) {
    const errorMsg = e.detail || '还书失败'
    returnResult.value = {
      success: false,
      message: errorMsg
    }
    
    returnHistory.value.unshift({
      time: new Date().toLocaleTimeString('zh-CN'),
      studentId: studentId,
      isbn: isbn,
      message: errorMsg,
      success: false
    })
  }
  
  returnLoading.value = false
}

// Return scanner - camera
const startReturnCameraScan = async () => {
  showReturnScanner.value = true
  returnScanImagePreview.value = ''
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  returnHtml5QrCode = new Html5Qrcode("return-qr-reader")
  
  try {
    await returnHtml5QrCode.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 250, height: 150 } },
      (decodedText) => {
        returnIsbn.value = decodedText
        stopReturnCameraScan()
      },
      () => {}
    )
  } catch (err) {
    console.error('Camera error:', err)
    alert('无法启动摄像头，请使用图片扫描')
    showReturnScanner.value = false
  }
}

const stopReturnCameraScan = async () => {
  if (returnHtml5QrCode && returnHtml5QrCode.isScanning) {
    await returnHtml5QrCode.stop()
  }
  showReturnScanner.value = false
}

// Return scanner - image
const triggerReturnImageUpload = () => {
  returnImageInput.value?.click()
}

const handleReturnImageScan = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  returnScanImagePreview.value = URL.createObjectURL(file)
  returnScanLoading.value = true
  
  try {
    const scanner = new Html5Qrcode("temp-return-scanner", { verbose: false })
    const decodedText = await scanner.scanFile(file, true)
    
    returnIsbn.value = decodedText
    returnScanLoading.value = false
    
    setTimeout(() => {
      returnScanImagePreview.value = ''
    }, 1000)
    
  } catch (err) {
    returnScanLoading.value = false
    alert('未能识别条形码，请手动输入ISBN')
  }
  
  event.target.value = ''
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
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
    console.error('Failed to load books', e)
  }
}

// 借阅记录相关
const loadRecords = async () => {
  try {
    const params = {
      keyword: recordSearchTerm.value || undefined,
      status: recordFilter.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    records.value = await borrowApi.getRecords(params)
    // Note: getRecords backend currently returns list. 
    // If I want pagination, I need backend to return total.
    // For now, let's just make search work.
  } catch (e) {
    console.error('Failed to load records', e)
  }
}

// Record search with debounce
let recordSearchTimeout = null
const handleRecordSearch = () => {
  clearTimeout(recordSearchTimeout)
  recordSearchTimeout = setTimeout(() => {
    // currentPage.value = 1 // Should reset page if pagination supported
    loadRecords()
  }, 300)
}

const loadOverdue = async () => {
  try {
    overdueRecords.value = await borrowApi.getOverdue()
  } catch (e) {
    console.error('Failed to load overdue', e)
  }
}

watch(recordFilter, loadRecords)

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
  }
  loadBooks()
  loadRecords()
  loadOverdue()
})

watch(activeMenu, (newVal) => {
  if (newVal === 'books') loadBooks()
  else if (newVal === 'users') loadUsers()
  else if (newVal === 'records') loadRecords()
  else if (newVal === 'overdue') loadOverdue()
})

onUnmounted(() => {
  stopCameraScan()
})

const bookImportInput = ref(null)
const userImportInput = ref(null)

const handleExportBooks = async () => {
  try {
    const blob = await batchApi.exportBooks()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `books_export_${new Date().toISOString().slice(0,10)}.xlsx`
    link.click()
  } catch (e) {
    alert('导出失败')
  }
}

const handleExportUsers = async () => {
  try {
    const blob = await batchApi.exportUsers()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `users_export_${new Date().toISOString().slice(0,10)}.xlsx`
    link.click()
  } catch (e) {
    alert('导出失败')
  }
}

const handleImportBooks = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    const res = await batchApi.importBooks(file)
    alert(res.message)
    loadBooks()
  } catch (e) {
    alert(e.detail || '导入失败')
  }
  e.target.value = ''
}

const handleImportUsers = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    const res = await batchApi.importUsers(file)
    alert(res.message)
    loadUsers()
  } catch (e) {
    alert(e.detail || '导入失败')
  }
  e.target.value = ''
}


</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: var(--md-surface-container-lowest);
}

.admin-nav {
  background: var(--md-surface);
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--md-elevation-1);
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
  color: var(--md-primary);
}

.role-chip {
  background: var(--md-primary-container);
  color: var(--md-on-primary-container);
  padding: 4px 12px;
  border-radius: var(--md-shape-corner-full);
  font-size: 12px;
  font-weight: 500;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  color: var(--md-on-surface-variant);
}

.logout-btn {
  height: 36px;
  padding: 0 16px;
}

.admin-layout {
  display: flex;
}

.sidebar {
  width: 240px;
  background: var(--md-surface);
  min-height: calc(100vh - 64px);
  padding: 16px 12px;
  box-shadow: var(--md-elevation-1);
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border: none;
  background: transparent;
  border-radius: var(--md-shape-corner-full);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  color: var(--md-on-surface-variant);
  margin-bottom: 4px;
}

.menu-item:hover {
  background: var(--md-surface-container);
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
}

.panel {
  background: var(--md-surface);
  border-radius: var(--md-shape-corner-large);
  padding: 24px;
  box-shadow: var(--md-elevation-1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.panel-header h2 {
  color: var(--md-on-surface);
}

.search-container {
  position: relative;
  max-width: 400px;
  margin-bottom: 24px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  opacity: 0.6;
}

.search-input {
  width: 100%;
  height: 48px;
  padding: 0 16px 0 48px;
  border: none;
  border-radius: var(--md-shape-corner-full);
  background: var(--md-surface-container-high);
  font-size: 14px;
  color: var(--md-on-surface);
}

.search-input:focus {
  outline: none;
  background: var(--md-surface-container-highest);
}

.filter-select {
  padding: 8px 16px;
  border: 1px solid var(--md-outline);
  border-radius: var(--md-shape-corner-small);
  background: var(--md-surface);
  font-size: 14px;
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
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--md-outline-variant);
}

.data-table th {
  color: var(--md-on-surface-variant);
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-table td {
  color: var(--md-on-surface);
  font-size: 14px;
}

.book-thumb {
  width: 40px;
  height: 56px;
  border-radius: var(--md-shape-corner-extra-small);
  background: var(--md-surface-container);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.book-thumb img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 4px;
}

.title-cell {
  font-weight: 500;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.isbn-cell {
  font-family: monospace;
  font-size: 13px;
  color: var(--md-on-surface-variant);
}

.category-chip {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--md-shape-corner-small);
  background: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
  font-size: 12px;
  font-weight: 500;
}

.status-chip {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--md-shape-corner-small);
  font-size: 12px;
  font-weight: 500;
}

.status-chip.borrowed {
  background: var(--md-tertiary-container);
  color: var(--md-on-tertiary-container);
}

.status-chip.returned {
  background: var(--md-primary-container);
  color: var(--md-on-primary-container);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  height: 32px;
  padding: 0 12px;
  font-size: 13px;
}

.btn-sm.danger {
  color: var(--md-error);
}

.overdue-row {
  background: var(--md-error-container);
}

.overdue-days {
  color: var(--md-error);
  font-weight: 600;
}

.empty-cell {
  text-align: center;
  padding: 48px !important;
  color: var(--md-on-surface-variant);
}

.empty-icon {
  font-size: 32px;
  margin-right: 12px;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--md-outline-variant);
}

.page-info {
  color: var(--md-on-surface-variant);
  font-size: 14px;
}

/* Book Dialog */
.book-dialog {
  width: 95%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.scan-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--md-outline-variant);
}

.scan-buttons {
  display: flex;
  gap: 12px;
}

.scan-btn {
  flex: 1;
  padding: 16px;
  border: 2px dashed var(--md-outline);
  border-radius: var(--md-shape-corner-medium);
  background: var(--md-surface-container-low);
  color: var(--md-on-surface-variant);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.scan-btn:hover {
  background: var(--md-surface-container);
  border-color: var(--md-primary);
  color: var(--md-primary);
}

.scanner-container {
  margin-top: 16px;
}

#qr-reader {
  border-radius: var(--md-shape-corner-medium);
  overflow: hidden;
}

.image-preview {
  margin-top: 16px;
  position: relative;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: var(--md-shape-corner-medium);
}

.scan-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 12px 24px;
  border-radius: var(--md-shape-corner-small);
  font-size: 14px;
}

.book-form {
  margin-top: 16px;
}

.form-layout {
  display: flex;
  gap: 24px;
}

.cover-section {
  flex-shrink: 0;
  text-align: center;
}

.cover-preview {
  width: 120px;
  height: 160px;
  border-radius: var(--md-shape-corner-medium);
  background: var(--md-surface-container);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: var(--md-elevation-2);
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  text-align: center;
  color: var(--md-on-surface-variant);
}

.no-cover span {
  font-size: 40px;
}

.fetching-text {
  margin-top: 8px;
  color: var(--md-primary);
}

.form-fields {
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--md-on-surface-variant);
}

.form-group input,
.form-group select {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  border: 1px solid var(--md-outline);
  border-radius: var(--md-shape-corner-extra-small);
  background: var(--md-surface);
  font-size: 14px;
  color: var(--md-on-surface);
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border: 2px solid var(--md-primary);
}

.isbn-row {
  display: flex;
  gap: 8px;
}

.isbn-row input {
  flex: 1;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .form-layout {
    flex-direction: column;
  }
  
  .cover-section {
    display: flex;
    justify-content: center;
  }
}



.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-container.small {
  margin: 0;
  width: 250px;
}

.search-container.small .search-input {
  height: 36px;
  font-size: 13px;
}

/* Scan Return Styles */
.scan-return-container {
  max-width: 600px;
}

.scan-input-section {
  margin-bottom: 24px;
}

.scan-hint {
  margin-top: 8px;
  color: var(--md-on-surface-variant);
}

.return-result {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: var(--md-shape-corner-medium);
  margin-bottom: 24px;
  font-size: 16px;
}

.return-result.success {
  background: var(--md-tertiary-container);
  color: var(--md-on-tertiary-container);
}

.return-result.error {
  background: var(--md-error-container);
  color: var(--md-on-error-container);
}

.result-icon {
  font-size: 24px;
  font-weight: bold;
}

.return-history {
  margin-top: 32px;
}

.return-history h3 {
  margin-bottom: 16px;
  color: var(--md-on-surface);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: var(--md-shape-corner-small);
  font-size: 14px;
}

.history-item.success {
  background: var(--md-surface-container);
}

.history-item.error {
  background: var(--md-error-container);
  opacity: 0.8;
}

.history-time {
  color: var(--md-on-surface-variant);
  font-size: 12px;
  min-width: 70px;
}

.history-isbn {
  font-family: monospace;
  color: var(--md-on-surface-variant);
  min-width: 140px;
}

.history-student {
  color: var(--md-primary);
  font-weight: 500;
  min-width: 90px;
}


.history-message {
  flex: 1;
  color: var(--md-on-surface);
}
</style>

<style scoped>
/* User Management Styles */
.add-user-section {
  padding: 16px;
  margin-bottom: 24px;
  background: var(--md-surface-container-low);
  border-radius: var(--md-shape-corner-medium);
}

.add-user-section .title-medium {
  margin-bottom: 16px;
  color: var(--md-on-surface);
}

.add-user-section .form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.add-user-section .form-group {
  flex: 1;
  margin-bottom: 0;
}

.add-user-section .input-field {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--md-outline);
  border-radius: var(--md-shape-corner-small);
  background: var(--md-surface);
  color: var(--md-on-surface);
}

.add-user-section .md-filled-button {
  height: 40px;
  padding: 0 24px;
}

.role-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.role-chip.admin {
  background-color: var(--md-primary-container);
  color: var(--md-on-primary-container);
}

.role-chip.student {
  background-color: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
}

.batch-section {
  max-width: 600px;
}

.batch-section h3 {
  margin-bottom: 16px;
  color: var(--md-on-surface);
}

.batch-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 32px;
}

.import-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hint-text {
  color: var(--md-on-surface-variant);
  opacity: 0.8;
}

.divider {
  height: 1px;
  background: var(--md-outline-variant);
  margin: 24px 0;
}
</style>

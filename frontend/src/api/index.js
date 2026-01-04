import axios from 'axios'

// API 基础配置
const api = axios.create({
    baseURL: import.meta.env.DEV ? 'http://localhost:18050' : '',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器 - 添加 token
api.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => Promise.reject(error)
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            window.location.href = '/login'
        }
        return Promise.reject(error.response?.data || error)
    }
)

// ==================== 认证 API ====================

export const authApi = {
    login: (student_id, password) =>
        api.post('/api/auth/login', { student_id, password }),

    changePassword: (old_password, new_password, token) =>
        api.post('/api/auth/change-password-with-token',
            { old_password, new_password },
            { params: { token } }
        )
}

// ==================== 图书 API ====================

export const bookApi = {
    getList: (params = {}) => api.get('/api/books', { params }),
    getCategories: () => api.get('/api/books/categories'),
    getStats: () => api.get('/api/books/stats'),
    getDetail: (id) => api.get(`/api/books/${id}`),
    create: (data) => api.post('/api/books', data),
    update: (id, data) => api.put(`/api/books/${id}`, data),
    delete: (id) => api.delete(`/api/books/${id}`)
}

// ==================== 用户管理 API ====================

export const userApi = {
    getList: (params = {}) => api.get('/api/users', { params }),
    create: (data) => api.post('/api/users', data),
    delete: (id) => api.delete(`/api/users/${id}`)
}

// ==================== 借阅 API ====================

export const borrowApi = {
    borrow: (bookId, days = 30) => api.post(`/api/borrow/${bookId}`, { days }),
    return: (recordId) => api.post(`/api/borrow/return/${recordId}`),
    returnByIsbn: (isbn, studentId = null) => api.post('/api/borrow/return-by-isbn', null, {
        params: { isbn, student_id: studentId }
    }),
    getRecords: (params = {}) => api.get('/api/borrow/records', { params }),
    getMyBorrows: () => api.get('/api/borrow/my'),
    getOverdue: () => api.get('/api/borrow/overdue')
}

export default api

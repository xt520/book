import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/LoginView.vue'),
        meta: { guest: true }
    },
    {
        path: '/',
        name: 'Home',
        component: () => import('../views/HomeView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/book/:id',
        name: 'BookDetail',
        component: () => import('../views/BookDetailView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/category',
        name: 'Category',
        component: () => import('../views/CategoryView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/profile',
        name: 'Profile',
        component: () => import('../views/ProfileView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/admin',
        name: 'Admin',
        component: () => import('../views/AdminView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null

    // 需要登录的页面
    if (to.meta.requiresAuth && !token) {
        return next('/login')
    }

    // 需要管理员权限
    if (to.meta.requiresAdmin && user?.role !== 'admin') {
        return next('/')
    }

    // 已登录用户访问登录页
    if (to.meta.guest && token) {
        return next(user?.role === 'admin' ? '/admin' : '/')
    }

    next()
})

export default router

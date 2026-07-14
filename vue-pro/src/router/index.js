import { createWebHistory, createRouter } from 'vue-router'

import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Courselist from '../views/Courselist.vue'
import CourseDetail from '../views/CourseDetail.vue'
import Cart from '../views/Cart.vue'
import Checkout from '../views/Checkout.vue'
import PaySuccess from '../views/PaySuccess.vue'
import CourseStudy from '../views/CourseStudy.vue'
import Search from '../views/Search.vue'
import User from '../views/User.vue'
import ResetPassword from '../views/ResetPassword.vue'
// 新增：AI 伴学与直播互动页面
import AIAssistant from '../views/AIAssistant.vue'
import LiveRoom from '../views/LiveRoom.vue'
import CourseStudyEnhanced from '../views/CourseStudyEnhanced.vue'
// 新增：视频上传页面
import VideoUpload from '../components/VideoUpload.vue'


const routes = [
    { path: '/', component: Home},
    { path: '/login', component: Login},
    { path: '/register', component: Register},
    { path: '/courses', component: Courselist},
    { path: '/courses/:id', component: CourseDetail},
    { path: '/cart', component: Cart},
    { path: '/checkout', component: Checkout},
    { path: '/paysuccess', component: PaySuccess},
    { path: '/course-study/:id', component: CourseStudy},
    { path: '/search', component: Search},
    { path: '/user', component: User},
    { path: '/reset-password', component: ResetPassword},
    // 新增路由：AI 伴学助手、直播间、增强版学习页
    { path: '/ai-assistant', component: AIAssistant},
    { path: '/live/:roomId', component: LiveRoom},
    { path: '/course-study-enhanced/:courseId', component: CourseStudyEnhanced},
    // 新增路由：视频上传
    { path: '/video-upload', component: VideoUpload},


]

const router = createRouter({
    history: createWebHistory(),
    routes,
})
router.beforeEach((to, from, next) => {
    // 白名单：无需登录即可访问
    var wlist = ['/','/login', '/register', '/reset-password','/course', '/courses/:id','/search','/ai-assistant']
    if (wlist.includes(to.path)) {
        next()
        return
    }
    var token = localStorage.getItem('token')
        if (token) {
            next()
        } else {
            next('/login')
        }

})

export default router
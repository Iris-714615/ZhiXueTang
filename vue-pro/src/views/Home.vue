<template>
  <div class="home-page">
    <!-- 三栏布局 -->
    <div class="layout-container">
      <!-- 左侧分类导航 -->
      <aside class="left-sidebar">
        <div class="category-panel">
          <ul class="category-list">
            <li v-for="cat in categories" :key="cat.id" class="category-item"
                @mouseenter="hoverCategory = cat.id" @mouseleave="hoverCategory = null"
                @click="goToCourses(cat.id)">
              <div class="category-text">
                <span class="category-main">{{ cat.name }}</span>
                <span class="category-divider">|</span>
                <span class="category-subs">
                  <span v-for="(sub, idx) in cat.children.slice(0, 3)" :key="sub.id">
                    {{ sub.name }}<span v-if="idx < cat.children.slice(0, 3).length - 1"> · </span>
                  </span>
                </span>
              </div>
              <i class="fas fa-chevron-right category-arrow"></i>
              <div class="sub-category-popup" v-show="hoverCategory === cat.id">
                <div class="sub-category-grid">
                  <a v-for="sub in cat.children" :key="sub.id" href="#"
                     @click.stop.prevent="goToCourses(sub.id)" class="sub-link">
                    {{ sub.name }}
                  </a>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 中间主内容区 -->
      <main class="main-content">
        <!-- Banner 轮播 -->
        <div class="banner-section">
          <div class="banner-carousel" @mouseenter="stopBannerAutoPlay" @mouseleave="startBannerAutoPlay">
            <div v-for="(slide, idx) in banners" :key="slide.id"
                 :class="['banner-slide', { active: currentBanner === idx }]"
                 :style="{ background: slide.color }"
                 @click="handleBannerClick(slide)">
              <div class="banner-content">
                <div class="banner-tag">{{ slide.tag }}</div>
                <h2 class="banner-title">{{ slide.title }}</h2>
                <p class="banner-subtitle">{{ slide.subtitle }}</p>
                <div class="banner-teacher">
                  <span class="teacher-name">{{ slide.teacher }}</span>
                  <span class="teacher-title">{{ slide.teacherTitle }}</span>
                </div>
                <button class="banner-btn">立即查看</button>
              </div>
              <div class="banner-decoration">
                <div class="deco-circle"></div>
                <div class="deco-circle small"></div>
              </div>
            </div>
            <button class="banner-arrow left" @click.stop="changeBanner(-1)">&lt;</button>
            <button class="banner-arrow right" @click.stop="changeBanner(1)">&gt;</button>
            <div class="banner-dots">
              <span v-for="(slide, idx) in banners" :key="idx"
                    :class="['dot', { active: currentBanner === idx }]"
                    @click.stop="currentBanner = idx"></span>
            </div>
          </div>
        </div>

        <!-- 精选好课 -->
        <section class="content-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="title-icon">精选好课</span>
              <span class="title-sub">专业课程 名师亲授 全方位服务</span>
            </h2>
            <a class="section-more" @click="goToAllCourses">查看全部 &gt;</a>
          </div>
          <div class="course-grid">
            <div v-for="course in featuredCourses" :key="course.id" class="course-card"
                 @click="goToCourseDetail(course.id)">
              <div class="card-image">
                <img v-if="course.image" :src="getFullUrl(course.image)" :alt="course.title" loading="lazy">
                <div v-else class="card-image-placeholder" :style="{ background: getGradient(course.id) }">
                  <span>{{ course.title.slice(0, 2) }}</span>
                </div>
                <span class="card-tag" v-if="course.discount">限时优惠</span>
                <span class="card-lessons" v-if="course.lessons">{{ course.lessons }}节</span>
              </div>
              <div class="card-body">
                <h3 class="card-title">{{ course.title }}</h3>
                <p class="card-desc">{{ course.description }}</p>
                <div class="card-meta" v-if="course.teacher">
                  <i class="fas fa-chalkboard-teacher"></i>
                  <span>{{ course.teacher }}</span>
                </div>
                <div class="card-footer">
                  <span class="card-price" v-if="course.price && course.price !== '0'">¥{{ course.price }}</span>
                  <span class="card-price free" v-else>免费</span>
                  <span class="card-students">{{ formatCount(course.studentCount) }}人报名</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- AI 学习之旅 -->
        <section class="content-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="title-icon ai-title">AI 学习之旅</span>
              <span class="title-sub">AI时代来临，找到下一个风口</span>
            </h2>
            <button class="interest-btn">兴趣标签</button>
          </div>
          <div class="course-grid">
            <div v-for="course in aiCourses" :key="course.id" class="course-card"
                 @click="goToCourseDetail(course.id)">
              <div class="card-image">
                <img v-if="course.image" :src="getFullUrl(course.image)" :alt="course.title" loading="lazy">
                <div v-else class="card-image-placeholder" :style="{ background: getGradient(course.id) }">
                  <span>{{ course.title.slice(0, 2) }}</span>
                </div>
                <span class="card-lessons" v-if="course.lessons">{{ course.lessons }}节</span>
                <span class="card-tag ai-tag">AI</span>
              </div>
              <div class="card-body">
                <h3 class="card-title">{{ course.title }}</h3>
                <p class="card-desc">{{ course.description }}</p>
                <div class="card-meta" v-if="course.teacher">
                  <i class="fas fa-chalkboard-teacher"></i>
                  <span>{{ course.teacher }}</span>
                </div>
                <div class="card-footer">
                  <span class="card-source">知乎知学堂</span>
                  <span class="card-price free">免费报名</span>
                </div>
              </div>
            </div>
          </div>
          <div class="more-courses-btn" @click="goToAllCourses">
            更多课程 <i class="fas fa-chevron-down"></i>
          </div>
        </section>

        <!-- 副业赚钱 -->
        <section class="content-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="title-icon">副业赚钱</span>
              <span class="title-sub">适合上班族赚钱的副业</span>
            </h2>
            <a class="section-more" @click="goToAllCourses">查看全部 &gt;</a>
          </div>
          <div class="course-grid">
            <div v-for="course in sideJobCourses" :key="course.id" class="course-card"
                 @click="goToCourseDetail(course.id)">
              <div class="card-image">
                <img v-if="course.image" :src="getFullUrl(course.image)" :alt="course.title" loading="lazy">
                <div v-else class="card-image-placeholder" :style="{ background: getGradient(course.id) }">
                  <span>{{ course.title.slice(0, 2) }}</span>
                </div>
                <span class="card-lessons" v-if="course.lessons">{{ course.lessons }}节</span>
              </div>
              <div class="card-body">
                <h3 class="card-title">{{ course.title }}</h3>
                <p class="card-desc">{{ course.description }}</p>
                <div class="card-meta" v-if="course.teacher">
                  <i class="fas fa-chalkboard-teacher"></i>
                  <span>{{ course.teacher }}</span>
                </div>
                <div class="card-footer">
                  <span class="card-source">知乎知学堂</span>
                  <span class="card-price free">免费</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 官方招募 -->
        <section class="content-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="title-icon">官方招募</span>
              <span class="title-sub">加入我们，共享知识价值</span>
            </h2>
            <a class="section-more" @click="goToAllCourses">查看全部 &gt;</a>
          </div>
          <div class="course-grid">
            <div v-for="course in recruitCourses" :key="course.id" class="course-card"
                 @click="goToCourseDetail(course.id)">
              <div class="card-image">
                <img v-if="course.image" :src="getFullUrl(course.image)" :alt="course.title" loading="lazy">
                <div v-else class="card-image-placeholder" :style="{ background: getGradient(course.id) }">
                  <span>{{ course.title.slice(0, 2) }}</span>
                </div>
                <span class="card-tag official-tag">官方</span>
              </div>
              <div class="card-body">
                <h3 class="card-title">{{ course.title }}</h3>
                <p class="card-desc">{{ course.description }}</p>
                <div class="card-meta" v-if="course.teacher">
                  <i class="fas fa-chalkboard-teacher"></i>
                  <span>{{ course.teacher }}</span>
                </div>
                <div class="card-footer">
                  <span class="card-source">知乎知学堂</span>
                  <span class="card-price free">免费</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 大学生成长 -->
        <section class="content-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="title-icon">大学生成长</span>
              <span class="title-sub">保研、留学、申博，全方位提升竞争力</span>
            </h2>
            <a class="section-more" @click="goToAllCourses">查看全部 &gt;</a>
          </div>
          <div class="course-grid">
            <div v-for="course in studentCourses" :key="course.id" class="course-card"
                 @click="goToCourseDetail(course.id)">
              <div class="card-image">
                <img v-if="course.image" :src="getFullUrl(course.image)" :alt="course.title" loading="lazy">
                <div v-else class="card-image-placeholder" :style="{ background: getGradient(course.id) }">
                  <span>{{ course.title.slice(0, 2) }}</span>
                </div>
                <span class="card-lessons" v-if="course.lessons">{{ course.lessons }}节</span>
              </div>
              <div class="card-body">
                <h3 class="card-title">{{ course.title }}</h3>
                <p class="card-desc">{{ course.description }}</p>
                <div class="card-meta" v-if="course.teacher">
                  <i class="fas fa-chalkboard-teacher"></i>
                  <span>{{ course.teacher }}</span>
                </div>
                <div class="card-footer">
                  <span class="card-source">知乎知学堂</span>
                  <span class="card-price free">免费</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <!-- 右侧边栏 -->
      <aside class="right-sidebar">
        <!-- 用户学习卡片 -->
        <div class="sidebar-card user-learn-card">
          <template v-if="userInfo">
            <div class="user-header">
              <img class="user-avatar-sm" src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="头像">
              <div class="user-name">{{ userInfo.username }}</div>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <span class="stat-num">{{ userStats.learnedCourses }}</span>
                <span class="stat-label">已学课程</span>
              </div>
              <div class="stat-item">
                <span class="stat-num">{{ userStats.readContent }}</span>
                <span class="stat-label">已读内容</span>
              </div>
            </div>
            <div class="user-course-list">
              <div class="user-course-tabs">
                <span :class="{ active: activeUserTab === 'purchased' }" @click="activeUserTab = 'purchased'">已购</span>
                <span :class="{ active: activeUserTab === 'recent' }" @click="activeUserTab = 'recent'">最近学习</span>
              </div>
              <div class="user-course-items">
                <div v-for="item in userCourses" :key="item.id" class="user-course-item" @click="goToCourseDetail(item.id)">
                  <div class="course-play-icon">
                    <i class="fas fa-play"></i>
                  </div>
                  <div class="item-info">
                    <span class="item-title">{{ item.title }}</span>
                    <span class="item-progress">{{ item.tag }} · 已完成 {{ item.completed }} 节，共 {{ item.total }} 节</span>
                  </div>
                </div>
              </div>
              <button class="go-study-btn" @click="router.push('/user')">前往学习中心 &gt;</button>
            </div>
          </template>
          <template v-else>
            <div class="login-prompt">
              <img class="login-avatar" src="https://api.dicebear.com/7.x/avataaars/svg?seed=guest" alt="未登录">
              <div class="prompt-title">登录后继续学习</div>
              <div class="prompt-sub">记录学习进度，获取个性化推荐</div>
              <button class="prompt-login-btn" @click="router.push('/login')">立即登录</button>
            </div>
          </template>
        </div>

        <!-- 精选学习路线 -->
        <div class="sidebar-card learning-routes">
          <h3 class="sidebar-title">精选学习路线</h3>
          <div class="route-categories">
            <div v-for="route in learningRoutes" :key="route.name" class="route-category">
              <div class="route-header" @click="toggleRoute(route.name)">
                <span class="route-icon" :style="{ background: route.color }">
                  <i :class="route.icon"></i>
                </span>
                <span class="route-name">{{ route.name }}</span>
                <span class="route-all">全部 &gt;</span>
              </div>
              <div class="route-items" v-show="expandedRoutes.includes(route.name)">
                <div v-for="sub in route.items" :key="sub.name" class="route-item">
                  <span class="route-item-name">{{ sub.name }}</span>
                  <span class="route-item-count">{{ sub.courseCount }} 门课程 · {{ sub.contentCount }} 篇内容</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 课程周榜 -->
        <div class="sidebar-card weekly-rank">
          <h3 class="sidebar-title">课程周榜</h3>
          <div class="rank-list">
            <div v-for="(item, idx) in weeklyRank" :key="item.id" class="rank-item"
                 @click="goToCourseDetail(item.id)">
              <span :class="['rank-num', { top3: idx < 3 }]">{{ idx + 1 }}</span>
              <div class="rank-info">
                <span class="rank-title">{{ item.title }}</span>
                <span class="rank-meta">{{ item.teacher }} · 共 {{ item.lessons }} 节</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 更多回答/文章 -->
        <div class="sidebar-card articles-card">
          <div class="articles-header">
            <h3 class="sidebar-title">更多回答 | 文章</h3>
            <a href="#" class="more-link">更多 &gt;</a>
          </div>
          <div class="article-list">
            <div class="article-item" v-for="article in articles" :key="article.id">
              <p class="article-title">{{ article.title }}</p>
              <p class="article-excerpt">{{ article.excerpt }}</p>
              <div class="article-meta">
                <span class="article-author">{{ article.author }}</span>
                <span class="article-stats">{{ article.upvotes }}赞同 · {{ article.comments }}评论</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- 右侧浮动工具栏 -->
    <FloatToolbar />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import config from '@/utils/config'
import FloatToolbar from '@/components/FloatToolbar.vue'

const router = useRouter()

// 分类数据
const categories = ref([
  { id: 1, name: '职场办公', children: [{id: 11, name: '设计'}, {id: 12, name: '办公软件'}, {id: 13, name: '职场技能'}, {id: 14, name: '项目管理'}] },
  { id: 2, name: '兴趣技能', children: [{id: 21, name: '摄影摄像'}, {id: 22, name: '写作'}, {id: 23, name: '绘画'}, {id: 24, name: '音乐'}] },
  { id: 3, name: '语言学习', children: [{id: 31, name: '雅思'}, {id: 32, name: '托福'}, {id: 33, name: '实用英语'}, {id: 34, name: '日语'}] },
  { id: 4, name: '考试考证', children: [{id: 41, name: '会计'}, {id: 42, name: '考研'}, {id: 43, name: 'CPA'}, {id: 44, name: 'CFA'}] },
  { id: 5, name: '编程', children: [{id: 51, name: '人工智能'}, {id: 52, name: '大数据'}, {id: 53, name: 'Python'}, {id: 54, name: '前端开发'}] },
  { id: 6, name: '通识', children: [{id: 61, name: '心理'}, {id: 62, name: '健康'}, {id: 63, name: '人文艺术'}, {id: 64, name: '哲学'}] }
])
const hoverCategory = ref(null)

// Banner 数据
const banners = ref([
  {
    id: 1,
    title: 'AI爆款短剧特训营',
    subtitle: 'AI轻松写短剧，让创意落地生金，0基础也能写出高完播率剧本',
    tag: '限时招募',
    teacher: '胡椒老师',
    teacherTitle: '实战派编剧讲师',
    color: 'linear-gradient(135deg, #ff8c00 0%, #ff5500 100%)',
    url: '/courses/1'
  },
  {
    id: 2,
    title: '新人写作计划',
    subtitle: '单篇300-5000！新人最高即月入过万，知乎官方扶持计划',
    tag: '限时专属价',
    teacher: '知乎知学堂',
    teacherTitle: '官方出品',
    color: 'linear-gradient(135deg, #00c6ff 0%, #0072ff 100%)',
    url: '/courses/2'
  },
  {
    id: 3,
    title: 'Python数据分析全能班',
    subtitle: '从零到数据分析师，10周掌握Pandas/NumPy/Matplotlib',
    tag: '全新升级',
    teacher: '李闻阅',
    teacherTitle: '资深数据科学家',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    url: '/courses/3'
  },
  {
    id: 4,
    title: '职场PPT高阶设计课',
    subtitle: '从逻辑到设计，打造高级感商务演示文稿',
    tag: '热门推荐',
    teacher: '陈西',
    teacherTitle: '设计美学讲师',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    url: '/courses/5'
  }
])
const currentBanner = ref(0)
let bannerTimer = null

// 各板块课程数据
const featuredCourses = ref([])
const aiCourses = ref([])
const sideJobCourses = ref([])
const recruitCourses = ref([])
const studentCourses = ref([])

// 课程图片生成工具
const img = (prompt) => `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(prompt)}&image_size=landscape_4_3`

// 精选好课
const mockFeatured = [
  { id: 101, title: 'AI爆款短剧特训营', description: 'AI轻松写短剧，让创意落地生金，实战派编剧讲师亲授', price: '0', studentCount: 12580, image: img('AI短剧创作课程封面，电影胶片与AI元素结合，橙色调，专业教育风格'), discount: false, teacher: '胡椒老师', lessons: 12 },
  { id: 102, title: 'Python数据分析全能班', description: '从零到数据分析师，10周掌握Pandas/NumPy/Matplotlib核心技能', price: '299', studentCount: 23400, image: img('Python数据分析课程封面，代码与数据图表，蓝色科技风格'), discount: true, teacher: '李闻阅', lessons: 36 },
  { id: 103, title: '雅思7分冲刺班', description: '听阅口写全面提升，名师带你冲刺雅思高分', price: '599', studentCount: 15600, image: img('雅思英语培训课程封面，英国元素与书本，清新蓝色风格'), discount: true, teacher: '王雅琪', lessons: 48 },
  { id: 104, title: '职场PPT高阶设计课', description: '从逻辑到设计，打造高级感商务演示文稿', price: '99', studentCount: 32100, image: img('PPT设计课程封面，精美幻灯片展示，粉色渐变风格'), discount: false, teacher: '陈西', lessons: 24 },
  { id: 105, title: '短视频拍摄与剪辑全流程', description: '手机也能拍大片，掌握短视频创作从拍摄到剪辑全流程', price: '0', studentCount: 45600, image: img('短视频制作课程封面，摄像机与剪辑界面，活力橙红风格'), discount: false, teacher: '老玉米', lessons: 18 },
  { id: 106, title: '新媒体运营全攻略', description: '从0到1搭建新媒体矩阵，掌握公众号/小红书/抖音运营技巧', price: '199', studentCount: 18900, image: img('新媒体运营课程封面，手机与社交媒体图标，紫色现代风格'), discount: true, teacher: '林墨', lessons: 30 }
]

// AI学习之旅
const mockAiCourses = [
  { id: 201, title: 'ChatGPT实战应用指南', description: '从Prompt工程到AI助手开发，全面掌握ChatGPT应用', price: '0', studentCount: 56700, image: img('ChatGPT AI应用课程封面，机器人与对话界面，蓝色科技风'), teacher: 'AI前线', lessons: 15 },
  { id: 202, title: 'AI绘画Midjourney大师课', description: '从入门到精通，掌握AI绘画核心技巧与商业应用', price: '0', studentCount: 34200, image: img('AI绘画Midjourney课程封面，艺术画作与AI元素，梦幻紫色风格'), teacher: '画师阿星', lessons: 20 },
  { id: 203, title: '大语言模型原理与实战', description: '深入理解LLM底层原理，动手实现自己的语言模型', price: '0', studentCount: 12300, image: img('大语言模型课程封面，神经网络与代码，深蓝科技风格'), teacher: '张岳', lessons: 28 },
  { id: 204, title: 'AI+办公效率提升课', description: '用AI工具10倍提升办公效率，涵盖写作/表格/演示', price: '0', studentCount: 42100, image: img('AI办公效率课程封面，办公场景与AI工具，绿色清新风格'), teacher: '效率达人', lessons: 12 },
  { id: 205, title: '机器学习入门到精通', description: '系统学习机器学习算法，含监督/无监督/强化学习', price: '0', studentCount: 28900, image: img('机器学习课程封面，算法图表与数据流，蓝色专业风格'), teacher: 'ML学院', lessons: 40 },
  { id: 206, title: '深度学习与计算机视觉', description: 'CNN/Transformer/YOLO全解析，实战项目驱动学习', price: '0', studentCount: 15600, image: img('深度学习计算机视觉课程封面，图像识别与神经网络，科技蓝风格'), teacher: 'CV实验室', lessons: 35 }
]

// 副业赚钱
const mockSideJob = [
  { id: 301, title: '新人写作计划', description: '单篇300-5000！从0到1成为短篇小说作者', price: '0', studentCount: 8920, image: img('写作副业课程封面，笔与笔记本，温暖黄色风格'), teacher: '知乎知学堂', lessons: 8 },
  { id: 302, title: '闲鱼副业变现指南', description: '0成本开店，月入3000-10000的闲鱼实操攻略', price: '0', studentCount: 23400, image: img('闲鱼副业课程封面，手机电商界面，橙色活力风格'), teacher: '副业老张', lessons: 10 },
  { id: 303, title: '自媒体爆款内容创作', description: '揭秘10w+爆款内容方法论，打造高转化自媒体账号', price: '0', studentCount: 31200, image: img('自媒体创作课程封面，内容创作与流量图标，红橙渐变风格'), teacher: '内容星球', lessons: 16 },
  { id: 304, title: '淘宝客从0到月入过万', description: '掌握淘客推广核心技巧，搭建被动收入管道', price: '0', studentCount: 17800, image: img('淘宝客推广课程封面，电商推广与佣金图表，橙红色风格'), teacher: '电商老王', lessons: 14 },
  { id: 305, title: '短视频带货实操课', description: '从选品到直播，短视频带货全链路实操指南', price: '0', studentCount: 45600, image: img('短视频带货课程封面，直播与商品展示，红色热情风格'), teacher: '带货达人', lessons: 20 },
  { id: 306, title: '知识付费课程制作指南', description: '从知识提炼到课程上线，打造自己的知识付费产品', price: '0', studentCount: 9800, image: img('知识付费课程制作封面，课程制作与知识图标，蓝色专业风格'), teacher: '知识匠人', lessons: 18 }
]

// 官方招募
const mockRecruit = [
  { id: 401, title: '知乎知学堂讲师招募计划', description: '成为知学堂认证讲师，分享你的专业知识', price: '0', studentCount: 5600, image: img('讲师招募计划封面，演讲台与麦克风，蓝色专业风格'), teacher: '知乎知学堂', lessons: 3 },
  { id: 402, title: '知乎答主成长计划', description: '从0到万粉答主，知乎官方扶持你的内容创作之路', price: '0', studentCount: 12300, image: img('答主成长计划封面，写作与成长图表，蓝色渐变风格'), teacher: '知乎官方', lessons: 5 },
  { id: 403, title: '创作者激励计划', description: '优质创作者专属激励，让你的知识产生价值', price: '0', studentCount: 8900, image: img('创作者激励计划封面，奖杯与创作元素，金色荣耀风格'), teacher: '知乎知学堂', lessons: 4 },
  { id: 404, title: '校园大使招募', description: '加入校园大使团队，连接校园与知识平台', price: '0', studentCount: 4500, image: img('校园大使招募封面，校园与团队合作元素，青春绿色风格'), teacher: '知乎知学堂', lessons: 2 },
  { id: 405, title: '城市合伙人计划', description: '深耕本地教育市场，与知乎知学堂共成长', price: '0', studentCount: 2300, image: img('城市合伙人计划封面，城市建筑与握手元素，蓝色商务风格'), teacher: '知乎知学堂', lessons: 6 },
  { id: 406, title: '内容合伙人专属通道', description: '优质内容机构专属合作通道，共建知识生态', price: '0', studentCount: 1800, image: img('内容合伙人封面，合作与生态元素，紫色专业风格'), teacher: '知乎知学堂', lessons: 4 }
]

// 大学生成长
const mockStudent = [
  { id: 501, title: '保研全攻略：从择校到复试', description: '985学长亲授保研全流程，成功率提升80%', price: '0', studentCount: 15600, image: img('保研攻略课程封面，大学校园与书本，蓝色学术风格'), teacher: '学霸君', lessons: 22 },
  { id: 502, title: '留学申请一站式指南', description: '从选校到签证，DIY留学申请全流程详解', price: '0', studentCount: 12300, image: img('留学申请指南封面，地球与飞机元素，蓝色国际风格'), teacher: '留学老司机', lessons: 28 },
  { id: 503, title: '考研政治冲刺班', description: '名师带你60天冲刺考研政治70+', price: '0', studentCount: 34500, image: img('考研政治课程封面，书本与笔记，红色励志风格'), teacher: '法考研习社', lessons: 23 },
  { id: 504, title: '大学生职业规划课', description: '找到适合你的职业方向，少走3年弯路', price: '0', studentCount: 21800, image: img('大学生职业规划封面，职业道路与指南针，蓝色规划风格'), teacher: '职业导师', lessons: 15 },
  { id: 505, title: '英语四六级冲刺课', description: '30天突破四六级，听力阅读写作全提升', price: '0', studentCount: 56700, image: img('英语四六级课程封面，英语字母与考试元素，蓝色学习风格'), teacher: '英语小站', lessons: 20 },
  { id: 506, title: '毕业论文写作指南', description: '从选题到答辩，手把手教你写出优秀毕业论文', price: '0', studentCount: 18900, image: img('论文写作指南封面，论文与笔，学术蓝色风格'), teacher: '学术帮', lessons: 12 }
]

// 用户信息
const userInfo = ref(null)
const userStats = ref({ learnedCourses: 8, readContent: 0 })
const activeUserTab = ref('purchased')
const userCourses = ref([
  { id: 1, title: '知乎知学堂「AI新编程副业实战营」', completed: 0, total: 3, tag: '体验课' },
  { id: 2, title: '知乎知学堂「AI爆款短剧特训营」', completed: 2, total: 2, tag: '体验课' }
])

// 学习路线
const expandedRoutes = ref(['Python'])
const learningRoutes = ref([
  {
    name: 'Python', color: '#3776ab', icon: 'fab fa-python',
    items: [
      { name: '基础入门', courseCount: 8, contentCount: 55 },
      { name: '进阶编程', courseCount: 2, contentCount: 37 },
      { name: '高级编程', courseCount: 10, contentCount: 147 }
    ]
  },
  {
    name: 'Office', color: '#2b579a', icon: 'fas fa-file-word',
    items: [
      { name: 'Excel', courseCount: 9, contentCount: 39 },
      { name: 'Word', courseCount: 3, contentCount: 21 },
      { name: 'PPT', courseCount: 5, contentCount: 39 },
      { name: '其他', courseCount: 2, contentCount: 7 }
    ]
  },
  {
    name: '设计', color: '#ff6b35', icon: 'fas fa-palette',
    items: [
      { name: '基础与原理', courseCount: 1, contentCount: 50 },
      { name: '设计软件', courseCount: 19, contentCount: 79 },
      { name: '应用场景', courseCount: 7, contentCount: 91 }
    ]
  }
])

// 课程周榜
const weeklyRank = ref([
  { id: 601, title: '解密「营养与健康」：「吃的对」如此…', teacher: '长轻营养食疗', lessons: 8 },
  { id: 602, title: '7天突破刑法', teacher: '法考研习社', lessons: 23 },
  { id: 603, title: '7天突破民法', teacher: '跟锦囊', lessons: 24 },
  { id: 604, title: '「民法」七天训练营', teacher: '住杠石', lessons: 5 },
  { id: 605, title: '自然语言处理在线课程（下）', teacher: '张岳', lessons: 83 },
  { id: 606, title: 'MONAI 加速医学影像深度学习', teacher: 'NVIDIA英伟达中国', lessons: 2 },
  { id: 607, title: 'AI爆款短剧特训营', teacher: '胡椒老师', lessons: 12 },
  { id: 608, title: 'Python数据分析全能班', teacher: '李闻阅', lessons: 36 }
])

// 文章/回答
const articles = ref([
  { id: 1, title: '为什么看了很多书，还是表达能力极差，该怎么办？', excerpt: '阅读是一种「输入」，思考才是输出的前提。看书和表达，两者分别对应...', author: '认知架构师', upvotes: '1.2万', comments: 386 },
  { id: 2, title: '30岁转行程序员，晚吗？', excerpt: '种一棵树最好的时间是十年前，其次是现在。转行没有早晚...', author: '码农老李', upvotes: '8932', comments: 245 },
  { id: 3, title: '如何高效学习一门新技能？', excerpt: '费曼学习法的核心是「以教代学」，用最简单的话解释给别人听...', author: '学习方法论', upvotes: '6754', comments: 178 }
])

// 获取完整 URL
const getFullUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return config.baseUrl + path
}

// 格式化数字（如 12580 -> 1.2万）
const formatCount = (count) => {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toString()
}

const getGradient = (id) => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
  ]
  return gradients[(id - 1) % gradients.length]
}

// Banner 轮播
const changeBanner = (dir) => {
  if (banners.value.length === 0) return
  currentBanner.value = (currentBanner.value + dir + banners.value.length) % banners.value.length
}

const startBannerAutoPlay = () => {
  bannerTimer = setInterval(() => changeBanner(1), 4000)
}

const stopBannerAutoPlay = () => {
  if (bannerTimer) clearInterval(bannerTimer)
}

const handleBannerClick = (slide) => {
  if (slide.url) window.open(slide.url, '_blank')
}

// 路由方法
const goToCourses = (catId) => {
  router.push({ path: '/courses', query: { top_category: catId } })
}

const goToCourseDetail = (id) => {
  router.push(`/courses/${id}`)
}

const goToAllCourses = () => {
  router.push('/courses')
}

// 获取分类
const fetchCategories = () => {
  request.get('/tcourse/cate/').then(res => {
    if (res.data.code === 200) {
      categories.value = res.data.data || []
    }
  }).catch(() => {})
}

// 获取 Banner
const fetchBanners = () => {
  request.get('/tcourse/banner/').then(res => {
    if (res.data.code === 200) {
      banners.value = res.data.data || []
    }
  }).catch(() => {})
}

// 获取课程（按 floor 分类）
const fetchCourses = (floor, targetRef) => {
  // 获取该 floor 下的分类
  request.get('/tcourse/recate/?floor=' + floor).then(res => {
    if (res.data.code === 200 && res.data.data && res.data.data.length > 0) {
      const firstCat = res.data.data[0]
      request.get('/tcourse/courses/?category=' + firstCat.id + '&floor=' + floor).then(res2 => {
        if (res2.data.code === 200) {
          targetRef.value = res2.data.data || []
        }
      }).catch(() => {})
    }
  }).catch(() => {})
}

// 获取所有课程作为补充数据
const fetchAllCourses = () => {
  request.get('/tcourse/allcourses/?page=1&page_size=12').then(res => {
    if (res.data.code === 200) {
      const all = res.data.data || []
      if (all.length >= 6) {
        if (featuredCourses.value.length === 0) featuredCourses.value = all.slice(0, 6)
        if (aiCourses.value.length === 0) aiCourses.value = all.slice(0, 6)
      }
      // 无论后端是否有数据，副业/官方招募/大学生成长都用丰富的 mock 数据填充
      fillMockCourses()
    } else {
      fillMockCourses()
    }
  }).catch(() => {
    fillMockCourses()
  })
}

const fillMockCourses = () => {
  if (featuredCourses.value.length === 0) featuredCourses.value = mockFeatured
  if (aiCourses.value.length === 0) aiCourses.value = mockAiCourses
  if (sideJobCourses.value.length === 0) sideJobCourses.value = mockSideJob
  if (recruitCourses.value.length === 0) recruitCourses.value = mockRecruit
  if (studentCourses.value.length === 0) studentCourses.value = mockStudent
}

const getUserInfo = () => {
  const token = localStorage.getItem('token')
  const username = localStorage.getItem('username')
  if (token && username) {
    userInfo.value = { token, username }
  }
}

const toggleRoute = (name) => {
  const idx = expandedRoutes.value.indexOf(name)
  if (idx >= 0) {
    expandedRoutes.value.splice(idx, 1)
  } else {
    expandedRoutes.value.push(name)
  }
}

onMounted(() => {
  getUserInfo()
  fetchCategories()
  fetchBanners()
  fetchCourses(1, featuredCourses)
  fetchCourses(2, aiCourses)
  fetchAllCourses()
  startBannerAutoPlay()
})

onUnmounted(() => {
  stopBannerAutoPlay()
})
</script>

<style scoped>
.home-page {
  background: #f6f6f6;
  min-height: 100vh;
  padding-top: 52px;
}

.layout-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  gap: 16px;
}

/* 左侧分类导航 */
.left-sidebar {
  width: 200px;
  flex-shrink: 0;
}

.category-panel {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  position: sticky;
  top: 68px;
}

.category-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.category-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.category-item:hover {
  background: #f0f6ff;
  border-left-color: #0066ff;
}

.category-text {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  margin-right: 8px;
}

.category-main {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
}

.category-divider {
  font-size: 12px;
  color: #d9d9d9;
  margin: 0 6px;
}

.category-subs {
  flex: 1;
  font-size: 12px;
  color: #8590a6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.category-arrow {
  font-size: 10px;
  color: #b4b4b4;
  margin-left: 8px;
}

.category-item:hover .category-main,
.category-item:hover .category-subs,
.category-item:hover .category-arrow {
  color: #0066ff;
}

.sub-category-popup {
  position: absolute;
  left: 100%;
  top: 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  padding: 12px;
  min-width: 280px;
  z-index: 100;
}

.sub-category-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sub-link {
  padding: 6px 12px;
  background: #f6f6f6;
  border-radius: 4px;
  color: #1a1a1a;
  text-decoration: none;
  font-size: 13px;
  transition: all 0.2s;
}

.sub-link:hover {
  background: #e8f0fe;
  color: #0066ff;
}

/* 中间主内容 */
.main-content {
  flex: 1;
  min-width: 0;
}

/* Banner */
.banner-section {
  margin-bottom: 24px;
}

.banner-carousel {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  height: 280px;
  background: #e8f0fe;
  cursor: pointer;
}

.banner-slide {
  display: none;
  height: 100%;
  padding: 40px 64px;
  position: relative;
}

.banner-slide.active {
  display: flex;
  align-items: center;
}

.banner-content {
  position: relative;
  z-index: 2;
  color: #fff;
  max-width: 75%;
}

.banner-tag {
  display: inline-block;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(4px);
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  margin-bottom: 16px;
  border: 1px solid rgba(255,255,255,0.3);
}

.banner-title {
  font-size: 30px;
  font-weight: 800;
  margin: 0 0 12px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.15);
  white-space: nowrap;
}

.banner-subtitle {
  font-size: 16px;
  margin: 0 0 20px;
  opacity: 0.95;
}

.banner-teacher {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}

.teacher-name {
  font-size: 16px;
  font-weight: 600;
}

.teacher-title {
  font-size: 13px;
  opacity: 0.85;
  padding: 2px 8px;
  background: rgba(255,255,255,0.15);
  border-radius: 4px;
}

.banner-btn {
  background: #fff;
  color: #ff5500;
  border: none;
  padding: 10px 28px;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.banner-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.banner-decoration {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.deco-circle {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  position: relative;
}

.deco-circle.small {
  width: 100px;
  height: 100px;
  position: absolute;
  top: -30px;
  right: -50px;
  background: rgba(255,255,255,0.1);
}

.banner-dots {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 3;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  cursor: pointer;
  transition: all 0.2s;
}

.dot.active {
  width: 20px;
  border-radius: 4px;
  background: #fff;
}

.banner-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.9);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  color: #1a1a1a;
  transition: all 0.2s;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.banner-arrow:hover {
  background: #fff;
  transform: translateY(-50%) scale(1.05);
}

.banner-arrow.left { left: 14px; }
.banner-arrow.right { right: 14px; }

/* 内容板块 */
.content-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 0;
}

.title-icon {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
}

.ai-title {
  color: #0066ff;
}

.title-sub {
  font-size: 14px;
  color: #8590a6;
  font-weight: 400;
}

.interest-btn {
  background: transparent;
  border: 1px solid #0066ff;
  color: #0066ff;
  padding: 4px 14px;
  border-radius: 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.interest-btn:hover {
  background: #e8f0fe;
}

/* 课程网格 */
.course-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.course-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebebeb;
  cursor: pointer;
  transition: all 0.2s;
}

.course-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.card-image {
  position: relative;
  height: 150px;
  overflow: hidden;
  background: #f0f0f0;
}

.card-image::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(to top, rgba(0,0,0,0.3), transparent);
  pointer-events: none;
  z-index: 1;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.course-card:hover .card-image img {
  transform: scale(1.05);
}

.card-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  font-weight: 700;
}

.card-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ff4d4f;
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
}

.card-tag.ai-tag {
  background: linear-gradient(135deg, #0066ff, #00a3ff);
  left: 8px;
  right: auto;
  top: 8px;
}

.card-tag.official-tag {
  background: linear-gradient(135deg, #ff8c00, #ff5500);
  left: 8px;
  right: auto;
  top: 8px;
}

.card-lessons {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  backdrop-filter: blur(4px);
}

.section-more {
  font-size: 13px;
  color: #8590a6;
  cursor: pointer;
  transition: color 0.2s;
  text-decoration: none;
}

.section-more:hover {
  color: #0066ff;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8590a6;
  margin-bottom: 8px;
}

.card-meta i {
  font-size: 11px;
  color: #b4b4b4;
}

.card-body {
  padding: 12px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 6px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 13px;
  color: #8590a6;
  margin: 0 0 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-price {
  font-size: 16px;
  font-weight: 700;
  color: #ff4d4f;
}

.card-price.free {
  color: #0066ff;
  font-size: 14px;
}

.card-students {
  font-size: 12px;
  color: #b4b4b4;
}

.card-source {
  font-size: 12px;
  color: #8590a6;
}

.more-courses-btn {
  text-align: center;
  padding: 16px;
  color: #8590a6;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
  margin-top: 8px;
}

.more-courses-btn:hover {
  color: #0066ff;
}

/* 右侧边栏 */
.right-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.sidebar-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 16px;
}

/* 用户学习卡片 */
.user-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.user-avatar-sm {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #e8f0fe;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.user-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 12px;
  color: #8590a6;
  margin-top: 4px;
}

.user-course-tabs {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.user-course-tabs span {
  font-size: 14px;
  color: #8590a6;
  cursor: pointer;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.user-course-tabs span.active {
  color: #1a1a1a;
  font-weight: 600;
  border-bottom-color: #0066ff;
}

.user-course-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f6f6f6;
  cursor: pointer;
  transition: background 0.2s;
}

.user-course-item:hover {
  background: #f9f9f9;
  margin: 0 -12px;
  padding: 10px 12px;
  border-radius: 6px;
}

.course-play-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: #e8f0fe;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0066ff;
  font-size: 12px;
  flex-shrink: 0;
}

.item-title {
  display: block;
  font-size: 13px;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.item-progress {
  font-size: 12px;
  color: #b4b4b4;
}

.go-study-btn {
  width: 100%;
  margin-top: 12px;
  padding: 8px;
  background: #e8f0fe;
  color: #0066ff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.go-study-btn:hover {
  background: #d0e4ff;
}

/* 学习路线 */
.route-categories {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.route-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 4px;
  cursor: pointer;
  transition: background 0.2s;
  border-radius: 6px;
}

.route-header:hover {
  background: #f6f6f6;
}

.route-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
}

.route-name {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.route-all {
  font-size: 12px;
  color: #8590a6;
}

.route-items {
  padding: 4px 0 4px 32px;
}

.route-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  cursor: pointer;
  transition: color 0.2s;
}

.route-item:hover .route-item-name {
  color: #0066ff;
}

.route-item-name {
  font-size: 13px;
  color: #1a1a1a;
}

.route-item-count {
  font-size: 12px;
  color: #b4b4b4;
}

/* 课程周榜 */
.rank-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rank-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.rank-item:hover {
  opacity: 0.8;
}

.rank-num {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #8590a6;
  background: #f0f0f0;
  border-radius: 3px;
  flex-shrink: 0;
  margin-top: 2px;
}

.rank-num.top3 {
  background: #ff4d4f;
  color: #fff;
}

.rank-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rank-title {
  font-size: 13px;
  color: #1a1a1a;
  line-height: 1.4;
}

.rank-meta {
  font-size: 12px;
  color: #b4b4b4;
}

/* 文章卡片 */
.articles-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.more-link {
  font-size: 13px;
  color: #8590a6;
  text-decoration: none;
}

.more-link:hover {
  color: #0066ff;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-item {
  padding-bottom: 16px;
  border-bottom: 1px solid #f6f6f6;
  cursor: pointer;
}

.article-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.article-item:hover .article-title {
  color: #0066ff;
}

.article-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 6px;
  line-height: 1.4;
  transition: color 0.2s;
}

.article-excerpt {
  font-size: 13px;
  color: #8590a6;
  margin: 0 0 8px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.article-author {
  color: #0066ff;
  font-weight: 500;
}

.article-stats {
  color: #b4b4b4;
}

.login-prompt {
  text-align: center;
  padding: 16px 0;
}

.login-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  margin-bottom: 12px;
  opacity: 0.7;
}

.prompt-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
  line-height: 1.4;
}

.prompt-sub {
  font-size: 13px;
  color: #8590a6;
  margin-bottom: 16px;
}

.prompt-login-btn {
  width: 100%;
  padding: 10px;
  background: #0066ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.prompt-login-btn:hover {
  background: #0052cc;
}
</style>

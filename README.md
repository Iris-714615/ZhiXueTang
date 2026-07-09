# 知乎知学堂（微服务与 AGI 混合架构）Web 端

> 基于 `ZhiXueTang_Web_Dev_Document.md` 开发设计文档的完整实现。
>
> 架构：**Vue 3 + TS + Pinia**（前端） + **Django + Channels**（核心业务/实时通信） + **FastAPI + LangGraph/LlamaIndex**（AI 微服务） + **Celery**（异步任务）。
>
> 这是一个完整的在线教育平台，包含课程展示、购物车、订单支付、学习中心、AI 伴学助手、直播间互动等核心功能。

---

## 一、项目架构总览

### 1.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────────┐
│                         浏览器（用户端）                              │
│                    http://localhost:5173                             │
└────────────┬───────────────────────────────┬─────────────────────────┘
             │ HTTP                          │ WebSocket
             ▼                              ▼
┌────────────────────────┐         ┌────────────────────────┐
│   Vue 3 + TS + Pinia   │         │   WebSocket 直播间      │
│   （前端 SPA）          │         │   ws://localhost:8000   │
│   端口：5173            │         │   /ws/live/<room_id>/   │
└──────────┬─────────────┘         └────────────────────────┘
           │ HTTP API                       ▲
           ▼                                │
┌───────────────────────────────────────────┴────────────────────────┐
│                Django + DRF + Channels（核心业务后端）               │
│                       端口：8000（HTTP + WebSocket）                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  euser   │  │ tcourse  │  │   live   │  │  tasks   │            │
│  │ 用户/订单 │  │ 课程/购物│  │ 直播Consumer│  │ Celery异步│            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└────────┬──────────────┬───────────────────────────┬─────────────────┘
         │              │                            │
         │   JWT 共享   │ HTTP 透传（SSE 代理）      │ 异步任务
         ▼              ▼                            ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│  MySQL（主库 edupro）        │    │  FastAPI AI 微服务           │
│  Redis（缓存/会话/Celery）   │    │  端口：8001（SSE 流式）       │
│  Elasticsearch（向量检索）   │    │  ┌────────────────────────┐  │
└──────────────────────────────┘    │  │ LangGraph Agent 编排   │  │
                                    │  │ LlamaIndex 双索引 RAG  │  │
                                    │  │ DashScope 千问 LLM     │  │
                                    │  └────────────────────────┘  │
                                    └──────────────────────────────┘
```

### 1.2 技术栈映射（文档 → 实现）

| 文档技术选型 | 实际实现 | 说明 |
| :--- | :--- | :--- |
| Golang (Gin) 核心业务 | **Django + DRF** | 沿用现有项目；通过守护线程实现异步回写 |
| Python FastAPI AI | **FastAPI** | 完全一致，独立 8001 端口运行 |
| Vue 3 + TS + Pinia | **Vue 3 + TS + Pinia** | 完全一致，新增 Pinia 状态管理 |
| LangChain/LangGraph/LlamaIndex | **同左** | LangGraph 状态图 + LlamaIndex RAG + ES 向量库 |
| WebSocket 直播 | **Django Channels** | `AsyncWebsocketConsumer` + InMemory 通道层 |
| Celery 异步任务 | **Celery + Redis** | PDF 向量化/字幕提取/报表任务 |
| SSE 流式响应 | **StreamingResponse + fetch ReadableStream** | FastAPI 下发 + Vue 原生流式消费 |
| JWT 鉴权 | **PyJWT（双服务共享密钥）** | Django 签发，FastAPI 验证 |
| LLM 大模型 | **千问 qwen-plus** | DashScope OpenAI 兼容接口 |

---

## 二、目录结构

```
知乎知学堂/
├── vue-pro/                          # Vue 3 前端
│   ├── src/
│   │   ├── components/               # 公共组件
│   │   │   ├── Header.vue            # 顶部导航（消息/私信/创作中心/头像）
│   │   │   ├── Footer.vue            # 底部信息
│   │   │   ├── AIChatWindow.vue      # AI 伴学聊天窗口（流式 Markdown）
│   │   │   ├── FloatToolbar.vue      # 浮动工具栏
│   │   │   └── WxPayModal.vue        # 微信支付弹窗
│   │   ├── views/                    # 页面视图
│   │   │   ├── Home.vue              # 首页（Banner + 分类 + 课程列表）
│   │   │   ├── Login.vue             # 登录页
│   │   │   ├── Register.vue          # 注册页
│   │   │   ├── ResetPassword.vue     # 重置密码
│   │   │   ├── Courselist.vue        # 课程列表
│   │   │   ├── CourseDetail.vue      # 课程详情
│   │   │   ├── Cart.vue              # 购物车
│   │   │   ├── Checkout.vue          # 结算页
│   │   │   ├── PaySuccess.vue        # 支付成功
│   │   │   ├── CourseStudy.vue       # 学习页
│   │   │   ├── CourseStudyEnhanced.vue # 增强版学习页（Pinia 进度同步）
│   │   │   ├── AIAssistant.vue       # AI 伴学助手页
│   │   │   ├── LiveRoom.vue          # 直播间（WebSocket 弹幕）
│   │   │   ├── Search.vue            # 搜索页
│   │   │   └── User.vue              # 个人中心
│   │   ├── services/                 # 服务封装
│   │   │   ├── aiService.ts          # SSE 流式 AI 对话
│   │   │   └── websocketService.ts   # WebSocket 直播
│   │   ├── store/                    # Pinia 状态管理
│   │   │   ├── userStore.ts          # 用户登录状态
│   │   │   ├── courseStore.ts        # 课程数据
│   │   │   ├── chatStore.ts          # 聊天消息
│   │   │   └── liveStore.ts          # 直播间弹幕
│   │   ├── utils/
│   │   │   ├── request.js            # axios 封装
│   │   │   └── config.js             # 环境配置
│   │   ├── router/index.js           # 路由配置
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html                    # SW 缓存清理脚本
│   └── package.json
│
├── myproject/                        # Django 核心业务后端
│   ├── manage.py
│   ├── requirements.txt
│   ├── myproject/
│   │   ├── settings/
│   │   │   ├── dev.py                # 开发配置（MySQL/Redis/Channels/日志）
│   │   │   ├── prod.py               # 生产配置
│   │   │   └── test.py               # 测试配置
│   │   ├── asgi.py                   # ASGI 入口（HTTP + WebSocket 路由）
│   │   ├── wsgi.py
│   │   └── urls.py                   # 根路由
│   ├── euser/                        # 用户与订单应用
│   │   ├── models.py                 # User/MyCourse/Comment/Refund/Recharge
│   │   ├── views.py                  # 登录/注册/订单/评价/退款
│   │   ├── ai_views.py               # SSE 网关代理 + 课程进度异步写入
│   │   ├── ser.py                    # 序列化器
│   │   └── urls.py
│   ├── tcourse/                      # 课程与购物车应用
│   │   ├── models.py                 # Category/Banner/Tags/Teacher/Courses
│   │   ├── views.py                  # 课程/购物车/订单/支付/搜索
│   │   ├── wxpay.py                  # 微信支付
│   │   ├── ser.py
│   │   └── urls.py
│   ├── live/                         # 直播互动应用
│   │   ├── consumers.py              # LiveRoomConsumer（WebSocket）
│   │   ├── routing.py                # ws/live/<room_id>/
│   │   ├── views.py                  # 直播间信息接口
│   │   └── urls.py
│   ├── tasks/                        # Celery 异步任务
│   │   ├── celery.py                 # Celery 配置
│   │   └── tasks.py                  # PDF 向量化/字幕提取/报表生成
│   ├── tools/                        # 工具集
│   │   ├── myjwt.py                  # JWT 签发与验证
│   │   ├── myredis.py                # Redis 封装
│   │   ├── sms.py                    # 短信发送
│   │   ├── email_sender.py           # 邮件发送
│   │   ├── pay.py                    # 支付宝支付
│   │   └── pass_create.py            # 密码生成
│   ├── middleware/
│   │   └── jwt_middleware.py         # JWT 中间件
│   └── static/upload/                # 静态资源（课程图/讲师头像/Banner）
│
└── ai-service/                       # FastAPI AI 微服务（独立运行）
    └── app/
        ├── main.py                   # FastAPI 入口 + CORS + JWT 中间件
        ├── auth.py                   # JWT 验证依赖
        ├── config.py                 # 全局配置（千问/ES/Redis/JWT）
        ├── models/schemas.py         # Pydantic 请求/响应模型
        ├── routers/
        │   ├── chat.py               # SSE 流式对话 /api/v1/ai/assistant/chat
        │   └── knowledge.py          # 知识库构建/检索/混合检索
        ├── services/
        │   ├── llm_service.py        # LangGraph Agent（意图识别→RAG/Chat/Code）
        │   └── rag_service.py        # LlamaIndex 双索引（VectorStore+Summary）
        ├── data_processing/          # 工厂模式数据处理
        │   ├── document_factory.py   # 工厂类
        │   ├── pdf_processor.py      # PDF 分片读取
        │   ├── word_processor.py     # Word 分片读取
        │   ├── web_crawler.py        # 网页爬取
        │   └── base.py               # 抽象基类
        ├── retrieval/                # 检索优化
        │   ├── hybrid_retriever.py   # 混合检索（归一化+rerank）
        │   ├── multi_retriever.py    # 多路召回（ES向量+Chroma+BM25）
        │   ├── query_rewriter.py     # 问题改写
        │   ├── reranker.py           # BGE-reranker 重排
        │   └── cache_manager.py      # Redis 缓存
        ├── vectorstore/              # 向量库
        │   ├── es_vector_store.py    # Elasticsearch 向量库（单例）
        │   ├── chroma_vector_store.py # Chroma 向量库（单例）
        │   └── embedding_model.py    # BGE-small-zh 向量模型（单例）
        └── data_sync/                # 数据同步（默认禁用）
            ├── binlog_listener.py    # MySQL Binlog 监听
            ├── rabbitmq_consumer.py  # RabbitMQ 消费者
            └── scheduled_tasks.py    # 定时任务
```

---

## 三、核心模块详解

### 3.1 AI 伴学助手（核心亮点）

基于 **LangGraph 状态图 + LlamaIndex 双索引 RAG** 实现智能伴学对话。

#### 架构流程

```
用户提问 → Agent 意图识别节点（LLM 判断）
            ├─ rag_question（课程知识问题）
            │   └─ RAG 节点
            │       ├─ 混合检索（问题改写→多路召回→rerank）
            │       ├─ 双索引智能路由（RouterQueryEngine）
            │       │   ├─ 细节查询 → VectorStoreIndex（KNN 语义检索）
            │       │   └─ 全局概括 → SummaryIndex（树形汇总）
            │       └─ LLM 基于检索上下文生成回答
            ├─ chat（闲聊/问候）
            │   └─ 通用对话节点（LLM 直接回答）
            └─ code_help（编程问题）
                └─ 代码助手节点（LLM + 代码示例）
```

#### 关键设计

| 模块 | 设计模式 | 说明 |
| :--- | :--- | :--- |
| RAG 双索引 | RouterQueryEngine | VectorStoreIndex（细节）+ SummaryIndex（概括），LLM 自动路由 |
| 数据处理 | 工厂模式 | `DataProcessorFactory` 根据 source 自动选择 PDF/Word/Web 处理器 |
| 向量库连接 | 单例模式 | ES/Chroma/Embedding 均用双重检查锁单例 |
| 混合检索 | 多路召回+归一化 | ES向量(0.4) + Chroma(0.3) + BM25(0.3) 加权融合 |
| 降级机制 | 优雅降级 | RAG 失败→降级为通用 LLM 对话，绝不中断 SSE 连接 |

#### SSE 流式协议

```
data: {"code": 200, "intent": "rag_question", "type": "intent"}\n\n
data: {"code": 200, "content": "你好", "type": "content"}\n\n
data: {"code": 200, "content": "呀！", "type": "content"}\n\n
...
data: {"code": 200, "sources": [...], "done": true, "type": "done"}\n\n
data: [DONE]\n\n
```

### 3.2 直播间互动（Django Channels）

- **协议**：WebSocket（`ws://localhost:8000/ws/live/<room_id>/`）
- **消费者**：`AsyncWebsocketConsumer`（全异步）
- **功能**：实时弹幕、在线人数统计、心跳保活（ping/pong）
- **通道层**：开发用 InMemory，生产换 `channels_redis`

### 3.3 课程业务（Django + DRF）

| 模块 | 功能 |
| :--- | :--- |
| 用户系统 | 注册/登录/短信验证/邮箱重置密码/个人信息 |
| 课程展示 | 分类导航/Banner轮播/课程列表/详情/搜索 |
| 购物流程 | 购物车/结算/优惠券/微信支付/支付宝回调 |
| 学习中心 | 我的课程/学习进度/收藏/评价 |
| 订单管理 | 订单列表/退款申请/售后流程/充值活动 |

### 3.4 异步任务（Celery）

| 任务 | 说明 |
| :--- | :--- |
| PDF 向量化 | 课程文档 PDF 异步分片向量化 |
| 字幕提取 | 视频字幕提取并入库 |
| 报表生成 | 用户学习报表定时生成 |
| 邮件发送 | 注册验证邮件异步发送 |

---

## 四、环境准备

### 4.1 基础服务

| 服务 | 版本 | 端口 | 说明 |
| :--- | :--- | :--- | :--- |
| MySQL | 8.0 | 3306 | 库名 `edupro`，账号 `root/root` |
| Redis | 7.0 | 6379 | 缓存/会话/Celery Broker |
| Elasticsearch | 8.x | 9200 | 向量检索（可选，AI 知识库用） |
| Node.js | ≥ 20.19 | — | 前端构建 |
| Python | ≥ 3.11 | — | 后端运行时 |

### 4.2 Django 后端依赖

```bash
cd myproject
pip install -r requirements.txt
```

依赖清单：
```
Django>=5.2,<6.0
djangorestframework>=3.15.0
django-cors-headers>=4.3.0
daphne>=4.1.0
channels>=4.0.0
PyMySQL>=1.1.0
redis>=5.0.0
celery>=5.3.0
PyJWT>=2.8.0
requests>=2.31.0
cryptography>=42.0.0
```

### 4.3 FastAPI AI 微服务依赖

```bash
cd ai-service
pip install fastapi uvicorn pyjwt llama-index langgraph elasticsearch
pip install llama-index-llms-openai-like llama-index-embeddings-huggingface
```

### 4.4 Vue 前端依赖

```bash
cd vue-pro
npm install
```

主要依赖：`vue@3.5` / `vue-router@4` / `pinia@3` / `element-plus@2.13` / `axios` / `marked`

---

## 五、启动顺序

> 建议开 4 个终端分别启动。

### ① 启动 MySQL / Redis / ES（前置）

确保 `localhost:3306` / `localhost:6379` / `localhost:9200` 可用。

### ② 启动 Django 后端（端口 8000，HTTP + WebSocket）

```bash
cd myproject
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

> 注：因 `INSTALLED_APPS` 首位为 `daphne`，runserver 已自动以 ASGI 模式运行，
> 同时支持 HTTP 与 WebSocket（`ws://localhost:8000/ws/live/<room_id>/`）

### ③ 启动 Celery Worker（异步任务）

```bash
cd myproject
celery -A tasks worker -l info -P solo
```

> Windows 用 `-P solo` 单进程模式；Linux/Mac 可用 `-P gevent`

（可选）启动定时任务：`celery -A tasks beat -l info`

### ④ 启动 FastAPI AI 微服务（端口 8001，SSE）

```bash
cd ai-service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

> 数据同步模块（Binlog/RabbitMQ/定时任务）默认禁用，
> 需开启时设置环境变量 `ENABLE_DATA_SYNC=1`

### ⑤ 启动 Vue 前端（端口 5173）

```bash
cd vue-pro
npm run dev
```

访问 http://localhost:5173

---

## 六、接口清单与访问入口

### 6.1 前端路由

| 路由 | 组件 | 说明 | 登录要求 |
| :--- | :--- | :--- | :--- |
| `/` | Home.vue | 首页（Banner+分类+课程） | 否 |
| `/login` | Login.vue | 登录 | 否 |
| `/register` | Register.vue | 注册 | 否 |
| `/reset-password` | ResetPassword.vue | 重置密码 | 否 |
| `/courses` | Courselist.vue | 课程列表 | 否 |
| `/courses/:id` | CourseDetail.vue | 课程详情 | 否 |
| `/search` | Search.vue | 搜索 | 否 |
| `/ai-assistant` | AIAssistant.vue | AI 伴学助手 | 否 |
| `/cart` | Cart.vue | 购物车 | 是 |
| `/checkout` | Checkout.vue | 结算 | 是 |
| `/paysuccess` | PaySuccess.vue | 支付成功 | 是 |
| `/course-study/:id` | CourseStudy.vue | 学习页 | 是 |
| `/course-study-enhanced/:courseId` | CourseStudyEnhanced.vue | 增强学习页 | 是 |
| `/live/:roomId` | LiveRoom.vue | 直播间 | 是 |
| `/user` | User.vue | 个人中心 | 是 |

### 6.2 Django 后端接口

#### 用户与认证（euser）

| 接口 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/login/` | POST | 登录（返回 JWT token + username + user_id） |
| `/send_sms/` | POST | 发送短信验证码 |
| `/register/` | POST | 注册 |
| `/send_email/` | POST | 发送邮箱验证码 |
| `/reset-password/` | POST | 重置密码 |
| `/userinfo/` | GET | 获取用户信息 |
| `/mycourse/` | GET | 我的课程 |
| `/myorder/` | GET | 我的订单 |
| `/cancelorder/` | POST | 取消订单 |
| `/comment/` | POST | 评价 |
| `/refund/` | POST | 申请退款 |
| `/recharge/` | POST | 充值 |
| `/ai/assistant/chat/` | POST | SSE 网关代理（透传至 FastAPI） |
| `/course/progress/` | POST | 课程进度异步写入 |

#### 课程与购物（tcourse）

| 接口 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/tcourse/cate/` | GET | 课程分类 |
| `/tcourse/nav/` | GET | 导航栏 |
| `/tcourse/banner/` | GET | 焦点图 |
| `/tcourse/tags/` | GET | 标签 |
| `/tcourse/courses/` | GET | 课程列表 |
| `/tcourse/allcourses/` | GET | 全部课程 |
| `/tcourse/allcate/` | GET | 全部分类 |
| `/tcourse/recate/` | GET | 推荐分类 |
| `/tcourse/detail/<id>` | GET | 课程详情 |
| `/tcourse/cart/` | POST/GET | 购物车 |
| `/tcourse/cartdel/` | POST | 删除购物车 |
| `/tcourse/orders/` | POST | 创建订单 |
| `/tcourse/pay/` | POST | 发起支付 |
| `/tcourse/search/` | GET | 搜索 |
| `/tcourse/testcelery/` | GET | 测试 Celery |

#### 直播（live）

| 接口 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/live/room/<room_id>/` | GET | 直播间信息 |
| `ws://localhost:8000/ws/live/<room_id>/` | WS | WebSocket 直播间 |

### 6.3 FastAPI AI 微服务接口

| 接口 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/health` | GET | 健康检查 |
| `/api/v1/ai/assistant/chat` | POST | SSE 流式对话（Agent 意图识别+RAG） |
| `/api/v1/ai/knowledge/build_index` | POST | 构建课程双索引 |
| `/api/v1/ai/knowledge/search` | POST | 双索引智能路由检索 |
| `/api/v1/ai/knowledge/hybrid_search` | POST | 混合检索增强（多路召回+rerank） |

---

## 七、JWT 鉴权约定

### 7.1 密钥共享

- **密钥**：`ZhiHu-ZhiXueTang-Secret-Key`
- **位置**：[ai-service/app/config.py](ai-service/app/config.py) 与 [myproject/tools/myjwt.py](myproject/tools/myjwt.py)
- **算法**：HS256

### 7.2 鉴权流程

```
1. 用户登录 → Django /login/ 签发 JWT（含 user_id, username, exp, iat）
2. 前端存 localStorage：token / username / user_id
3. 前端请求附带 Header：Authorization: Bearer <token>
4. FastAPI 中间件校验 /api/v1/ai/* 的 token
5. CORS 预检（OPTIONS）直接放行
```

### 7.3 关键修复记录

- Django `myjwt.py` 统一使用固定密钥（避免每次启动随机生成）
- FastAPI `main.py` 中间件放行 OPTIONS 预检请求
- FastAPI `chat.py` 路由移除重复的 `verify_token` Depends（中间件已校验）

---

## 八、数据库模型

### 8.1 用户模块（euser）

| 表名 | 说明 | 关键字段 |
| :--- | :--- | :--- |
| tuser | 用户 | username, password, phone, email, points, account, avatar |
| my_course | 我的课程 | user, course, course_type, start_time, end_time, status, progress |
| comment | 评价 | user, course, content, star |
| refund | 退款记录 | user, order_no, amount, status |
| refund_process | 售后流程 | refund, approver, approve_time, status |
| recharge_activity | 充值活动 | amount, give_amount, start_time, end_time, tcount, count |
| recharge_record | 充值记录 | user, amount, recharge_date, pay_type, is_give |

### 8.2 课程模块（tcourse）

| 表名 | 说明 | 关键字段 |
| :--- | :--- | :--- |
| category | 课程分类 | name, pid, level, image, is_recommend, floor, top_category |
| nav_cate | 导航栏 | name, url, weight |
| banner | 焦点图 | image, url, weight, is_show |
| tag | 标签 | title, image, description, is_recommend, is_online |
| teacher | 讲师 | avatar, role, name, title, description |
| courses | 课程 | name, intro, price, teacher, cover, video_url |

---

## 九、架构亮点

1. **双引擎混合微服务**：Django 处理高 ACID 事务业务，FastAPI 专注 AI 编排，通过 JWT 解耦
2. **SSE 流式伴学**：FastAPI `StreamingResponse` + Vue `ReadableStream`，逐字打字效果
3. **LangGraph 智能路由**：意图识别自动分发至 RAG / Chat / Code 节点
4. **LlamaIndex 双索引**：VectorStoreIndex（细节）+ SummaryIndex（概括），LLM 自动路由
5. **混合检索增强**：问题改写 → 多路召回 → 归一化加权 → BGE-reranker 重排
6. **优雅降级机制**：RAG 索引未构建时自动降级为通用 LLM 对话，保证用户体验
7. **Channels 直播间**：全异步 WebSocket，组广播弹幕，心跳保活
8. **Celery 削峰**：PDF OCR、字幕提取、报表生成异步化
9. **Pinia 跨组件状态**：用户/课程/聊天/直播状态统一管理
10. **工厂模式数据处理**：PDF/Word/Web 处理器可扩展（开闭原则）

---

## 十、端口约定

| 服务 | 端口 | 说明 |
| :--- | :--- | :--- |
| Vue 前端 | 5173 | Vite 开发服务器 |
| Django 后端 | 8000 | HTTP + WebSocket |
| FastAPI AI | 8001 | SSE 流式对话 |
| MySQL | 3306 | 主数据库 |
| Redis | 6379 | 缓存/会话/Celery |
| Elasticsearch | 9200 | 向量检索 |
| RabbitMQ | 5672 | 消息队列（可选） |

---

## 十一、生产环境建议

- Channels 通道层从 `InMemoryChannelLayer` 切换为 `channels_redis`
- MySQL 启用主从读写分离；Redis 哨兵集群；ES 分片 + KNN 专区
- FastAPI 通过 gunicorn + uvicorn worker 多进程部署
- 静态资源与上传文件迁移至对象存储（七牛/MinIO）
- 前端构建后由 Nginx 托管，API 反向代理至 Django/FastAPI
- Celery Worker 与 Beat 分离部署，启用 Sentinel 监控
- JWT 密钥通过环境变量注入，不硬编码
- 开启 HTTPS，强制 CSRF 保护
- 日志收集接入 ELK 栈

---

## 十二、常见问题

### Q1：浏览器显示旧项目（KidoAI）而非知乎知学堂？

**原因**：旧项目 Service Worker 缓存拦截了 localhost:5173 的请求

**解决**：`vue-pro/index.html` 已添加 SW 自动注销和 caches 清理脚本，清除浏览器缓存后重试

### Q2：AI 对话报 "Failed to fetch"？

**原因**：CORS 预检请求被 JWT 中间件拦截，或 RAG 索引未构建导致异常中断

**解决**：
- `main.py` 已放行 OPTIONS 预检请求
- `chat.py` 已添加 `@router.options("/chat")` 路由
- `llm_service.py` 的 `rag_node` 已加降级机制，索引未构建时降级为通用对话

### Q3：登录后 Header 仍显示未登录？

**原因**：`getUserInfo()` 只在 `onMounted` 执行一次，登录跳转不刷新

**解决**：已用 Pinia `userStore` 全局管理登录状态，`Login.vue` 登录成功后调用 `userStore.setUser()`

### Q4：ai-service 启动后进程崩溃？

**原因**：数据同步模块（Binlog/RabbitMQ）依赖外部服务

**解决**：已用 `ENABLE_DATA_SYNC` 环境变量控制，默认禁用。需开启时设置 `ENABLE_DATA_SYNC=1`

### Q5：Elasticsearch 报 `hosts must be specified`？

**原因**：`tcourse/views.py` 中 `Elasticsearch()` 未传 hosts 参数

**解决**：已修改为 `Elasticsearch(hosts=["http://localhost:9200"])`

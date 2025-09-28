# 语灵智能角色扮演前端项目说明文档

## 项目概述

语灵是一个基于 Vue 3 + TypeScript 的智能角色扮演前端应用，旨在提供丰富的AI角色扮演体验和语音对话功能。项目采用现代化的前端技术栈，支持实时语音交互、角色扮演检测、流式对话等功能。

## 技术栈

- **框架**: Vue 3.5.21 (Composition API + `<script setup>`)
- **构建工具**: Vite 7.1.6
- **语言**: TypeScript 5.9.2
- **UI组件库**: Element Plus 2.11.3
- **样式**: TailwindCSS 4.1.13
- **路由**: Vue Router 4
- **HTTP客户端**: Axios 1.12.2
- **3D图形**: Three.js 0.180.0
- **其他**: Lodash, Marked, Qiniu SDK

## 如何运行前端程序

### 环境要求

- Node.js >= 16.0.0
- pnpm (推荐) 或 npm

### 安装依赖

```bash
cd web
pnpm install
# 或
npm install
```

### 启动开发服务器

```bash
pnpm dev
# 或
npm run dev
```

前端服务将在 `http://localhost:9988` 启动，并自动打开浏览器。

### 构建生产版本

```bash
pnpm build
# 或
npm run build
```

### 预览生产构建

```bash
pnpm preview
# 或
npm run preview
```

### 类型检查

```bash
pnpm type-check
# 或
npm run type-check
```

## 后端服务依赖

为了完整体验所有功能，需要启动以下后端服务：

1. **用户管理服务** (端口 14101) - 处理用户登录注册
2. **角色扮演检测服务** (端口 9100) - 检测用户输入的角色扮演意图
3. **角色扮演流式服务** (端口 8000) - 提供角色扮演和对话功能
4. **RAG 工作流服务** (端口 9004) - 处理普通对话
5. **TTS 语音合成服务** (端口 8080) - 文字转语音 (可选)
6. **FunASR 语音识别服务** (WebSocket 端口 10095) - 语音转文字 (可选)

## 项目架构设计

### 目录结构

```
web/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口层
│   │   ├── axios.ts       # Axios 实例配置
│   │   ├── userController.ts      # 用户管理接口
│   │   ├── roleplayController.ts  # 角色扮演接口
│   │   ├── voiceConversation.ts   # 语音对话接口
│   │   ├── handleUserToken.ts     # Token 处理
│   │   └── types/         # 类型定义
│   ├── components/        # 可复用组件
│   │   ├── VoiceChatPanel.vue     # 语音聊天面板
│   │   ├── VoiceWave3D.vue        # 3D 语音波形
│   │   └── user/          # 用户相关组件
│   ├── composables/       # 组合式函数
│   │   └── useAudioManager.ts     # 音频管理
│   ├── router/            # 路由配置
│   ├── stores/            # 状态管理
│   ├── styles/            # 全局样式
│   ├── utils/             # 工具函数
│   ├── views/             # 页面组件
│   │   ├── home.vue       # 首页
│   │   ├── Conversation.vue       # 对话页面
│   │   └── NotFound.vue   # 404页面
│   └── assets/            # 静态资源
├── vite.config.ts         # Vite 配置
├── package.json           # 项目配置
└── tsconfig.json          # TypeScript 配置
```

### 核心模块规格

#### 1. API 接口层 (`src/api/`)

**axios.ts** - HTTP 客户端配置
- 统一的 axios 实例
- 请求/响应拦截器
- Token 自动注入
- 白名单机制

**userController.ts** - 用户管理接口
- 用户登录/注册
- 用户信息管理
- 密码重置/修改
- 用户列表获取

**roleplayController.ts** - 角色扮演接口
- 角色扮演意图检测
- 角色扮演流式自我介绍
- 角色对话流式交互
- SSE 事件处理

**voiceConversation.ts** - 语音对话接口
- FunASR WebSocket 语音识别
- RAG 工作流流式对话
- TTS 语音合成
- 音频数据处理

#### 2. 组件层 (`src/components/`)

**VoiceWave3D.vue** - 3D 语音波形可视化
- 基于 Three.js 的 3D 渲染
- 实时音频频谱分析
- 动态波形效果
- 支持自定义颜色和强度

**VoiceChatPanel.vue** - 语音聊天面板
- 语音录制控制
- 实时状态显示
- 音频播放管理
- 错误处理

#### 3. 组合式函数 (`src/composables/`)

**useAudioManager.ts** - 音频管理
- 麦克风录音控制
- 音频频谱分析
- 音量检测
- 设备权限管理

#### 4. 页面组件 (`src/views/`)

**home.vue** - 首页
- 角色选择界面
- 搜索功能
- 角色卡片展示
- 响应式布局

**Conversation.vue** - 对话页面
- 语音对话界面
- 3D 波形显示
- 状态指示器
- 聊天记录
- 角色信息展示

#### 5. 工具函数 (`src/utils/`)

**serviceHealthCheck.ts** - 服务健康检查
- 多服务状态监控
- HTTP/WebSocket 连接检测
- 响应时间统计
- 错误诊断

### 数据流架构

```
用户交互 → 页面组件 → 组合式函数 → API接口 → 后端服务
    ↓           ↓           ↓          ↓
  事件处理 → 状态管理 → 数据处理 → HTTP/WS → 响应处理
```

### 状态管理

项目采用 Vue 3 的响应式系统和组合式函数进行状态管理：
- 用户状态：通过 `userStore.ts` 管理
- 音频状态：通过 `useAudioManager` 管理
- 对话状态：在组件内部管理

### 路由设计

- `/` - 重定向到首页
- `/home` - 首页，角色选择
- `/conversation` - 对话页面
- `/*` - 404 页面

### 样式架构

- **TailwindCSS**: 原子化CSS框架，提供快速样式开发
- **Element Plus**: 组件库样式
- **自定义样式**: `meteor.css` 提供特效样式

### 开发配置

**Vite 配置特性**:
- 路径别名：`@` 指向 `src` 目录
- 开发服务器：端口 9988，自动打开浏览器
- 代理配置：`/organization/*` 代理到后端服务
- 插件：Vue SFC 支持、TailwindCSS 集成

**TypeScript 配置**:
- 严格模式启用
- 路径映射配置
- Vue 类型支持

## 特色功能

1. **智能角色扮演检测**: 自动识别用户的角色扮演意图
2. **实时语音交互**: 支持语音输入和语音输出
3. **3D 可视化效果**: 动态语音波形展示
4. **流式对话**: 实时流式响应，提升用户体验
5. **多服务健康检查**: 自动检测后端服务状态
6. **响应式设计**: 适配不同屏幕尺寸

## 开发指南

### 添加新的API接口

1. 在 `src/api/types/` 中定义类型
2. 在对应的 controller 文件中实现接口函数
3. 在组件中导入并使用

### 添加新的组件

1. 在 `src/components/` 中创建 Vue 组件
2. 使用 TypeScript 和 Composition API
3. 遵循项目的命名规范

### 样式开发

1. 优先使用 TailwindCSS 类名
2. 复杂样式可以在 `src/styles/` 中定义
3. 组件特定样式使用 scoped CSS

## 部署说明

1. 构建生产版本：`pnpm build`
2. 将 `dist` 目录部署到静态文件服务器
3. 配置反向代理，将 `/organization/*` 代理到后端服务
4. 确保所有后端服务正常运行

## 故障排除

1. **跨域问题**: 检查 Vite 代理配置和后端 CORS 设置
2. **服务连接失败**: 使用服务健康检查工具诊断
3. **音频权限问题**: 确保浏览器允许麦克风访问
4. **WebSocket 连接失败**: 检查防火墙和网络配置

## 技术支持

如遇到问题，请检查：
1. 浏览器控制台错误信息
2. 网络请求状态
3. 后端服务日志
4. 项目文档和测试指南

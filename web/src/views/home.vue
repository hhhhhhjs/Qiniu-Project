<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <!-- 顶部导航栏 -->
    <header class="flex justify-between items-center px-6 py-4 bg-white/80 backdrop-blur-sm border-b border-gray-200/50">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-sm">AI</span>
        </div>
        <span class="text-xl font-semibold text-gray-800">智能助手</span>
      </div>

      <div class="flex items-center space-x-4">
        <el-button text class="text-gray-600 hover:text-gray-800">帮助</el-button>
        <el-button type="primary" @click="handleLogin">登录</el-button>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex flex-col items-center justify-center px-6 py-16">
      <!-- 欢迎标题 -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-gray-800 mb-4">
          你好，我是你的<span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">智能角色扮演者</span>
        </h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
          旨在扮演各种角色，在解答问题的同时提供丰富的情绪价值！
        </p>
      </div>

      <!-- 搜索输入框 -->
      <div class="w-full max-w-2xl mb-12">
        <div class="relative">
          <el-input
            v-model="searchQuery"
            placeholder="有什么可以帮你的吗？试试问我任何问题..."
            size="large"
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #suffix>
              <div class="flex items-center space-x-2 pr-2">
                <el-button :icon="Microphone" circle size="small" class="voice-btn" />
                <el-button :icon="Search" type="primary" circle size="small" @click="handleSearch" />
              </div>
            </template>
          </el-input>
        </div>
      </div>

      <!-- 功能卡片 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl mb-16">
        <div
          v-for="feature in features"
          :key="feature.name"
          class="feature-card p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer border border-gray-100 hover:border-blue-200"
          @click="handleFeatureClick(feature)"
        >
          <div class="flex flex-col items-center text-center">
            <div class="w-12 h-12 rounded-lg flex items-center justify-center mb-3" :class="feature.bgColor">
              <component :is="feature.icon" class="w-6 h-6" :class="feature.iconColor" />
            </div>
            <span class="text-sm font-medium text-gray-700">{{ feature.name }}</span>
          </div>
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="text-center text-gray-500 text-sm">
        <p>点击上方功能卡片快速开始，或直接在搜索框中输入你的问题</p>
      </div>
    </main>

    <!-- 登录弹窗 -->
    <el-dialog
      v-model="showLoginDialog"
      width="800px"
      :show-close="true"
      :close-on-click-modal="false"
      :title="null"
      class="login-dialog"
    >
      <div class="flex h-96">
        <!-- 左侧介绍区域 -->
        <div class="w-1/2 bg-gradient-to-br from-blue-500 to-purple-600 text-white p-8 flex flex-col justify-center items-center rounded-l-lg">
          <div class="text-center">
            <!-- 头像 -->
            <div class="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mb-6">
              <el-icon class="text-4xl text-white">
                <ChatDotRound />
              </el-icon>
            </div>

            <!-- 标题 -->
            <h2 class="text-2xl font-bold mb-4">登录后免费使用完整功能</h2>

            <!-- 功能介绍 -->
            <div class="space-y-3 text-sm opacity-90">
              <div class="flex items-center justify-center space-x-2">
                <el-icon><EditPen /></el-icon>
                <span>一键润色写作</span>
              </div>
              <div class="flex items-center justify-center space-x-2">
                <el-icon><PieChart /></el-icon>
                <span>图片视频生成</span>
              </div>
              <div class="flex items-center justify-center space-x-2">
                <el-icon><Document /></el-icon>
                <span>网页文件解析</span>
              </div>
            </div>

            <!-- 下载提示 -->
            <div class="mt-8 p-4 bg-white/10 rounded-lg">
              <h3 class="font-semibold mb-2">下载豆包电脑版</h3>
              <p class="text-xs opacity-80">你的全能 AI 助手，助力每日工作学习</p>
              <el-button
                class="mt-3 w-full"
                type="primary"
                size="small"
                style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3);"
              >
                <el-icon class="mr-1"><Download /></el-icon>
                下载电脑版
              </el-button>
            </div>
          </div>
        </div>

        <!-- 右侧登录表单 -->
        <div class="w-1/2 p-8 bg-white rounded-r-lg">
          <login-form @login-success="handleLoginSuccess" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  Microphone,
  ChatDotRound,
  EditPen,
  Document,
  PieChart,
  VideoCamera,
  Brush,
  Download
} from '@element-plus/icons-vue'
import LoginForm from '@/components/LoginForm.vue'
import { useRouter } from 'vue-router'

// 响应式数据
const showLoginDialog = ref<boolean>(false)
const searchQuery = ref('')
const router = useRouter()

// 功能卡片数据
const features = ref([
  {
    name: '智能对话',
    icon: ChatDotRound,
    bgColor: 'bg-blue-100',
    iconColor: 'text-blue-600',
    action: 'chat'
  },
  {
    name: '文本创作',
    icon: EditPen,
    bgColor: 'bg-green-100',
    iconColor: 'text-green-600',
    action: 'write'
  },
  {
    name: '文档分析',
    icon: Document,
    bgColor: 'bg-purple-100',
    iconColor: 'text-purple-600',
    action: 'analyze'
  },
  {
    name: '数据洞察',
    icon: PieChart,
    bgColor: 'bg-orange-100',
    iconColor: 'text-orange-600',
    action: 'insight'
  },
  {
    name: '视频理解',
    icon: VideoCamera,
    bgColor: 'bg-red-100',
    iconColor: 'text-red-600',
    action: 'video'
  },
  {
    name: '图像生成',
    icon: Brush,
    bgColor: 'bg-pink-100',
    iconColor: 'text-pink-600',
    action: 'image'
  }
])

// 方法
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入你的问题')
    return
  }

  // 这里可以处理搜索逻辑
  ElMessage.info(`正在处理: ${searchQuery.value}`)
  // 可以跳转到聊天页面或处理搜索
}

const handleFeatureClick = (feature: any) => {
  ElMessage.info(`点击了: ${feature.name}`)
  // 这里可以根据不同的功能跳转到不同页面或执行不同操作
}

const handleLoginSuccess = () => {
  showLoginDialog.value = false
  ElMessage.success('登录成功！')
  // 这里可以处理登录成功后的逻辑
}

const handleLogin = () => {
    showLoginDialog.value = true
}

</script>

<style scoped>
.search-input :deep(.el-input__wrapper) {
  border-radius: 24px;
  padding: 12px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: #3b82f6;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
}

.search-input :deep(.el-input__inner) {
  font-size: 16px;
  color: #374151;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: #9ca3af;
}

.voice-btn {
  background: transparent !important;
  border: none !important;
  color: #6b7280 !important;
}

.voice-btn:hover {
  background: #f3f4f6 !important;
  color: #374151 !important;
}

.feature-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover {
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }

  h1 {
    font-size: 2.5rem !important;
  }

  .search-input {
    margin: 0 1rem;
  }
}

@media (max-width: 640px) {
  .px-6 {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  h1 {
    font-size: 2rem !important;
  }

  .text-xl {
    font-size: 1.125rem !important;
  }
}

/* 登录弹窗样式 */
.login-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.login-dialog :deep(.el-dialog__header) {
  display: none;
}

.login-dialog :deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
}

/* 登录弹窗响应式调整 */
@media (max-width: 768px) {
  .login-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
}
</style>
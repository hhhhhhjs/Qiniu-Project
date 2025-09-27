<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <!-- 顶部导航栏 -->
    <header
      class="flex justify-between items-center px-6 py-2 bg-white/80 backdrop-blur-sm border-b border-gray-200/50"
    >
      <div class="w-20 h-20">
        <img src="@/assets/images/yuling.png" alt="logo" />
      </div>

      <div class="flex items-center space-x-4">
        <el-button text class="text-gray-600 hover:text-gray-800"
          >帮助</el-button
        >
        <el-button type="primary" @click="handleLogin">登录</el-button>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex flex-col items-center justify-center px-6">
      <!-- 欢迎标题 -->
      <div class="text-center mb-12">
        <div class="meteor-frame inline-block px-10 py-6 rounded-full relative">
          <span class="meteor-border"></span>
          <h1 class="m-0">
            <span
              class="meteor-content text-5xl font-bold text-gray-800 leading-tight inline-block"
            >
              你好，我是
              <span
                class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
                >语灵</span
              >
              你的<span
                class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
                >智能角色扮演者</span
              >
            </span>
          </h1>
        </div>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed mt-4">
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
                <el-button
                  :icon="Microphone"
                  circle
                  size="small"
                  class="voice-btn"
                />
                <el-button
                  :icon="Search"
                  type="primary"
                  circle
                  size="small"
                  @click="handleSearch"
                />
              </div>
            </template>
          </el-input>
        </div>
      </div>

      <!-- 功能卡片 -->
      <div
        class="grid grid-cols-3 md:grid-cols-3 gap-10 w-[45%] max-w-4xl mb-16"
      >
        <el-card
          v-for="feature in features"
          :key="feature.id"
          class="phone-card cursor-pointer hover:shadow-lg transition-shadow"
          @click="handleFeatureClick(feature)"
          :body-style="{ padding: '0' }"
          shadow="hover"
        >
          <div
            class="bg-[#0B0B0C] rounded-2xl overflow-hidden h-80 w-full cursor-pointer"
          >
            <img
              :src="feature.background"
              :alt="feature.roleName"
              class="w-full h-full object-cover"
            />
          </div>
        </el-card>
      </div>

      <!-- 底部提示 -->
      <div class="text-center text-gray-500 text-sm">
        <p>点击上方功能卡片快速开始，或直接在搜索框中输入你想要扮演的角色</p>
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
      <div class="flex h-[400px]">
        <!-- 左侧介绍区域 -->
        <div
          class="w-1/2 p-8 flex flex-col justify-center items-center rounded-l-lg"
        >
          <img src="@/assets/images/yuling.png" alt="logo" />
        </div>

        <!-- 右侧登录/注册表单 -->
        <div class="w-1/2 bg-white rounded-r-lg">
          <KeepAlive>
            <component
              :is="currentComponent"
              @login-success="handleLoginSuccess"
              @register-click="handleRegister"
              @register-success="handleRegisterSuccess"
              @login-click="handleLogin"
            ></component>
          </KeepAlive>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Ref, ref, shallowRef } from 'vue'
import type { Component } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Microphone, Message } from '@element-plus/icons-vue'
import LoginForm from '@/components/user/LoginForm.vue'
import { useRouter } from 'vue-router'
// 导入图片
import jixiaomeiImg from '@/assets/images/roles/jixiaomei.jpg'
import petAssistant from '@/assets/images/roles/petAssistant.jpg'
import healthAssistant from '@/assets/images/roles/healthAssistant.jpg'
// 组件
import RegisterForm from '@/components/user/RegisterForm.vue'
import * as lodash from 'lodash'
// 角色扮演相关
import { detectRoleplayIntent } from '@/api/roleplayController'

interface UserInfo {
  id: string | number
  email: string
  name: string
  phone: string | number
}

// 响应式数据
const showLoginDialog = ref<boolean>(false)
const searchQuery = ref('')
const currentComponent = shallowRef<Component>(LoginForm)
const router = useRouter()

interface featureType {
  id: number
  roleName: string
  background: string
}

// 功能卡片数据
const features: Ref<Array<featureType>> = ref([
  {
    id: 1,
    roleName: '集小美',
    background: jixiaomeiImg,
  },
  {
    id: 2,
    roleName: '猫狗宠物助手',
    background: petAssistant,
  },
  {
    id: 3,
    roleName: '养生助手',
    background: healthAssistant,
  },
])

// 方法
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入你想要扮演的角色')
    return
  }

  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage({
      message: '哎呀，登录后再来试试吧(•̀⌓• )~',
      type: 'warning',
    })
    return
  }

  try {
    // 第一步：角色扮演意图检测
    const intentResult = await detectRoleplayIntent({
      text: searchQuery.value.trim()
    })

    if (!intentResult.is_roleplay) {
      // 不是角色扮演请求，显示提示
      ElMessage({
        message: '我是一个智能角色扮演 AI，请输入相关的角色名',
        type: 'warning'
      })
      return
    }

    // 是角色扮演请求，跳转到对话页面并传递角色信息
    if (intentResult.role_name) {
      router.push({
        path: '/conversation',
        query: {
          userid: 1, // TODO: 修改为真实用户 id
          robotRoleName: intentResult.role_name,
          isRoleplay: 'true', // 标识这是角色扮演模式
          originalInput: searchQuery.value.trim() // 传递原始输入用于角色设定
        },
      })
    } else {
      ElMessage.error('未能识别到具体的角色名称，请重新输入')
    }
  } catch (error) {
    console.error('角色扮演检测失败:', error)
    ElMessage.error('角色扮演检测失败，请稍后重试')
  }
}

// 原始的点击处理函数
const handleFeatureClickOriginal = (feature: any) => {
  // 直接跳转到对话页面，不需要登录验证
  const token = localStorage.getItem('token')
  let userid = 'guest' // 默认访客ID

  // 如果已经登录，使用真实用户ID
  if (token) {
    try {
      // const userInfoStr = localStorage.getItem('userInfo')!
      // const userInfo: UserInfo = JSON.parse(userInfoStr)
      // userid = userInfo.id.toString()
      // 跳转到对话页面
      router.push({
        path: '/conversation',
        query: {
          userid: 1, // TODO: 修改为真实用户 id
          robotRoleName: feature.roleName,
        },
      })
    } catch (error) {
      console.warn('解析用户信息失败，使用访客模式')
    }
  } else {
    ElMessage({
      message: '哎呀，登录后再来试试吧(•̀⌓• )~',
      type: 'warning',
    })
  }
}

// 使用 lodash 防抖包装的功能点击处理函数
const handleFeatureClick = lodash.debounce(handleFeatureClickOriginal, 300)

const handleLoginSuccess = () => {
  showLoginDialog.value = false
  // 这里可以处理登录成功后的逻辑
}

const handleLogin = (message: string) => {
  showLoginDialog.value = true
  console.log('登录', message)
  if (message) {
    currentComponent.value = LoginForm
  }
}

const handleRegister = (message: string) => {
  if (message) {
    currentComponent.value = RegisterForm
  }
}

const handleRegisterSuccess = (value: string) => {
  if (value) {
    currentComponent.value = LoginForm
  }
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

.phone-card {
  border: none;
  background: transparent;
}
.phone-card :deep(.el-card__body) {
  padding: 0;
  background: transparent;
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

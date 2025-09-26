<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <!-- 顶部导航栏 - 与 home 组件保持一致 -->
    <header class="flex justify-between items-center px-6 py-2 bg-white/80 backdrop-blur-sm border-b border-gray-200/50">
      <div class="w-20 h-20">
        <img src="@/assets/images/yuling.png" alt="logo" />
      </div>
      <div class="flex items-center space-x-4">
        <el-button text class="text-gray-600 hover:text-gray-800">帮助</el-button>
        <el-button type="primary" @click="goHome">返回首页</el-button>
      </div>
    </header>

    <!-- 404 内容区域 -->
    <main class="flex items-center justify-center px-6 relative overflow-hidden" style="height: calc(100vh - 100px);">
      <div class="text-center z-10 relative">
        <div class="error-code text-6xl md:text-7xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          404
        </div>
        <div class="text-xl md:text-2xl mb-3 font-semibold text-gray-800">页面未找到</div>
        <div class="text-base mb-6 text-gray-600 max-w-md mx-auto leading-relaxed">
          抱歉，您访问的页面不存在或已被移除
        </div>
        <div class="flex gap-3 justify-center flex-wrap">
          <el-button
            type="primary"
            @click="goHome"
            class="px-6 py-2 font-semibold transition-all duration-300 hover:-translate-y-1"
          >
            返回首页
          </el-button>
          <el-button
            @click="goBack"
            class="px-6 py-2 font-semibold transition-all duration-300 hover:-translate-y-1"
          >
            返回上页
          </el-button>
        </div>
      </div>

      <!-- 浮动装饰元素 -->
      <div class="floating-elements absolute inset-0 pointer-events-none">
        <div class="element element-1 absolute w-20 h-20 bg-blue-200/30 rounded-full top-1/5 left-1/10"></div>
        <div class="element element-2 absolute w-30 h-30 bg-purple-200/30 rounded-full top-3/5 right-1/6"></div>
        <div class="element element-3 absolute w-15 h-15 bg-blue-300/40 rounded-full bottom-1/5 left-1/5"></div>
        <div class="element element-4 absolute w-12 h-12 bg-purple-300/30 rounded-full top-1/3 right-1/4"></div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/home')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
/* 自定义动画效果 */
.error-code {
  animation: bounce 2s infinite;
}

.element {
  animation: float 6s ease-in-out infinite;
}

.element-1 {
  animation-delay: 0s;
}

.element-2 {
  width: 120px;
  height: 120px;
  animation-delay: 2s;
}

.element-3 {
  width: 60px;
  height: 60px;
  animation-delay: 4s;
}

.element-4 {
  width: 48px;
  height: 48px;
  animation-delay: 3s;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
  60% {
    transform: translateY(-4px);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-15px) rotate(180deg);
    opacity: 0.6;
  }
}

/* 自定义 Tailwind 扩展类 */
.w-30 {
  width: 7.5rem;
}

.h-30 {
  height: 7.5rem;
}

.w-15 {
  width: 3.75rem;
}

.h-15 {
  height: 3.75rem;
}

.w-12 {
  width: 3rem;
}

.h-12 {
  height: 3rem;
}

.left-1\/10 {
  left: 10%;
}

.right-1\/6 {
  right: 16.666667%;
}

.right-1\/4 {
  right: 25%;
}

.left-1\/5 {
  left: 20%;
}

.top-1\/5 {
  top: 20%;
}

.top-1\/3 {
  top: 33.333333%;
}

.top-3\/5 {
  top: 60%;
}

.bottom-1\/5 {
  bottom: 20%;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .error-code {
    font-size: 4rem !important;
  }

  .element-2 {
    width: 80px;
    height: 80px;
  }

  .element-3 {
    width: 40px;
    height: 40px;
  }

  .element-4 {
    width: 32px;
    height: 32px;
  }
}
</style>

<template>
  <div class="login-form-container">
    <div class="text-center mb-6">
      <h3 class="text-xl font-semibold text-gray-800 mb-2">欢迎登录</h3>
    </div>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      size="large"
      @submit.prevent="handleSubmit"
    >
      <el-form-item prop="account">
        <el-input
          v-model="form.account"
          placeholder="请输入账号"
          :prefix-icon="User"
          clearable
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          :prefix-icon="Lock"
          show-password
          clearable
          @keyup.enter="handleSubmit"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          class="w-full"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ loading ? '登录中...' : '登录' }}
        </el-button>
      </el-form-item>
    </el-form>

    <div class="text-center text-sm text-gray-500 mt-4">
      <span>还没有账号？</span>
      <el-button type="primary" text @click="handleRegister">立即注册</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

// 定义事件
const emit = defineEmits<{
  'login-success': [userInfo: any]
  'register-click': [isRegister: string]
}>()

// 响应式数据
const formRef = ref()
const loading = ref(false)

const form = reactive({
  account: '',
  password: ''
})

const rules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '账号长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    // 模拟登录请求
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 模拟登录成功
    const userInfo = {
      id: 1,
      username: form.account,
      email: `${form.account}@example.com`
    }

    ElMessage.success('登录成功！')
    
    // 触发登录成功事件，传递用户信息
    emit('login-success', userInfo)

  } catch (error) {
    ElMessage.error('登录失败，请检查账号密码')
  } finally {
    loading.value = false
  }
}

const handleRegister = () => {
  emit('register-click', 'RegisterForm')
}
</script>

<style scoped>
.login-form-container {
  padding: 20px;
  max-width: 400px;
  margin: 0 auto;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
  height: 44px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>

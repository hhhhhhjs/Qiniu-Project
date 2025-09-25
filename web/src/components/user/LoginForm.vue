<template>
  <div class="login-form-container">
    <div class="text-center mb-8 mt-10">
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
      <el-form-item prop="phone">
        <el-input
          v-model="form.phone"
          placeholder="请输入手机号"
          :prefix-icon="Phone"
          clearable
        />
      </el-form-item>
      <div class="text-right text-sm -mt-2 mb-2 flex place-content-between">
        <img :src="captchaUrl" alt="验证码" v-if="captchaUrl" class="w-20 h-6 block">
        <el-link type="primary" :underline="false" @click="handleGetCode">获取验证码</el-link>
      </div>


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

      <el-form-item prop="code">
        <el-input
          v-model="form.code"
          placeholder="请输入验证码"
          :prefix-icon="Message"
          clearable
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

    <div class="text-center text-sm text-gray-500 mt-0">
      <span>还没有账号？</span>
      <el-link @click="handleRegister">立即注册</el-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Phone, Message, Lock } from '@element-plus/icons-vue'
import { login, getVerifyCode } from '@/api/userController'

// 定义事件
const emit = defineEmits<{
  'login-success': [userInfo: any]
  'register-click': [isRegister: string]
}>()

// 响应式数据
const formRef = ref()
const loading = ref<boolean>(false)
const captchaUrl = ref<string>('')

const form = reactive({
  phone: '',
  code: '',
  password: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: ['blur', 'change'] }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleGetCode = async () => {
  if (!form.phone) {
    ElMessage.warning('请先输入手机号')
    return
  }
  try {
    const blob = await getVerifyCode() as unknown as Blob
    if (captchaUrl.value) URL.revokeObjectURL(captchaUrl.value)
    captchaUrl.value = URL.createObjectURL(blob)
  } catch (e: any) {
    const msg = e?.response?.data?.message || '获取验证码失败'
    ElMessage.error(msg)
  }
}

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    const payload = {
      phone: form.phone,
      password: btoa(form.password),
      code: form.code
    }
    const res = await login(payload as any)
    if(res.success){
      localStorage.setItem('token', res.obj)
      ElMessage.success('登录成功！')
      emit('login-success', 'loginSuccess')
    } else {
      ElMessage.error(res.msg || '登录失败')
    }

  } catch (e: any) {
    const msg = e?.response?.data?.message || '登录失败，请检查手机号、密码或验证码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const handleRegister = () => {
  emit('register-click', 'RegisterForm')
}

onBeforeUnmount(() => {
  if (captchaUrl.value) URL.revokeObjectURL(captchaUrl.value)
})

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

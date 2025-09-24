<template>
  <div class="login-form-container">
    <div class="text-center mb-6">
      <h3 class="text-xl font-semibold text-gray-800 mb-2">创建账号</h3>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      size="large"
      @submit.prevent="handleSubmit"
    >
      <el-form-item prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入用户名"
          :prefix-icon="User"
          clearable
        />
      </el-form-item>

      <el-form-item prop="email">
        <el-input
          v-model="form.email"
          placeholder="请输入邮箱"
          clearable
        />
      </el-form-item>

      <el-form-item prop="phone">
        <el-input
          v-model="form.phone"
          placeholder="请输入手机号"
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
        />
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          :prefix-icon="Lock"
          show-password
          clearable
        />
      </el-form-item>

      <el-form-item prop="agree" class="agree-item">
        <el-checkbox v-model="form.agree">我已阅读并同意《用户协议》和《隐私政策》</el-checkbox>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          class="w-full"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ loading ? '注册中...' : '注册' }}
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { addUser } from '@/api/userController'

// 事件定义
const emit = defineEmits<{
  'register-success': [registerSuccess: string]
  'login-click': [loginSuccess: string]
}>()

// 表单引用与状态
const formRef = ref()
const loading = ref(false)

const form = reactive({
  name: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  agree: false,
})

const validateConfirm = (rule: any, value: string, callback: Function) => {
  void rule
  if (!value) return callback(new Error('请再次输入密码'))
  if (value !== form.password) return callback(new Error('两次输入的密码不一致'))
  callback()
}

const validateAgree = (rule: any, value: boolean, callback: Function) => {
  void rule
  if (!value) return callback(new Error('请选择同意协议'))
  callback()
}

const rules = {
  name: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirm, trigger: ['blur', 'change'] }
  ],
  agree: [
    { validator: validateAgree, trigger: 'change' }
  ]
}

// 提交方法
const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    loading.value = true

    const payload = {
      name: form.name,
      email: form.email,
      phone: form.phone,
      password: form.password
    }
    await addUser(payload as any)

    ElMessage.success('注册成功！')
    emit('register-success', 'registerSuccess')
  } catch (e: any) {
    const msg = e?.response?.data?.message || '注册失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const handleGoLogin = () => {
  emit('login-click', 'successLogin')
}
</script>

<style scoped>
.login-form-container {
  max-width: 360px; /* 稍微增加宽度，但保持紧凑 */
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

/* 收紧表单头部间距与协议字号 */
.login-form-container .text-center { margin-bottom: 8px; }
:deep(.el-checkbox__label) { font-size: 12px; }


:deep(.el-input__wrapper) {
  border-radius: 10px;
  height: 38px;
  padding: 0 10px;
}

:deep(.el-input__inner) {
  font-size: 14px;
}

:deep(.el-form-item) {
  margin-bottom: 18px; /* 仍为错误提示预留空间，同时整体再收紧一些 */
}

:deep(.el-button) {
  border-radius: 10px;
  height: 36px; /* 调小按钮高度 */
}

:deep(.el-form-item__content) {
  position: relative;
}

/* 阅读用户协议 — 单独收紧与按钮间距 */
.agree-item {
  margin-bottom: 12px; /* 再往上提一点，仍保留错误提示空间 */
}

:deep(.el-form-item__error) {
  position: absolute;
  top: 100%;
  left: 0;
  margin: 2px 0 0 0; /* 与输入框保持极小距离 */
  padding: 0;
  font-size: 12px;
  line-height: 1.2;
  white-space: nowrap; /* 避免换行导致高度增加 */
  pointer-events: none; /* 避免影响交互 */
}
</style>
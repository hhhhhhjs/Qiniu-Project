<template>
  <div class="login-form-container">
    <div class="text-center mb-6">
      <h3 class="text-xl font-semibold text-gray-800 mb-2">创建账号</h3>
      <p class="text-gray-600 text-sm">填写以下信息完成注册</p>
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
          placeholder="请输入用户名"
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

      <el-form-item prop="agree">
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

    <div class="text-center text-sm text-gray-500 mt-4">
      <span>已经有账号？</span>
      <el-button type="primary" text @click="handleGoLogin">去登录</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'


// 事件定义
const emit = defineEmits<{
  'register-success': [registerSuccess: string]
  'login-click': []
}>()

// 表单引用与状态
const formRef = ref()
const loading = ref(false)

const form = reactive({
  account: '',
  email: '',
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
  account: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
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

    // 调用后端注册接口
    await registerApi({ account: form.account, password: form.password, email: form.email })

    ElMessage.success('注册成功！')
    emit('register-success', 'registerSuccess')
  } catch (e) {
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleGoLogin = () => {
  emit('login-click')
}
</script>

<style scoped>
.login-form-container {
  max-width: 320px;
  width: 100%;
  padding: 8px;
  margin: 0 auto;
  box-sizing: border-box;
}

/* 收紧表单头部间距与协议字号 */
.login-form-container .text-center { margin-bottom: 12px; }
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
  margin-bottom: 12px;
}

:deep(.el-button) {
  border-radius: 10px;
  height: 40px;
}

:deep(.el-form-item__error) {
  position: static; /* 让错误提示占据文档流，避免与下一个输入重叠 */
  margin-top: 4px;
}
</style>
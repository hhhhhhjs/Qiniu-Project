<template>
  <div class="min-h-screen  from-slate-950 via-slate-900 to-slate-800 text-slate-100">
    <div class="mx-auto max-w-6xl px-4 py-8">
      <!-- 右侧：登录表单 -->
      <el-card class="bg-slate-900/60 border border-white/10 backdrop-blur col-span-1" shadow="hover">
        <div class="mb-4">
          <div class="text-xl font-semibold">登录账号</div>
          <div class="text-xs text-slate-400 mt-1">登录后免费享受激情扮演！</div>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="space-y-2">
          <el-form-item label="账号" prop="account">
            <el-input v-model="form.account" :prefix-icon="User" placeholder="手机号 / 邮箱 / 用户名" clearable />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" :prefix-icon="Lock" placeholder="密码" show-password />
          </el-form-item>
          <el-button type="primary" size="large" class="w-full" >登录</el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'



const formRef = ref()
const form = reactive({ account: '', password: '' })
const rules = {
  account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}





</script>

<style scoped>
</style>
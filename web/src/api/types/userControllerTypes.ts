export interface Login {
  code: string // 验证码
  phone: string
  password: string // base64 处理后的密码
}

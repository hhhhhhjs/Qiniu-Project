export interface Login {
  code: string // 验证码
  phone: string
  password: string // base64 处理后的密码
}

export interface addUserType {
  email: string
  name: string
  password: string
  phone: string
}

export interface editUserMesType {
  email: string
  id: number
  name: string
  phone: string
}

export interface changeUserPasswordType {
  id: string | number
  password: string
  newPassword: string
}
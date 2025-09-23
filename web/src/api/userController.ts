import request from './axios'
import type { Login } from './types/userControllerTypes'


// 获取验证码
export const getVerifyCode = () => {
  return request.get('/organization/user/pictureCode')
}

// 登录
export const login = (data: Login) => {
  return request.post('/user/login', data)
}

// 注册
// export const register = (data: RegisterPayload) => {
//   return request.post('/user/register', data)
// }

// 登出
export const logout = () => {
  return request.post('/user/logout')
}

// 获取用户信息
export const getProfile = () => {
  return request.get('/user/profile')
}

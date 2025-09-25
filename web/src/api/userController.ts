import request from './axios'
import type { Login, addUserType, editUserMesType, changeUserPasswordType } from './types/userControllerTypes'


// 获取验证码
export const getVerifyCode = (): Promise<Blob> => {
  return request.get('/user/pictureCode', { responseType: 'blob' })
}

// 通用 API 响应接口
interface ApiResponse<T = any> {
  code: number
  success?: boolean
  obj?: T
  msg: string
}

// 登录
export const login = (data: Login): Promise<ApiResponse> => {
  return request.post('/user/login', data)
}

// 登出
export const logout = (): Promise<ApiResponse> => {
  return request.delete('/user')
}

// 新增用户 && 注册
export const addUser = (data: addUserType): Promise<ApiResponse> => {
  return request.post('/user', data)
}

// 修改用户信息
export const editUserMes = (data: editUserMesType): Promise<ApiResponse> => {
  return request.put('/user/updateUser', data)
}

// 删除用户信息
export const deleteUserMes = (id: number | string): Promise<ApiResponse> => {
  return request.delete('/user/deleteUser', {
    params: {
      id
    }
  })
}

// 获取用户信息列表
export const getUserList = (): Promise<ApiResponse> => {
  return request.get('/user/list')
}

// 重置用户密码
export const resetUserPassword = (id: number | string): Promise<ApiResponse> => {
  return request.put('/user/reset', {
    id
  })
}

// 修改用户密码
export const changeUserPassword = (data: changeUserPasswordType): Promise<ApiResponse> => {
  return request.put(`/user/updatePassword/${data.id}`, data)
}

// 获取单个用户信息
export const getUserMes = (userId: string | number): Promise<ApiResponse> => {
  return request.get('/user/userInfo', {
    params: {
      userId
    }
  })
}
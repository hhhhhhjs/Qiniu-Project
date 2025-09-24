import request from './axios'
import type { Login, addUserType, editUserMesType, changeUserPasswordType } from './types/userControllerTypes'


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
  return request.delete('/user')
}

// 新增用户 && 注册
export const addUser = (data: addUserType) => {
  return request.post('/user', data)
}

// 修改用户信息
export const editUserMes = (data: editUserMesType) => {
  return request.put('/user/updateUser', data)
}

// 删除用户信息
export const deleteUserMes = (id: number | string) => {
  return request.delete('/user/deleteUser', {
    params: {
      id
    }
  })
}

// 获取用户信息列表
export const getUserList = () => {
  return request.get('/user/list')
}

// 重置用户密码
export const resetUserPassword = (id: number | string) => {
  return request.put('user/reset', {
    id
  })
}

// 修改用户密码
export const changeUserPassword = (data: changeUserPasswordType) => {
  return request.put(`/user/updatePassword/${data.id}`, data)
}

// 获取单个用户信息
export const getUserMes = (userId: string | number) => {
  return request.get('/user/userInfo', {
    params: {
      userId
    }
  })
}
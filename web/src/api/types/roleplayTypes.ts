// 角色扮演意图检测相关类型
export interface RoleplayIntentRequest {
  text: string
}

export interface RoleplayIntentResponse {
  is_roleplay: boolean
  intent_label: 'roleplay' | 'not_roleplay' | 'unsure'
  confidence: number
  role_name: string | null
  triggers: string[]
  reasoning: string
}

// 角色扮演流式自我介绍相关类型
export interface RoleplayStreamRequest {
  text: string
}

export interface RoleplayStreamFinalData {
  role_name: string
  profession: string
  abilities: string[]
  style: string
  self_introduction: string
}

// 角色对话流式相关类型
export interface RoleChatStreamRequest {
  role_name: string
  profession: string
  abilities: string | string[]
  style: string
  user_input: string
  history?: Array<{
    role: 'user' | 'assistant'
    content: string
  }>
}

// SSE 事件类型
export interface SSEEvent {
  event: 'start' | 'normalize' | 'recall' | 'rerank' | 'delta' | 'done' | 'final' | 'end' | 'warn' | 'error'
  ts?: string
  elapsed_ms?: number
  text?: string
  hit_count?: number
  skipped?: boolean
  candidates?: number
  preview?: string
  reason?: string
  answer?: string
  timings?: any
  total_ms?: number
  stage?: string
  message?: string
  data?: any
  error?: string
}

// 通用 API 响应接口
export interface ApiResponse<T = any> {
  code: number
  success?: boolean
  obj?: T
  msg: string
}

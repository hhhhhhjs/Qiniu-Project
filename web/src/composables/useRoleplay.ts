import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { startRoleplayStream, startRoleChatStream } from '@/api/roleplayController'
import type { RoleplayStreamFinalData } from '@/api/types/roleplayTypes'

export function useRoleplay() {
  const route = useRoute()
  
  // 角色扮演相关状态
  const isRoleplayMode = computed(() => route.query.isRoleplay === 'true')
  const originalInput = computed(() => route.query.originalInput as string || '')
  const roleplayData = ref<RoleplayStreamFinalData | null>(null)
  const isIntroductionComplete = ref(false)

  // 角色扮演初始化函数
  async function initializeRoleplay(
    onStreamingMessage?: (messageId: string, text: string) => void,
    onFinishMessage?: (messageId: string) => void,
    onStartMessage?: () => string | undefined,
    onPlayTTS?: (text: string) => void
  ) {
    if (!isRoleplayMode.value || !originalInput.value) {
      console.log('跳过角色扮演初始化:', { 
        isRoleplayMode: isRoleplayMode.value, 
        originalInput: originalInput.value 
      })
      return
    }

    // 防止重复初始化
    if (isIntroductionComplete.value || roleplayData.value) {
      console.log('角色扮演已初始化，跳过重复初始化')
      return
    }

    try {
      console.log('开始角色扮演初始化...', { originalInput: originalInput.value })

      // 第二步：调用角色自我介绍流式接口
      let fullIntroduction = ''
      const messageId = onStartMessage?.()

      if (!messageId) {
        throw new Error('无法创建消息')
      }

      await startRoleplayStream(
        { text: originalInput.value },
        (event) => {
          switch (event.event) {
            case 'start':
              console.log('角色扮演开始', event.ts)
              break

            case 'normalize':
              console.log('文本标准化完成:', event.text, `耗时: ${event.elapsed_ms}ms`)
              break

            case 'recall':
              console.log('召回完成:', `命中数量: ${event.hit_count}`, `耗时: ${event.elapsed_ms}ms`)
              break

            case 'rerank':
              console.log('重排序完成:', `候选数: ${event.candidates}`, `耗时: ${event.elapsed_ms}ms`)
              if (event.preview) {
                console.log('预览内容:', event.preview.substring(0, 100) + '...')
              }
              break

            case 'delta':
              if (event.text) {
                fullIntroduction += event.text
                onStreamingMessage?.(messageId, fullIntroduction)
              }
              break

            case 'done':
              console.log('处理完成:', `总耗时: ${event.total_ms}ms`)
              break

            case 'final':
              // 保存角色数据用于后续对话
              // final 事件的整个 event 对象（除了 event 字段）就是角色数据
              const { event: eventType, ...roleData } = event
              if (roleData && Object.keys(roleData).length > 0) {
                roleplayData.value = roleData as RoleplayStreamFinalData
                console.log('角色数据已保存:', roleplayData.value)
              }
              break

            case 'end':
              onFinishMessage?.(messageId)
              isIntroductionComplete.value = true

              // 播放 TTS 语音
              if (fullIntroduction.trim()) {
                onPlayTTS?.(fullIntroduction)
              }
              console.log('角色自我介绍完成')
              break

            case 'warn':
            case 'error':
              console.warn('角色扮演警告:', event.error || event.message)
              break

            default:
              console.log('未知事件类型:', event.event, event)
              break
          }
        }
      )
    } catch (error) {
      console.error('角色扮演初始化失败:', error)
      ElMessage.error('角色扮演初始化失败，请稍后重试')
    }
  }

  // 角色扮演对话处理函数
  async function handleRoleplayChat(
    content: string,
    messageId: string,
    onStreamingMessage?: (messageId: string, text: string) => void,
    onFinishMessage?: (messageId: string) => void,
    onPlayTTS?: (text: string) => void
  ): Promise<void> {
    if (!roleplayData.value) {
      throw new Error('角色数据未准备就绪')
    }

    let fullResponse = ''

    // 获取对话历史（简化版，暂时使用空数组，后续可以扩展）
    const history: Array<{role: 'user' | 'assistant', content: string}> = []

    await startRoleChatStream(
      {
        role_name: roleplayData.value.role_name,
        profession: roleplayData.value.profession,
        abilities: roleplayData.value.abilities,
        style: roleplayData.value.style,
        user_input: content,
        history: history
      },
      (event) => {
        switch (event.event) {
          case 'start':
            console.log('角色对话开始', event.ts)
            break

          case 'normalize':
            console.log('文本标准化完成:', event.text, `耗时: ${event.elapsed_ms}ms`)
            break

          case 'recall':
            console.log('召回完成:', `命中数量: ${event.hit_count}`, `耗时: ${event.elapsed_ms}ms`)
            break

          case 'rerank':
            console.log('重排序完成:', `候选数: ${event.candidates}`, `耗时: ${event.elapsed_ms}ms`)
            break

          case 'delta':
            if (event.text) {
              fullResponse += event.text
              onStreamingMessage?.(messageId, fullResponse)
            }
            break

          case 'done':
            console.log('处理完成:', `总耗时: ${event.total_ms}ms`)
            break

          case 'end':
            onFinishMessage?.(messageId)

            // 播放 TTS 语音
            if (fullResponse.trim()) {
              onPlayTTS?.(fullResponse)
            }
            break

          case 'warn':
          case 'error':
            console.warn('角色对话警告:', event.error || event.message)
            break

          default:
            console.log('未知事件类型:', event.event, event)
            break
        }
      }
    )
  }

  // 重置角色扮演状态
  function resetRoleplayState() {
    roleplayData.value = null
    isIntroductionComplete.value = false
  }

  return {
    // 状态
    isRoleplayMode,
    originalInput,
    roleplayData,
    isIntroductionComplete,
    
    // 方法
    initializeRoleplay,
    handleRoleplayChat,
    resetRoleplayState
  }
}

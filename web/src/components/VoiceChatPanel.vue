<template>
  <div class="voice-chat-panel">
    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="{ 'user-message': message.isUser, 'ai-message': !message.isUser }"
        :data-is-user="message.isUser"
        :data-message-id="message.id"
      >
        <div class="message-bubble" :class="{ 'streaming': message.isStreaming }">
          <div
            class="message-content"
            v-if="message.isUser || !message.htmlContent"
          >
            {{ message.content }}
          </div>
          <div
            v-else
            class="message-content markdown-content"
            v-html="message.htmlContent"
          ></div>
          <div class="message-time">
            {{ formatTime(message.timestamp) }}
            <span v-if="message.isStreaming" class="streaming-indicator">●</span>
            <!-- 调试信息 -->
            <span class="debug-info" style="font-size: 10px; opacity: 0.5; margin-left: 5px;">
              {{ message.isUser ? 'USER' : 'AI' }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 实时语音转文字显示 -->
      <div v-if="currentTranscript" class="message-item user-message realtime">
        <div class="message-bubble realtime-bubble">
          <div class="message-content">{{ currentTranscript }}</div>
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框区域 -->
    <div class="input-area">
      <div class="input-container">
        <el-input
          v-model="inputText"
          placeholder="输入消息或使用语音对话..."
          size="large"
          class="chat-input"
          @keyup.enter="sendMessage"
          :disabled="isProcessing"
        >
          <template #suffix>
            <div class="flex items-center space-x-2 pr-2">
              <el-button
                :icon="Microphone"
                circle
                size="small"
                class="voice-btn"
                :class="{ active: isListening }"
                @click="toggleVoiceInput"
              />
              <el-button
                :icon="Promotion"
                type="primary"
                circle
                size="small"
                @click="sendMessage"
                :disabled="!inputText.trim() || isProcessing"
              />
            </div>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { Microphone, Promotion } from '@element-plus/icons-vue'
import { marked } from 'marked'

// 消息接口定义
interface ChatMessage {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
  isStreaming?: boolean // 是否正在流式更新
  htmlContent?: string // 渲染后的 HTML 内容
}

// Props
interface Props {
  isListening?: boolean
  currentTranscript?: string
  isProcessing?: boolean
}

// 使用 withDefaults 编译器宏来设置默认值
const props = withDefaults(defineProps<Props>(), {
  isListening: false,
  currentTranscript: '',
  isProcessing: false
})

// Emits
const emit = defineEmits<{
  sendMessage: [content: string]
  toggleVoice: []
}>()

// 响应式数据
const inputText = ref('')
const messages = ref<ChatMessage[]>([])
const messagesContainer = ref<HTMLElement>()

// 函数方法
const sendMessage = () => {
  if (!inputText.value.trim() || props.isProcessing) return

  const messageId = `user_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`
  const message: ChatMessage = {
    id: messageId,
    content: inputText.value.trim(),
    isUser: true,
    timestamp: new Date()
  }

  console.log('👤 创建用户消息:', {
    messageId,
    isUser: message.isUser,
    content: message.content,
    totalMessages: messages.value.length
  })

  messages.value.push(message)

  console.log('👤 用户消息已添加到列表:', {
    messageId,
    newTotalMessages: messages.value.length,
    lastMessage: messages.value[messages.value.length - 1]
  })

  emit('sendMessage', inputText.value.trim())
  inputText.value = ''

  scrollToBottom()
}

const toggleVoiceInput = () => {
  emit('toggleVoice')
}

// 渲染 Markdown 为 HTML
const renderMarkdown = (content: string): string => {
  try {
    const result = marked(content)
    return typeof result === 'string' ? result : content
  } catch (error) {
    console.error('Markdown 渲染失败:', error)
    return content // 如果渲染失败，返回原始内容
  }
}

// 添加 AI 消息（一次性完整消息）
const addAIMessage = (content: string) => {
  const messageId = `ai_complete_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`
  const message: ChatMessage = {
    id: messageId,
    content,
    isUser: false,
    timestamp: new Date(),
    isStreaming: false,
    htmlContent: renderMarkdown(content)
  }

  console.log('🤖 创建完整AI消息:', { messageId, isUser: message.isUser })
  messages.value.push(message)
  scrollToBottom()
}

// 开始流式 AI 消息
const startStreamingAIMessage = (): string => {
  const messageId = `ai_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`
  const message: ChatMessage = {
    id: messageId,
    content: '',
    isUser: false,
    timestamp: new Date(),
    isStreaming: true,
    htmlContent: ''
  }

  console.log('🤖 创建AI消息:', {
    messageId,
    isUser: message.isUser,
    totalMessages: messages.value.length,
    allMessageIds: messages.value.map(m => ({ id: m.id, isUser: m.isUser }))
  })

  messages.value.push(message)

  console.log('🤖 AI消息已添加到列表:', {
    messageId,
    newTotalMessages: messages.value.length,
    lastMessage: messages.value[messages.value.length - 1]
  })

  scrollToBottom()
  return messageId
}

// 更新流式消息内容
const updateStreamingMessage = (messageId: string, newContent: string) => {
  console.log('🔍 查找要更新的消息:', {
    messageId,
    totalMessages: messages.value.length,
    allMessageIds: messages.value.map(m => ({ id: m.id, isUser: m.isUser }))
  })

  // 额外的安全检查：确保messageId是AI消息的格式
  if (!messageId.startsWith('ai_')) {
    console.error('❌ 错误：尝试更新非AI消息!', { messageId })
    return
  }

  const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
  if (messageIndex !== -1) {
    const message = messages.value[messageIndex]

    // 双重安全检查：确保我们更新的是AI消息
    if (message.isUser) {
      console.error('❌ 错误：尝试更新用户消息!', {
        messageId,
        messageIndex,
        isUser: message.isUser,
        content: message.content
      })
      return
    }

    // 三重安全检查：确保消息ID匹配
    if (message.id !== messageId) {
      console.error('❌ 错误：消息ID不匹配!', {
        expectedId: messageId,
        actualId: message.id,
        messageIndex
      })
      return
    }

    console.log('📝 更新流式消息:', {
      messageId,
      isUser: message.isUser,
      contentLength: newContent.length,
      messageIndex
    })

    // 使用Vue的响应式更新方式
    messages.value[messageIndex] = {
      ...message,
      content: newContent,
      htmlContent: renderMarkdown(newContent)
    }
    scrollToBottom()
  } else {
    console.warn('⚠️ 未找到要更新的消息:', messageId)
  }
}

// 完成流式消息
const finishStreamingMessage = (messageId: string) => {
  // 额外的安全检查：确保messageId是AI消息的格式
  if (!messageId.startsWith('ai_')) {
    console.error('❌ 错误：尝试完成非AI消息!', { messageId })
    return
  }

  const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
  if (messageIndex !== -1) {
    const message = messages.value[messageIndex]

    // 双重安全检查：确保我们完成的是AI消息
    if (message.isUser) {
      console.error('❌ 错误：尝试完成用户消息!', {
        messageId,
        messageIndex,
        isUser: message.isUser,
        content: message.content
      })
      return
    }

    // 三重安全检查：确保消息ID匹配
    if (message.id !== messageId) {
      console.error('❌ 错误：消息ID不匹配!', {
        expectedId: messageId,
        actualId: message.id,
        messageIndex
      })
      return
    }

    console.log('✅ 完成流式消息:', { messageId, isUser: message.isUser })

    // 使用Vue的响应式更新方式
    messages.value[messageIndex] = {
      ...message,
      isStreaming: false,
      htmlContent: renderMarkdown(message.content)
    }
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 监听实时转录变化，自动滚动
watch(() => props.currentTranscript, () => {
  if (props.currentTranscript) {
    scrollToBottom()
  }
})

// 清除所有消息（调试用）
const clearMessages = () => {
  console.log('🧹 清除所有消息')
  messages.value = []
}

// 暴露方法给父组件
defineExpose({
  addAIMessage,
  startStreamingAIMessage,
  updateStreamingMessage,
  finishStreamingMessage,
  clearMessages
})

// 初始化示例消息
onMounted(() => {
  const welcomeMessage: ChatMessage = {
    id: 'welcome_ai_message',
    content: '你好！我是你的AI助手，你可以通过语音或文字与我对话。',
    isUser: false,
    timestamp: new Date(),
    isStreaming: false,
    htmlContent: '你好！我是你的AI助手，你可以通过语音或文字与我对话。'
  }

  console.log('🎯 初始化欢迎消息:', {
    id: welcomeMessage.id,
    isUser: welcomeMessage.isUser
  })

  messages.value = [welcomeMessage]
})
</script>

<style scoped>
.voice-chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  scroll-behavior: smooth;
  max-height: 300px;
}

.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.3);
  border-radius: 2px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.5);
}

.message-item {
  margin-bottom: 12px;
  display: flex;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  word-wrap: break-word;
}

.message-item.user-message .message-bubble {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
  color: white !important;
  border-bottom-right-radius: 6px;
}

.message-item.ai-message .message-bubble {
  background: rgba(255, 255, 255, 0.9) !important;
  color: #374151 !important;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-bottom-left-radius: 6px;
}

.realtime-bubble {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
  opacity: 0.8;
  border: 2px dashed rgba(255, 255, 255, 0.5) !important;
}

.message-content {
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 4px;
}

/* Markdown 内容样式 */
.markdown-content {
  word-wrap: break-word;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin: 0.5em 0;
  font-weight: bold;
}

.markdown-content h1 { font-size: 1.2em; }
.markdown-content h2 { font-size: 1.1em; }
.markdown-content h3 { font-size: 1.05em; }

.markdown-content p {
  margin: 0.5em 0;
}

.markdown-content ul,
.markdown-content ol {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.markdown-content li {
  margin: 0.2em 0;
}

.markdown-content code {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content pre {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.8em;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.markdown-content pre code {
  background: none;
  padding: 0;
}

.markdown-content blockquote {
  border-left: 3px solid #ddd;
  margin: 0.5em 0;
  padding-left: 1em;
  color: #666;
}

.markdown-content strong {
  font-weight: bold;
}

.markdown-content em {
  font-style: italic;
}

/* 流式显示效果 */
.streaming {
  position: relative;
}

.streaming::after {
  content: '';
  position: absolute;
  right: 8px;
  bottom: 8px;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.streaming-indicator {
  color: #3b82f6;
  animation: pulse 1.5s infinite;
  margin-left: 4px;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  text-align: right;
}

.ai-message .message-time {
  text-align: left;
}

.typing-indicator {
  display: flex;
  gap: 3px;
  margin-top: 4px;
  justify-content: center;
}

.typing-indicator span {
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  30% {
    transform: scale(1);
    opacity: 1;
  }
}

.input-area {
  padding: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(255, 255, 255, 0.5);
}

.input-container {
  position: relative;
}

.chat-input :deep(.el-input__wrapper) {
  border-radius: 24px;
  padding: 12px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
}

.chat-input :deep(.el-input__wrapper:hover) {
  border-color: #3b82f6;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
}

.chat-input :deep(.el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
}

.chat-input :deep(.el-input__inner) {
  font-size: 14px;
  color: #374151;
}

.chat-input :deep(.el-input__inner::placeholder) {
  color: #9ca3af;
}

.voice-btn {
  background: transparent !important;
  border: none !important;
  color: #6b7280 !important;
  transition: all 0.3s ease;
}

.voice-btn:hover {
  background: #f3f4f6 !important;
  color: #374151 !important;
}

.voice-btn.active {
  background: linear-gradient(135deg, #ef4444, #dc2626) !important;
  color: white !important;
  animation: pulse-red 1.5s infinite;
}

@keyframes pulse-red {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .chat-messages {
    padding: 12px;
    max-height: 250px;
  }
  
  .input-area {
    padding: 12px;
  }
  
  .message-bubble {
    max-width: 85%;
    padding: 10px 14px;
  }
  
  .message-content {
    font-size: 13px;
  }
}
</style>

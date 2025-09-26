<template>
  <div class="voice-chat-panel">
    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="{ 'user-message': message.isUser, 'ai-message': !message.isUser }"
      >
        <div class="message-bubble">
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
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

// 消息接口定义
interface ChatMessage {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
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

// 方法
const sendMessage = () => {
  if (!inputText.value.trim() || props.isProcessing) return
  
  const message: ChatMessage = {
    id: Date.now().toString(),
    content: inputText.value.trim(),
    isUser: true,
    timestamp: new Date()
  }
  
  messages.value.push(message)
  emit('sendMessage', inputText.value.trim())
  inputText.value = ''
  
  scrollToBottom()
}

const toggleVoiceInput = () => {
  emit('toggleVoice')
}

const addAIMessage = (content: string) => {
  const message: ChatMessage = {
    id: Date.now().toString(),
    content,
    isUser: false,
    timestamp: new Date()
  }
  
  messages.value.push(message)
  scrollToBottom()
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

// 暴露方法给父组件
defineExpose({
  addAIMessage
})

// 初始化示例消息
onMounted(() => {
  messages.value = [
    {
      id: '1',
      content: '你好！我是你的AI助手，你可以通过语音或文字与我对话。',
      isUser: false,
      timestamp: new Date()
    }
  ]
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

.user-message .message-bubble {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border-bottom-right-radius: 6px;
}

.ai-message .message-bubble {
  background: rgba(255, 255, 255, 0.9);
  color: #374151;
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

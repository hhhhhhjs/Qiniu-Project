/**
 * 服务健康检查工具
 * 用于检查本地模型服务是否正常运行
 */

export interface ServiceStatus {
  name: string
  endpoint: string
  status: 'online' | 'offline' | 'checking'
  error?: string
  responseTime?: number
}

/**
 * 检查所有服务状态
 */
export async function checkAllServices(): Promise<ServiceStatus[]> {
  const services = [
    {
      name: 'FunASR 语音识别',
      endpoint: 'ws://localhost:10195',
      type: 'websocket' as const
    },
    {
      name: 'RAG 对话服务',
      endpoint: 'http://localhost:9004/v1/workflow/stream',
      type: 'http' as const
    },
    {
      name: 'TTS 语音合成',
      endpoint: 'http://localhost:8080',
      type: 'http' as const
    }
  ]

  const results = await Promise.all(
    services.map(service => checkService(service))
  )

  return results
}

/**
 * 检查单个服务状态
 */
async function checkService(service: {
  name: string
  endpoint: string
  type: 'http' | 'websocket'
}): Promise<ServiceStatus> {
  const startTime = Date.now()
  
  try {
    if (service.type === 'websocket') {
      return await checkWebSocketService(service.name, service.endpoint, startTime)
    } else {
      return await checkHttpService(service.name, service.endpoint, startTime)
    }
  } catch (error) {
    return {
      name: service.name,
      endpoint: service.endpoint,
      status: 'offline',
      error: error instanceof Error ? error.message : 'Unknown error',
      responseTime: Date.now() - startTime
    }
  }
}

/**
 * 检查 HTTP 服务
 */
async function checkHttpService(
  name: string, 
  endpoint: string, 
  startTime: number
): Promise<ServiceStatus> {
  try {
    // 对于 RAG 服务，尝试发送一个测试请求
    if (endpoint.includes('workflow/stream')) {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({ text: 'test' }),
        signal: AbortSignal.timeout(5000) // 5秒超时
      })
      
      if (response.ok) {
        return {
          name,
          endpoint,
          status: 'online',
          responseTime: Date.now() - startTime
        }
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } else {
      // 对于其他 HTTP 服务，尝试简单的 GET 请求
      const response = await fetch(endpoint, {
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      })
      
      return {
        name,
        endpoint,
        status: response.ok ? 'online' : 'offline',
        responseTime: Date.now() - startTime,
        error: response.ok ? undefined : `HTTP ${response.status}`
      }
    }
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'HTTP request failed')
  }
}

/**
 * 检查 WebSocket 服务
 */
async function checkWebSocketService(
  name: string, 
  endpoint: string, 
  startTime: number
): Promise<ServiceStatus> {
  return new Promise((resolve) => {
    const ws = new WebSocket(endpoint)
    let resolved = false
    
    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true
        ws.close()
        resolve({
          name,
          endpoint,
          status: 'offline',
          error: 'Connection timeout',
          responseTime: Date.now() - startTime
        })
      }
    }, 5000)
    
    ws.onopen = () => {
      if (!resolved) {
        resolved = true
        clearTimeout(timeout)
        ws.close()
        resolve({
          name,
          endpoint,
          status: 'online',
          responseTime: Date.now() - startTime
        })
      }
    }
    
    ws.onerror = (error) => {
      if (!resolved) {
        resolved = true
        clearTimeout(timeout)
        resolve({
          name,
          endpoint,
          status: 'offline',
          error: 'WebSocket connection failed',
          responseTime: Date.now() - startTime
        })
      }
    }
  })
}

/**
 * 格式化服务状态报告
 */
export function formatServiceReport(services: ServiceStatus[]): string {
  let report = '🔍 服务状态检查报告\n\n'
  
  services.forEach(service => {
    const statusIcon = service.status === 'online' ? '✅' : '❌'
    const responseTime = service.responseTime ? `(${service.responseTime}ms)` : ''
    
    report += `${statusIcon} ${service.name}: ${service.status.toUpperCase()} ${responseTime}\n`
    report += `   端点: ${service.endpoint}\n`
    
    if (service.error) {
      report += `   错误: ${service.error}\n`
    }
    
    report += '\n'
  })
  
  const onlineCount = services.filter(s => s.status === 'online').length
  const totalCount = services.length
  
  report += `📊 总结: ${onlineCount}/${totalCount} 个服务在线\n`
  
  if (onlineCount === totalCount) {
    report += '🎉 所有服务运行正常，可以开始语音对话！'
  } else {
    report += '⚠️  部分服务离线，请检查相应的服务是否已启动'
  }
  
  return report
}

/**
 * 在控制台显示服务状态
 */
export async function logServiceStatus(): Promise<void> {
  console.log('🔍 正在检查服务状态...')
  
  const services = await checkAllServices()
  const report = formatServiceReport(services)
  
  console.log(report)
  
  return Promise.resolve()
}

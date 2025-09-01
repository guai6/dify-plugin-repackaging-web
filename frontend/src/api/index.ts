import axios, { AxiosInstance, AxiosResponse } from 'axios'
import type { 
  Task, 
  MarketParams, 
  GithubParams, 
  FileInfo, 
  StorageInfo, 
  SystemStatus, 
  ApiConfig,
  UploadResponse,
  PaginationParams
} from '@/types'
import { ElMessage } from '@/utils/element'

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('API Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('Response Error:', error.response?.status, error.response?.data)
    
    // 统一错误处理
    const message = error.response?.data?.detail || error.message || '请求失败'
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 任务相关API
export const taskApi = {
  // 获取任务列表
  getTasks: (params?: PaginationParams): Promise<Task[]> => 
    api.get('/tasks', { params }).then(res => res.data),
  
  // 获取单个任务
  getTask: (taskId: string): Promise<Task> => 
    api.get(`/tasks/${taskId}`).then(res => res.data),
  
  // 创建Market任务
  createMarketTask: (params: MarketParams): Promise<Task> => 
    api.post('/tasks/market', params).then(res => res.data),
  
  // 创建Github任务
  createGithubTask: (params: GithubParams): Promise<Task> => 
    api.post('/tasks/github', params).then(res => res.data),
  
  // 上传文件并创建Local任务
  uploadFile: (file: File, platform?: string, suffix?: string): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    if (platform) formData.append('platform', platform)
    if (suffix) formData.append('suffix', suffix)
    
    return api.post('/tasks/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000 // 2分钟超时
    }).then(res => res.data)
  },
  
  // 取消任务
  cancelTask: (taskId: string): Promise<void> => 
    api.delete(`/tasks/${taskId}`).then(res => res.data),
  
  // 下载任务结果
  downloadResult: (taskId: string): string => 
    `/api/v1/tasks/${taskId}/download`
}

// 文件相关API
export const fileApi = {
  // 获取文件列表
  getFiles: (fileType: string = 'all'): Promise<FileInfo[]> => 
    api.get('/files', { params: { file_type: fileType } }).then(res => res.data),
  
  // 获取存储信息
  getStorageInfo: (): Promise<StorageInfo> => 
    api.get('/files/storage').then(res => res.data),
  
  // 下载文件
  downloadFile: (fileType: string, filename: string): string => 
    `/api/v1/files/download/${fileType}/${filename}`,
  
  // 删除文件
  deleteFile: (fileType: string, filename: string): Promise<void> => 
    api.delete(`/files/${fileType}/${filename}`).then(res => res.data),
  
  // 清理临时文件
  cleanupTempFiles: (): Promise<{ message: string }> => 
    api.post('/files/cleanup').then(res => res.data),
  
  // 获取文件内容URL
  getFileContentUrl: (fileType: string, filename: string): string => 
    `/api/v1/files/content/${fileType}/${filename}`
}

// 系统相关API
export const systemApi = {
  // 获取系统状态
  getSystemStatus: (): Promise<SystemStatus> => 
    api.get('/system/status').then(res => res.data),
  
  // 获取API配置
  getApiConfig: (): Promise<ApiConfig> => 
    api.get('/system/config').then(res => res.data),
  
  // 更新API配置
  updateApiConfig: (config: ApiConfig): Promise<{ message: string; config: ApiConfig }> => 
    api.put('/system/config', config).then(res => res.data),
  
  // 健康检查
  healthCheck: (): Promise<any> => 
    api.get('/system/health').then(res => res.data),
  
  // 获取版本信息
  getVersion: (): Promise<any> => 
    api.get('/system/version').then(res => res.data)
}

// WebSocket连接工具
export class WebSocketClient {
  private ws: WebSocket | null = null
  private taskId: string
  private onMessage: (message: any) => void
  private onError: (error: Event) => void
  private onClose: (event: CloseEvent) => void
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  constructor(
    taskId: string,
    onMessage: (message: any) => void,
    onError: (error: Event) => void = () => {},
    onClose: (event: CloseEvent) => void = () => {}
  ) {
    this.taskId = taskId
    this.onMessage = onMessage
    this.onError = onError
    this.onClose = onClose
  }

  connect() {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/v1/tasks/ws/${this.taskId}`
      
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket连接已建立')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          this.onMessage(message)
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        this.onError(error)
      }
      
      this.ws.onclose = (event) => {
        console.log('WebSocket连接已关闭')
        this.onClose(event)
        
        // 自动重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
            this.connect()
          }, this.reconnectDelay * this.reconnectAttempts)
        }
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      this.onError(error as Event)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}

export default api
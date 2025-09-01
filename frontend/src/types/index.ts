// 任务状态枚举
export enum TaskStatus {
  PENDING = 'pending',
  DOWNLOADING = 'downloading',
  EXTRACTING = 'extracting',
  PACKAGING = 'packaging',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// 处理模式枚举
export enum ProcessMode {
  MARKET = 'market',
  GITHUB = 'github',
  LOCAL = 'local'
}

// 任务接口
export interface Task {
  id: number
  task_id: string
  task_name?: string
  mode: string
  status: string
  parameters?: Record<string, any>
  progress: number
  current_step?: string
  total_steps: number
  created_at: string
  started_at?: string
  completed_at?: string
  input_file_path?: string
  output_file_path?: string
  file_size?: number
  error_message?: string
}

// 任务进度接口
export interface TaskProgress {
  task_id: string
  status: string
  progress: number
  current_step: string
  message: string
  timestamp: string
}

// WebSocket消息接口
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

// Market模式参数
export interface MarketParams {
  author: string
  name: string
  version: string
  platform?: string
  suffix?: string
}

// Github模式参数
export interface GithubParams {
  repo: string
  release: string
  asset_name: string
  platform?: string
  suffix?: string
}

// Local模式参数
export interface LocalParams {
  file_name: string
  platform?: string
  suffix?: string
}

// 文件信息接口
export interface FileInfo {
  name: string
  path: string
  size: number
  type: string
  created_at: string
  task_id?: string
}

// 存储信息接口
export interface StorageInfo {
  total_space: number
  used_space: number
  free_space: number
  upload_count: number
  output_count: number
}

// 系统状态接口
export interface SystemStatus {
  cpu_percent: number
  memory_percent: number
  disk_percent: number
  system_info: Record<string, string>
  app_info: Record<string, string>
  timestamp: string
}

// API配置接口
export interface ApiConfig {
  github_api_url: string
  marketplace_api_url: string
  pip_mirror_url: string
}

// 上传响应接口
export interface UploadResponse {
  task_id: string
  filename: string
  size: number
  status: string
}

// 通用API响应接口
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 分页参数接口
export interface PaginationParams {
  skip?: number
  limit?: number
  status?: string
}
import request from '@/utils/request';

// 获取数据集列表
export function getSystemConfig() {
  return request.get('/api/sysconfig')
}


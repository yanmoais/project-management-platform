import service from '@/utils/request'
import { ElMessage } from 'element-plus'

/**
 * 通用导出功能
 * @param {string} url - API URL
 * @param {object} params - 查询参数
 * @param {string} filename - 导出文件名
 */
export async function exportData(url, params, filename = 'export.xlsx') {
  try {
    const response = await service({
      url: url,
      method: 'get',
      params: { ...params, export: 1 }, // Assume backend handles 'export=1' or similar
      responseType: 'blob'
    })
    
    // Check if response is JSON (error case)
    if (response.type === 'application/json') {
        const reader = new FileReader()
        reader.onload = () => {
            const res = JSON.parse(reader.result)
            ElMessage.error(res.msg || '导出失败')
        }
        reader.readAsText(response)
        return
    }

    const blob = new Blob([response])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败')
  }
}

import { ref } from 'vue'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import { getOperationLabel, getOperationValue, booleanToText, textToBoolean } from '@/utils/stepConstants'

export function useTestStepExcel() {
  
  const downloadTemplate = () => {
    // Define headers
    const headers = [
      '步骤名称', 
      '操作类型(Web操作/游戏操作)', 
      '操作事件(如:单击/输入/登录)', 
      '元素定位参数', 
      '操作参数值', 
      '操作次数', 
      '暂停时间(秒)', 
      '标签页跳转(是/否)', 
      '断言设置(是/否)', 
      '截图设置(是/否)', 
      '遮挡物处理(是/否)', 
      '无图片遮挡物开启(是/否)'
    ]
    
    // Create a sample row
    const sampleRow = [
      '示例步骤1', 
      'Web操作', 
      '输入', 
      'id=username', 
      'admin', 
      1, 
      1, 
      '否', 
      '否', 
      '否', 
      '否', 
      '否'
    ]

    const wsData = [headers, sampleRow]
    const ws = XLSX.utils.aoa_to_sheet(wsData)
    
    // Set column widths
    ws['!cols'] = [
      { wch: 20 }, // 步骤名称
      { wch: 25 }, // 操作类型
      { wch: 25 }, // 操作事件
      { wch: 30 }, // 元素定位参数
      { wch: 20 }, // 操作参数值
      { wch: 10 }, // 操作次数
      { wch: 15 }, // 暂停时间
      { wch: 15 }, // 标签页跳转
      { wch: 15 }, // 断言设置
      { wch: 15 }, // 截图设置
      { wch: 15 }, // 遮挡物处理
      { wch: 20 }  // 无图片遮挡物开启
    ]

    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '测试步骤模板')
    
    XLSX.writeFile(wb, '测试步骤导入模板.xlsx')
  }

  const importExcel = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result)
          const workbook = XLSX.read(data, { type: 'array' })
          const firstSheetName = workbook.SheetNames[0]
          const worksheet = workbook.Sheets[firstSheetName]
          
          // Convert to JSON array of arrays
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
          
          if (jsonData.length < 2) {
            ElMessage.warning('Excel文件内容为空或格式不正确')
            resolve([])
            return
          }
          
          // Skip header row
          const rows = jsonData.slice(1)
          const newSteps = []
          
          rows.forEach((row, index) => {
            if (!row || row.length === 0) return
            
            // Map columns to fields
            // Assuming strict column order as in template
            const stepName = row[0]
            if (!stepName) return // Skip empty rows

            const operationTypeRaw = row[1] || 'Web操作'
            const operationEventRaw = row[2] || '单击'
            
            const step = {
              id: Date.now() + index + Math.floor(Math.random() * 10000),
              step_name: stepName,
              operation_type: operationTypeRaw.includes('游戏') ? 'game' : 'web',
              operation_event: getOperationValue(operationEventRaw),
              operation_params: row[3] || '',
              input_value: row[4] || '',
              operation_count: parseInt(row[5]) || 1,
              pause_time: parseInt(row[6]) || 1,
              tab_switch_enabled: textToBoolean(row[7]),
              assertion_enabled: textToBoolean(row[8]),
              screenshot_enabled: textToBoolean(row[9]),
              blocker_enabled: textToBoolean(row[10]),
              no_image_click_enabled: textToBoolean(row[11]),
              
              // Defaults for complex objects
              assertion_config: { custom_assertions: [], image_assertions: [], ui_assertions: [] },
              screenshot_config: { format: 'png', full_page: false, path: 'screenshots/', prefix: 'screenshot_step', quality: 90, timing: 'after' },
              login_register_config: {
                email_locator: '',
                password_locator: '',
                repeat_password_locator: '',
                submit_button_locator: '',
                address_url: '',
                account: '',
                password: '',
                last_event: ''
              },
              auth_temp_credentials_list: [],
              auth_regen_on_open: false,
              
              // Other defaults
              tab_switch_action: 'no',
              tab_target_name: '',
              tab_target_url: '',
              assertion_type: 'ui',
              assertion_method: 'pytest-selenium',
              assertion_params: '',
              no_image_click_count: 0,
              captcha_retry_enabled: 'no',
              captcha_next_event: 'click',
              captcha_next_params: ''
            }
            
            newSteps.push(step)
          })
          
          resolve(newSteps)
        } catch (error) {
          console.error('Error parsing Excel:', error)
          ElMessage.error('解析Excel文件失败')
          reject(error)
        }
      }
      
      reader.readAsArrayBuffer(file)
    })
  }

  return {
    downloadTemplate,
    importExcel
  }
}

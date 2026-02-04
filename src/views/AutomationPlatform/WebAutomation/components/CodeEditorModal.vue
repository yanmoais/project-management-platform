<template>
  <el-dialog
    v-model="visible"
    :title="`代码管理 - ${currentFileName}`"
    width="95%"
    top="2vh"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
    class="code-editor-dialog modern-dialog"
    destroy-on-close
  >
    <div class="ide-layout" v-loading="loading">
      <div class="ide-header">
        <div class="file-tab active">
          <el-icon><Document /></el-icon>
          <span class="filename">{{ currentFileName || 'Loading...' }}</span>
        </div>
        <div class="header-actions">
           <el-button size="small" type="primary" plain @click="fetchCode">
            <el-icon><Refresh /></el-icon> 重置
           </el-button>
        </div>
      </div>
      
      <div class="ide-main">
        <div ref="editorContainer" class="monaco-editor-container"></div>
      </div>
      
      <div class="ide-footer">
        <div class="status-left">
          <span>Python</span>
          <span>UTF-8</span>
        </div>
        <div class="status-right">
           <span>{{ lineCount }} 行</span>
           <span v-if="currentFile" class="full-path" :title="currentFile">{{ currentFile }}</span>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer-custom">
        <el-button @click="handleClose" class="ide-btn">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving" class="ide-btn save-btn">
          <el-icon><finished /></el-icon> 保存文件
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, nextTick, computed } from 'vue'
import axios from 'axios'
import * as monaco from 'monaco-editor'
import { ElMessage } from 'element-plus'
import { Document, Refresh, Finished } from '@element-plus/icons-vue'

import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'
import cssWorker from 'monaco-editor/esm/vs/language/css/css.worker?worker'
import htmlWorker from 'monaco-editor/esm/vs/language/html/html.worker?worker'
import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker'

self.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === 'json') {
      return new jsonWorker()
    }
    if (label === 'css' || label === 'scss' || label === 'less') {
      return new cssWorker()
    }
    if (label === 'html' || label === 'handlebars' || label === 'razor') {
      return new htmlWorker()
    }
    if (label === 'typescript' || label === 'javascript') {
      return new tsWorker()
    }
    return new editorWorker()
  }
}

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const editorContainer = ref(null)
const currentFile = ref('')
const lineCount = ref(0)
let editor = null

const currentFileName = computed(() => {
  if (!currentFile.value) return ''
  return currentFile.value.split(/[\\/]/).pop()
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    // Reset state before loading new file
    currentFile.value = ''
    lineCount.value = 0
    // If editor exists from previous session (and wasn't disposed), dispose it now
    if (editor) {
      editor.dispose()
      editor = null
    }
    
    nextTick(() => {
      initEditor()
      fetchCode()
    })
  } else {
    // Dialog closing
    if (editor) {
      editor.dispose()
      editor = null
    }
  }
})

const handleClose = () => {
  emit('update:modelValue', false)
}

const initEditor = () => {
  if (editor) return
  
  if (editorContainer.value) {
    monaco.editor.defineTheme('ide-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#1e1e1e',
        'editor.lineHighlightBackground': '#2d2d2d'
      }
    })

    editor = monaco.editor.create(editorContainer.value, {
      value: '',
      language: 'python',
      theme: 'ide-dark',
      automaticLayout: true,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      fontSize: 14,
      fontFamily: "'Fira Code', Consolas, 'Courier New', monospace",
      lineNumbers: 'on',
      renderWhitespace: 'selection',
      tabSize: 4,
      padding: { top: 15, bottom: 15 }
    })
    
    editor.onDidChangeModelContent(() => {
      lineCount.value = editor.getModel().getLineCount()
    })
    
    // Ensure layout is correct after initialization
    setTimeout(() => {
        editor.layout()
    }, 100)
  }
}

const fetchCode = async () => {
  if (!props.projectId) return
  
  loading.value = true
  try {
    const params = { project_id: props.projectId }
    if (props.filePath) {
        params.file_path = props.filePath
    }
    
    const res = await axios.get('/api/automation/management/code/get', {
      params: params
    })
    
    if (res.data.code === 200) {
      const code = res.data.data.content
      currentFile.value = res.data.data.file_path
      if (editor) {
        editor.setValue(code)
        lineCount.value = editor.getModel().getLineCount()
        // Ensure layout update after content load
        setTimeout(() => {
            editor.layout()
        }, 50)
      }
    } else {
      ElMessage.error(res.data.message || '获取代码失败')
      if (editor) {
         editor.setValue(`# Error: ${res.data.message}\n# Please check if the file exists.`)
      }
    }
  } catch (error) {
    console.error('Fetch code error:', error)
    if (error.response && error.response.status === 404) {
       ElMessage.error('文件不存在')
       // Try to get filename from error response data
       if (error.response.data && error.response.data.data && error.response.data.data.file_path) {
           currentFile.value = error.response.data.data.file_path
       } else {
           currentFile.value = '未知文件'
       }
       if (editor) editor.setValue('# 文件不存在，请先保存项目以生成测试文件')
    } else {
       ElMessage.error('获取代码失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!editor) return
  
  saving.value = true
  const code = editor.getValue()
  
  try {
    const res = await axios.post('/api/automation/management/code/save', {
      project_id: props.projectId,
      content: code
    })
    
    if (res.data.code === 200) {
      ElMessage.success('保存成功')
      emit('saved')
      // Don't close, just save
      // handleClose() 
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (error) {
    console.error('Save code error:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
    editor = null
  }
})
</script>

<style scoped>
.ide-layout {
  height: 80vh;
  display: flex;
  flex-direction: column;
  background-color: #1e1e1e;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #3c3c3c;
}

.ide-header {
  height: 35px;
  background-color: #252526;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 10px;
}

.file-tab {
  height: 100%;
  padding: 0 15px;
  background-color: #1e1e1e;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  border-top: 2px solid #007acc;
}

.file-tab.active {
  background-color: #1e1e1e;
}

.ide-main {
  flex: 1;
  overflow: hidden;
}

.monaco-editor-container {
  width: 100%;
  height: 100%;
}

.ide-footer {
  height: 22px;
  background-color: #007acc;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  font-size: 12px;
}

.status-left, .status-right {
  display: flex;
  gap: 15px;
}

.full-path {
  opacity: 0.8;
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-footer-custom {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
}

.ide-btn {
  min-width: 100px;
}
</style>

<style>
.modern-dialog {
  border-radius: 8px;
  overflow: hidden;
}

.modern-dialog .el-dialog__header {
  padding: 15px 20px;
  margin-right: 0;
  border-bottom: 1px solid #dcdfe6;
  background-color: #f5f7fa;
}

.modern-dialog .el-dialog__body {
  padding: 0; /* Remove padding to let IDE take full space */
  background-color: #1e1e1e;
}

.modern-dialog .el-dialog__footer {
  padding: 15px 20px;
  border-top: 1px solid #dcdfe6;
  background-color: #f5f7fa;
}
</style>

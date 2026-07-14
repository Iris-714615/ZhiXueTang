<template>
  <div class="video-upload-container">
    <div class="upload-area" @dragover.prevent @drop="handleDrop" @click="selectFile">
      <input
        ref="fileInput"
        type="file"
        accept="video/*"
        @change="handleFileSelect"
        style="display: none"
      />
      <div v-if="!file" class="upload-placeholder">
        <i class="el-icon-upload"></i>
        <p>拖拽视频文件到此处或点击选择</p>
        <p class="tips">支持 MP4, AVI, MOV, WMV 等常见视频格式</p>
      </div>
      <div v-else class="file-info">
        <i class="el-icon-video-camera"></i>
        <p class="filename">{{ file.name }}</p>
        <p class="filesize">{{ formatFileSize(file.size) }}</p>
      </div>
    </div>

    <div v-if="file" class="upload-controls">
      <el-select v-model="selectedCourse" placeholder="请选择课程" style="width: 300px; margin-right: 10px;">
        <el-option
          v-for="course in courses"
          :key="course.id"
          :label="course.name"
          :value="course.id"
        ></el-option>
      </el-select>
      
      <el-button 
        type="primary" 
        :disabled="uploading || !selectedCourse"
        @click="startUpload"
      >
        {{ uploading ? `上传中... ${uploadProgress}%` : '开始上传' }}
      </el-button>
    </div>

    <div v-if="uploading" class="upload-progress">
      <el-progress :percentage="uploadProgress" :stroke-width="20" />
      <div class="speed-info">
        <span>已上传: {{ uploadedChunks }}/{{ totalChunks }} 片段</span>
        <span v-if="uploadSpeed">速度: {{ uploadSpeed }}/s</span>
      </div>
    </div>

    <div v-if="uploadResult" class="upload-result">
      <el-alert
        :title="uploadResult.msg"
        :type="uploadResult.code === 200 ? 'success' : 'error'"
        :closable="false"
      />
    </div>

    <div v-if="processingStatus" class="processing-status">
      <h4>视频处理状态</h4>
      <p>视频文件: {{ processingStatus.video_path }}</p>
      <p>字幕文件: {{ processingStatus.subtitle_path }}</p>
      <p>状态: {{ processingStatus.status }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const fileInput = ref(null)
const file = ref(null)
const selectedCourse = ref('')
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadedChunks = ref(0)
const totalChunks = ref(0)
const uploadResult = ref(null)
const processingStatus = ref(null)
const courses = ref([])
const uploadStartTime = ref(null)
const uploadSpeed = ref('')

// 分片大小：5MB
const CHUNK_SIZE = 5 * 1024 * 1024

const handleFileSelect = (event) => {
  const selectedFile = event.target.files[0]
  if (selectedFile && selectedFile.type.startsWith('video/')) {
    file.value = selectedFile
  } else {
    ElMessage.error('请选择有效的视频文件')
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const droppedFiles = event.dataTransfer.files
  if (droppedFiles.length > 0 && droppedFiles[0].type.startsWith('video/')) {
    file.value = droppedFiles[0]
  } else {
    ElMessage.error('请选择有效的视频文件')
  }
}

const selectFile = () => {
  fileInput.value?.click()
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const calculateSpeed = () => {
  if (!uploadStartTime.value) return ''
  const elapsed = (Date.now() - uploadStartTime.value) / 1000 // 秒
  const uploadedBytes = uploadedChunks.value * CHUNK_SIZE
  const speed = uploadedBytes / elapsed
  return formatFileSize(speed)
}

const startUpload = async () => {
  if (!file.value || !selectedCourse.value) {
    ElMessage.error('请选择视频文件和课程')
    return
  }

  uploading.value = true
  uploadStartTime.value = Date.now()
  uploadProgress.value = 0
  uploadedChunks.value = 0
  
  const fileSize = file.value.size
  totalChunks.value = Math.ceil(fileSize / CHUNK_SIZE)
  
  try {
    for (let i = 0; i < totalChunks.value; i++) {
      const start = i * CHUNK_SIZE
      const end = Math.min(start + CHUNK_SIZE, fileSize)
      const chunk = file.value.slice(start, end)
      
      const formData = new FormData()
      formData.append('chunk', chunk)
      formData.append('chunk_index', i)
      formData.append('total_chunks', totalChunks.value)
      formData.append('filename', file.value.name)
      formData.append('course_id', selectedCourse.value)
      
      const response = await fetch('/tcourse/upload-video/', {
        method: 'POST',
        body: formData
      })
      
      const result = await response.json()
      
      if (result.code !== 200) {
        throw new Error(result.msg || '上传失败')
      }
      
      uploadedChunks.value = i + 1
      uploadProgress.value = Math.round((uploadedChunks.value / totalChunks.value) * 100)
      uploadSpeed.value = calculateSpeed()
    }
    
    uploadResult.value = { code: 200, msg: '视频上传完成，后台正在处理...' }
    
    // 查询处理状态
    await checkProcessingStatus(selectedCourse.value)
  } catch (error) {
    console.error('上传失败:', error)
    uploadResult.value = { code: 500, msg: `上传失败: ${error.message}` }
  } finally {
    uploading.value = false
  }
}

const checkProcessingStatus = async (courseId) => {
  try {
    // 模拟视频路径（实际应从上传结果获取）
    const videoPath = `/upload/videos/${courseId}/${file.value.name}`
    const response = await fetch(`/tcourse/video-status/?video_path=${encodeURIComponent(videoPath)}`)
    const result = await response.json()
    
    if (result.code === 200) {
      processingStatus.value = {
        video_path: videoPath,
        subtitle_path: videoPath.replace('.mp4', '.srt'),
        status: result.data.indexed ? '已完成' : result.data.has_subtitle ? '字幕生成完成' : '处理中'
      }
    }
  } catch (error) {
    console.error('查询处理状态失败:', error)
  }
}

// 获取课程列表
const loadCourses = async () => {
  try {
    const response = await fetch('/tcourse/courses/')
    const result = await response.json()
    if (result.code === 200) {
      courses.value = result.data.map(course => ({
        id: course.id,
        name: course.name
      }))
    }
  } catch (error) {
    console.error('获取课程列表失败:', error)
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.video-upload-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-placeholder i {
  font-size: 48px;
  color: #8c939d;
  margin-bottom: 16px;
  display: block;
}

.filename {
  font-weight: bold;
  margin: 10px 0;
  word-break: break-all;
}

.filesize {
  color: #909399;
  font-size: 14px;
}

.tips {
  color: #909399;
  font-size: 14px;
}

.upload-controls {
  margin: 20px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-progress {
  margin: 20px 0;
}

.speed-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.upload-result {
  margin-top: 20px;
}

.processing-status {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
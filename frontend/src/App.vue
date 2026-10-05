<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <h1>🤖 AI图像分类系统</h1>
        <p class="subtitle">基于深度学习的图像识别与分类</p>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 左侧：图片上传区 -->
        <div class="upload-section">
          <el-card class="upload-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📷 图片上传</span>
                <el-tag type="info">{{ currentModel }}</el-tag>
              </div>
            </template>

            <el-upload
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              accept="image/*"
            >
              <div v-if="!imageUrl" class="upload-placeholder">
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="upload-text">
                  <p>将图片拖拽到此处，或<em>点击上传</em></p>
                  <p class="upload-hint">支持 JPG / PNG / BMP / GIF 格式</p>
                </div>
              </div>
              <div v-else class="preview-container">
                <img :src="imageUrl" class="preview-image" />
              </div>
            </el-upload>

            <div class="action-buttons">
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                :disabled="!selectedFile"
                @click="classifyImage"
              >
                {{ loading ? '识别中...' : '开始分类' }}
              </el-button>
              <el-button size="large" @click="clearImage">清除</el-button>
            </div>
          </el-card>
        </div>

        <!-- 右侧：分类结果区 -->
        <div class="result-section">
          <el-card class="result-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📊 分类结果</span>
                <el-tag v-if="result" type="success">Top-5 预测</el-tag>
              </div>
            </template>

            <div v-if="!result" class="empty-result">
              <el-empty description="上传图片并点击「开始分类」查看结果" />
            </div>

            <div v-else class="result-content">
              <!-- 主要预测结果 -->
              <div class="main-prediction">
                <div class="prediction-icon">🎯</div>
                <div class="prediction-info">
                  <h3>{{ result.predictions[0].label }}</h3>
                  <p class="confidence-text">
                    置信度: {{ result.predictions[0].confidence }}%
                  </p>
                </div>
              </div>

              <!-- Top-5 详细结果 -->
              <div class="predictions-list">
                <div
                  v-for="(pred, index) in result.predictions"
                  :key="index"
                  class="prediction-item"
                >
                  <div class="pred-rank">{{ index + 1 }}</div>
                  <div class="pred-info">
                    <span class="pred-label">{{ pred.label }}</span>
                    <el-progress
                      :percentage="pred.confidence"
                      :stroke-width="20"
                      :format="(p) => p + '%'"
                      :color="getProgressColor(index)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 模型选择 -->
          <el-card class="model-card" shadow="hover">
            <template #header>
              <span>⚙️ 模型选择</span>
            </template>
            <el-radio-group v-model="currentModel" @change="switchModel">
              <el-radio-button label="resnet50">ResNet-50</el-radio-button>
              <el-radio-button label="vgg16">VGG-16</el-radio-button>
              <el-radio-button label="mobilenet_v2">MobileNet-V2</el-radio-button>
            </el-radio-group>
          </el-card>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

// 状态变量
const selectedFile = ref(null)
const imageUrl = ref('')
const loading = ref(false)
const result = ref(null)
const currentModel = ref('resnet50')

// 文件选择处理
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  imageUrl.value = URL.createObjectURL(file.raw)
  result.value = null
}

// 清除图片
const clearImage = () => {
  selectedFile.value = null
  imageUrl.value = ''
  result.value = null
}

// 图像分类
const classifyImage = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择一张图片')
    return
  }

  loading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const response = await axios.post('/api/classify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (response.data.success) {
      result.value = response.data
      ElMessage.success('分类完成！')
    } else {
      ElMessage.error(response.data.error || '分类失败')
    }
  } catch (error) {
    ElMessage.error('请求失败：' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// 切换模型
const switchModel = async (model) => {
  try {
    await axios.post('/api/switch_model', { model_name: model })
    ElMessage.success(`已切换到 ${model} 模型`)
  } catch (error) {
    ElMessage.error('模型切换失败')
  }
}

// 进度条颜色
const getProgressColor = (index) => {
  const colors = ['#67c23a', '#409eff', '#e6a23c', '#f56c6c', '#909399']
  return colors[index] || '#909399'
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 30px 0;
  text-align: center;
}

.header-content h1 {
  color: white;
  font-size: 32px;
  margin: 0;
  font-weight: 700;
}

.subtitle {
  color: rgba(255, 255, 255, 0.8);
  margin: 8px 0 0;
  font-size: 16px;
}

.main-content {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.content-wrapper {
  display: flex;
  gap: 30px;
}

.upload-section {
  flex: 1;
}

.result-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 60px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text p {
  color: #606266;
  margin: 8px 0;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.preview-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.preview-image {
  max-width: 100%;
  max-height: 260px;
  object-fit: contain;
  border-radius: 8px;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.empty-result {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-prediction {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #67c23a 0%, #409eff 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 24px;
}

.prediction-icon {
  font-size: 48px;
  margin-right: 20px;
}

.prediction-info h3 {
  margin: 0;
  font-size: 24px;
}

.confidence-text {
  margin: 8px 0 0;
  font-size: 16px;
  opacity: 0.9;
}

.predictions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.prediction-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pred-rank {
  width: 32px;
  height: 32px;
  background: #f0f2f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #606266;
  flex-shrink: 0;
}

.pred-info {
  flex: 1;
}

.pred-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #303133;
}

.model-card {
  margin-top: auto;
}
</style>

# 🤖 AI图像分类系统

基于深度学习的图像识别与分类系统，使用 PyTorch 预训练模型，支持多种 CNN 架构。

## ✨ 功能特性

- 📷 支持多种图片格式上传（JPG/PNG/BMP/GIF）
- 🧠 支持多种预训练模型（ResNet-50/VGG-16/MobileNet-V2）
- 📊 Top-5 分类结果展示
- 🎨 美观的现代化 UI 界面
- 🔄 实时模型切换

## 🛠️ 技术栈

### 前端
- Vue 3 + Vite
- Element Plus UI 组件库
- Axios HTTP 客户端

### 后端
- Python Flask
- PyTorch + torchvision
- Pillow 图像处理

## 🚀 快速开始

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

后端将运行在 http://localhost:5000

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 http://localhost:3000

### 3. 使用系统

1. 打开浏览器访问 http://localhost:3000
2. 拖拽或点击上传一张图片
3. 点击「开始分类」按钮
4. 查看 Top-5 分类结果

## 📁 项目结构

```
AI图像分类系统/
├── backend/                 # 后端服务
│   ├── app.py              # Flask 主程序
│   ├── requirements.txt    # Python 依赖
│   ├── models/             # 模型相关文件
│   ├── uploads/            # 上传文件存储
│   └── utils/              # 工具模块
│       ├── classifier.py   # 图像分类器
│       └── preprocess.py   # 图像预处理
├── frontend/               # 前端应用
│   ├── index.html          # 入口页面
│   ├── package.json        # Node.js 依赖
│   ├── vite.config.js      # Vite 配置
│   └── src/
│       ├── main.js         # Vue 入口
│       └── App.vue         # 主组件
└── README.md               # 项目说明
```

## 📝 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/classify` | POST | 图像分类 |
| `/api/models` | GET | 获取可用模型列表 |
| `/api/switch_model` | POST | 切换分类模型 |

## 🔧 扩展建议

1. **自定义数据集训练**：使用自己的数据集微调模型
2. **添加更多模型**：集成 EfficientNet、Vision Transformer 等
3. **批量分类**：支持多张图片同时分类
4. **历史记录**：保存分类历史，支持查看和导出
5. **部署上线**：使用 Docker 容器化部署

## 📄 License

MIT License

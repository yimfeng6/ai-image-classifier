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

# 下载 ImageNet 类别标签（只需跑一次）
python download_labels.py

# 启动服务
python app.py
```

> **为什么要有 `download_labels.py` 这一步？**
> PyTorch 模型输出的是类别**索引**（0~999），要翻译成「Golden Retriever」
> 这样的名字，得有一份索引到名字的对照表。这个脚本负责把它下载到
> `backend/models/imagenet_labels.json`。
>
> **少了这一步，程序会直接报错停下**，不会给你一堆没有意义的结果 ——
> 这是特意改成这样的，见下面「已知取舍」。

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
│   ├── app.py               # Flask 主程序
│   ├── download_labels.py   # 下载 ImageNet 类别标签
│   ├── requirements.txt     # Python 依赖
│   ├── models/              # 类别标签（由上面那个脚本生成）
│   ├── uploads/             # 上传文件存储
│   └── utils/               # 工具模块
│       ├── classifier.py    # 图像分类器
│       └── preprocess.py    # 图像预处理
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

## ⚖️ 已知取舍

**标签文件缺失时直接报错，不做降级。**

原来的写法是「找不到标签文件就返回 `class_0` ~ `class_999`」。后果是：
程序照常启动、接口照常返回、界面照常显示，只是所有结果都变成
「class_916」这种没有意义的东西 —— **不报错、不警告**。

功能"能用"但输出是废的，这是最难发现的一类错误，因为没有任何信号
提示你出了问题。现在改成直接抛 `FileNotFoundError`，并在错误信息里
写明怎么解决。

**`switch_model` 每次切换都重新加载整个模型。**
单用户演示够用，但加载要好几秒；而且用 `global` 变量在多线程下不安全。
要上生产得改成启动时把所有模型都加载好，切换时只换引用。

**上传的图片不会自动清理。**
`backend/uploads/` 会越攒越多。演示前手动清一下就行，或者加个定时清理。

---

## 🔧 扩展建议

1. **自定义数据集训练**：使用自己的数据集微调模型
2. **添加更多模型**：集成 EfficientNet、Vision Transformer 等
3. **批量分类**：支持多张图片同时分类
4. **历史记录**：保存分类历史，支持查看和导出
5. **部署上线**：使用 Docker 容器化部署

## 📄 License

MIT License

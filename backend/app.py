"""
基于深度学习的图像分类系统 - 后端主程序
使用 Flask 框架提供 RESTful API
"""
import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.classifier import ImageClassifier
from utils.preprocess import allowed_file

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化分类器（使用预训练的 ResNet50）
classifier = ImageClassifier(model_name='resnet50')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '图像分类服务运行正常'})


@app.route('/api/classify', methods=['POST'])
def classify_image():
    """
    图像分类接口
    接收上传的图片文件，返回分类结果
    """
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，请上传 JPG/PNG/BMP 图片'}), 400

    try:
        # 保存文件
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 进行分类预测
        results = classifier.predict(filepath, top_k=5)

        return jsonify({
            'success': True,
            'filename': file.filename,
            'predictions': results
        })

    except Exception as e:
        return jsonify({'error': f'分类失败: {str(e)}'}), 500


@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    models = [
        {
            'name': 'resnet50',
            'description': 'ResNet-50 - 深度残差网络，平衡精度与速度',
            'accuracy': '76.1% (ImageNet Top-1)'
        },
        {
            'name': 'vgg16',
            'description': 'VGG-16 - 经典卷积网络，结构简洁',
            'accuracy': '71.3% (ImageNet Top-1)'
        },
        {
            'name': 'mobilenet_v2',
            'description': 'MobileNet-V2 - 轻量级网络，适合移动端',
            'accuracy': '71.8% (ImageNet Top-1)'
        }
    ]
    return jsonify({'models': models})


@app.route('/api/switch_model', methods=['POST'])
def switch_model():
    """切换分类模型"""
    data = request.get_json()
    model_name = data.get('model_name', 'resnet50')

    try:
        global classifier
        classifier = ImageClassifier(model_name=model_name)
        return jsonify({'success': True, 'message': f'已切换到 {model_name} 模型'})
    except Exception as e:
        return jsonify({'error': f'模型切换失败: {str(e)}'}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("  AI 图像分类系统后端服务")
    print("  访问地址: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)

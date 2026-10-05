"""
图像分类器模块
使用 PyTorch 预训练模型进行图像分类
"""
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import json
import os


class ImageClassifier:
    """图像分类器类"""

    # 支持的模型
    SUPPORTED_MODELS = {
        'resnet50': models.resnet50,
        'vgg16': models.vgg16,
        'mobilenet_v2': models.mobilenet_v2,
    }

    def __init__(self, model_name='resnet50'):
        """
        初始化分类器
        Args:
            model_name: 模型名称，支持 resnet50/vgg16/mobilenet_v2
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.model = self._load_model(model_name)
        self.model.eval()
        self.labels = self._load_labels()
        self.transform = self._get_transforms()

    def _load_model(self, model_name):
        """加载预训练模型"""
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型: {model_name}，可选: {list(self.SUPPORTED_MODELS.keys())}")

        print(f"正在加载 {model_name} 模型...")
        model_fn = self.SUPPORTED_MODELS[model_name]
        model = model_fn(pretrained=True)
        model = model.to(self.device)
        print(f"{model_name} 模型加载完成，使用设备: {self.device}")
        return model

    def _load_labels(self):
        """加载 ImageNet 类别标签"""
        labels_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'imagenet_labels.json')
        if os.path.exists(labels_path):
            with open(labels_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        # 如果没有标签文件，返回默认的1000个类别编号
        return {str(i): f"class_{i}" for i in range(1000)}

    def _get_transforms(self):
        """获取图像预处理流水线"""
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def predict(self, image_path, top_k=5):
        """
        对图像进行分类预测
        Args:
            image_path: 图片文件路径
            top_k: 返回前K个预测结果
        Returns:
            list: 预测结果列表，每个元素包含 label, confidence, class_id
        """
        # 加载并预处理图像
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image)
        input_batch = input_tensor.unsqueeze(0).to(self.device)

        # 推理
        with torch.no_grad():
            output = self.model(input_batch)

        # 获取概率分布
        probabilities = torch.nn.functional.softmax(output[0], dim=0)

        # 获取 Top-K 结果
        top_probs, top_indices = torch.topk(probabilities, top_k)

        results = []
        for i in range(top_k):
            class_id = str(top_indices[i].item())
            confidence = top_probs[i].item()
            label = self.labels.get(class_id, f"class_{class_id}")
            results.append({
                'class_id': class_id,
                'label': label,
                'confidence': round(confidence * 100, 2)
            })

        return results

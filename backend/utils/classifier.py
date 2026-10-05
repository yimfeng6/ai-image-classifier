"""
图像分类器模块
使用 PyTorch 预训练模型进行图像分类
"""
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.models import (MobileNet_V2_Weights, ResNet50_Weights,
                                VGG16_Weights)
from PIL import Image
import json
import os


class ImageClassifier:
    """图像分类器类"""

    # 支持的模型：名字 → (构造函数, 预训练权重)
    #
    # 这里用 weights=... 而不是老写法 pretrained=True。
    # pretrained 从 torchvision 0.13 起就废弃了，跑起来会打警告；
    # weights 写法更明确 —— 直接指明用哪一版权重，
    # 将来还能换成 IMAGENET1K_V2 之类精度更高的版本。
    SUPPORTED_MODELS = {
        'resnet50':     (models.resnet50,     ResNet50_Weights.IMAGENET1K_V1),
        'vgg16':        (models.vgg16,        VGG16_Weights.IMAGENET1K_V1),
        'mobilenet_v2': (models.mobilenet_v2, MobileNet_V2_Weights.IMAGENET1K_V1),
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
        model_fn, weights = self.SUPPORTED_MODELS[model_name]
        model = model_fn(weights=weights)
        model = model.to(self.device)
        print(f"{model_name} 模型加载完成，使用设备: {self.device}")
        return model

    def _load_labels(self):
        """
        加载 ImageNet 类别标签（索引 → 名字）。

        找不到就**报错停下** —— 不要静默降级。

        原来这里写的是「找不到就返回 class_0..class_999」。后果是：
        程序照常启动、接口照常返回、界面照常显示，只是所有结果都变成
        "class_207" 这种没有意义的东西。**不报错、不警告。**

        功能"能用"但输出是废的 —— 这是最难发现的一类错误，因为没有任何
        信号提示你出了问题。缺东西就报错，让人去补，这才是对的。
        """
        labels_path = os.path.join(os.path.dirname(__file__), '..', 'models',
                                   'imagenet_labels.json')
        if not os.path.exists(labels_path):
            raise FileNotFoundError(
                f"缺少类别标签文件: {os.path.abspath(labels_path)}\n"
                f"  运行 `python download_labels.py` 生成它。"
            )
        with open(labels_path, 'r', encoding='utf-8') as f:
            return json.load(f)

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

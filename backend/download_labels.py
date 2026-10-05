# -*- coding: utf-8 -*-
"""
download_labels.py
功能：下载 ImageNet 的 1000 个类别名，写成 backend/models/imagenet_labels.json

────────────────────────────────────────────────────────
为什么需要这一步
────────────────────────────────────────────────────────

PyTorch 的预训练模型输出的是 **类别索引**（0~999），不是名字。
`classifier.py` 会把索引翻译成名字，靠的就是这个 labels 文件。

原来的代码里缺少这个文件，而 `classifier.py` 在找不到时的处理是：

    return {str(i): f"class_{i}" for i in range(1000)}

**静默降级** —— 程序照常跑，界面照常显示，只是所有结果都变成
「class_207」这种没有意义的东西。功能"能用"，但输出是废的，
而且不报错、不警告。

这是这次要修的主要问题：**补上标签文件，并且把静默降级改成报错。**

为什么用脚本下载而不是直接把 JSON 提交进仓库
    1000 个类别名约 15 KB，提交进去也行。但写成脚本的好处是：
    · 别人克隆下来知道这东西哪来的、怎么重新生成
    · 换个语言版本只要改 URL
    · 不用把第三方数据当成自己的文件塞进仓库

运行：
    python download_labels.py
"""

import json
import os
import sys

import requests

# 目标路径：backend/models/imagenet_labels.json
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(HERE, "models")
OUT_PATH = os.path.join(MODELS_DIR, "imagenet_labels.json")

# 数据源，按顺序尝试。
#
# 第一个是「简化标签」：每个类别一个干净的名字（Golden Retriever），
# 适合直接显示在界面上。
# 第二个是 PyTorch 官方的类别名，名字里带拉丁学名（golden retriever,
# Labrador retriever...），做备选。
SOURCES = [
    ("imagenet-simple-labels",
     "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels"
     "/master/imagenet-simple-labels.json"),
    ("pytorch/hub",
     "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"),
]

TIMEOUT = 30
EXPECTED = 1000


def fetch(url: str) -> list[str]:
    """下载并解析成 1000 个名字的列表。"""
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=TIMEOUT)
    resp.raise_for_status()

    if url.endswith(".json"):
        labels = resp.json()
    else:
        labels = [line.strip() for line in resp.text.strip().split("\n") if line.strip()]

    if len(labels) != EXPECTED:
        raise ValueError(f"期望 {EXPECTED} 个类别，实际拿到 {len(labels)} 个")
    return labels


def main() -> int:
    print("=" * 58)
    print("  下载 ImageNet 类别标签")
    print("=" * 58)

    labels = None
    for name, url in SOURCES:
        print(f"\n  尝试 {name} ...")
        try:
            labels = fetch(url)
            print(f"  ✓ 成功，拿到 {len(labels)} 个类别")
            break
        except Exception as e:
            print(f"  ✗ 失败: {type(e).__name__}: {e}")

    if labels is None:
        print("\n  所有数据源都失败了。")
        print("  检查网络，或者手动下载后放到:", OUT_PATH)
        return 1

    # 类别索引 → 名字。索引就是列表下标，这是 ImageNet 的约定。
    mapping = {str(i): name for i, name in enumerate(labels)}

    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=0)

    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"\n  已写入: {OUT_PATH} ({size_kb:.1f} KB)")
    print(f"  抽样:")
    for i in (0, 207, 281, 999):
        print(f"    {i:>3} → {mapping[str(i)]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

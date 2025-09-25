#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import cv2
from pathlib import Path
from onnxocr.onnx_paddleocr import ONNXPaddleOcr

# ========= 配置：按你的需求改 =========
INPUT_DIR  = Path("/home/yaf/workspace/server/campus_rag_project/data/output")
OUTPUT_DIR = Path("/home/yaf/workspace/server/campus_rag_project/data/txt_data")
USE_GPU = False            # 你是CPU就保持 False
USE_ANGLE_CLS = True       # 文本行方向分类
CONF_THRES = 0.0           # 置信度阈值：只保留文本→设 0.0；想过滤低分可改成 0.8
MIN_CHARS  = 1             # 最短文本长度过滤
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
# ====================================

def list_images(root: Path):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if Path(fn).suffix.lower() in IMG_EXTS:
                yield Path(dirpath) / fn

def extract_texts(ocr_result, conf_thres=CONF_THRES, min_chars=MIN_CHARS):
    """
    兼容 onnxocr 的输出结构：[[ [points, (text, score)], ... ]]
    """
    if not ocr_result:
        return []

    detections = ocr_result[0] if isinstance(ocr_result, list) and len(ocr_result) > 0 else ocr_result

    # 上->下，再左->右排序
    def sort_key(det):
        pts = det[0]
        min_y = min(p[1] for p in pts)
        min_x = min(p[0] for p in pts)
        return (min_y, min_x)

    detections = sorted(detections, key=sort_key)

    texts = []
    for det in detections:
        text, score = det[1][0], det[1][1]
        if score >= conf_thres and len(text.strip()) >= min_chars:
            texts.append(text.strip())
    return texts

def main():
    if not INPUT_DIR.exists():
        print(f"[ERR] 输入目录不存在：{INPUT_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[INFO] 初始化 OCR 模型 ...")
    t0 = time.time()
    model = ONNXPaddleOcr(use_angle_cls=USE_ANGLE_CLS, use_gpu=USE_GPU)
    print(f"[OK] 模型加载完成，用时 {time.time() - t0:.2f}s\n")

    files = list(list_images(INPUT_DIR))
    if not files:
        print(f"[WARN] 在 {INPUT_DIR} 下未找到图片（支持扩展名：{sorted(IMG_EXTS)}）")
        return

    total_imgs = 0
    total_lines = 0
    total_fail  = 0

    for img_path in files:
        rel_path = img_path.relative_to(INPUT_DIR)
        out_path = (OUTPUT_DIR / rel_path).with_suffix(".txt")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"[SKIP] 读图失败：{img_path}")
                total_fail += 1
                continue

            t1 = time.time()
            result = model.ocr(img)
            texts = extract_texts(result)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(texts))

            dt = time.time() - t1
            print(f"[OK] {img_path}  →  {out_path} | 行数={len(texts)} | {dt:.3f}s")
            total_imgs += 1
            total_lines += len(texts)

        except Exception as e:
            print(f"[ERR] {img_path} 处理失败：{e}")
            total_fail += 1

    print("\n===== 完成 =====")
    print(f"总文件：{len(files)} | 成功：{total_imgs} | 失败：{total_fail} | 总文本行：{total_lines}")
    print(f"输出目录：{OUTPUT_DIR}")

if __name__ == "__main__":
    main()

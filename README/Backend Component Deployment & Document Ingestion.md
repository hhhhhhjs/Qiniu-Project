# PDF处理

## 1. 将PDF按页转为JPG

 `sudo apt-get install -y poppler-utils`

```
pdftoppm -jpeg -r 300 input.pdf out/page
```

## 2. 部署onnx_ocr将JPG转为txt

部署见：`https://github.com/jingsongliujing/OnnxOCR/blob/main/Readme_cn.md`

代码见：`campus_rag_ocr.py`

## 3. 利用zhipuai免费大模型接口 对数据进行清洗和总结

```
pip install zhipuai
```

代码见：` summary_text.py ` 

## 4. Milvus

```
pip install -U "pymilvus[milvus_lite]"
```

使用：`Milvus Lite`

代码入库见：` insert_milvus.py ` 

## 5. 部署BGE模型

代码见：`bge_api.py`

接口文档见: ·BGE Embedding Service 接口文档（v1.0.0）·

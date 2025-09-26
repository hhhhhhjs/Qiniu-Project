#!/bin/bash
# 部署五个服务到指定端口

# 激活环境（如果有的话）
# source ~/anaconda3/bin/activate your_env

# 去口语化接口
nohup uvicorn reduce_colloquial_rewriting:app --host 0.0.0.0 --port 9000 > logs/reduce.log 2>&1 &

# Milvus 召回接口
nohup uvicorn milvus_recall_api:app --host 0.0.0.0 --port 9001 > logs/milvus.log 2>&1 &

# BGE 重排接口
nohup uvicorn bge_api:app --host 0.0.0.0 --port 9002 > logs/bge.log 2>&1 &

# LLM 生成接口
nohup uvicorn llm_api:app --host 0.0.0.0 --port 9003 > logs/llm.log 2>&1 &

# 工作流主接口
nohup uvicorn main:app --host 0.0.0.0 --port 9004 > logs/main.log 2>&1 &

echo "所有服务已启动，请查看 logs/ 下的日志文件。"

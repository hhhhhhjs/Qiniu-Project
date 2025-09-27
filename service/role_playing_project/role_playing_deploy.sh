#!/bin/bash
# 部署五个服务到指定端口

# 激活环境（如果有的话）
# source ~/anaconda3/bin/activate your_env

export ZHIPUAI_API_KEY="4dc3c4e045814b799df1e7098228cf86.BeIMESXJ5LkjAnGf"
export ZHIPUAI_MODEL="glm-4.5"

# 意图识别接口
nohup uvicorn intent_api:app --host 0.0.0.0 --port 9100 > logs/intent_api.log 2>&1 &

# 角色聊天接口
nohup uvicorn app_role_chat:app --host 0.0.0.0 --port 9101 > logs/app_role_chat.log 2>&1 &

# 自我介绍接口
nohup uvicorn app_roleplay_stream:app --host 0.0.0.0 --port 9103 > logs/app_roleplay_stream.log 2>&1 &

echo "所有服务已启动，请查看 logs/ 下的日志文件。"


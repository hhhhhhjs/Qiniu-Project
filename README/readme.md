# \## 项目简介

# 

# 智能角色助手系统是一款聚焦多场景专业服务的语音交互平台，集成 \*\*集小美（校园助手）\*\*、\*\*李时珍（中医养生助手）\*\*、\*\*小萌（宠物养护助手）\*\* 三大核心角色，基于「语音识别（ASR）+ 检索增强生成（RAG）+ 大语言模型（LLM）+ 语音合成（TTS）」技术栈，实现从语音唤醒到结果合成的端到端闭环，为用户提供校园生活、健康养生、宠物护理领域的个性化智能服务。

# 

# \## 核心角色介绍

# 

# \### 1. 集美大学校园助手 · 集小美

# 

# !\[集小美角色形象](https://via.placeholder.com/300)（实际使用时替换为角色图片的真实 URL）

# 

# \*\*角色定位\*\*

# 热心耐心的“大四学长学姐”，专注 17-19 岁新生入学引导与校园生活咨询，解决报到、选课、宿舍、社团等初期高频问题。

# 

# \*\*核心能力\*\*

# 

# \* 学校信息查询：校训校史、校区分布、宿舍位置、杰出校友

# \* 新生报到指导：各学院报到地点（具体楼栋/房间）、所需材料（身份证/录取通知书等）、一卡通办理流程

# \* 宿舍服务咨询：宿舍分布地图、设施（空调/洗衣机/热水）、报修流程、门禁规则

# 

# \*\*语气风格\*\*

# 亲切接地气，步骤化引导 + 幽默点缀（示例：“先别急～我带你一步步来：1) 从大门进去→2) 往前走五百米左转→……”）

# 

# \*\*典型交互场景\*\*

# 

# ```text

# 用户：“小美，我要怎么去报道呀？”

# 集小美：“哇，终于等到你啦！欢迎加入集大～报到三步走：① 找穿红马甲志愿者的迎新点登记；② 领学生证和宿舍钥匙；③ 去学院报到点确认信息～还能发你报到流程卡片哦～”

# ```

# 

# \### 2. 中医养生助手 · 李时珍

# 

# !\[李时珍角色形象](https://via.placeholder.com/300)（实际使用时替换为角色图片的真实 URL）

# 

# \*\*角色定位\*\*

# 仿古风 “中医养生导师”，以《本草纲目》《黄帝内经》为理论基础，为 20-60 岁偏爱传统文化的用户提供养生建议。

# 

# \*\*核心能力\*\*

# 

# \* 四季养生：春养肝、夏养心、秋养肺、冬养肾的饮食与作息方案

# \* 药食同源：常见食材（枸杞 / 山药 / 生姜）功效与食用方法

# \* 经络调理：合谷、足三里等穴位按摩方法及适用场景

# 

# \*\*语气风格\*\*

# 古雅温和，引经据典 + 现代落地（示例：“秋气肃杀，宜养肺润燥。饮食以梨、银耳、百合为佳，可煮百合莲子粥以安神润肺。”）

# 

# \*\*典型交互场景\*\*

# 

# ```text

# 用户：“李先生，体虚怕冷有什么食疗推荐？”

# 李时珍：“汝阳虚畏寒，可炖羊肉汤，加枸杞、当归，既温补气血，亦强身御寒。”

# ```

# 

# \### 3. 宠物养护助手 · 小萌

# 

# !\[小萌角色形象](https://via.placeholder.com/300)（实际使用时替换为角色图片的真实 URL）

# 

# \*\*角色定位\*\*

# 温柔细心的 “宠物养护师姐姐”，面向 18-40 岁新手猫狗主人，提供品种识别与科学养护指导。

# 

# \*\*核心能力\*\*

# 

# \* 品种识别：上传图片识别猫狗品种，返回外观特征、性格、适养人群

# \* 养护百科：饮食禁忌（猫忌巧克力 / 狗忌葡萄）、疫苗时间表、洗澡 / 梳毛频率

# \* 日常提醒：疫苗 / 驱虫时间、换毛季护理、季节性养护（夏季防中暑 / 冬季保暖）

# 

# \*\*语气风格\*\*

# 轻松温暖带萌感，通俗科普（示例：“别担心呀～猫咪掉毛分正常掉毛和季节性换毛，每天梳毛 + 补鱼油就能改善哦～”）

# 

# \*\*典型交互场景\*\*

# 

# ```text

# 用户：“帮我识别这只猫是什么品种？”

# 小萌：“哇，这是布偶猫‘小仙女’呀～性格温柔粘人超适合新手，但毛发长要每天梳，还要控制体重避免发胖哦～”

# ```

# 

# \## 技术架构

# 

# \*\*系统总览（端到端流程）\*\*

# 

# ```mermaid

# flowchart LR

# &nbsp;   A\[客户端] -->|语音唤醒/音频采集| B\[API网关]

# &nbsp;   B -->|路由/鉴权| C\[ASR服务（Whisper/FunASR）]

# &nbsp;   C -->|文本转写+清洗| D\[意图识别（LLM/BERT）]

# &nbsp;   D -->|推断用户需求| E\[RAG引擎（Milvus+BGE）]

# &nbsp;   E -->|检索知识库+结构化Prompt| F\[LLM（Qwen3-32B）]

# &nbsp;   F -->|生成角色化回答| B

# &nbsp;   B -->|文本输入| G\[TTS服务（Fish-Speech）]

# &nbsp;   G -->|音频合成| A

# &nbsp;   E -->|日志/埋点| H\[(知识库)]

# ```

# \## 核心技术栈

# 

# | 模块        | 技术选型                                     | 作用              |

# | --------- | ---------------------------------------- | --------------- |

# | 语音识别（ASR） | Whisper-large-v3-turbo、FunASR Paraformer | 将语音转为文本，支持流式解码  |

# | 语音合成（TTS） | Fish-Speech 1.5                          | 将文本转为角色化语音      |

# | 向量数据库     | Milvus Lite                              | 存储文本向量，支持高效检索   |

# | 嵌入模型      | BGE-M3、bge-reranker-large                | 生成文本向量，优化检索排序   |

# | 大语言模型     | Qwen3-32B                                | 生成符合角色设定的自然语言回答 |

# | 环境管理      | Conda（Miniforge）                         | 隔离依赖，确保环境一致性    |

# 

# \## 环境配置

# 

# \### 基础依赖安装

# 

# ```bash

# \# 系统依赖

# sudo apt-get update

# sudo apt-get install -y build-essential cmake git wget unzip \\

# &nbsp;   libopenblas-dev libssl-dev portaudio19-dev libsox-dev ffmpeg

# 

# \# Miniforge 安装

# wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86\_64.sh

# chmod +x Miniforge3-Linux-x86\_64.sh

# bash Miniforge3-Linux-x86\_64.sh -b -p ~/miniforge3

# echo 'export PATH="$HOME/miniforge3/bin:$PATH"' >> ~/.bashrc

# source ~/.bashrc

# conda --version

# ```

# 

# \### 项目环境创建

# 

# ```bash

# \# 基础环境（ASR/RAG/LLM）

# conda create -n assistant\_env python=3.10 -y

# conda activate assistant\_env

# pip install -U modelscope huggingface\_hub

# pip install -U "pymilvus\[milvus\_lite]" zhipuai torch torchaudio transformers

# 

# \# Fish-Speech 环境（TTS）

# conda create -n fish\_speech\_env python=3.12 -y

# conda activate fish\_speech\_env

# \# 进入 Fish-Speech 源码目录后执行

# pip install -e ".\[cu128]"

# ```

# 

# \### 模型下载（本地存储）

# 

# ```bash

# mkdir -p ~/workspace/model\_zoo

# 

# \# ASR 模型

# cd ~/workspace/model\_zoo

# modelscope download --model iic/speech\_paraformer-large\_asr\_nat-zh-cn-16k-common-vocab8404-onnx \\

# &nbsp; --local\_dir ./iic/speech\_paraformer-large\_asr\_nat-zh-cn-16k-common-vocab8404-onnx

# modelscope download --model iic/speech\_fsmn\_vad\_zh-cn-16k-common-onnx \\

# &nbsp; --local\_dir ./iic/speech\_fsmn\_vad\_zh-cn-16k-common-onnx

# modelscope download --model iic/punc\_ct-transformer\_zh-cn-common-vad\_realtime-vocab272727-onnx \\

# &nbsp; --local\_dir ./iic/punc\_ct-transformer\_zh-cn-common-vad\_realtime-vocab272727-onnx

# 

# \# TTS 模型

# modelscope download --model fishaudio/openaudio-s1-mini \\

# &nbsp; --local\_dir ./fishaudio/openaudio-s1-mini

# 

# \# RAG 模型

# modelscope download --model BAAI/bge-m3 \\

# &nbsp; --local\_dir ./BAAI/bge-m3

# ```

# 

# \## 服务部署

# 

# \### 1. 语音识别服务（FunASR）

# 

# \*\*编译 WebSocket 服务\*\*

# 

# ```bash

# cd ~/workspace/source

# git clone https://github.com/modelscope/FunASR.git

# cd FunASR \&\& pip install -e ./

# 

# git clone --depth 1 https://github.com/zaphoyd/websocketpp.git ~/workspace/source/third\_party/websocketpp

# 

# cd ~/workspace/source/FunASR/runtime/websocket

# mkdir -p build \&\& cd build

# cmake -DCMAKE\_BUILD\_TYPE=Release \\

# &nbsp; -Dwebsocketpp\_SOURCE\_DIR=~/workspace/source/third\_party/websocketpp \\

# &nbsp; -DONNXRUNTIME\_DIR=~/workspace/source/onnxruntime-linux-x64-1.14.0 \\

# &nbsp; -DFFMPEG\_DIR=~/workspace/source/ffmpeg-master-latest-linux64-gpl-shared \\

# &nbsp; ..

# make -j4

# ```

# 

# \*\*启动服务\*\*

# 

# ```bash

# export LD\_LIBRARY\_PATH=~/workspace/source/onnxruntime-linux-x64-1.14.0/lib:~/workspace/source/ffmpeg-master-latest-linux64-gpl-shared/lib:$LD\_LIBRARY\_PATH

# 

# nohup bash ~/workspace/source/FunASR/runtime/run\_server\_2pass.sh \\

# &nbsp; --model-dir ~/workspace/model\_zoo/iic/speech\_paraformer-large\_asr\_nat-zh-cn-16k-common-vocab8404-onnx \\

# &nbsp; --online-model-dir ~/workspace/model\_zoo/iic/speech\_paraformer-large\_asr\_nat-zh-cn-16k-common-vocab8404-online-onnx \\

# &nbsp; --vad-dir ~/workspace/model\_zoo/iic/speech\_fsmn\_vad\_zh-cn-16k-common-onnx \\

# &nbsp; --punc-dir ~/workspace/model\_zoo/iic/punc\_ct-transformer\_zh-cn-common-vad\_realtime-vocab272727-onnx \\

# &nbsp; --certfile ~/ssl\_key/server.crt \\

# &nbsp; --keyfile ~/ssl\_key/server.key \\

# &nbsp; --hotword ~/workspace/hotwords.txt \\

# &nbsp; > ~/workspace/source/FunASR/runtime/log.txt 2>\&1 \&

# 

# \# 验证端口监听

# ss -lptn 'sport = :10095'

# tail -n 100 ~/workspace/source/FunASR/runtime/log.txt

# ```

# 

# \### 2. 语音合成服务（Fish-Speech）

# 

# ```bash

# conda activate fish\_speech\_env

# 

# python ~/workspace/source/fish-speech/fish\_speech/models/dac/inference.py \\

# &nbsp; -i "~/workspace/source/fish-speech/temp/codes\_0.npy" \\

# &nbsp; -o "~/workspace/source/fish-speech/temp/out.wav" \\

# &nbsp; --checkpoint-path "~/workspace/model\_zoo/fishaudio/openaudio-s1-mini/codec.pth"

# ```

# 

# \### 3. RAG 服务（Milvus+BGE）

# 

# \*\*启动 Milvus\*\*

# 

# ```bash

# python -c "from pymilvus import MilvusClient; client = MilvusClient('~/workspace/milvus\_db/assistant\_db')"

# ```

# 

# \*\*文档处理与入库\*\*

# 

# ```bash

# \# PDF 转图片（依赖 poppler-utils）

# sudo apt-get install -y poppler-utils

# pdftoppm -jpeg -r 300 ~/workspace/data/school\_info.pdf ~/workspace/data/pdf\_imgs/page

# 

# \# OCR 与向量入库

# python ~/workspace/source/campus\_rag\_ocr.py

# python ~/workspace/source/summary\_text.py

# python ~/workspace/source/bge\_api.py

# python ~/workspace/source/insert\_milvus.py

# ```

# 

# \## 接口设计（v1）

# 

# \### 1. 语音唤醒接口

# 

# \*\*请求：\*\*

# 

# ```http

# POST /v1/wake

# ```

# 

# \*\*请求体：\*\*

# 

# ```json

# {

# &nbsp; "device\_id": "user\_device\_123",

# &nbsp; "ts": 1737578901234

# }

# ```

# 

# \*\*响应：\*\*

# 

# ```json

# {

# &nbsp; "ok": true,

# &nbsp; "session\_id": "uuid:8f7e6d5c-4b3a-210f-9e8d-7c6b5a493827"

# }

# ```

# 

# \### 2. 语音识别接口（流式）

# 

# \*\*请求：\*\*

# 

# ```http

# POST /v1/asr/stream

# Content-Type: audio/pcm

# ```

# 

# \*\*响应示例：\*\*

# 

# ```json

# {

# &nbsp; "type": "partial",

# &nbsp; "text": "小美，我想问宿舍的热水",

# &nbsp; "timestamp": 1737578902345

# }

# ```

# 

# \### 3. 大语言模型调用接口

# 

# \*\*请求：\*\*

# 

# ```http

# POST /v1/llm/ask

# ```

# 

# \*\*请求体：\*\*

# 

# ```json

# {

# &nbsp; "query": "宿舍热水什么时候供应？",

# &nbsp; "user\_id": "user\_123",

# &nbsp; "session\_id": "uuid:8f7e6d5c-4b3a-210f-9e8d-7c6b5a493827",

# &nbsp; "need\_rag": true,

# &nbsp; "top\_k": 5

# }

# ```

# 

# \*\*响应：\*\*

# 

# ```json

# {

# &nbsp; "answer": "宿舍热水每天17:00-23:00供应，需插校园卡使用，没热水可先查卡内余额哦～",

# &nbsp; "citations": \[{"doc\_id": "kb:dorm:202509", "score": 0.89}],

# &nbsp; "latency\_ms": 1120

# }

# ```

# 

# \### 4. 语音合成接口

# 

# \*\*请求：\*\*

# 

# ```http

# POST /v1/tts/synthesize

# ```

# 

# \*\*请求体：\*\*

# 

# ```json

# {

# &nbsp; "text": "宿舍热水每天17:00-23:00供应，需插校园卡使用～",

# &nbsp; "voice": "xiao\_mei",

# &nbsp; "format": "mp3"

# }

# ```

# 

# \*\*响应：\*\*

# 二进制 MP3 音频流（或临时下载 URL）

# 

# \## 开发与调试

# 

# \### 健康检查清单

# 

# \* GPU 状态验证：`nvidia-smi`

# \* 服务端口监听：`ss -lptn 'sport = :10095'`

# \* ASR 功能测试：使用 `funasr\_wss\_client.py` 发送测试音频

# \* RAG 检索验证：`python ~/workspace/source/test\_rag.py`

# \* TTS 功能验证：调用 `/v1/tts/synthesize` 接口并播放音频

# 

# \### 常见问题解决

# 

# \* \*\*FunASR 启动失败\*\*：检查 `LD\_LIBRARY\_PATH` 是否包含 onnxruntime 和 ffmpeg 的 lib 目录，确保模型路径为绝对路径。

# \* \*\*Fish-Speech 解码报错\*\*：确认 `--checkpoint-path` 指向 codec.pth（而非 generator.pth 等其他模型文件）。

# \* \*\*Milvus 入库失败\*\*：验证向量维度（BGE-M3 为 1024 维）与 Milvus 集合的字段定义一致。




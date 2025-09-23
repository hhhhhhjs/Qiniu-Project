# FunASR 实时听写 + Fish-Speech 1.5（基础合成链路）部署文档

> 目标：在一台 Ubuntu 主机上完成 FunASR 实时 2-Pass WebSocket 服务的部署与联调，并准备 Fish-Speech 的基础推理链路（从语义码恢复音频）。
> 适用：CUDA/NVIDIA GPU 环境（已安装驱动），可访问外网下载模型。

------

## 一、系统与环境准备

### 1) 基础依赖

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake git wget unzip \
    libopenblas-dev libssl-dev \
    portaudio19-dev libsox-dev ffmpeg
```

### 2) Conda 环境（ASR）

```bash
conda create -n funasr_env python=3.10 -y
conda activate funasr_env
# 根据你的记录：CUDA 12.1
conda install pytorch==2.0.1 torchaudio==2.0.2 pytorch-cuda=12.1 -c pytorch -c nvidia -y
```

### 3) 目录结构

```bash
mkdir -p ~/workspace/{source,server,model_zoo,data}
cd ~/workspace
```

------

## 二、FunASR 源码与安装

### 1) 拉取并本地安装

```bash
cd ~/workspace/source
# 方式A：Git（推荐）
git clone https://github.com/modelscope/FunASR.git
cd FunASR
pip3 install -e ./
```

> 如果你是用的 `FunASR-main.zip`，解压后 `mv FunASR-main FunASR` 再执行 `pip install -e ./` 即可。

### 2) 运行时依赖（onnxruntime/ffmpeg 二进制）

> 你采用了官方预编译包，继续沿用。

```bash
cd ~/workspace/source
wget https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ASR/dep_libs/onnxruntime-linux-x64-1.14.0.tgz
tar -zxvf onnxruntime-linux-x64-1.14.0.tgz

wget https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ASR/dep_libs/ffmpeg-master-latest-linux64-gpl-shared.tar.xz
tar -xvf ffmpeg-master-latest-linux64-gpl-shared.tar.xz
```

> **动态库路径（关键）：**

```bash
export LD_LIBRARY_PATH=~/workspace/source/onnxruntime-linux-x64-1.14.0/lib:~/workspace/source/ffmpeg-master-latest-linux64-gpl-shared/lib:$LD_LIBRARY_PATH
```

------

## 三、模型下载（ASR + VAD + 标点 + LM + ITN）

### 1) 安装 ModelScope

```bash
pip3 install -U modelscope huggingface_hub
```

### 2) 下载模型到本地 `model_zoo`

```bash
cd ~/workspace/model_zoo

# （可选）Whisper-large-v3-turbo，仅存放不参与 FunASR 2-Pass
modelscope download --model iic/Whisper-large-v3-turbo --local_dir ./iic/Whisper-large-v3-turbo

# Paraformer ONNX（离线/在线）
modelscope download --model iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-onnx \
  --local_dir ./iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-onnx

modelscope download --model iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online-onnx \
  --local_dir ./iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online-onnx

# VAD
modelscope download --model iic/speech_fsmn_vad_zh-cn-16k-common-onnx \
  --local_dir ./iic/speech_fsmn_vad_zh-cn-16k-common-onnx

# 标点
modelscope download --model iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727-onnx \
  --local_dir ./iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727-onnx

# 语言模型（FST）
modelscope download --model damo/speech_ngram_lm_zh-cn-ai-wesp-fst \
  --local_dir ./damo/speech_ngram_lm_zh-cn-ai-wesp-fst

# 数字/时间等反向文本正规化（ITN）
modelscope download --model thuduj12/fst_itn_zh \
  --local_dir ./thuduj12/fst_itn_zh
```

> **目录检查：**

- `~/workspace/model_zoo/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-onnx`
- `~/workspace/model_zoo/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online-onnx`
- `~/workspace/model_zoo/iic/speech_fsmn_vad_zh-cn-16k-common-onnx`
- `~/workspace/model_zoo/iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727-onnx`
- `~/workspace/model_zoo/damo/speech_ngram_lm_zh-cn-ai-wesp-fst`
- `~/workspace/model_zoo/thuduj12/fst_itn_zh`

------

## 四、WebSocket 服务端编译（FunASR/runtime/websocket）

### 1) 依赖准备（websocketpp）

```bash
cd ~/workspace/source
git clone --depth 1 https://github.com/zaphoyd/websocketpp.git
mv websocketpp third_party/  # 目录名与CMake参数保持一致更直观
```

### 2) 编译

```bash
cd ~/workspace/source/FunASR/runtime/websocket
mkdir -p build && cd build

cmake -DCMAKE_BUILD_TYPE=Release \
  -Dwebsocketpp_SOURCE_DIR=~/workspace/source/third_party/websocketpp \
  -DONNXRUNTIME_DIR=~/workspace/source/onnxruntime-linux-x64-1.14.0 \
  -DFFMPEG_DIR=~/workspace/source/ffmpeg-master-latest-linux64-gpl-shared \
  ..

make -j4
```

> **可执行文件位置**：`~/workspace/source/FunASR/runtime/websocket/build/bin/`
> **库依赖检查**（若有 “not found” 就要补 `LD_LIBRARY_PATH`）：

```bash
ldd ~/workspace/source/FunASR/runtime/websocket/build/bin/funasr-wss-server-2pass | grep "not found" || echo "依赖完整"
```

------

## 五、启动 FunASR 2-Pass WebSocket 服务

### 1) SSL 证书与热词

- 证书：`~/ssl_key/server.crt` 与 `~/ssl_key/server.key`
- 热词：`~/workspace/hotwords.txt`（如无可不传）

### 2) 启动命令（按你今天的用法）

```bash
cd ~/workspace/source/FunASR/runtime
export LD_LIBRARY_PATH=~/workspace/source/onnxruntime-linux-x64-1.14.0/lib:~/workspace/source/ffmpeg-master-latest-linux64-gpl-shared/lib:$LD_LIBRARY_PATH

nohup bash run_server_2pass.sh \
  --model-dir       ~/workspace/model_zoo/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-onnx \
  --online-model-dir ~/workspace/model_zoo/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online-onnx \
  --vad-dir         ~/workspace/model_zoo/iic/speech_fsmn_vad_zh-cn-16k-common-onnx \
  --punc-dir        ~/workspace/model_zoo/iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727-onnx \
  --lm-dir          ~/workspace/model_zoo/damo/speech_ngram_lm_zh-cn-ai-wesp-fst \
  --itn-dir         ~/workspace/model_zoo/thuduj12/fst_itn_zh \
  --certfile        ~/ssl_key/server.crt \
  --keyfile         ~/ssl_key/server.key \
  --hotword         ~/workspace/hotwords.txt \
  > log.txt 2>&1 &
```

> **端口检查（默认 10095）：**

```bash
ss -lptn 'sport = :10095'
tail -n 200 -f log.txt
nvidia-smi
```

------

## 六、客户端联调（本机直连）

### 1) 准备音频

```bash
cd ~/workspace/data
ffmpeg -i test.m4a -ac 1 -ar 16000 output.wav -y
```

### 2) 运行 Python 客户端

```bash
cd ~/workspace/source/FunASR/runtime/python/websocket
pip install websockets soundfile humanfriendly  # 你已安装过，可忽略
# SSL=1 走 wss，自签证书需信任或关闭校验（FunASR客户端提供 --ssl 1/2/0 选项）
python3 funasr_wss_client.py \
  --host 127.0.0.1 \
  --port 10095 \
  --mode 2pass \
  --ssl 1 \
  --audio_in ~/workspace/data/output.wav
```

> **常见切换**：`--ssl 0`（纯 ws）；`--ssl 2`（跳过证书校验，视客户端实现而定）。

------

## 七、Fish-Speech 1.5 基础推理链路（从语义码到音频）

> 你今天主要卡在**检查点文件类型**与**输入文件类型**的对应关系。
> **核心原则**：
>
> - `fish_speech/models/dac/inference.py` 读取的是**语义码（codes_\*.npy）\**或\**音频**并用**Codec/DAC**权重进行**解码**到音频。
> - **Checkpoint 路径必须是 Codec（如 OpenAudio-S1-Mini 的 `codec.pth`）**，不是 Fish-Speech 生成器的 `generator.pth`。

### 1) 新建环境并安装

```bash
conda create -n fish-speech python=3.12 -y
conda activate fish-speech

cd ~/workspace/source
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
pip install -e .[cu128]  # 你已安装过Torch(CUDA 12.8索引)，此处沿用
```

### 2) 下载（或已下载）Codec 权重

```bash
cd ~/workspace/model_zoo
modelscope download --model fishaudio/openaudio-s1-mini --local_dir ./fishaudio/openaudio-s1-mini
# 其中包含 codec.pth 与 model.pth（codec 才是解码器）
```

### 3) 路线A：用已有语义码恢复音频（你已经拿到了 codes_0.npy）

```bash
# 假设 codes_0.npy 位于 ~/workspace/source/fish-speech/temp/codes_0.npy
cd ~/workspace/source/fish-speech

python fish_speech/models/dac/inference.py \
  -i "temp/codes_0.npy" \
  -o "temp/out.wav" \
  --checkpoint-path "~/workspace/model_zoo/fishaudio/openaudio-s1-mini/codec.pth"
```

> ✅ 关键：`--checkpoint-path` 必须指向 **codec.pth**。
> 你之前多次尝试把 `generator.pth`、`model.pth` 传进去，会导致报错或无效。

### 4) 路线B：先将音频编码成语义码，再解码回音频（简单自验证）

```bash
# 1 把一段音频（16k 单通道）转语义码（不同分支/脚本会有不同入口；若使用 text2semantic 需先准备prompt）
ffmpeg -i ~/workspace/data/clone.m4a -ac 1 -ar 16000 ~/workspace/data/clone.wav -y

# 2 （若你只有语义码而没有完整 T2S 流程，可跳过这步；完整T2S需要text2semantic生成codes）
# 3 直接用 DAC 将 codes_0.npy 解码为 wav
python fish_speech/models/dac/inference.py \
  -i "temp/codes_0.npy" \
  -o "temp/out.wav" \
  --checkpoint-path "~/workspace/model_zoo/fishaudio/openaudio-s1-mini/codec.pth"
```

> **关于你看到的“未来警告”**：
> “保留从原始路径（tools/vqgan/inference.py）访问接口的能力，但此接口可能在后续版本中被删除”，意思是旧路径还能用，但**尽快切到新脚本**（你现在用的 `fish_speech/models/dac/inference.py` 就是新的）。

------

## 八、常见问题速查

1. **端口未监听 / 服务未起**

```bash
ss -lptn 'sport = :10095' || echo "10095 端口空闲"
tail -n 200 ~/workspace/source/FunASR/runtime/log.txt
```

- 多半是动态库没找到（补 `LD_LIBRARY_PATH`），或模型路径写成了「模型名」而非「本地路径」。
- 本文推荐**全部使用本地绝对路径**，避免拉取失败/网络波动。

1. **ldd 提示 not found**

```bash
ldd .../funasr-wss-server-2pass | grep "not found"
# 补齐 LD_LIBRARY_PATH 如上
```

1. **Numpy/依赖冲突（你已解决）**

```bash
pip uninstall -y numpy || true
conda install -y -c conda-forge "numpy=1.26.4"
```

1. **Fish-Speech 报错（Checkpoint 不匹配）**
   确保 `--checkpoint-path` 是 **openaudio-s1-mini/codec.pth**，而不是 `generator.pth` 或 `model.pth`。
2. **在容器里 systemctl 相关报错**
   这是正常的（容器里无 systemd）。用 `nohup ... &` 或 Supervisor/PM2 等进程守护即可。

------

## 九、服务联调给前端的最小交付物

- **WebSocket(S) 地址**：
  - `wss://<your_ip_or_domain>:10095`（若 `--ssl 1`）
  - `ws://<your_ip_or_domain>:10095`（若 `--ssl 0`）
- **协议**：FunASR runtime WebSocket（支持单段/流式）；你已验证过 `runtime/python/websocket/funasr_wss_client.py`。
- **音频规范**：`16kHz / 单声道 / PCM16（.wav）` 最稳。
- **返回**：中间结果（增量）+ 尾句重写（2-pass 修正）+ 标点 + ITN。
- **热词**：`hotwords.txt`（一行一个）可选。
- **示例客户端**：`funasr_wss_client.py`（Python），可据此改为前端 WebSocket 流式推送。

------

## 十、快速健康检查清单

-  `nvidia-smi` 正常；GPU 有剩余显存
-  `LD_LIBRARY_PATH` 包含 onnxruntime 与 ffmpeg 的 `lib` 目录
-  模型目录都在：`~/workspace/model_zoo/...`
-  `funasr-wss-server-2pass` 可执行，`ldd` 依赖完整
-  `ss -lptn 'sport = :10095'` 有进程监听
-  客户端本地音频压成 16k/mono，能返回增量转写与终稿
-  Fish-Speech 的 `codec.pth` 可用，`codes_0.npy → out.wav` 成功

------

### 附：你最终正确的两条关键命令（留档）

**启动 FunASR（全本地路径版）**

```bash
nohup bash ~/workspace/source/FunASR/runtime/run_server_2pass.sh \
  --model-dir       ~/workspace/model_zoo/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-onnx \
  --online-model-dir ~/workspace/model_zoo/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online-onnx \
  --vad-dir         ~/workspace/model_zoo/iic/speech_fsmn_vad_zh-cn-16k-common-onnx \
  --punc-dir        ~/workspace/model_zoo/iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727-onnx \
  --lm-dir          ~/workspace/model_zoo/damo/speech_ngram_lm_zh-cn-ai-wesp-fst \
  --itn-dir         ~/workspace/model_zoo/thuduj12/fst_itn_zh \
  --certfile        ~/ssl_key/server.crt \
  --keyfile         ~/ssl_key/server.key \
  --hotword         ~/workspace/hotwords.txt \
  > ~/workspace/source/FunASR/runtime/log.txt 2>&1 &
```

**Fish-Speech 从语义码解码音频**

```bash
python ~/workspace/source/fish-speech/fish_speech/models/dac/inference.py \
  -i "~/workspace/source/fish-speech/temp/codes_0.npy" \
  -o "~/workspace/source/fish-speech/temp/out.wav" \
  --checkpoint-path "~/workspace/model_zoo/fishaudio/openaudio-s1-mini/codec.pth"
```


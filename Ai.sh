#!/bin/bash

# Configuration
PROJECT_DIR="q_control"
LLAMA_DIR="$PROJECT_DIR/engine"
# Using a 0.5B profile to ensure smooth operation on the 1GB memory of the Pi 3B
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q8_0.gguf"
MODEL_FILE="qwen2.5-0.5b-q8.gguf"
PORT=8080

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

# 1. Initialize Folders
mkdir -p "$LLAMA_DIR"
cd "$PROJECT_DIR" || exit

# 2. Download Engine (Portable binary for ARM64/Pi 3B)
if [ ! -f "engine/llama-server" ]; then
    echo "Installing Core Components..."
    curl -L "https://github.com/ggerganov/llama.cpp/releases/download/b4610/llama-b4610-bin-arm64.zip" -o "engine/tool.zip"
    unzip -q "engine/tool.zip" -d "engine/temp"
    mv engine/temp/build/bin/llama-server engine/
    rm -rf engine/temp engine/tool.zip
    chmod +x engine/llama-server
fi

# 3. Download Model
if [ ! -f "$MODEL_FILE" ]; then
    echo "Downloading Intelligence Profile..."
    wget "$MODEL_URL" -O "$MODEL_FILE"
fi

# 4. Create Dashboard (Optimized for Mobile and Internal App View)
cat <<EOF > index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Q Control</title>
    <style>
        :root { --bg: #0a0a0a; --card: #161616; --accent: #00ffff; --text: #ffffff; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; height: -webkit-fill-available; overflow: hidden; }
        header { padding: 15px; border-bottom: 1px solid #333; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
        .status-container { display: flex; flex-direction: column; align-items: flex-end; }
        .status { font-size: 10px; color: var(--accent); text-transform: uppercase; letter-spacing: 2px; }
        .ip-display { font-size: 9px; color: #666; font-family: monospace; margin-top: 2px; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; background: radial-gradient(circle at top right, #111, #0a0a0a); }
        .msg { max-width: 85%; padding: 12px 16px; border-radius: 20px; line-height: 1.5; font-size: 15px; word-wrap: break-word; }
        .user { align-self: flex-end; background: var(--accent); color: #000; border-bottom-right-radius: 4px; font-weight: 500; box-shadow: 0 4px 15px rgba(0, 255, 255, 0.2); }
        .q { align-self: flex-start; background: var(--card); border-bottom-left-radius: 4px; border: 1px solid #333; }
        #input-area { padding: 15px 15px 30px 15px; background: var(--card); display: flex; gap: 10px; border-top: 1px solid #333; flex-shrink: 0; }
        input { flex: 1; background: #000; border: 1px solid #444; color: #fff; padding: 14px; border-radius: 15px; outline: none; font-size: 16px; }
        input:focus { border-color: var(--accent); }
        button { background: var(--accent); color: #000; border: none; padding: 0 20px; border-radius: 15px; font-weight: bold; cursor: pointer; transition: transform 0.1s; }
        button:active { transform: scale(0.95); }
    </style>
</head>
<body>
    <header>
        <div style="font-weight: bold; font-size: 18px; letter-spacing: -1px;">Q SYSTEM</div>
        <div class="status-container">
            <div class="status">● ONLINE</div>
            <div class="ip-display">$LOCAL_IP</div>
        </div>
    </header>
    <div id="chat">
        <div class="msg q">System online. All modules active. How can I help you, Ramona?</div>
    </div>
    <div id="input-area">
        <input type="text" id="msg" placeholder="Type instruction..." autocomplete="off">
        <button id="send-btn">SEND</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('msg');
        const btn = document.getElementById('send-btn');

        input.addEventListener('keypress', (e) => { if(e.key === 'Enter') send(); });
        btn.onclick = send;

        async function send() {
            const val = input.value.trim();
            if(!val) return;
            
            chat.innerHTML += '<div class="msg user">' + val + '</div>';
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const qMsg = document.createElement('div');
            qMsg.className = 'msg q';
            qMsg.innerText = '...';
            chat.appendChild(qMsg);
            chat.scrollTop = chat.scrollHeight;

            try {
                const response = await fetch('/completion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: "<|im_start|>system\nName: Q. User: Ramona. Language: British English. No special characters or backticks. Formatting: If code is requested, use 'Language: Code' format without backticks. [cite: 2025-12-17]<|im_end|>\n<|im_start|>user\n" + val + "<|im_end|>\n<|im_start|>assistant\n",
                        n_predict: 512,
                        stream: false,
                        temperature: 0.7
                    })
                });
                const data = await response.json();
                qMsg.innerText = data.content.trim();
            } catch (e) {
                qMsg.innerText = "Connection lost.";
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
EOF

# 5. Launch the system
echo "-------------------------------------------------------"
echo "Q System is now active."
echo "Access it on this device: http://localhost:$PORT"
echo "Access it on other devices: http://$LOCAL_IP:$PORT"
echo "-------------------------------------------------------"

./engine/llama-server \
    -m "$MODEL_FILE" \
    --port "$PORT" \
    --host 0.0.0.0 \
    --path . \
    --ctx-size 2048 \
    --threads 4 \
    --mlock

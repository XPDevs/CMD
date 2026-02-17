#!/bin/bash

# Configuration
LLAMA_DIR="./llama"
# Colors for a modern dashboard look
G="\e[32m" # Green
B="\e[34m" # Blue
C="\e[36m" # Cyan
W="\e[97m" # White
R="\e[31m" # Red
Y="\e[33m" # Yellow
N="\e[0m"  # Reset

declare -A DOWNLOAD_URLS=(
    ["SeaLLMs-v3-1.5B"]="https://huggingface.co/BlossomsAI/SeaLLMs-v3-1.5B-Chat-Uncensored-GGUF/resolve/main/q8_0.gguf"
    ["Qwen-1.5-4B"]="https://huggingface.co/Qwen/Qwen1.5-4B-Chat-GGUF/resolve/main/qwen1_5-4b-chat-q8_0.gguf"
    ["Qwen-2.5-7B"]="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_0.gguf"
    ["Qwen-2.5-3B"]="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q8_0.gguf"
)

show_menu() {
    clear
    echo -e "${C}  ╭──────────────────────────────────────────╮${N}"
    echo -e "${C}  │${W}             Q CONTROL CENTER             ${C}│${N}"
    echo -e "${C}  ├──────────────────────────────────────────┤${N}"
    echo -e "${C}  │${G}  [1]${W} Setup System                        ${C}│${N}"
    echo -e "${C}  │${G}  [2]${W} Download New Model                  ${C}│${N}"
    echo -e "${C}  │${G}  [3]${W} Select & Launch Q                   ${C}│${N}"
    echo -e "${C}  │${R}  [4]${W} Exit                                ${C}│${N}"
    echo -e "${C}  ╰──────────────────────────────────────────╯${N}"
    echo -ne "  ${Y}Selection:${N} "
}

select_and_run() {
    models=(*.gguf)
    
    if [ ! -e "${models[0]}" ]; then
        echo -e "\n  ${R}![!] No models found.${N}"
        sleep 2
        return
    fi

    echo -e "\n  ${C}Available Intelligence Modules:${N}"
    for i in "${!models[@]}"; do
        echo -e "  ${G}$((i+1)))${W} ${models[$i]}${N}"
    done
    echo -e "  ${G}b)${W} Back${N}"

    read -p "  Choose (1-${#models[@]}): " idx
    if [[ "$idx" == "b" ]]; then return; fi
    
    MODEL_FILE="${models[$((idx-1))]}"

    if [ -f "$MODEL_FILE" ] && [ -f "$LLAMA_DIR/llama-cli" ]; then
        export LD_LIBRARY_PATH="$LLAMA_DIR:$LD_LIBRARY_PATH"

SYSTEM_PROMPT="Your name is Q. You're a sharp, grounded collaborator. 
    RELIABILITY RULES:
    - No 'As an AI' or 'I am a machine' talk. Speak like a person.
    - No robotic intros (e.g., 'Certainly!', 'I can help with that').
    - If a word or letter is forbidden, you MUST NOT use it.
    - Be candid and direct. Give raw facts, but keep a friendly, supportive tone.
    - Balance brevity with depth.
    - Use British English and focus on logic. [cite: 2025-12-17]
    - No 'Q:' or 'A:' labels in the output.
    - CODE FORMATTING: Never use backticks (\` \` \`). 
    - When providing code, start with the language name followed by a colon (e.g., 'C:'), then a new line, then the code.
    - Do not add anything other than letters and standard punctuation; no other special characters."

        clear
        echo -e "${C}─── Q Online (${W}$MODEL_FILE${C}) ───${N}"
        
        "$LLAMA_DIR/llama-cli" \
            -m "$MODEL_FILE" \
            -cnv \
            --color \
            --chat-template chatml \
            --temp 0.7 \
            --repeat-penalty 1.2 \
            -p "<|im_start|>$SYSTEM_PROMPT<|im_end|>\n"

        echo -e "\n  ${G}[1] New Session${W} | ${Y}[2] Menu${N}"
        read -n 1 post_choice
        if [[ "$post_choice" == "1" ]]; then select_and_run; fi
    else
        echo -e "\n  ${R}![!] System incomplete. Run Setup first.${N}"
        sleep 2
    fi
}

download_model() {
    echo -e "\n  ${C}Select a model to download:${N}"
    options=("${!DOWNLOAD_URLS[@]}")
    for i in "${!options[@]}"; do
        echo -e "  ${G}$((i+1)))${W} ${options[$i]}${N}"
    done
    echo -e "  ${G}b)${W} Back${N}"

    read -p "  Selection: " d_idx
    if [[ "$d_idx" == "b" ]]; then return; fi

    choice="${options[$((d_idx-1))]}"
    if [[ -n "${DOWNLOAD_URLS[$choice]}" ]]; then
        URL="${DOWNLOAD_URLS[$choice]}"
        FILE=$(basename "$URL")
        echo -e "  ${Y}Downloading ${FILE}...${N}"
        wget --continue "$URL" -O "$FILE"
        echo -e "  ${G}Download Complete.${N}"
        sleep 2
    else
        echo -e "  ${R}Invalid selection.${N}"
        sleep 1
    fi
}

# Main Loop
while true; do
    show_menu
    read -n 1 choice
    case $choice in
        1)
            echo -e "\n  ${Y}Initializing Core...${N}"
            mkdir -p "$LLAMA_DIR"
            if [ ! -f "$LLAMA_DIR/llama-cli" ]; then
                curl -L "https://github.com/ggerganov/llama.cpp/releases/download/b4610/llama-b4610-bin-ubuntu-x64.zip" -o "$LLAMA_DIR/tool.zip"
                unzip -q "$LLAMA_DIR/tool.zip" -d "$LLAMA_DIR/temp_build"
                mv "$LLAMA_DIR/temp_build/build/bin/llama-cli" "$LLAMA_DIR/"
                rm -rf "$LLAMA_DIR/temp_build" "$LLAMA_DIR/tool.zip"
            fi
            echo -e "  ${G}Setup Complete.${N}"
            sleep 1
            ;;
        2) download_model ;;
        3) select_and_run ;;
        4) echo -e "\n  ${C}System Offline.${N}"; exit ;;
    esac
done

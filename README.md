# Ma Sói Online

Trò chơi Ma Sói web-based, chạy local, với AI agents (LLM).

## Cấu trúc

```
werewolf/           ← root
├── .env            ← API keys & config (KHÔNG commit)
├── .env.example    ← mẫu .env
├── venv/           ← virtual environment Python (root-level)
├── run.py          ← khởi động server
├── backend/
│   ├── main.py
│   ├── game.py / resolver.py / room_manager.py
│   ├── agents/     ← AI agent + providers
│   ├── roles/      ← định nghĩa vai trò
│   ├── db/         ← SQLite models
│   └── logs/       ← game.db + log files
└── frontend/
    ├── templates/  ← lobby.html, game.html
    └── static/
        ├── css/custom.css
        └── js/     ← seat-circle, chat-panel, ws-client, lobby
```

## Cài đặt

```bash
# 1. Tạo venv ở root (nếu chưa có)
python3 -m venv venv

# 2. Kích hoạt venv
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate             # Windows

# 3. Cài dependencies
pip install -r backend/requirements.txt

# 4. Cấu hình API keys
cp .env.example .env
# Sửa .env: thêm GEMINI_API_KEYS hoặc OPENAI_API_KEYS

# 5. Chạy
python run.py
# → http://localhost:8000
```

## Providers

| Provider | Env var | Ghi chú |
|---|---|---|
| Gemini | `GEMINI_API_KEYS=key1,key2` | Primary |
| OpenRouter/OpenAI | `OPENAI_API_KEYS=sk-or-...` | Fallback |
| Ollama (local) | `OLLAMA_ENABLED=true` | phi3:mini mặc định |
| Qwen vLLM | `QWEN_VLLM_ENABLED=true` | Self-hosted |

## Road Map

* [x] Chế độ chơi cơ bản với các key
* [] Cho Agent có suy nghĩ và cách hành động như con người
* [] Kịch bản mở rộng
    * [] Thêm nhân vật mở rộng
    * [] Thêm kịch bản mở rộng
    * [] Thêm kịch bản tự do
* [] Giao diện hiển thị mới
* [] Cập nhật assets với các hình ảnh nhân vật
* [] Thêm tính năng cho agent + admin
* [] Nhiều người chơi
    * [] Đăng nhập và database
    * [] Admin cấp tài khoản và cấp phát
    * [] Tự tạo tải khoản và đặt tên
* [] Realease
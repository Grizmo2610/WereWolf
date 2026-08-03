"""Khởi động server Ma Sói Online từ thư mục gốc."""
import os
import sys

# Thêm backend/ vào sys.path để import hoạt động
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend", "frontend"],
        app_dir="backend",
        log_level="info",
    )

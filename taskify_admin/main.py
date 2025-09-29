import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from taskify_components.taskify_common.src.expection import register_exception_handlers

app = FastAPI()

# 注册全局异常
register_exception_handlers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=10000, log_level="info", reload=True)

#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/17 下午4:19 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : main.py
# @desc : README.md

# 标准库导入
import os

# 第三方库导入
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 本地模块导入
from backend.api import review, github, history, mindmap
from backend.core.logger import Config, setup_logger

# 初始化FastAPI应用
app = FastAPI(
    title="RadishRobot",
    description="一个使用大型语言模型api进行代码审查、重构、文档生成和关系链可视化的工具。",
    version="0.1.0"
)

# 加载配置和安装记录器，添加简单错误处理
try:
    config = Config("config.yaml")
    logger = setup_logger(config)
    logger.info("FastAPI 服务启动")

except Exception as e:
    print(f"配置加载失败: {e}")
    raise

# 配置CORS以允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://localhost:4173"],  # 调整前端URL
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],


)
# https://github.com/Ashisheng2005/Live2dTK
# 包含API路由器
# 重构
app.include_router(review)
# github
app.include_router(github)
# 历史记录
app.include_router(history)
# 可视化节点
app.include_router(mindmap)


# Root endpoint
@app.get("/")
async def root():
    """
    用于基本项目信息的根端点。
    返回：包含项目详细信息的JSON。
    """

    return JSONResponse({
        "message": "欢迎来到RadishRobot!",
        "endpoints": {
            "/health": "Check API status",
            "/github/fetch": "Fetch code from GitHub repository",
            "/review": "Review and refactor code"
        },
        "docs": "/docs"
    })


# 运行状况检查端点
@app.get("/health")
async def health_check():
    """
    用于验证API状态的健康检查端点。
    返回：包含状态和消息的字典。
    """
    logger.info("请求运行状况检查")
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # from backend.core.parser import CodeTree

    # demo = CodeTree()
    # code = """
    # def fun():
    #     print("This is text string!")
    #
    # for i in range(10):
    #     fun()
    # """
    # code_tokens = demo.processing_coed("python", code)
    # print(code_tokens)

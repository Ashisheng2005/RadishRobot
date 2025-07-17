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
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# 本地模块导入
from backend.api import review, github, history, mindmap
from backend.core.logger import Config, setup_logger
from socket import gethostname, gethostbyname_ex    # 获取ip地址

# 加载配置和安装记录器

try:
    config = Config("config.yaml")
    logger = setup_logger(config)

    # ip选配，如果存在多个ip，选择一个可用的，尼玛这就是个坑，谁知道虚拟ip也会被检测到
    host_ip = config.get_nested("server_set", "host_ip")
    if host_ip == "auto":
        hostname = gethostname()
        ip_list = gethostbyname_ex(hostname)[2]
        if len(ip_list) == 1:
            host_ip = ip_list[0]

        else:
            print("Multiple ips have been detected. Please select a suitable one:\n")
            for id, ip in enumerate(ip_list, start=1):
                print(f"\033[0;32;40m{id}\033[0m: \033[0;31;40m{ip}\033[0m")

            try:
                id = int(input(">>> "))
                host_ip = ip_list[id - 1]

            except Exception as e:
                logger.info(f"select ip Error: {e}")
                exit()

    else:
        # 验证ip格式
        if len(host_ip.split(".")) == 4:
            for i in host_ip.split("."):
                if 0 <= int(i) <= 255:
                    continue

                else:
                    logger.info(f"配置的ip地址不符合，请填写正确格式ip地址")
                    exit()

    post = config.get_nested("server_set", "post")
    public = config.get_nested("server_set", "public")
    mode = config.get_nested("server_set", "mode")
    logger.info(f"FastAPI 服务启动成功")

except Exception as e:
    print(f"配置加载失败: {e}")
    raise


# 初始化FastAPI应用
app = FastAPI(
    title="RadishRobot",
    description="一个使用大型语言模型api进行代码审查、重构、文档生成和关系链可视化的工具。",
    version="0.0.1"
)


try:
    # 读取
    data = """import path from "path"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),

    },
  },
  optimizeDeps: {
    include: ['vis-network'],
  },

  build: {
    rollupOptions: {
      external: [],
    },
    minify: 'esbuild',
    outDir: 'dist',
    sourcemap: false,
  },

  server: {
    fs: {
      allow: ['.'],
    },
    host: '0.0.0.0',
    port: 5173,
    proxy: {
        '/api': {
            target: 'http://host_ip:post',
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/api/, ''),
        },
    },
  },
})"""

    # 替换本地ip
    data = data.replace("host_ip:post", host_ip + f":{post}" if public == "True" else f"localhost:{post}")

    # 覆盖
    with open("./rr_frontend/vite.config.ts", "w") as f:
        f.write(data)

    logger.info(f"自动ip配置成功，ip: {host_ip}, post: {post}")

except Exception as e:
    logger.info(f"自动ip配置失败，请手动修改./rr_frontend/vite.config.ts 文件的host_ip:post字段")

# 本地使用
local_allow_origins = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://localhost:4173"]
# 跨设备使用
public_allow_origins = [f"http://{host_ip}:3000", f"http://{host_ip}:5173", f"http://{host_ip}:{post}", f"http://{host_ip}:4173"]


# 配置CORS以允许前端访问
app.add_middleware(
    CORSMiddleware,
    # 调整前端URL
    allow_origins=public_allow_origins if public.lower() == "true" else local_allow_origins,
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

if mode.lower() == "test":
    logger.info(f"当前模式： Test")
    # 加载静态资源
    app.mount("/static", StaticFiles(directory="./static"), name="static")

    # 根路径返回 index.html
    @app.get("/")
    async def serve_index():
        logger.info("Serving index.html")
        return FileResponse("./static/index.html")

    # 日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response


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

# @app.get("/test")
# async def test_history():
#     return {"message": "Test history endpoint"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


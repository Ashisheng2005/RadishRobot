#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/5/31 下午16:30
# @Author  : Huzhaojun
# @Version : V 1.0
# @File    : review.py
# @desc    : 使用大型语言模型的代码审查和API重构

from fastapi import APIRouter, Form, HTTPException
from typing import Optional
from backend.core.parser import CodeTree
from backend.core.analyzer import Analyzer
from backend.core.model import send_message
from backend.core.logger import Config, setup_logger
from backend.database.sqlite_db import save_review

# 加载配置和安装记录器
config = Config("./config.yaml")
logger = setup_logger(config)

router = APIRouter(prefix="/api/review", tags=["review"])


@router.post("/")
async def review_code(code: Optional[str] = Form(None), github_url: Optional[str] = Form(None), branch: str = Form("main"), path: str = Form("")):
    """
    审查和重构代码，支持直接代码输入或GitHub URL。
    支持多种语言（Python, c++, Java, JavaScript, c#）。
    返回：每个文件的问题、优化代码、文档和复杂性指标。
    """

    if not code and not github_url:
        logger.info("没有提供代码或GitHub URL")
        raise HTTPException(status_code=400, detail="请提供代码或GitHub网址")

    try:
        # 初始化解析器和分析器
        code_tree = CodeTree()
        analyzer = Analyzer()

        # 存储多个文件的结果
        results = []

        # 处理GitHub输入
        if github_url:
            from backend.api.github import fetch_github_code
            code_files = await fetch_github_code(github_url, branch, path)
            logger.info(f"Fetched {len(code_files)} files from GitHub")

        else:
            # 单一代码输入，假设基于内容的语言，或者默认为Python
            language = "python"  # 默认值，将在下面进行细化
            code_files = {"input": {"language": language, "code": code}}

        for file_path, file_data in code_files.items():
            code = file_data["code"]
            language = file_data["language"]

            # 如果需要，优化语言检测（例如，直接输入）
            if language == "python" and not code.strip().endswith(".py") and "def " not in code:
                # Simple heuristic for other languages
                if "class " in code and "{" in code:
                    language = "java" if "public" in code else "cs"
                elif "function " in code or "=>" in code:
                    language = "js"
                elif "#include" in code or "int main" in code:
                    language = "cpp"
                logger.info(f"Refined language for {file_path}: {language}")

            # 使用Tree-sitter解析代码
            try:
                tokens = code_tree.processing_coed(language, code)
                if not tokens:
                    logger.error(f"Code parsing failed for {file_path}: No tokens generated")
                    results.append({
                        "file": file_path,
                        "language": language,
                        "error": "Code parsing failed",
                        "tokens": []
                    })
                    continue
            except Exception as e:
                logger.error(f"Parsing failed for {file_path}: {str(e)}")
                results.append({
                    "file": file_path,
                    "language": language,
                    "error": f"Parsing failed: {str(e)}",
                    "tokens": []
                })
                continue

            # 用Lizard分析复杂度
            try:
                complexity_data = analyzer.analyze_source_code(f".{language}", code)
                logger.info(f"Complexity analysis for {file_path}: {complexity_data}")
            except Exception as e:
                logger.warning(f"Complexity analysis failed for {file_path}: {str(e)}")
                complexity_data = {"error": str(e)}

            logger.info(f"向API发送提示 {file_path}")
            grok_response = send_message(code)

            # 检查API响应
            logger.info(f"API 回复: {grok_response}")
            try:
                if grok_response["state"] == 500:
                    logger.error(f"API 失败 {file_path}: {grok_response['message']}")
                    results.append({
                        "file": file_path,
                        "language": language,
                        "error": grok_response["message"],
                        "tokens": tokens,
                        "complexity": complexity_data
                    })
                    continue
            except TypeError as e:
                logger.info(f"API 回复参数state参数异常 {e}")
                return {"results": "Error Server reply"}

            # 解析响应（假设API返回带有问题、optimized_code、文档的JSON）
            result = {
                "file": file_path,
                "language": language,
                "code": code,
                "issues": grok_response["message"].get("issues", "No issues detected"),
                "optimized_code": grok_response["message"].get("optimized_code", code),
                "documentation": grok_response["message"].get("documentation", "# No documentation"),
                "complexity": complexity_data,
                "github_url": github_url,
                "branch": branch,
                "tokens": tokens
            }

            print(result)

            # 将评论保存到数据库
            save_review(result)
            # logger.info(f"评审结果保存于 {file_path}")

            results.append(result)

        return {"results": results}

    except Exception as e:
        logger.error(f"评论失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"评论失败: {str(e)}")
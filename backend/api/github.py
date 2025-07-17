#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/17 下午10:57 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : github.py
# @desc : README.md


from fastapi import APIRouter, HTTPException
from github import Github, GithubException
from backend.core.logger import Config, setup_logger
from dotenv import load_dotenv
import os

# 加载配置和安装记录器
config = Config("./config.yaml")
logger = setup_logger(config)
GITHUB_TOKEN = config.get_nested("github_set", "token", default="")

router = APIRouter(prefix="/api/github", tags=["github"])


async def fetch_github_code(github_url: str, branch: str = "main", path: str = "") -> dict:
    """
    从GitHub仓库获取代码，支持多种语言（.py、.cpp、.java、.js、.cs）。
    参数:
    github_url：存储库的URL（例如https://github.com/owner/repo）。
    branch：目标分支（默认：main）。
    path：指定的文件或目录路径（默认为root）。
    返回：包含语言和代码字符串的字典。
    """

    if not GITHUB_TOKEN:
        logger.error("GitHub token not configured")
        raise HTTPException(status_code=500, detail="GitHub token不存在，请检查配置文件")

    try:
        g = Github(GITHUB_TOKEN)
        # 提取存储库名称（格式：https://github.com/owner/repo）
        repo_name = github_url.split("github.com/")[1].rstrip("/")
        logger.info(f"Fetching code from GitHub repository: {repo_name}, branch: {branch}, path: {path}")
        repo = g.get_repo(repo_name)

        # 从指定的路径和分支获取内容
        contents = repo.get_contents(path, ref=branch)
        if not isinstance(contents, list):
            contents = [contents]

        # 支持的文件扩展名
        supported_extensions = (".py", ".cpp", ".java", ".js", ".cs")
        code_files = {}

        for content in contents:
            if content.type == "file" and content.path.endswith(supported_extensions):
                try:
                    lang = content.path.split(".")[-1]  # e.g., "py" for Python
                    code = content.decoded_content.decode("utf-8")
                    code_files[content.path] = {"language": lang, "code": code}
                    logger.info(f"获取文件: {content.path}")

                except Exception as e:
                    logger.warning(f"文件解码失败 {content.path}: {str(e)}")

            elif content.type == "dir":
                # 递归地获取子目录中的文件
                sub_contents = repo.get_contents(content.path, ref=branch)
                for sub_content in sub_contents:
                    if sub_content.path.endswith(supported_extensions):
                        try:
                            lang = sub_content.path.split(".")[-1]
                            code = sub_content.decoded_content.decode("utf-8")
                            code_files[sub_content.path] = {"language": lang, "code": code}
                            logger.info(f"获取文件: {sub_content.path}")

                        except Exception as e:
                            logger.warning(f"文件解码失败 {sub_content.path}: {str(e)}")

        if not code_files:
            logger.warning(f"在存储库中没有找到支持的文件: {repo_name}")
            raise HTTPException(status_code=404, detail="不支持代码文件 (.py, .cpp, .java, .js, .cs) found")

        return code_files

    except GithubException as e:
        logger.error(f"GitHub API错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"无法访问GitHub仓库: {str(e)}")

    except Exception as e:
        logger.error(f"获取代码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取代码失败: {str(e)}")


@router.get("/fetch")
async def get_github_code(github_url: str, branch: str = "main", path: str = ""):
    """
    从GitHub仓库获取代码的API端点

    :param github_url: 必须以https://github.com/开头的有效URL
    :param branch: 默认'main'分支
    :param path: 仓库中的文件路径（可选）
    :return: {"files": 代码内容} if success else {"error": 错误信息}
    """

    # 验证github_url格式
    if not github_url.startswith("https://github.com/"):
        return {"error": "Invalid GitHub URL. Must start with 'https://github.com/'"}

    # 验证branch/path非恶意输入（简单示例）
    if ".." in branch or ".." in path:
        return {"error": "Invalid branch or path parameter"}

    try:
        code_files = await fetch_github_code(github_url, branch, path)

        # 处理空结果
        if not code_files:
            return {"error": "No files found at specified path"}

    except ValueError as ve:
        return {"error": f"Validation error: {str(ve)}"}

    except TimeoutError:
        return {"error": "Request timed out"}

    except Exception as e:
        # 记录详细错误到日志
        logger.error(f"Internal error: {str(e)}")
        return {"error": "Failed to fetch code. Check repository accessibility"}

    return {"files": code_files}

#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/6/6 下午11:35 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : history.py
# @desc : 历史节点，返回数据库中保存的历史数据

from fastapi import APIRouter, Form, HTTPException
from typing import Optional
from backend.core.parser import CodeTree
from backend.core.analyzer import Analyzer
from backend.core.model import send_message
from backend.core.logger import Config, setup_logger
from backend.database.sqlite_db import save_review, get_reviews

# 加载配置和安装记录器
config = Config("./config.yaml")
logger = setup_logger(config)

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/")
async def history_data():
    """
    根据特定格式返回保存在数据库中的历史记录
    :return:
            [
          {
            "id": "1",
            "timestamp": "2025-06-06T15:25:00Z",
            "code": "print('Hello')",
            "results": "No issues found",
            "github_url": "https://github.com/owner/repo",
            "branch": "main"
          }
        ]

    """

    return get_reviews()



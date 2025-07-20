#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/7/19 下午7:50 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : deleteHistory.py
# @desc : README.md

from fastapi import APIRouter, Form, HTTPException
from typing import Optional
from backend.core.logger import Config, setup_logger
from backend.database.sqlite_db import delete_review

# 加载配置和安装记录器
config = Config("./config.yaml")
logger = setup_logger(config)

router = APIRouter(prefix="/api/deleteHistory", tags=["deleteHistory"])


@router.post("/")
async def delete_history(data_id: str = Form("")):
    """
    删除用户指定的记录

    :param data_id: 记录行标
    :return:
    """

    logger.info(f"data_id: {data_id}")

    if not data_id:
        logger.info("没有提供记录行标")
        raise HTTPException(status_code=400, detail="记录删除失败")

    try:
        results = delete_review(int(data_id))

        if results:
            logger.info(f"记录{data_id} 删除成功")

    except Exception as err:
        logger.info(f"删除记录出现错误，{err}")
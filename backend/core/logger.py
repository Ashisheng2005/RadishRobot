#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/30 下午11:53 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : logger.py
# @desc : README.md

import logging
import yaml
import os


class Config:
    """加载YAML配置文件并提供对设置的访问。"""

    def __init__(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_path} 不存在.")
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_nested(self, *keys, default=None):
        value = self.config
        for key in keys:
            if not isinstance(value, dict):
                return default
            if key not in value:
                return default
            value = value[key]
        return value


def setup_logger(config: Config):
    """
    集中日志设置，实现跨模块的一致日志记录。
    :return 配置好的logger对象
    """

    log_level = config.get_nested('logging', 'level', default='INFO')
    log_file = config.get_nested('logging', 'file', default='./logs/app.log')

    # os.makedirs(os.path.dirname(log_file), exist_ok=True)
    # 安全创建日志目录
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # 验证日志级别有效性
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level not in valid_levels:
        log_level = 'INFO'
        print(f"无效日志级别，使用默认INFO")

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
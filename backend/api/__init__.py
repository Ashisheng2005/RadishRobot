#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/17 下午10:57 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : __init__.py
# @desc : README.md

from .github import router as github
from .review import router as review
from .history import router as history
from .mindmap import router as mindmap
from .deleteHistory import router as deleteHistory

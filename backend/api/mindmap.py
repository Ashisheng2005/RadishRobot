#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/6/12 下午10:57
# @Author : Huzhaojun
# @Version：V 1.0
# @File : mindmap.py
# @desc : README.md
import os.path
from os import listdir
from json import dumps, loads

from fastapi import APIRouter, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
from tree_sitter import Language, Parser
from backend.core.parser import CodeTree
from backend.core.logger import Config, setup_logger
from backend.core.model import send_message
from backend.database.sqlite_db import save_review

# 加载配置和安装记录器
config = Config("./config.yaml")
logger = setup_logger(config)

router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])


class FileInput(BaseModel):
    path: str
    content: str


class MindmapRequest(BaseModel):
    files: List[FileInput]
    github_url: Optional[str] = None
    branch: Optional[str] = "main"


class Node(BaseModel):
    id: str
    label: str
    details: str
    code: str


class Edge(BaseModel):
    from_: str
    to: str


class MindmapResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


async def call_llm(content: str) -> str:
    """
    简单概括函数作用，返回指定数量的简介

    :param content: 函数内容
    :return: str
    """

    reply = send_message(message=f"请简要描述函数作用，80字以内：{content}", join=False, clean_data=False)

    return reply['message']


def ask_suffix(language: str, prompt: str = False) -> str:
    """
    询问指定语言的文件后缀

    :param prompt: 额外的提示词
    :param language: 语言名称
    :return: str
    """

    # 这里感觉怪怪的，下次优化把这里改一下，Ciallo~
    if prompt:
        reply = send_message(message=f"{prompt}", join=False, clean_data=False)

    else:
        reply = send_message(message=f"请直接返回{language}语言的文件后缀名，不带点号", join=False, clean_data=False)

    return str(reply['message'])


def create_language_dict(file_path: str = "./language.json") -> Dict:
    """
    初始化语言后缀映射表，判断当前存在的是否与语言库一一对应，有缺漏或者文件不存在则尝试修复

    :param file_path: 数据文件保存位置
    :return: Dict
    """

    language_dict = {}
    language_dict_ = {}
    try:
        logger.info(f"初始化语言后缀表")

        if os.path.isfile(file_path):
            with open(file_path, "r", encoding='utf-8') as file:
                language_dict_ = loads(file.read())

        # 剔除项目前缀 tree-sitter-
        language_list = [item[12:] for item in listdir("./backend/core/vendor")]

        for language_project in language_list:
                language = language_project
                if language_dict.get(language, False):
                    continue

                pattern = config.get_nested("model_set", "PATTERN", default=False)
                if pattern == "local":
                    # 这里留一个中间变量为以后的返回内容验证做准备
                    language_suffix = ask_suffix(language)
                    language_dict[language] = language_suffix
                    logger.info(f"询问本地模型后缀回复 {language}: {language_suffix}")

                elif pattern == "cloud":
                    language_suffix = ask_suffix(prompt = f"请按顺序返回{'、'.join(language_list)}语言的文件后缀名，不带点号且以空格分割，例如cpp py java")
                    for i in range(len(language_list)):
                        language_dict[language_list[i]] = language_suffix.split()[i]

                    break

    except Exception as err:
        logger.info(f"initial language dict error: {err}")

    # 反转，使用后缀作为key， 语言名称作为value
    if not language_dict_:
        for key in language_dict:
            language_dict_[language_dict[key]] = key.replace('-', "_")

        # 保存
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(dumps(language_dict_, ensure_ascii=False))

    return language_dict_


def extract_functions(file_content: str, file_path: str, code_type: str) -> Tuple[list, list]:
    """使用 CodeTree 提取函数及其调用关系"""

    logger.info(f"提取函数特征并分析调用关系: {file_content[:10]}, {file_path}, {code_type}")
    nodes = []
    edges = []

    try:
        # 初始化 CodeTree
        code_tree = CodeTree()

        # 验证代码类型
        if code_type not in code_tree.name_mapping_table:
            logger.warning(f"不支持的语言: {code_type} ({file_path})")
            return [], []

        # 解析语法树
        parser = Parser()
        parser.set_language(code_tree.name_mapping_table[code_type])
        tree = parser.parse(bytes(file_content, "utf-8"))
        root_node = tree.root_node

        # 存储函数和调用关系
        function_nodes = []
        function_calls = {}

        def get_identifier(node: Node) -> str:
            """从节点提取标识符（如函数名）"""
            if node.type == 'identifier':
                identifier = code_tree.index_to_code_token(
                    (node.start_point, node.end_point), file_content.split("\n")
                )
                logger.debug(f"提取 identifier: {identifier}")
                return identifier
            elif node.type == 'attribute':
                # 处理 self.method 的情况
                identifiers = []
                for child in node.children:
                    if child.type == 'identifier':
                        identifiers.append(code_tree.index_to_code_token(
                            (child.start_point, child.end_point), file_content.split("\n")
                        ))
                # 返回最后一个 identifier（如 _live2d_）
                if identifiers:
                    identifier = identifiers[-1]
                    logger.debug(f"提取 attribute identifier: {identifier}")
                    return identifier
            for child in node.children:
                result = get_identifier(child)
                if result:
                    logger.debug(f"递归提取 identifier: {result}")
                    return result
            return ""

        def traverse_node(node: Node, current_function: str = None):
            """递归遍历语法树，提取函数定义和调用"""
            nonlocal function_nodes, function_calls

            if node.type == 'function_definition':
                func_name = get_identifier(node)
                if func_name:
                    func_id = f"{file_path}:{func_name}"
                    func_code = code_tree.index_to_code_token(
                        (node.start_point, node.end_point), file_content.split("\n")
                    )
                    function_nodes.append({
                        "id": func_id,
                        "label": func_name,
                        "details": "",
                        "code": func_code
                    })
                    function_calls[func_id] = set()
                    current_function = func_id
                    logger.debug(f"定义函数: {func_id}")

            elif node.type == 'call':
                # 提取被调用函数名
                func_name = None
                for child in node.children:
                    if child.type in ('identifier', 'attribute'):
                        func_name = get_identifier(child)
                        break

                if func_name and current_function:
                    called_func_id = f"{file_path}:{func_name}"
                    function_calls[current_function].add(called_func_id)
                    logger.debug(f"检测到调用: {current_function} -> {called_func_id}")

            # 递归遍历子节点
            for child in node.children:
                traverse_node(child, current_function)

        # 遍历语法树
        traverse_node(root_node)

        # 生成节点和边
        nodes.extend(function_nodes)
        for caller, callees in function_calls.items():
            logger.info(f"caller: {caller}, callees: {callees}")
            for callee in callees:
                if any(node["id"] == callee for node in nodes):
                    edges.append({"from_": caller, "to": callee})
                    logger.info(f"添加边: {caller} -> {callee}")

        logger.info(f"处理完成，nodes: {len(nodes)} 个, edges: {len(edges)} 条")
        return nodes, edges

    except Exception as e:
        logger.error(f"解析 {file_path} 失败: {str(e)}")
        return [], []


@router.post("/")
async def generate_mindmap(request: MindmapRequest):
    nodes = []
    edges = []

    for file in request.files:
        # 推断代码类型
        extension = file.path.split('.')[-1]

        # code_type = {
        #     'py': 'python',
        #     'js': 'javascript',
        #     'java': 'java',
        #     'cpp': 'cpp',
        #     'cs': 'c_sharp'
        # }.get(extension, '')

        code_type = create_language_dict().get(extension, '')

        if code_type:
            file_nodes, file_edges = extract_functions(file.content, file.path, code_type)

            # 为节点添加大模型生成的描述
            for node in file_nodes:
                llm_description = await call_llm(node["code"])
                node["details"] = llm_description

            nodes.extend(file_nodes)
            edges.extend(file_edges)

    if not nodes:
        raise HTTPException(status_code=400, detail="未找到可解析的函数")

    _map = {
        'nodes': nodes,
        'edges': edges
    }

    results = {
        "file": "project",
        "language": str(code_type),
        "code": "",
        "issues": "",
        "optimized_code": "",
        "documentation": "",
        "complexity": "",
        "timestamp": "",
        "github_url": request.github_url,
        "branch": request.branch,
        "map": _map
    }

    save_review(results)

    return MindmapResponse(nodes=nodes, edges=edges)


if __name__ == '__main__':
    code = """def extract_functions(file_content: str, file_path: str, code_type: str) -> Tuple[list, list]:

    logger.info(f"提取函数特征并分析调用关系: {file_content[:10]}, {file_path}, {code_type}")
    nodes = []
    edges = []
    """

    print(ask_suffix(language="python"))

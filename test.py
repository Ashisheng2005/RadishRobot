# coding:utf-8

from os import listdir
import os
from json import loads, dumps


def create_language_dict(file_path: str = "./language.config"):
    """
    初始化语言后缀映射表，判断当前存在的是否与语言库一一对应，有缺漏或者文件不存在则尝试修复

    :param file_path: 数据文件保存位置
    :return: Dict
    """

    language_dict = {}
    try:
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding='utf-8') as file:
                language_dict = loads(file.read())

        for language_project in listdir("./backend/core/vendor"):
            if language_project.startswith("tree-sitter-"):
                language = language_project[12:]
                if language_dict.get(language, False):
                    continue

                # 这里留一个中间变量为以后的返回内容验证做准备
                language_suffix = "None"
                language_dict[language] = language_suffix

    except Exception as err:
        print(f"initial language dict error: {err}")

    return language_dict

print(create_language_dict())
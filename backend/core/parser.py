#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/17 下午11:03 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : parser.py
# @desc : README.md

import os
from tree_sitter import Language, Parser


class CodeTree:

    _BUILT = False
    # _LANGUAGES = {
    #     "java": ("java", "java"),
    #     "python": ("python", "python"),
    #     "cpp": ("cpp", "cpp"),
    #     "c_sharp": ("c_sharp", "c_sharp"),
    #     "javascript": ("javascript", "javascript")
    # }

    _LANGUAGES = [i.lstrip('tree-sitter-').replace("-", "_") for i in os.listdir("./backend/core/vendor")]

    def __init__(self):
        if not CodeTree._BUILT:
            self.build_language_library()
            # 初始化类属性
            for item in CodeTree._LANGUAGES:
                setattr(CodeTree, f"{item}_LANGUAGE",
                        Language('./backend/core/build/my-languages.so', item))

            # 构建统一的映射表
            CodeTree.name_mapping_table = {
                item: getattr(CodeTree, f"{item}_LANGUAGE")
                for item in CodeTree._LANGUAGES
            }

            CodeTree._BUILT = True

        # 实例属性引用类属性
        self.name_mapping_table = CodeTree.name_mapping_table
        for item in CodeTree._LANGUAGES:
            setattr(self, f"{item}_LANGUAGE", getattr(CodeTree, f"{item}_LANGUAGE"))


    def build_language_library(self):
        """
        构建语言库， 动态生成语言映射表
        :return:
        """

        Language.build_library(
            './backend/core/build/my-languages.so',
            [
                f'./backend/core/vendor/tree-sitter-{item.replace("_", "-")}' for item in CodeTree._LANGUAGES
            ]
        )

    def processing_coed(self, code_type: str, code: str):

        if code_type not in self.name_mapping_table:
            raise ValueError(f"Unsupported language: {code_type}")

        # 获取对应的语言逻辑方法
        language = self.name_mapping_table[code_type]
        # 初始化
        code_parse = Parser()
        # 指定方法类型
        code_parse.set_language(language)
        # 填入需要分析的源代码，按照utf-8编码转为字节码
        tree = code_parse.parse(bytes(code, "utf-8"))

        # 获取根节点
        # root_node = tree.root_node
        # 定位代码token
        tokens_index = self.tree_to_token_index(tree.root_node)

        # 获取对应代码划分
        code_loc = code.split("\n")
        # code_tokens = [self.index_to_code_token(x, code_loc) for x in tokens_index]
        return [self.index_to_code_token(x, code_loc) for x in tokens_index]

    def tree_to_token_index(self, root_node) -> [((int, int), (int, int))]:
        """
        提取非注释代码token的起止位置

        :return list[tuple[tuple[int,int], tuple[int, int]]]
        """

        if 'comment' in root_node.type:
            return []

        if not root_node.children or 'string' in root_node.type:
            return [(root_node.start_point, root_node.end_point)]

        tokens = []
        for child in root_node.children:
            tokens.extend(self.tree_to_token_index(child))
        return tokens

    def index_to_code_token(self, index, code_lines):
        """
        根据位置元组提取代码文本

        :param index:   (start_point, end_point)位置元组
        :param code_lines:    按行分割的代码列表
        :return:        对应代码文本
        """

        (start_line, start_col), (end_line, end_col) = index

        if start_line == end_line:
            return code_lines[start_line][start_col:end_col]

        lines = [
            code_lines[start_line][start_col:],
            *code_lines[start_line + 1:end_line],
            code_lines[end_line][:end_col]
        ]

        return "\n".join(lines)


if __name__ == '__main__':
    demo = CodeTree()
    code = """
def fun():
    print("This is text string!")

for i in range(10):
    fun()
"""
    code_tokens = demo.processing_coed("python", code)
    print(code_tokens)

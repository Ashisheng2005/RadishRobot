#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/17 下午11:04 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : analyzer.py
# @desc : README.md

import lizard


class Analyzer:

    def __init__(self):
        ...

    def data_clean(self, data) -> dict:
        file_ = {}
        fun_ = []
        data = data.__dict__
        for key in data.keys():
            if key == "function_list":
                _fun = {}
                for fun in data[key]:
                    _fun["cyclomatic_complexity"] = fun.cyclomatic_complexity
                    _fun["nloc"] = fun.nloc
                    _fun["token_count"] = fun.token_count
                    _fun["name"] = fun.name
                    _fun["long_name"] = fun.long_name
                    _fun["start_line"] = fun.start_line
                    _fun["end_line"] = fun.end_line
                    _fun["full_parameters"] = fun.full_parameters
                    _fun["filename"] = fun.filename
                    _fun["top_nesting_level"] = fun.top_nesting_level
                    _fun["fan_in"] = fun.fan_in
                    _fun["fan_out"] = fun.fan_out
                    _fun["general_fan_out"] = fun.general_fan_out
                    _fun["max_nesting_depth"] = fun.max_nesting_depth
                fun_.append(_fun)
            else:
                file_[f"{key}"] = data[key]

        file_["function_list"] = fun_

        return file_

    def analyze_file(self, path:str):
        data = lizard.analyze_file(path)
        return self.data_clean(data)

    def analyze_source_code(self, code_type: str, code: str) -> dict:
        data = lizard.analyze_file.analyze_source_code(code_type, code)
        return self.data_clean(data)


if __name__ == '__main__':
    demo = Analyzer()
    # data = demo.analyze_file("./parser.py")
    data = demo.analyze_source_code(".py", "print('Hello World!')")

    # print(data)
    for key in data.keys():
        print(key, data[key])


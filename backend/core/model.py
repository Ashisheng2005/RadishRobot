#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/17 下午11:04 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : model.py
# @desc : README.md
import logging

# 日志函数
from backend.core.logger import setup_logger, Config
from json import loads, JSONDecodeError
from typing import Dict, Any, Optional
import re

import requests
from openai import OpenAI
from ollama import chat, ChatResponse

user_config = Config(r".\config.yaml")
# user_config = Config("./config.yaml")
logger = setup_logger(user_config)

model_name = user_config.get_nested('model_set', "MODEL_NAME")
pattern = user_config.get_nested('model_set', "PATTERN")
polling = bool(eval(user_config.get_nested("model_set", "POLLING", default=True)))
max_retries = user_config.get_nested("model_set", "MAX_RETRIES", default=3)


def create_prompt(message: str) -> str:
    """
    提示词初始化

    :param message: 用户提问
    :return: 合成后的提示词
    """

    prompt = """你是一个代码分析助手，必须返回一个严格的JSON对象，包含以下字段：
- "issues": 字符串，列出代码问题，每项以">"开头，换行分隔，例如 ">性能问题: ... >逻辑问题: ..."
- "optimized_code": 字符串，包含优化后的代码，确保代码中的换行符和引号正确转义
- "documentation": 字符串，包含代码说明
返回结果必须是单个JSON对象，不包含列表包裹、代码块标记（如```json）或其他无关文本。所有转义字符以字符串的方式返回防止json解析失败，示例：
{"issues": ">性能问题: 未优化循环 >逻辑问题: 未处理边界条件","optimized_code": "def example():\\\\n    pass","documentation": "优化了循环结构"}
用户消息："""

    return prompt + message


def create_polling_prompt(message: str) -> str:
    """
    轮询的提示词合成，

    :param message: 轮询提示
    :return: 合成后的提示词
    """

    promppt = """返回的JSON格式不正确，请修复为单个JSON对象，包含以下字段：
- "issues": 字符串，列出代码问题，每项以">"开头，换行分隔
- "optimized_code": 字符串，包含优化后的代码，确保换行符和引号正确转义
- "documentation": 字符串，包含代码说明
不要包含列表包裹、代码块标记或其他无关文本。示例：
{"issues": ">性能问题: 未优化循环 >逻辑问题: 未处理边界条件","optimized_code": "def example():\\n    pass","documentation": "优化了循环结构"}
错误数据："""

    return promppt + message


def send_message(message: str, join: bool = True, clean_data: bool = True) -> dict:

    if pattern == "cloud":

        # 初始化OpenAI客户端
        client = OpenAI(
            api_key=user_config.get_nested(model_name, 'API_KEY', default=''),
            base_url=user_config.get_nested(model_name, 'BASE_URL', default='')
        )

        return get_general_api_response(client, model_name, message, join, clean_data)

    elif pattern == "local":
        logger.info(f"本地ollama回复")

        return ollama_server(model_name=model_name, message=message, join=join, clean_data=clean_data)

    else:
        return return_template(state=500, message="配置文件错误，请假查配置选项")


def ollama_server(model_name: str, message: str, join: bool = True, clean_data: bool = True) -> Dict[str, Any]:
    """
    调用ollama接口， 但前提是ollama开启且正在运行所需的模型

    :param clean_data:
    :param join: 是否拼接prompt
    :param model_name: 调用的模型名称
    :param message: 用户消息
    :return: dict(state: int, message: str)
    """

    # 预创建prompt避免重复构建
    if join:
        prompt = create_prompt(message)
        prompts = create_polling_prompt(message)

    else:
        prompt = message
        prompts = message

    # 多次轮询
    for attempt in range(1, max_retries + 1):
        logger.info(f"轮询 {attempt}: >>>")

        try:
            # 非流式输出
            response: ChatResponse = chat(model=model_name, messages=[
                {
                    "role": "user",
                    "content": prompt if attempt == 1 or not join else prompts
                },
            ])

            reply = response['message']['content'].strip()
            if reply == "" or reply is None:
                logger.info("API 返回内容为空")
                if attempt == max_retries:
                    return return_template(state=False, message="服务请求不可用，请检查ollama服务是否启动，请稍后再试")

                continue

            logger.info(f"API 返回内容: {reply}")

            if not clean_data:
                return return_template(200, reply)

            # 清理代码块标记
            clean_reply = clean_json_response(reply)

            # 处理可能的列表包裹
            # if reply.startswith("[{") and reply.endswith("}]"):
            #     reply = reply[1:-1].strip()

            # return return_template(state=200, message=reply)
            # 编码转化，防止出现编码错误
            # reply = str(reply.encode("utf-8").decode("utf-8"))

            # 转义字符的处理
            # reply = reply.replace("\\", "\\\\")
            # reply = reply.replace(r'"""', r'\\"\\"\\"')
            # reply = reply.replace('"issues"', '\n"issues"')

            logger.info(f"API 返回内容处理结果: {clean_reply}")

            # 尝试直接解析JSON
            try:
                reply_json = loads(clean_reply)
                return return_template(state=200, message=reply_json)

            except JSONDecodeError as err:
                logger.warning(f"JSON解析失败: reply: [{reply}] [error： {err}]")

                # 最终尝试时使用宽松解析
                if attempt == max_retries:
                    return extract_fallback_json(clean_reply)

                # # 定义正则表达式
                # patterns = {
                #     'issues': r'"issues":\s*"([^"\\]*(?:\\.[^"\\]*)*)",',
                #     'optimized_code': r'"optimized_code":\s*"([^"\\]*(?:\\.[^"\\]*)*)",',
                #     'documentation': r'"documentation":\s*"([^"\\]*(?:\\.[^"\\]*)*)"(?=",|$)'
                # }
                #
                # try:
                #     message_ = {
                #         "issues": re.search(patterns["issues"], reply, re.DOTALL).group(0),
                #         "optimized_code": re.search(patterns["optimized_code"], reply, re.DOTALL).group(0),
                #         "documentation": re.search(patterns["documentation"], reply, re.DOTALL).group(0)
                #     }
                #
                #     return return_template(state=200, message=message_)
                #
                # except AttributeError as err:
                #     logger.info(f"JSON解析失败: reply: [{reply}] [error: {err}]")
                #
                #     if attempt == max_retries:
                #         return return_template(state=500, message=reply)
                #
                #     else:
                #         continue

        except Exception as err:
            logger.error(f"请求异常: {err}")
            if attempt == max_retries:
                return return_template(state=500, message=f"服务请求失败: {str(err)}")


def clean_json_response(raw: str) -> str:
    """
    清理JSON响应中的代码块标记

    :param raw: 需要处理的字符对象
    :return: 字典对象
    """

    # 移除代码块标记
    if raw.startswith("```json") and raw.endswith("```"):
        return raw[7:-3].strip()
    if raw.startswith("```") and raw.endswith("```"):
        return raw[3:-3].strip()
    return raw


def extract_fallback_json(content: str) -> Dict[str, Any]:
    """
    最终回退的JSON提取方法

    :param content: 需要解析的字符串
    :return: 字典对象
    """

    try:
        # 尝试宽松解析
        return return_template(200, loads(content))

    except JSONDecodeError:
        # 提取核心字段
        patterns = {
            'issues': r'"issues"\s*:\s*"(.*?)(?<!\\)"',
            'optimized_code': r'"optimized_code"\s*:\s*"(.*?)(?<!\\)"',
            'documentation': r'"documentation"\s*:\s*"(.*?)(?<!\\)"'
        }

        result = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # 处理转义字符
                result[key] = match.group(1).replace('\\"', '"')

        if result:
            return return_template(state=200, message=result)

    return return_template(state=500, message=content)


def return_template(state: int = None,  message: str or dict = None) -> Dict:
    """
    请求返回的模板，通过参数构造dict对象
    :param state: 状态，True：请求成功， False： 异常
    :param message: 返回内容
    :return: 一个dict对象
    """

    temp = {
        "state": state,
        "message": message
    }
    return temp


def get_general_api_response(client, model_name, message: str, join: bool = True, clean_data: bool = True) -> Dict:
    """
        调用deepseek的API，并获取返回内容

        :param clean_data:
        :param join:
        :param model_name:
        :param client:
        :param message : [str] 用户的消息或系统提示词
        :return: 返回一个dict对象
        """

    try:

        logger.info(f"get {model_name} response: [message: {message}]")
        messages_to_send = []
        messages_to_send.append({"role": "user", "content": create_prompt(message) if join else message})

        # 回复最大token
        MAX_TOKEN = user_config.get_nested(model_name, "MAX_TOKEN", default=2000)
        # 模型选择
        MODEL = user_config.get_nested(model_name, "MODEL", default="deepseek-reasoner")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages_to_send,
            # temperature=TEMPERATURE,
            max_tokens=MAX_TOKEN,
            stream=False
        )

        if not response.choices:
            logger.info("API 返回内容为空")
            return return_template(state=False, message="服务请求不可用，请稍后再试")

        reply = response.choices[0].message.content.strip()

        logger.info(f"API 返回内容: {reply}")

        if not clean_data:
            return reply

        reply = clean_json_response(reply)
        logger.info("reply 前后缀清理成功")

        try:
            reply_json = loads(reply)
            return return_template(state=200, message=reply_json)

        except ValueError as err:
            logger.info(f"JSON解析失败: reply: [{reply}] [error： {err}]")

            return extract_fallback_json(reply)

    except Exception as e:
        error_information = str(e)
        logger.error(f"API 调用失败 : {str(e)}", exc_info=True)

        if "real name verification" in error_information:
            logger.error("错误：API 服务商反馈请完成实名认证后再使用！")

        elif "rate" in error_information:
            logger.error("错误：API 服务商反馈当前访问 API 服务频次达到上限，请稍后再试！")

        elif "paid" in error_information:
            logger.error("错误：API 服务商反馈您正在使用付费模型，请先充值再使用或使用免费额度模型！")

        elif "Api key is invalid" in error_information:
            logger.error("错误：API 服务商反馈 API KEY 不可用，请检查配置选项！")

        elif "busy" in error_information:
            logger.error("错误：API 服务商反馈服务器繁忙，请稍后再试！")

        else:
            logger.error("错误：" + str(e))

        return return_template(state=500, message="服务请求不可用，请稍后再试")


def get_deepseek_response(client, model_name, message: str) -> Dict:
    """
    调用deepseek的API，并获取返回内容

    :param model_name:
    :param client:
    :param message : [str] 用户的消息或系统提示词
    :return: 返回一个dict对象
    """

    try:

        logger.info(f"get deepseek response: [message: {message}]")
        messages_to_send = []
        # messages_to_send.append({"role": "system", "content": "你将扮演我的工作助理，请按照指示回答，不要有多余语句"})
        messages_to_send.append({"role": "user", "content": create_prompt(message)})

        # 回复最大token
        MAX_TOKEN = user_config.get_nested(model_name, "MAX_TOKEN", default=2000)
        # 模型选择
        MODEL = user_config.get_nested(model_name, "MODEL", default="deepseek-reasoner")
        # 回复热度
        TEMPERATURE = user_config.get_nested(model_name, "TEMPERATURE", default=0.1)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages_to_send,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKEN,
            stream=False
        )

        if not response.choices:
            logger.info("API 返回内容为空")
            return return_template(state=False, message="服务请求不可用，请稍后再试")

        reply = response.choices[0].message.content.strip()

        reply = clean_json_response(reply)
        logger.info("reply 前后缀清理成功")

        logger.info(f"API 返回内容: {reply}")
        # return return_template(state=200, message=reply)

        try:
            reply_json = loads(reply)
            return return_template(state=200, message=reply_json)

        except ValueError as err:
            logger.info(f"json value error: reply: [{reply}] [error： {err}]")
            # 定义正则表达式
            patterns = {
                'issues': r'"issues":\s*".*?",',
                'optimized_code': r'"optimized_code":\s*".*?",',
                # 可能会用为用户设置的最大token长度限制返回内容中断，从而引发的格式错误
                'documentation': r'"documentation":\s*".*?"(?=",|$)'
            }
            message_ = {
                "issues": re.search(patterns["issues"], reply, re.DOTALL).group(0),
                "optimized_code": re.search(patterns["optimized_code"], reply, re.DOTALL).group(0),
                "documentation": re.search(patterns["documentation"], reply, re.DOTALL).group(0)
            }

            return return_template(state=200, message=message_)

    except Exception as e:
        error_information = str(e)
        logger.error(f"API 调用失败 : {str(e)}", exc_info=True)

        if "real name verification" in error_information:
            logger.error("错误：API 服务商反馈请完成实名认证后再使用！")

        elif "rate" in error_information:
            logger.error("错误：API 服务商反馈当前访问 API 服务频次达到上限，请稍后再试！")

        elif "paid" in error_information:
            logger.error("错误：API 服务商反馈您正在使用付费模型，请先充值再使用或使用免费额度模型！")

        elif "Api key is invalid" in error_information:
            logger.error("错误：API 服务商反馈 API KEY 不可用，请检查配置选项！")

        elif "busy" in error_information:
            logger.error("错误：API 服务商反馈服务器繁忙，请稍后再试！")

        else:
            logger.error("错误：" + str(e))

        return return_template(state=500, message="服务请求不可用，请稍后再试")


def get_siliconflow_response(client, model_name, message: str) -> Dict:
    """
    调用硅基流动平台的API

    :param client:
    :param model_name:
    :param message:
    :return:
    """
    try:

        logger.info(f"get siliconflow response: [message: {message}]")
        messages_to_send = []
        # messages_to_send.append({"role": "system", "content": "你将扮演我的工作助理，请按照指示回答，不要有多余语句"})
        messages_to_send.append({"role": "user", "content": create_prompt(message)})

        # 回复最大token
        MAX_TOKEN = user_config.get_nested(model_name, "MAX_TOKEN", default=2000)
        # 模型选择
        MODEL = user_config.get_nested(model_name, "MODEL", default="deepseek-reasoner")
        # 回复热度
        TEMPERATURE = user_config.get_nested(model_name, "TEMPERATURE", default=0.1)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages_to_send,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKEN,
            stream=False
        )

        if not response.choices:
            logger.info("API 返回内容为空")
            return return_template(state=False, message="服务请求不可用，请稍后再试")

        reply = response.choices[0].message.content.strip()

        reply = clean_json_response(reply)
        logger.info("reply 前后缀清理成功")

        logger.info(f"API 返回内容: {reply}")
        # return return_template(state=200, message=reply)

        try:
            reply_json = loads(reply)
            return return_template(state=200, message=reply_json)

        except ValueError as err:
            logger.info(f"json value error: reply: [{reply}] [error： {err}]")
            # 定义正则表达式
            patterns = {
                'issues': r'"issues":\s*".*?",',
                'optimized_code': r'"optimized_code":\s*".*?",',
                # 可能会用为用户设置的最大token长度限制返回内容中断，从而引发的格式错误
                'documentation': r'"documentation":\s*".*?"(?=",|$)'
            }
            message_ = {
                "issues": re.search(patterns["issues"], reply, re.DOTALL).group(0),
                "optimized_code": re.search(patterns["optimized_code"], reply, re.DOTALL).group(0),
                "documentation": re.search(patterns["documentation"], reply, re.DOTALL).group(0)
            }

            return return_template(state=200, message=message_)

    except Exception as e:
        error_information = str(e)
        logger.error(f"API 调用失败 : {str(e)}", exc_info=True)

        if "real name verification" in error_information:
            logger.error("错误：API 服务商反馈请完成实名认证后再使用！")

        elif "rate" in error_information:
            logger.error("错误：API 服务商反馈当前访问 API 服务频次达到上限，请稍后再试！")

        elif "paid" in error_information:
            logger.error("错误：API 服务商反馈您正在使用付费模型，请先充值再使用或使用免费额度模型！")

        elif "Api key is invalid" in error_information:
            logger.error("错误：API 服务商反馈 API KEY 不可用，请检查配置选项！")

        elif "busy" in error_information:
            logger.error("错误：API 服务商反馈服务器繁忙，请稍后再试！")

        else:
            logger.error("错误：" + str(e))

        return return_template(state=500, message=str(e))




if __name__ == '__main__':
    reply = send_message("这是一个测试，通讯正常则回复’测试成功‘")
    print(reply)


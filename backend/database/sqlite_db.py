#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/5/31 下午4:05 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : sqlite_db.py
# @desc : README.md


import sqlite3
from datetime import datetime
from json import dumps, loads
from backend.core.logger import Config, setup_logger


config = Config("./config.yaml")
logger = setup_logger(config)
DB_PATH = "./backend/database/review_history.db"


def delete_review(data_id: int):
    """
    根据行标删除数据，并且自动恢复有序行标

    :param data_id: 需要删除的行标
    :return: 一个状态码？
    """

    conn = None

    try:
        conn = sqlite3.connect("./backend/database/review_history.db")
        c = conn.cursor()
        # 删除
        c.execute(f"""delete from reviews where id=?""", (data_id,))

        # 指向数据不存在
        if c.rowcount == 0:
            logger.info(f"未找到ID:{data_id} 的数据")
            return False

        # 恢复有序
        c.execute(f"""update reviews set id=id-1 where id > ?""", (data_id,))

        # 提交业务
        conn.commit()
        return True

    except Exception as err:
        logger.info(f"记录删除失败 {err}")
        return False

    finally:
        if conn:
            conn.close()


def save_review(results: dict):
    """
    保存代码审查结果到数据库。


    :param results: 包含以下参数
        code:            原始代码字符串
        issues:          审查发现的问题
        optimized_code:  优化后的代码字符串
        documentation:   相关文档说明
        github_url:      GitHub 仓库 URL（可选）
        branch:          分支名称（可选，默认为 main）
    :return:                None
    """

    conn = None

    try:
        conn = sqlite3.connect("./backend/database/review_history.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                file TEXT,
                language TEXT,
                code TEXT,
                issues TEXT,
                optimized_code TEXT,
                documentation TEXT,
                complexity TEXT,
                timestamp TEXT,
                github_url TEXT,
                branch TEXT,
                map TEXT
            )
        """)

        # 使用ISO格式存储时间
        timestamp = str(datetime.now().isoformat())

        # complexity 是一个字典，需要将他转为字符
        try:
            complexity = dumps(results.get("complexity", ""))

        except Exception as err:
            complexity = ""
            logger.info(f"complexity 转换json失败")

        try:
            map = dumps(results.get("map", ""))

        except Exception as err:
            map = ""
            logger.info(f"map 转换json失败")


        # logger.info(f"issues: {issues}")
        # issues_json = dumps(issues, ensure_ascii=False)

        c.execute("""
            INSERT INTO reviews (file, language, code, issues, optimized_code, documentation, complexity, timestamp, github_url, branch, map)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (results.get("file", ""), results.get("language", ""),
              results.get("code", ""), results.get("issues", ""),
              results.get("optimized_code", ""), results.get("documentation", ""),
              complexity, timestamp,
              results.get("github_url", ""), results.get("branch", ""), map
              )
                  )

        conn.commit()
        logger.info("记录保存成功")

    except Exception as e:
        logger.error(f"记录保存失败: {str(e)}")

    finally:
        if conn:
            conn.close()


def save_map(results: dict):
    """
    保存已经处理的节点， 暂时使用，可能合并两个保存函数
    :param results:
    :return:
    """

    conn = None
    try:
        conn = sqlite3.connect("./backend/database/review_history.db")
        c = conn.cursor()
        c.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY,
                    file TEXT,
                    language TEXT,
                    code TEXT,
                    issues TEXT,
                    optimized_code TEXT,
                    documentation TEXT,
                    complexity TEXT,
                    timestamp TEXT,
                    github_url TEXT,
                    branch TEXT,
                    map TEXT
                )
            """)

        # 使用ISO格式存储时间
        timestamp = str(datetime.now().isoformat())
        map = ""
        # complexity 是一个字典，需要将他转为字符
        try:
            complexity = dumps(results.get("complexity", ""))

        except Exception as err:
            complexity = ""
            logger.info(f"complexity 转换json失败")

        try:
            map = dumps(results.get("map", ""))

        except Exception as err:
            logger.info(f"map 转换json失败")

        # logger.info(f"issues: {issues}")
        # issues_json = dumps(issues, ensure_ascii=False)

        c.execute("""
                INSERT INTO reviews (file, language, code, issues, optimized_code, documentation, complexity, timestamp, github_url, branch, map)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (results.get("file", ""), results.get("language", ""),
                  results.get("code", ""), results.get("issues", ""),
                  results.get("optimized_code", ""), results.get("documentation", ""),
                  complexity, timestamp,
                  results.get("github_url", ""), results.get("branch", ""), map
                  )
            )

        conn.commit()
        logger.info("记录保存成功")

    except Exception as e:
        logger.error(f"记录保存失败: {str(e)}")

    finally:
        if conn:
            conn.close()


def get_reviews():
    """
    从数据库获取所有代码审查和流程图的历史记录。
    :return: 包含历史记录的列表，格式为 [
        {
            "id": str,
            "file": str,
            "timestamp": str,
            "code": str,
            "results": [
                "language": str,
                "issues": str,
                "optimized_code": str,
                "documentation":str,
                "complexity": str,
            ]
            "github_url": str,
            "branch": str,
            "map": json,
        }, ...
    ]
    """

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # 启用行工厂
            cursor = conn.cursor()
            cursor.execute("SELECT id, file, language, code, issues, optimized_code, documentation, complexity, timestamp, github_url, branch, map FROM reviews")

            history = []
            for row in cursor.fetchall():
                history.append({
                    "id": str(row["id"]),
                    "file": row["file"] or "unknown",
                    "timestamp": row["timestamp"],
                    "code": row["code"],
                    # "results": row["issues"],  # issues 映射到 results
                    "results": [{
                        # "file": row["file"] or "unknown",
                        "language": row["language"] or "",
                        "issues": row["issues"] or "",
                        "optimized_code": row["optimized_code"] or "",
                        "documentation": row["documentation"] or "",
                        "complexity": loads(row["complexity"]) if row["complexity"] else {}
                    }],
                    "github_url": row["github_url"] or "",
                    "branch": row["branch"] or "main",
                    "map": loads(row["map"]) if row["map"] else {}
                })

            logger.info(f"Retrieved {len(history)} review records from database")

            return history

    except sqlite3.Error as e:
        logger.error(f"数据库发生错误: {str(e)}")

    except Exception as e:
        logger.error(f"意料以外的异常: {str(e)}")

    finally:
        if conn:
            conn.close()

    return []

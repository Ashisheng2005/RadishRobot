## 各目录和文件说明

## 文件布局

```
RadishRobot/
├── backend/                     # FastAPI后端
│   ├── api/                     # API路由
│   │   ├── review.py            # 代码审查API
│   │   ├── history.py			# 历史记录API
│   │   └── github.py            # GitHub集成API
│   ├── core/                    # 核心逻辑
|   |   ├── vendor/				# 存放tree-sitter需要用到的数据，通过git clone获取
|   |   ├── build/				# 存放解析代码生成的语法树
|   |   ├── log/			    # 日志文件存储目录
│   │   ├── parser.py            # Tree-sitter解析
│   │   ├── analyzer.py          # Lizard分析
|   |   ├── logger.py			# 日志和系统配置模块				
│   │   └── model.py             # 模型API调用
│   └── database/                # 数据库操作
│       ├── review_history.db	# 启动后生成的数据库文件
│       └── sqlite_db.py         # SQLite逻辑
|
├── frontend/                    # React前端
│   ├── public/                  # 静态资源
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/                     # React源代码
│   │   ├── components/          # React组件
│   │   │   ├── CodeInput.js
│   │   │   ├── GithubInput.js
│   │   │   └── ResultDisplay.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── tailwind.css
│   ├── package.json
│   └── tailwind.config.js
├── tests/                       # 测试代码
│   ├── backend/
│   │   ├── test_review.py
│   │   └── test_parser.py
│   ├── frontend/
│   │   └── test_components.js
│   └── test_data/
│       ├── sample.py
│       └── sample.cpp
├── docs/                        # 文档
│   ├── api.md
│   ├── setup.md
│   └── architecture.md
├── scripts/                     # 辅助脚本
│   ├── setup_db.py
│   └── lint_code.py
├── deploy/                      # 部署配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── vercel.json
|
├── .gitignore
├── README.md
├── main.py                  # FastAPI入口
├── requirements.txt         # Python依赖
├── .env                     # 环境变量
├── config.yaml				# 配置文件

```

**backend/**: 包含FastAPI后端的所有代码，模块化组织API、核心逻辑和数据库操作。

- api/: 定义API端点，如代码审查（/review）和GitHub集成（/github）。
- core/: 实现代码解析（Tree-sitter）、复杂度分析（Lizard）和模型API调用（多模型API）。
- database/: 管理SQLite数据库，存储审查历史。
- main.py: FastAPI应用入口，启动服务器。
- requirements.txt: 列出Python依赖（如fastapi, tree-sitter, lizard）。
- .env: 存储敏感信息（如API密钥、GitHub token）。

**frontend/**: 包含React前端代码，使用Tailwind CSS进行样式设计。

- public/: 静态文件，如主HTML和图标。
- src/: React组件和主应用逻辑，分为代码输入、GitHub URL输入和结果展示。
- package.json: 列出Node.js依赖（如react, tailwindcss）。

**tests/**: 包含单元测试和集成测试，确保代码质量。

- backend/: 测试API端点和解析逻辑。
- frontend/: 测试React组件渲染。
- test_data/: 提供示例Python和C++代码用于测试。

**docs/**: 存放项目文档，便于团队和面试官了解。

- api.md: 描述API端点和参数。
- setup.md: 说明如何安装和运行项目。
- architecture.md: 描述系统架构和数据流。

**scripts/**: 包含辅助脚本，如数据库初始化和代码格式化。

**deploy/**: 包含部署相关配置文件，支持Docker和Vercel。

**.gitignore**: 忽略临时文件（如__pycache__, node_modules, .env）。

**README.md**: 项目概述，包含文件布局说明和快速启动指南。

**LICENSE**: 推荐MIT许可证，便于开源分享。



## 关键文件内容

**backend/main.py**: 初始化FastAPI应用，加载API路由和数据库连接。

**backend/core/parser.py**: 使用Tree-sitter解析Python和C++代码，提取语法树。

**frontend/src/App.js**: 主React组件，协调代码输入和结果展示。

**tests/test_review.py**: 测试审查API，确保正确返回问题列表和优化代码。

**deploy/Dockerfile**: 定义后端和前端的容器化环境。

**README.md**: 详细说明项目目标、文件结构、安装步骤和贡献指南。






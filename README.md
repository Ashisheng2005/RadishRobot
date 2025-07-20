# RaidishRobot

跨语言代码审查与重构工具



![github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)		![python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)     	![](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)		![npm](https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=white)

![vison](https://img.shields.io/badge/RadishRobot-v0.0.1-blue)		![python](https://img.shields.io/badge/python-3.8%2B-blue)		![todo](https://img.shields.io/badge/todo_list-GitHub_Project-blue)		![npm](https://img.shields.io/badge/npm-10.9.2-blue)



## 项目概述

这是一个基于大模型API的Web应用，旨在为开发者提供跨语言（Python、C++等多种语言）代码审查、重构和文档生成服务。用户可上传代码或输入GitHub仓库URL，工具利用多模型 API检测代码问题、优化代码并生成文档，生成函数思维导图，解决中小团队的代码质量和迁移痛点，通过函数导图也能够帮助用户快速上手陌生仓库。

- **目标**: 提供实用、轻量级的代码审查工具，支持跨语言重构和自动化文档生成。
- **技术栈**: FastAPI（后端），React + Tailwind CSS + shadcn-ui（前端），Tree-sitter（代码解析），API（模型推理）。
- **状态**: 测试中（v0.0.1）。



:warning: 项目处于开发初期，请勿置于非安全环境使用以防为您带来不便



## 功能效果

部署且配置成功后可见当前版本网页：

![index](https://github.com/Ashisheng2005/RadishRobot/blob/main/docs/index.png)



### **代码审查**功能示例

我们在这里给出一段一维动规的题解：

```python
def donggui():
    # 一维动态规划
    f = [0 for i in range(n+1)]
    f[1] = mp[0][0]
    for i in range(2, n+1):
        for j in range(i, 0, -1):
            f[j] = max(f[j], f[j-1]) + mp[i-1][j-1]

    ans = max(f)
    return ans

print(donggui())
```

将代码贴入代码框，点击审查代码按钮(本地模型：**qwen2.5:7b**回复)

![](https://github.com/Ashisheng2005/RadishRobot/blob/main/docs/test_local_1.png)

模型给出了两个存在的问题和优化后的代码以及重构总结，测试是基于本地模型**qwen2.5:7b**的回复，如果改为云端API，回复会更完美，但同时也会增加时间损耗。



### **获取Github代码**功能示例

目前的流程只是通过获取项目匹配后缀文件的代码然后贴到代码框中。这种方法存在很多的问题（高token消耗，回复量大导致的格式问题等），后续根据需要会改变功能，

示例：github ： https://github.com/Ashisheng2005/Live2dTK

![](https://github.com/Ashisheng2005/RadishRobot/blob/main/docs/test_local_2.png)



### 思维导图功能

获取github项目代码，通过抽象语法树抽解函数节点，然后进行可视化展现，（**强烈建议本功能使用本地模型，速度非常快，如果是云端API，可能需要等超级久**！！！）

示例: github : https://github.com/Ashisheng2005/CuckooIDE

![](https://github.com/Ashisheng2005/RadishRobot/blob/main/docs/test_local_3.gif)

软乎乎的非常丝滑！！！



### 查看历史记录功能

点击后可以在**右侧抽屉栏**中选择恢复记录，类型**Project**为思维导图，**input**为代码审查



## 文件布局

详见 [文件布局](https://github.com/Ashisheng2005/RadishRobot/blob/main/docs/files.md)



## 快速启动

1. ### 配置环境:
   
   ***python环境要求***： 
   
   开发版本是是3.8，推荐使用3.8或以上版本，但高版本也支持，如果出现因为版本原因的错误欢迎在github上提issues
   
   ​	3.10以下可能会触发BUG: *ERROR:asyncio:Exception in callback ProactorBasePipeTransport.call_connection_lost(None)*，目前已被官方收录GitHub: https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/7524, 日志记录时可以不以理会，后续官方给出解决方法会第一时间修复。
   
   日志记录示例：
   
   ```bash
   2025-06-10 23:27:49,353 - asyncio - ERROR - Exception in callback _ProactorBasePipeTransport._call_connection_lost(None)
   handle: <Handle _ProactorBasePipeTransport._call_connection_lost(None)>
   Traceback (most recent call last):
     File "D:\python\lib\asyncio\events.py", line 81, in _run
       self._context.run(self._callback, *self._args)
     File "D:\python\lib\asyncio\proactor_events.py", line 162, in _call_connection_lost
       self._sock.shutdown(socket.SHUT_RDWR)
   ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。
   ```
   
   
   
   ***库配置***：
   
   ```bash
   pip install -r requirements.txt
   ```
   
   
   
2. #### **安装npm工具**

   **Win:**

   官方网站： https://www.nodejs.com.cn/download.html， 选择对应系统配置后下载安装包安装即可

   

   **Linux:**

   ```bash
   sudo apt update
   sudo apt install nodejs npm
   ```

   

3. #### **编辑配置文件**:

   ```yaml
   model_set:
     MODEL_NAME: "deepseek" # 模型名称，如果是云端API则填写下方对应配置开头，如果是本地则填写模型具体名称
     PATTERN: "cloud"	 	# 模型，cloud 云端， local 本地（默认ollama后端）
     POLLING: "True"		# 因为本地模型较小，可能回答格式有问题，添加一个轮询机制，是否开启
     MAX_RETRIES: 3		# 最大轮询次数
   
   server_set:
     host_ip: "auto"		# ip地址配置，auto表示自动配置，也可以手动强制配置指定ip
     post: 8000			# 这里指定的是后端端口，不推荐修改，因为作者还没有处理到这一部分
     public: "True"		# True表示公开服务，自动网络配置会将服务开放，填写其他表示服务仅本地使用，外部无法访问
   
   # deepseek 官方
   deepseek:
     API_KEY: ""	# deepseek的用户api_key， 再用户中心可获得
     BASE_URL: "https://api.deepseek.com"
     MAX_TOKEN: 50000	# 最大返回token数量，建议设置大一些，否则会截断数据触发错误
     MODEL: "deepseek-reasoner"
   
   # 硅基流动
   siliconflow:
     model: ""
     MAX_TOKEN: 32768	# 免费的Qwen/QwQ-32B模型强制最大token为32768
     API_KEY: ""	# siliconflow的用户api_key， 再用户中心可获得
     BASE_URL: "https://api.siliconflow.cn/v1/"
     
   
   github_set:
     token: ""	# 如果需要处理github项目，则需要用户添加github的token
   
   
   logging:
     level: "INFO"
     file: "./logs/app.log"	# 日志位置
   
   ```




​	自定义云端api, 前提是兼容openAI的交互格式：

```yaml
api_name:
	model: ""	# 模型名称
	MAX_TOKEN:	# 最大token，不同的平台可能会有不同的限制要求
	API_KEY:	# api的key
	BASE_URL:	# 基本的url， 会自动拼接末尾的 chat/completions，请注意填写格式
```

​	

我们以deepseek为例：

```yaml
deepseek:
  API_KEY: ""	# deepseek的用户api_key， 再用户中心可获得
  BASE_URL: "https://api.deepseek.com"
  MAX_TOKEN: 50000	# 最大返回token数量，建议设置大一些，否则会截断数据触发错误
  MODEL: "deepseek-reasoner"
```



构建的完整请求url为 https://api.deepseek.com/chat/completions ， 官方为了符合openai的标准，实际的请求url也可以为 https://api.deepseek.com/v1/chat/completions

**`deepseek-chat` 模型指向 DeepSeek-V3-0324，** 通过指定 `model='deepseek-chat'` 调用。

**`deepseek-reasoner` 模型指向 DeepSeek-R1-0528，** 通过指定 `model='deepseek-reasoner'` 调用。

自定义完成后直接修改MODEL_NAME参数即可



1. **后端启动**：

   

   ```bash
   python main.py
   ```

   

   自动网络配置服务会扫描本地可用ip，当然也包括虚拟网卡的ip，如果出现多个ip，会让用户选择合适的ip， 例如：

   ```bash
   Multiple ips have been detected. Please select a suitable one:
   
   1: 10.16.0.1
   2: 192.168.111.1
   3: 192.168.0.106
   >>> 3
   ```

   选择一个填写**冒号前的 id** 回车即可。

   

   启动后回显如下：

   ```bash
   2025-07-14 23:12:05,778 - backend.core.logger - INFO - FastAPI 服务启动成功
   2025-07-14 23:12:05,780 - backend.core.logger - INFO - 自动ip配置成功，ip: 192.168.0.106, post: 8000
   INFO:     Started server process [26412]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```

   

   访问 http://127.0.0.1:8000/  或者 **自己指定的ip+8000** 端口会显示：

   ```json
   {"message":"欢迎来到RadishRobot!","endpoints":{"/health":"Check API status","/github/fetch":"Fetch code from GitHub repository","/review":"Review and refactor code"},"docs":"/docs"}
   ```

   显示如上则表示启动成功

   

2. **前端启动**:

   

   ```bash
   cd rr_frontend
   npm run dev
   ```

   回显如下：

   ```bash
   > rr_frontend@0.0.0 dev
   > vite
   
   
     VITE v6.3.5  ready in 4262 ms
   
     ➜  Local:   http://localhost:5173/	# 这里可能会出现多个ip，选择配置的ip访问
     ➜  Network: use --host to expose
     ➜  press h + enter to show help
   ```

   访问 http://localhost:5173/ 显示

   ![](https://github.com/Ashisheng2005/RadishRobot/blob/main/docs/index.png)

   

3. **添加更多语言**

   项目中对于代码审计是基于 Python Tree-sitter(github：https://github.com/tree-sitter/py-tree-sitter)， 而完整的语言包没法上传，所以需要自己下载，这里给出五种语言的下载命令

   

   **切换到vendor目录下**

   ```bash
   cd ./RadishRobot/backend/core/vendor
   ```

   **Python**

   ```bash
   git clone https://github.com/tree-sitter/tree-sitter-python
   ```

   **C++**

   ```bash
   git clone https://github.com/tree-sitter/tree-sitter-cpp
   ```

   **Java**

   ```bash
   git clone https://github.com/tree-sitter/tree-sitter-java
   ```

   **C#**

   ```bash
   git clone https://github.com/tree-sitter/tree-sitter-c-sharp
   ```

   **Javascript**

   ```bash
   git clone https://github.com/tree-sitter/tree-sitter-javascript
   ```

   

   安装完成后可见于 RadishRobot\backend\core\vendor 目录下：

   ```bash
    tree-sitter-c-sharp
    tree-sitter-cpp
    tree-sitter-java
    tree-sitter-javascript
    tree-sitter-python
   ```

   

   当这五种语言完全不足以满足用户需求的时候，用户可以自己下载更多的语言库，在官网(https://github.com/tree-sitter/tree-sitter/wiki/List-of-parsers) 中可以查找想要的语言，复制对应的**链接**，在**RadishRobot\backend\core\vendor** 目录下执行

   ```bash
   git clone https://github.com/xxxxxxxxx/tree-sitter-XXXXXXXXXXX
   ```

   安装后重启后端即可。

   

   

4. #### **修改默认端口**

   1. 开发模式中修改配置文件 ".\RadishRobot\rr_frontend\node_modules\vite\dist\node\constants.js" 末尾处配置项：

      除非专业人员否则不建议改动该文件内容，会导致很多bug

      ```js
      const DEFAULT_DEV_PORT = 5173;		# 开发模式的post
      const DEFAULT_PREVIEW_PORT = 4173;	# 预览模式的post
      ```

   

5. **Linux配置可能存在的问题**

   1. 执行 **npm run dev** 提示 **sh: 1: vite: Permission denied**， 解决方法：

      ```bash
      cd RadishRobot/rr_frontend
      chmod +x node_modules/.bin/vite
      ```

      这是由于文件没有足够的执行权限，提权之后即可

      

   2. 依旧是执行 **npm run dev** 时候提示 **Platform-specific optional dependencies not being included in `package-lock.json` when reinstalling with `node_modules` present**， [https://github.com/npm/cli/issues/4828],依照官方给出的方法需要完全删除 node_modules 文件夹，但这样太麻烦了，我将node_modules文件夹完整上传本身就是为了方便用户搭建，节省环境配置时间，解决方法：

      ```bash
      cd RadishRobot/rr_frontend
      npm install
      ```

      由于项目开发环境为Win，可能会有些文件与Linux环境不匹配，不必删除，直接 install 重置一下即可。

      

   3.  在 Linux 环境下执行 **npm run build** 出现 **sh: 1: tsc: Permission denied** 错误提示

      GitHub收录： https://github.com/npm/cli/issues/3189

      问题是没有权限导致的，如果项目是刚从仓库拉取，则需要连续执行

      ```bash
      cd RadishRobot/rr_frontend
      npm install
      chmod +x node_modules/.bin/vite
      chmod +x node_modules/.bin/tsc		# 否则只需执行这一条即可
      ```

      

   4. ***FileNotFoundError: 配置文件 .\config.yaml 不存在.*** 或者 ***UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd0 in position 17: invalid continuation byte*** 

      检查文件，如果文件存在则是文件编码问题，如果不存在可回到github上恢复一下

      ```bash
      vim config.yaml
      :set fileencoding=utf-8		# 强制转为utf-8编码
      :wq
      ```

      

   5. ***RuntimeError: Failed to import distutils. You may need to install setuptools.*** 这大概是python3.12及以上版本导致的bug，python 3.12 中 distutils 被移除了，但可以使用pip install setuptools 来获得这个包

      ```bash
      pip install setuptools
      ```

      



## Release 版本部署

当前提供release的版本为 Complete 包模式，包含 build 之后的所有内容，方便用户快速部署。

该版本可快速部署非开发环境服务，下载最新的release版本后将文件夹解压，首先创建python环境(推荐虚拟环境)：

```bash
pip install -r requirements.txt
```

按照开发模式中的配置选项修改配置文件后，只需执行：

```bash
python main.py
```

成功运行后访问8000端口即可使用。





## 非Release版本打包部署

如果需要做一些特别的设置（比如修改开放端口等），需要先处于开放模式调试成功之后再打包。



### 参数设置

```yaml
server_set:
  # auto 自动配置（Automatic configuration） ; 或者强制指定（Fixed ip address: XXX.XXX.XXX.XXX）
  host_ip: "auto"
  # 端口
  port: 8000
  # 公开服务 false true
  public: "false"
  # Development、dp、Dp 开发模式； Test、test 测试模式
  mode: "dp"
```

 

host_ip： 设置为auto会自动检测设备ip，如果有多个ip会让给出选择，任选其一。也可以是强制指定IP地址

port：端口，默认是8000，可根据需要自行修改，但是修改完之后需要处于开发模式执行以此覆盖其他附属文件参数。

public：公开服务设置，设置为true之后服务可以被外部访问，但需要再防火墙中对端口提前设置好。

mode：执行模式，可选开发模式/测试模式之一：

​	开发模式：前后分离，可实现实时参数修改，但启动需要两条命令

​	测试模式：前后不分离，需要提前对资源打包，参数不可修改，启动只需要一条命令



### 基本流程

修改各项参数之后执行：

```bash
python main.py
cd rr_frontend
npm run dev
```



测试项目流程闭环（各项功能正常）后，打包

```bash
cd rr_frontend
npm run build
```



打包完成之后，**将打包后的 dist 文件夹内容移动到根目录下的 static 文件夹中**

```bash
cp ./rr_frontend/dist/* ./static
```



移动成功之后，**将配置文件中的执行模式改为test**，执行命令即可

```bash
python main.py
```





## 【流式更新日志】

2025.7.3 

修复了本地轮询后缀表机制的bug

2025.7.14

修复配置文件路径bug

优化部分处理流程和网络配置数据方式

添加网络自动配置功能，添加**仅本地使用**和**开放使用**两种模式

适配Linux平台，支持在Linux平台搭建对外开放服务

2025.7.17

打包推出Release 0.0.1体验版本

分流支持 **开发** 和 **测试 **两种模式

2025.7.19

修复config.yaml 文件编码跨平台异常问题

 添加记录删除功能

修复React框架异步更新机制导致的传参问题

优化整体执行流程

修复大量跨平台部署bug



## 许可证
MIT License


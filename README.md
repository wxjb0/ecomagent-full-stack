# 电商全链路多Agent智能体系统

一个基于Python + LangChain + Streamlit构建的完整电商运营多Agent系统，涵盖市场洞察、选品策略、内容创作、投放优化和售后舆情全流程。

## 功能特性

- 🤖 5个专业Agent协同工作
- 🧠 支持长链推理与记忆共享
- 📊 内置模拟数据，开箱即用
- 🎨 可视化Web界面
- 🔌 支持接入真实大模型(GPT-4, Claude, DeepSeek等)
- 🗄️ 数据库支持(SQLite/MySQL/PostgreSQL)
- 🚀 RESTful API接口

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入你的API Key
```

### 3. 运行可视化界面

```bash
streamlit run app.py
```

### 4. 运行API服务

```bash
python run_api.py
```

### 5. 命令行运行

```bash
python main.py
```

## 项目架构

```
ecommerce_multi_agent_pro/
├── config/          # 配置管理
├── core/            # 核心Agent实现
├── data/            # 数据层
├── api/             # API接口
├── utils/           # 工具函数
└── app.py           # 可视化界面
```

## 扩展开发

详见文档中的扩展开发指南。

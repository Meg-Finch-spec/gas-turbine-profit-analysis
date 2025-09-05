# 燃气轮机利润分析系统

这是一个使用Streamlit开发的燃气轮机利润分析系统，可以帮助用户分析燃气轮机的运行成本和利润情况。

## 功能特点

- 支持多币种和数量级选择（元、百万元、美元、百万美元）
- 实时维护项目添加和删除功能
- 自动货币转换和统一单位计算
- 详细的成本和利润分析报告

## 部署指南

要将此应用部署到Streamlit Community Cloud，您需要将代码推送到GitHub仓库，然后从Streamlit Community Cloud连接到该仓库。

### 步骤1：安装Git

如果您的系统中没有安装Git，请先下载并安装：https://git-scm.com/downloads

### 步骤2：初始化Git仓库并推送到GitHub

打开命令行工具，导航到项目目录，然后执行以下命令：

```bash
# 初始化Git仓库
git init

# 添加远程仓库
git remote add origin https://github.com/Meg-Finch-spec/gas-turbine-profit-analysis.git

# 创建.gitignore文件
echo "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n# Environment\n.venv/\n.env\n.env.local\n.env.development.local\n.env.test.local\n.env.production.local\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n*~\n\n# OS\n.DS_Store\nThumbs.db\n\n# Logs\nlogs\n*.log\n\n# Runtime data\npids\n*.pid\n*.seed\n*.pid.lock\n\n# Coverage directory used by tools like istanbul\ncoverage/\n*.lcov\n\n# nyc test coverage\n.nyc_output/" > .gitignore

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit"

# 推送到GitHub
git push -u origin master
```

### 步骤3：部署到Streamlit Community Cloud

1. 访问 https://share.streamlit.io/
2. 点击 "New app" 按钮
3. 选择您的GitHub仓库：Meg-Finch-spec/gas-turbine-profit-analysis
4. 选择分支（默认为master）
5. 指定主文件路径：gas_turbine_analysis.py
6. 点击 "Deploy!" 按钮

## 运行本地开发服务器

如果您想在本地运行应用，请执行以下命令：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行Streamlit应用
streamlit run gas_turbine_analysis.py
```
# Capital Scout AI 外联代理

## 概览
本项目提供一个可演示的外联自动化流水线：
- 从 CSV 读取线索
- 生成个性化外联文案（A/B 两个版本 + 两封跟进）
- 产出 Instantly 与 Airtable 的可导入 CSV
- 生成活动计划与日志

## 前提与环境
- Windows 10/11（推荐）或 macOS/Linux
- 已安装 Python 3.11 并加入 PATH
- 可选：OpenAI API Key（放在 `.env` 或 `OPENAI_API_KEY`）
- 仅在真实生成时需要联网

## 从零开始安装
1. 下载项目
   - 方式 A：`git clone https://github.com/calloftheNIGHT2023/Capital-Scout-AI.git`
   - 方式 B：在 GitHub 下载 ZIP 并解压
2. 在项目根目录打开终端
3. 创建并激活虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate
```
4. 安装依赖
```bash
pip install -r requirements.txt
```
5. （可选）配置 OpenAI API Key
   - 在项目根目录创建 `.env`：
```
OPENAI_API_KEY=你的key
```

## 运行（冒烟测试 / 演示模式）
```bash
python run_agent.py --input data/leads.csv --out outputs --campaign "week6-demo" --dry-run
```

## 运行（真实 OpenAI 文案生成）
```bash
python run_agent.py --input data/leads.csv --out outputs --campaign "week6-demo"
```

## 桌面应用
```bash
python app_desktop.py
```

## 打包为 Windows EXE
```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```
输出文件位于 `dist/CapitalScoutAI.exe`。

## 输出文件
- `outputs/leads_clean.csv`
- `outputs/outreach_pack.json`
- `outputs/instantly_import.csv`
- `outputs/airtable_import.csv`
- `outputs/campaign_plan.md`
- `outputs/logs/run.log`

## 输出如何使用
- Instantly：导入 `outputs/instantly_import.csv`，用于 A/B 测试发送
- Airtable：导入 `outputs/airtable_import.csv`，用于跟踪打开/回复等指标

## 截图占位
### Apollo 导出

### OpenAI Prompt + Output

### Instantly 活动界面

### Airtable 表格

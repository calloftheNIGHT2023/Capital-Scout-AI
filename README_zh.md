# Capital Scout AI 外联代理

## 概览
本项目提供一个可演示的外联自动化流水线：
- 从 CSV 读取线索
- 生成个性化外联文案（A/B 两个版本 + 两封跟进）
- 产出 Instantly 与 Airtable 的可导入 CSV
- 生成活动计划与日志

## 环境要求
- Python 3.11
- OpenAI API Key（放在 `.env` 或 `OPENAI_API_KEY` 中；如缺失则输出 `[DEMO COPY]` 占位文案）

## 安装
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行（冒烟测试）
```bash
python run_agent.py --input data/leads.csv --out outputs --campaign "week6-demo" --dry-run
```

## 输出文件
- `outputs/leads_clean.csv`
- `outputs/outreach_pack.json`
- `outputs/instantly_import.csv`
- `outputs/airtable_import.csv`
- `outputs/campaign_plan.md`
- `outputs/logs/run.log`

## 截图占位
### Apollo 导出

### OpenAI Prompt + Output

### Instantly 活动界面

### Airtable 表格

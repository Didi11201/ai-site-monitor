# 🧠 AI Site Monitor

一个基于 **Python + Hugging Face AI 模型** 的自动化网站监测 Agent。  
它会每 12 小时自动检查一批网站，判断是否出现“促销/优惠/折扣”等内容。

---

## 🚀 功能
- 异步爬取上千个网站（高效率）
- AI 自动分析是否包含促销类信息
- 结果保存为 CSV 文件（`results.csv`）
- 自动在 GitHub Actions 上定时运行（每 12 小时）
- 全程免费，无需服务器或 API Key

---

## 📂 文件结构
ai-site-monitor/
├── monitor.py # 主程序：抓取网页并AI分析
├── sites.csv # 网址列表
├── config.yml # 可配置关键词、输出、通知方式
├── requirements.txt # 依赖
└── .github/workflows/monitor.yml # GitHub 自动任务

---

## 🧩 快速上手

1️⃣ **编辑网站列表**
   打开 `sites.csv`，每行一个网址，例如：
https://www.newbalance.com/
https://us.puma.com/
https://chefrubber.com/

2️⃣ **修改配置**
在 `config.yml` 中可以更改：
```yaml
keywords: ["sale", "discount", "promotion", "优惠", "折扣"]
output: results.csv
notify: false
interval_hours: 12
3️⃣ 自动运行
无需手动启动，GitHub Actions 会：

每 12 小时运行一次；

把检测结果写入 results.csv；

自动提交到仓库。

📊 查看结果
打开仓库中的 results.csv 文件，可以看到每次运行的检测结果：

时间	网址	检测结果
2025-10-24 10:00:00	https://us.puma.com/	✅ 有促销
2025-10-24 10:00:00	https://chefrubber.com/	— 未发现促销

🔔 启用通知（可选）
未来你可以开启通知提醒，例如：

Telegram Bot

Email SMTP

Discord Webhook

修改 config.yml：

notify: telegram
然后在仓库 Settings → Secrets and variables → Actions 添加凭证即可。

🧠 模型说明
使用 Hugging Face 的轻量模型：

distilbert-base-uncased-finetuned-sst-2-english
用于文本情感与相关性分析，无需 API Key。

💡 常见问题
Q: 能监控中文网站吗？
A: 可以。AI 模型和关键词列表都支持中文内容。

Q: 每次运行多久？
A: 约 10–30 分钟，取决于网站数量。

Q: 会不会被封？
A: 请求频率低且分布式运行，不会造成异常访问。

🧩 后续扩展（ABC 选项）
A： 加入 Telegram 通知

B： 接入 Google Sheets 输出

C： 加入多模型判断提升准确率

👩‍💻 项目作者：你

✅ 完全开源、免费、自运行的 AI 网站监测 Agent。

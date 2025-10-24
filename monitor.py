import aiohttp
import asyncio
import csv
import re
import time
import yaml
from pathlib import Path
from datetime import datetime
from transformers import pipeline

# ========== 加载配置 ==========
CONFIG_PATH = Path("config.yml")
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
else:
    config = {"keywords": ["sale", "discount", "promotion", "offer", "clearance"],
              "notify": False,
              "output": "results.csv"}

# ========== 读取网站列表 ==========
SITES_PATH = Path("sites.csv")
if not SITES_PATH.exists():
    print("⚠️ 未找到 sites.csv，请先创建该文件。")
    exit()

with open(SITES_PATH, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    sites = [row[0].strip() for row in reader if row]

# ========== 初始化AI模型 ==========
print("🧠 正在加载AI模型（首次加载可能较慢）...")
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# ========== 异步抓取网页 ==========
async def fetch(session, url):
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status == 200:
                text = await resp.text(errors="ignore")
                return url, text
            else:
                return url, f"Error: {resp.status}"
    except Exception as e:
        return url, f"Exception: {str(e)}"

async def crawl_all():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in sites]
        results = await asyncio.gather(*tasks)
        return results

# ========== 关键词 + AI 判断 ==========
def check_promotions(text, keywords):
    text_lower = text.lower()
    if any(k.lower() in text_lower for k in keywords):
        return True

    # 提取网页前1000字符
    snippet = text[:1000]
    prediction = classifier(snippet)[0]
    if prediction["label"] == "POSITIVE" and prediction["score"] > 0.9:
        return True
    return False

# ========== 主程序 ==========
async def main():
    print(f"🚀 开始检测，共 {len(sites)} 个网站...")
    results = await crawl_all()
    detected = []

    for url, content in results:
        if "Error" in content or "Exception" in content:
            status = "❌ 访问失败"
        else:
            has_promo = check_promotions(content, config.get("keywords", []))
            status = "✅ 有促销" if has_promo else "— 未发现促销"
        detected.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, status])
        print(f"{url} → {status}")

    # 写入CSV
    output_path = Path(config.get("output", "results.csv"))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["时间", "网址", "检测结果"])
        writer.writerows(detected)

    print(f"\n📝 结果已写入 {output_path.resolve()}")

if __name__ == "__main__":
    asyncio.run(main())

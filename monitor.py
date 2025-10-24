import aiohttp
import asyncio
import csv
import re
from datetime import datetime
from pathlib import Path
import yaml

# ========== 加载配置 ==========
CONFIG_PATH = Path("config.yml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

KEYWORDS = config.get("keywords", ["sale", "discount", "offer", "促销", "折扣", "优惠", "满减", "特价"])
SITES_PATH = Path("sites.csv")
OUTPUT_CSV = Path("results.csv")
OUTPUT_HTML = Path("results.html")

# ========== 抓取网页（含自动重试） ==========
async def fetch(session, url, retries=1):
    for attempt in range(retries + 1):
        try:
            async with session.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status == 200:
                    text = await resp.text(errors="ignore")
                    return text, None
                else:
                    return None, f"HTTP {resp.status}"
        except asyncio.TimeoutError:
            err = "超时"
        except aiohttp.ClientConnectorError:
            err = "连接错误"
        except Exception as e:
            err = str(e)
        if attempt < retries:
            await asyncio.sleep(2)
    return None, err

# ========== 提取关键词句子 ==========
def extract_promotion_snippet(text):
    snippets = []
    for kw in KEYWORDS:
        pattern = re.compile(r"([^.。!?]*?" + re.escape(kw) + r"[^.。!?]*[。!?])", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            snippets.append(match.group(1).strip())
    return snippets[:2]

# ========== 检查网站 ==========
async def check_site(session, url):
    html, error = await fetch(session, url)
    if not html:
        return (url, f"❌ 访问失败（{error}）", "")
    snippets = extract_promotion_snippet(html)
    if snippets:
        return (url, "✅ 有促销", " / ".join(snippets))
    else:
        return (url, "🚫 无促销", "")

# ========== 生成 HTML 报告 ==========
def save_html(results):
    html = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>AI Site Monitor Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #fafafa; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #333; color: white; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .ok { color: green; font-weight: bold; }
            .fail { color: red; font-weight: bold; }
            .none { color: #999; }
        </style>
    </head>
    <body>
        <h2>🧠 AI Site Monitor 检测结果</h2>
        <table>
            <tr><th>时间</th><th>网址</th><th>检测结果</th><th>促销摘要</th></tr>
    """
    for row in results:
        time, url, status, summary = row
        status_class = (
            "ok" if "✅" in status else "fail" if "❌" in status else "none"
        )
        html += f"<tr><td>{time}</td><td>{url}</td><td class='{status_class}'>{status}</td><td>{summary}</td></tr>\n"
    html += """
        </table>
    </body></html>
    """
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🌐 HTML 报告已生成：{OUTPUT_HTML.resolve()}")

# ========== 主逻辑 ==========
async def main():
    async with aiohttp.ClientSession() as session:
        with open(SITES_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            sites = [row["url"] for row in reader]

        results = []
        for site in sites:
            res = await check_site(session, site)
            results.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *res))

        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["时间", "网址", "检测结果", "促销摘要"])
            writer.writerows(results)

        save_html(results)
        print(f"\n✅ 检测完成，结果已写入：{OUTPUT_CSV.resolve()}")

if __name__ == "__main__":
    asyncio.run(main())

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
OUTPUT_PATH = Path("results.csv")

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
        if attem

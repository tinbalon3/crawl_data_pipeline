import asyncio, re, html, hashlib, sys
from urllib.parse import urljoin, urlparse
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError

HEADLESS      = True          # False → thấy trình duyệt
CONCURRENCY   = 5             # tab song song
BLOCKS        = "p,h1,h2,h3,h4,h5,h6,figcaption"
OUT_DIR       = Path("html_out")
OUT_DIR.mkdir(exist_ok=True)


# ---------- helper ----------
def slugify(url: str) -> str:
    p = urlparse(url)
    part = re.sub(r'[^0-9a-zA-Z]+', '-', p.path)[:50].strip('-')
    h    = hashlib.sha1(url.encode()).hexdigest()[:6]
    return f"{p.netloc}_{part or 'root'}_{h}.html"

def clean(t: str) -> str:
    return html.escape(re.sub(r"\s+", " ", t).strip(), quote=False)

async def auto_scroll(page, step=1000, pause=0.4):
    prev = None
    while True:
        cur = await page.evaluate("document.documentElement.scrollHeight")
        if cur == prev: break
        prev = cur
        await page.evaluate(f"window.scrollBy(0,{step})")
        await asyncio.sleep(pause)


# ---------- crawl one ----------
async def fetch_one(browser, sem, url: str, alt_tag: str):
    async with sem:
        try:
            page = await browser.new_page(user_agent=
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await auto_scroll(page)

            data = await page.evaluate(f"""
            () => {{
              const sel = "{BLOCKS}";
              const blocks = Array.from(document.querySelectorAll(sel))
                .map(el => el.innerText.trim().replace(/\\s+/g,' '))
                .filter(Boolean);
              const imgs = new Set();
              document.querySelectorAll('img').forEach(i=>i.src&&imgs.add(i.src));
              document.querySelectorAll('meta[property="og:image"]')
                .forEach(m=>m.content&&imgs.add(m.content));
              return {{blocks, images:[...imgs]}};
            }}""")
            await page.close()
        except TimeoutError:
            print(f"⏰ Timeout: {url}")
            return
        except Exception as e:
            print(f"⚠️  Error ({url}): {e}")
            return

    # ---- build html ----
    paragraphs = "\n".join(f"<p>{clean(t)}</p>" for t in data["blocks"])
    imgs_html  = "\n".join(
        f'<img src="{html.escape(urljoin(url,src))}" alt="{html.escape(alt_tag)}">\n'
        f'<p><em>{html.escape(alt_tag)}</em></p>'
        for src in data["images"]
    )

    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    full  = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>{html.escape(url)}</title>
<style>
 body{{font-family:Arial,Helvetica,sans-serif;max-width:820px;margin:auto;line-height:1.6}}
 img{{max-width:100%;margin-top:1rem}}
</style></head>
<body><!-- Generated {stamp} -->
{paragraphs}
<hr>
{imgs_html}
</body></html>"""

    out = OUT_DIR / slugify(url)
    out.write_text(full, encoding="utf-8")
    print(f"✅ {url}  →  {out.name}")


# ---------- batch ----------
async def main(file_paths: list[str]):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS, args=["--no-sandbox"])
        sem = asyncio.Semaphore(CONCURRENCY)

        tasks = []
        for fp in file_paths:
            with open(fp, encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            if not lines:
                print(f"⚠️  {fp}: file rỗng.")
                continue
            alt_tag, *urls = lines            # dòng đầu = alt
            tasks += [fetch_one(browser, sem, u, alt_tag) for u in urls]

        await asyncio.gather(*tasks)
        await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Dùng: python batch_crawl_to_html.py <urls1.txt> [urls2.txt ...]")
        sys.exit(1)
    asyncio.run(main(sys.argv[1:]))

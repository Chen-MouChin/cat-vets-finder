"""把貓健康站的 frontend/vets.html 打包成單一 index.html（課程作業交付用）。

做的事：
- css/theme.css、css/nav.css、js/theme.js、data/vets.js 全部內嵌
- 拿掉廣告位、favicon、結構化資料、canonical
- 站內相對連結改成貓健康站的絕對網址，本頁的導覽連結改成 #
- 其餘一字不改，和線上的獸醫院查詢頁是同一份程式

用法：python build_single.py [--src ../cat-health-tw/frontend] [--out index.html]
"""
import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SITE = "https://chen-mouchin.github.io/cat-health-tw/"
HERE = Path(__file__).parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(HERE.parent / "cat-health-tw" / "frontend"))
    ap.add_argument("--out", default=str(HERE / "index.html"))
    args = ap.parse_args()
    src = Path(args.src)
    html = (src / "vets.html").read_text(encoding="utf-8")

    def read(rel):
        return (src / rel).read_text(encoding="utf-8")

    # 1. 樣式與腳本內嵌
    css = read("css/theme.css") + "\n" + read("css/nav.css")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)  # 註解拿掉（裡面有相對路徑的範例字串）
    html = re.sub(r'<link rel="stylesheet" href="css/theme\.css">\s*<link rel="stylesheet" href="css/nav\.css[^"]*">',
                  "<style>\n" + css + "\n</style>", html, count=1)
    html = html.replace('<script src="js/theme.js"></script>', "<script>\n" + read("js/theme.js") + "\n</script>", 1)
    html = html.replace('<script src="data/vets.js"></script>', "<script>\n" + read("data/vets.js").rstrip() + "\n</script>", 1)

    # 2. 拿掉不屬於單檔的東西
    html = re.sub(r'\s*<link rel="(?:icon|apple-touch-icon)"[^>]*>', "", html)
    html = re.sub(r'\s*<meta property="og:image"[^>]*>', "", html)
    html = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", html, flags=re.S)
    html = re.sub(r'\s*<link rel="canonical"[^>]*>', "", html)
    html = re.sub(r'\s*<meta property="og:url"[^>]*>', "", html)
    html = re.sub(r'\s*<aside class="site-ad-(?:banner|anchor)".*?</aside>', "", html, flags=re.S)
    html = html.replace('<script src="js/ads.js"></script>\n', "")

    # 3. 站內連結改絕對網址；本頁自己的連結改 #
    html = html.replace('href="vets.html"', 'href="#"')
    html = re.sub(r'href="((?:index|library|breeds|about|editorial|privacy)\.html(?:#[\w-]+)?|articles/index\.html)"',
                  lambda m: f'href="{SITE}{m.group(1)}"', html)

    # 4. 標題與說明
    html = html.replace("<title>獸醫院查詢 — 貓健康站</title>",
                        "<title>全台動物醫院查詢（單檔版）— 貓健康站</title>", 1)

    leftover = re.findall(r'(?:src|href)="(?!https?:|#|tel:|mailto:|\$\{)[^"]+"', html)
    if leftover:
        print("還有相對路徑沒處理：", sorted(set(leftover)))
        sys.exit(1)

    out = Path(args.out)
    out.write_text(html, encoding="utf-8")
    print(f"→ {out}（{out.stat().st_size / 1024:.0f} KB）")


if __name__ == "__main__":
    main()

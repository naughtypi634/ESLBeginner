"""Scratch tool: report rendered page/section heights for a generated lesson HTML.

Usage: python build/measure_lesson.py "MD/_19-Time Clauses.html"
Prints, per .lesson-section, its height and which page slot it lands in, plus
the height of each table so content can be sized to fill a page exactly.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGE_H = 1122 - 91  # A4 at 96dpi minus 12mm top/bottom margin


def main() -> None:
    html = Path(sys.argv[1]).resolve()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html.read_text(encoding="utf-8"), wait_until="networkidle")
        data = page.evaluate(
            """() => {
                const out = [];
                document.querySelectorAll('.lesson-section').forEach((s, i) => {
                    const h2 = s.querySelector('h2');
                    const tables = [...s.querySelectorAll('table')].map(t => ({
                        head: [...t.querySelectorAll('th')].map(x => x.textContent.trim()).join('|'),
                        rows: t.querySelectorAll('tr').length - 1,
                        h: Math.round(t.getBoundingClientRect().height),
                    }));
                    out.push({
                        i,
                        title: h2 ? h2.textContent.trim() : '?',
                        h: Math.round(s.getBoundingClientRect().height),
                        tables,
                    });
                });
                return out;
            }"""
        )
        browser.close()
    print(f"usable page height ~{PAGE_H}px")
    for s in data:
        print(f"\n[{s['i']}] {s['title']}  height={s['h']}px  fill={s['h']/PAGE_H:.0%} of a page")
        for t in s["tables"]:
            print(f"    table {t['head'][:40]:42s} rows={t['rows']:2d} h={t['h']}px")


if __name__ == "__main__":
    main()

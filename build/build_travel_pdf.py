#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESLBeginner · 旅游英语实用手册 PDF builder (black & white edition)
==================================================================
Sources:
  MD/旅游英语实用手册.docx
  MD/ESL-travel english phrases.pdf   (words -> 单词, sentences -> 句子)
Output:  PDF/旅游英语实用手册.pdf

Pipeline: content (this script) -> markdown w/ raw LaTeX -> pandoc + xelatex
Design:   build/preamble.tex  (print-ready black & white)

Usage:
    python build/build_travel_pdf.py            # build PDF
    python build/build_travel_pdf.py --png      # also render previews
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"F:\AI project\ESLBeginner")
GEN_DIR = ROOT / "build" / "tex"
PDF_DIR = ROOT / "PDF"
PREVIEW = ROOT / "build" / "preview"
PANDOC = r"C:\Users\ZZC\AppData\Local\Pandoc\pandoc.exe"
TEMPLATE = ROOT / "build" / "template.tex"
PREAMBLE = ROOT / "build" / "preamble.tex"
MIKTEX_BIN = r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"
OUT_NAME = "旅游英语实用手册"


# ---------------------------------------------------------------- helpers
def esc(s: str) -> str:
    return (
        s.replace("\\", r"\textbackslash{}")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("$", r"\$")
        .replace("&", r"\&")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("%", r"\%")
        .replace("^", r"\textasciicircum{}")
        .replace("~", r"\textasciitilde{}")
    )


def raw(latex: str) -> str:
    return "```{=latex}\n" + latex + "\n```\n\n"


def arg(s: str) -> str:
    return esc(s)


# ---------------------------------------------------------------- emit
def T_cover():
    return raw(
        "\\thispagestyle{empty}\n"
        "\\vspace*{46mm}\n"
        "\\begin{center}\n"
        "  {\\fontsize{30pt}{38pt}\\selectfont\\bfseries 旅游英语实用手册}\\par\n"
        "  \\vspace{10pt}\n"
        "  {\\color{muted}\\fontsize{14pt}{19pt}\\selectfont Travel English Phrases}\\par\n"
        "  \\vspace{16pt}\n"
        "  {\\color{hairline}\\rule{0.55\\textwidth}{0.8pt}}\\par\n"
        "  \\vspace{14pt}\n"
        "  {\\color{muted}\\small 按场景分类 · 单词 + 句子速查}\\par\n"
        "  \\vspace{6pt}\n"
        "  {\\color{muted}\\small 机场 · 交通 · 酒店 · 餐饮 · 购物 · 观光 · 应急}\\par\n"
        "\\end{center}\n"
        "\\clearpage\n"
    )


def T_section(num, cn, en):
    return raw(f"\\eslsection{{{arg(num)}}}{{{arg(cn)}}}{{{arg(en)}}}")


def T_sub(cn, en):
    return raw(f"\\eslsubheader{{{arg(cn)}}}{{{arg(en)}}}")


def T_word_grid(items):
    """Two-column word grid: English bold left, Chinese muted right."""
    lines = [
        "\\par\\vspace{2pt}",
        "\\noindent\\begin{tabularx}{\\textwidth}{@{}>{\\RaggedRight}X@{\\hspace{14pt}}>{\\RaggedRight}X@{}}",
    ]
    for i in range(0, len(items), 2):
        left = items[i]
        right = items[i + 1] if i + 1 < len(items) else ("", "")
        cells = []
        for en, cn in (left, right):
            if en:
                cells.append("{\\bfseries " + esc(en) + "}\\hfill{\\color{muted}" + esc(cn) + "}")
            else:
                cells.append("")
        lines.append("  " + " & ".join(cells) + " \\\\ \\hline")
    lines.append("\\end{tabularx}\\par\\vspace{4pt}")
    return raw("\n".join(lines))


def T_sent(en, cn):
    return raw(f"\\eslpair{{{arg(en)}}}{{{arg(cn)}}}")


# ---------------------------------------------------------------- content
# 单词 = words, 句子 = sentences（合并 docx 与 ESL-travel english phrases.pdf）
SECTIONS = [
    dict(
        num="01", cn="机场与飞行", en="AIRPORT & FLIGHT",
        words=[
            ("check-in counter", "值机柜台"), ("check in", "办理值机"),
            ("boarding pass", "登机牌"), ("boarding gate", "登机口"),
            ("boarding time", "登机时间"), ("carry-on", "随身行李"),
            ("checked baggage", "托运行李"), ("overweight", "超重"),
            ("fragile", "易碎"), ("liquids", "液体"),
            ("window seat", "靠窗座位"), ("aisle seat", "靠过道座位"),
            ("one-way", "单程"), ("return / round-trip", "往返"),
            ("arrivals", "到达"), ("departures", "出发"),
            ("on time", "准点"), ("delayed", "延误"),
            ("canceled", "取消"), ("stopover / layover", "中转"),
            ("long-haul flight", "长途航班"), ("economy / business / first class", "经济/商务/头等舱"),
            ("duty-free shop", "免税店"), ("tax refund", "退税"),
            ("charging station", "充电站"), ("baggage claim", "行李提取"),
            ("blanket", "毯子"), ("excess baggage fee", "超重费"),
            ("information desk", "问询台"), ("ID", "身份证件"),
            ("oversized", "超大"), ("book a ticket", "订票"),
            ("travel agency", "旅行社"), ("convenience store", "便利店"),
            ("supermarket", "超市"), ("recline button", "座椅调节按钮"),
        ],
        sents=[
            ("Excuse me, how do I check in?", "请问怎么办理值机？"),
            ("Where is the check-in counter?", "值机柜台在哪里？"),
            ("How do I get to the boarding gate?", "去登机口怎么走？"),
            ("What time is my flight?", "我的航班几点起飞？"),
            ("How much luggage am I allowed to carry on?", "我能带多少随身行李？"),
            ("Are meals included?", "含餐吗？"),
            ("Where is the information desk?", "问询台在哪里？"),
            ("I'd like a window seat, please.", "我想要靠窗的座位。"),
            ("Could I have an aisle seat?", "可以给我靠过道的座位吗？"),
            ("Is my luggage overweight?", "我的行李超重了吗？"),
            ("When does boarding start?", "几点开始登机？"),
            ("Is the flight on time?", "航班准点吗？"),
            ("Could I have some orange juice, please?", "请给我一杯橙汁。"),
            ("May I have a blanket?", "能给我一条毯子吗？"),
            ("Excuse me, could I switch seats with you?", "打扰一下，能和你换座位吗？"),
            ("I think you're in my seat.", "您好像坐了我的位子。"),
            ("Can you help me put my luggage away?", "能帮我放一下行李吗？"),
            ("Does my seat have a charging port?", "我的座位有充电口吗？"),
            ("What time do we land?", "我们几点落地？"),
            ("My luggage didn't arrive.", "我的行李没到。"),
        ],
    ),
    dict(
        num="02", cn="到达与入境", en="ARRIVAL & CUSTOMS",
        words=[
            ("immigration", "入境检查"), ("customs", "海关"),
            ("passport", "护照"), ("visa", "签证"),
            ("purpose of visit", "来访目的"), ("sightseeing", "观光"),
            ("baggage claim area", "行李提取处"), ("currency exchange", "货币兑换"),
            ("money change", "换钱"), ("taxi stand", "出租车停靠点"),
            ("ATM", "自动取款机"), ("connecting flight", "转机航班"),
            ("declare", "申报"),
        ],
        sents=[
            ("Where is the baggage claim area?", "行李提取处在哪里？"),
            ("Where is the currency exchange?", "在哪里换钱？"),
            ("Where is the taxi stand?", "出租车停靠点在哪里？"),
            ("Where is the immigration / customs?", "入境检查 / 海关在哪里？"),
            ("I am traveling for sightseeing.", "我是来观光的。"),
            ("I am traveling for business.", "我是来出差的。"),
            ("I am traveling to visit my family.", "我是来探亲的。"),
            ("I am traveling for study.", "我是来学习的。"),
            ("I will be here for two weeks.", "我会在这里待两周。"),
            ("I am staying at the Grand Hotel.", "我住在格兰德酒店。"),
            ("I have a connecting flight.", "我要转机。"),
            ("Which gate is my connecting flight?", "我的转机航班在几号登机口？"),
            ("Do you have anything to declare? — No, nothing.", "有要申报的吗？— 没有。"),
            ("Where can I exchange money?", "在哪里能换钱？"),
            ("Is there an ATM nearby?", "附近有取款机吗？"),
            ("Could you exchange this into US dollars?", "能把这些换成美元吗？"),
        ],
    ),
    dict(
        num="03", cn="市内交通", en="GETTING AROUND",
        words=[
            ("bus", "公交车"), ("subway / metro", "地铁"),
            ("train", "火车"), ("fare", "车费"),
            ("stop", "公交站"), ("station", "火车站 / 地铁站"),
            ("platform", "站台"), ("one-way ticket", "单程票"),
            ("round-trip ticket", "往返票"), ("taxi", "出租车"),
            ("ride-hailing", "网约车"), ("pickup point", "上车点"),
            ("trunk", "后备箱"), ("seat", "座位"),
            ("go straight", "直走"), ("turn left / right", "左转 / 右转"),
        ],
        sents=[
            ("Take me to this address, please.", "请去这个地址。"),
            ("Could you help me with my luggage?", "能帮我搬一下行李吗？"),
            ("How much is the fare?", "车费多少钱？"),
            ("Keep the change.", "不用找了。"),
            ("Does this bus go to the city center?", "这趟公交车到市中心吗？"),
            ("Does this train go to the airport?", "这趟火车到机场吗？"),
            ("How long does it take to get to the airport?", "到机场要多久？"),
            ("Which stop should I get off at?", "我该在哪一站下车？"),
            ("Could you tell me when we get there?", "到了请告诉我一声。"),
            ("I'd like a one-way ticket to ..., please.", "我要一张去……的单程票。"),
            ("Where can I buy a metro card?", "在哪里买地铁卡？"),
            ("Do you accept Alipay / WeChat Pay?", "收支付宝 / 微信支付吗？"),
            ("Can I use my credit card?", "我能用信用卡吗？"),
            ("Excuse me, is this seat taken?", "请问这个位子有人吗？"),
            ("Excuse me, how do I get to ...?", "请问去……怎么走？"),
            ("Is it far from here?", "离这里远吗？"),
            ("Could you show me on the map?", "能在地图上指给我看吗？"),
        ],
    ),
    dict(
        num="04", cn="酒店", en="HOTEL",
        words=[
            ("reservation / booking", "预订"), ("check-in", "入住"),
            ("check-out", "退房"), ("breakfast", "早餐"),
            ("Wi-Fi", "无线网络"), ("air conditioner", "空调"),
            ("fridge / mini-bar", "冰箱 / 迷你吧"), ("room service", "客房服务"),
            ("towels", "毛巾"), ("toilet paper", "卫生纸"),
            ("bedsheets", "床单"), ("toothbrush", "牙刷"),
            ("shampoo", "洗发水"), ("body wash", "沐浴露"),
            ("conditioner", "护发素"), ("bottled water", "瓶装水"),
            ("laundry service", "洗衣服务"), ("pillow", "枕头"),
        ],
        sents=[
            ("I'm here to check in. I have a reservation under the name of Wang.", "我来入住，以 Wang 的名字预订了。"),
            ("Is breakfast included?", "含早餐吗？"),
            ("What time is breakfast served?", "早餐几点供应？"),
            ("What time is check-in / check-out?", "几点入住 / 几点退房？"),
            ("Does the room have Wi-Fi?", "房间有无线网络吗？"),
            ("Can you help me with Wi-Fi?", "能帮我弄一下无线网络吗？"),
            ("Wi-Fi isn't working.", "无线网络用不了。"),
            ("What floor am I on?", "我在几楼？"),
            ("My room needs towels.", "我的房间需要毛巾。"),
            ("Could I please have room service?", "请帮我安排客房服务。"),
            ("Could I have an extra pillow, please?", "能再给我一个枕头吗？"),
            ("The air conditioner isn't working.", "空调坏了。"),
            ("Could you send someone to fix it?", "能派人来修一下吗？"),
            ("Could I leave my luggage here until 3 p.m.?", "行李能寄存到下午三点吗？"),
            ("Do you have a laundry service?", "有洗衣服务吗？"),
            ("How do I get to the city center from here?", "从这里怎么去市中心？"),
            ("I'd like to check out, please.", "我要退房。"),
            ("Could you call a taxi for me?", "能帮我叫一辆出租车吗？"),
        ],
    ),
    dict(
        num="05", cn="餐饮", en="RESTAURANT",
        words=[
            ("menu", "菜单"), ("appetizer / starter", "开胃菜"),
            ("soup", "汤"), ("salad", "沙拉"),
            ("dessert", "甜点"), ("bill / check", "账单"),
            ("tip", "小费"), ("ketchup", "番茄酱"),
            ("napkin", "餐巾纸"), ("straw", "吸管"),
            ("refill", "续杯"), ("well done", "全熟"),
            ("medium", "五分熟"), ("medium rare", "三分熟"),
            ("rare", "一分熟"), ("vegetarian / vegan", "素食 / 纯素"),
            ("allergy", "过敏"), ("takeout / to go", "外带"),
            ("boil / fry / roast / steam", "煮 / 煎炸 / 烤 / 蒸"),
        ],
        sents=[
            ("A table for two, please.", "请给我两人的位子。"),
            ("Could we sit by the window?", "能坐窗边吗？"),
            ("May I see a menu, please?", "请给我菜单。"),
            ("I would like to order, please.", "我要点餐。"),
            ("Could you recommend some popular dishes?", "能推荐几道受欢迎的菜吗？"),
            ("What's your best / top-seller?", "你们最受欢迎的是什么？"),
            ("What's your special?", "你们的特色菜是什么？"),
            ("I'll have the grilled chicken.", "我要烤鸡。"),
            ("I'll take this one, please.", "我要这个。"),
            ("Can I please have a glass of water?", "请给我一杯水。"),
            ("No ice, please.", "不要冰。"),
            ("Can I ask for a refill?", "能续杯吗？"),
            ("Can I have another one?", "能再给我一份吗？"),
            ("Could I have extra sauce, please?", "能多给点酱吗？"),
            ("I didn't order this.", "我没点这个。"),
            ("I'm allergic to peanuts.", "我对花生过敏。"),
            ("Is this vegetarian?", "这是素的吗？"),
            ("May I have the bill, please?", "请买单。"),
            ("Is service included?", "含服务费吗？"),
            ("Can we pay separately?", "我们能分开付吗？"),
            ("Could I get this to go?", "这个打包带走。"),
            ("How long is the wait?", "要等多久？"),
        ],
    ),
    dict(
        num="06", cn="购物", en="SHOPPING",
        words=[
            ("size", "尺码"), ("fitting room", "试衣间"),
            ("discount", "折扣"), ("sale", "特价"),
            ("receipt", "小票"), ("cash", "现金"),
            ("credit card", "信用卡"), ("cashier", "收银台"),
            ("tax refund", "退税"), ("duty-free", "免税"),
            ("return", "退货"), ("exchange", "换货"),
            ("pricey", "昂贵"), ("disposable", "一次性的"),
        ],
        sents=[
            ("Excuse me, where can I find ...?", "请问在哪里能找到……？"),
            ("Excuse me, how much is this?", "请问这个多少钱？"),
            ("Do you offer discounts?", "有折扣吗？"),
            ("Do you have a sale?", "有特价活动吗？"),
            ("Does this come in a bigger / smaller size?", "有大一码 / 小一码的吗？"),
            ("Can I try this on?", "能试穿吗？"),
            ("Where is the fitting room?", "试衣间在哪里？"),
            ("What is your return and exchange policy?", "你们的退换货政策是什么？"),
            ("What forms of payment do you accept?", "你们接受什么支付方式？"),
            ("Can you recommend something similar to this?", "有类似的可以推荐吗？"),
            ("Can I pay by card?", "能刷卡吗？"),
            ("Do you accept Alipay / Apple Pay?", "收支付宝 / Apple Pay 吗？"),
            ("Could I get a receipt?", "请给我小票。"),
            ("Is this tax-free?", "这个是免税的吗？"),
            ("Could I get a tax refund form?", "能给我一张退税单吗？"),
            ("I'd like to return this.", "我想退货。"),
            ("It's a little pricey.", "有点贵。"),
            ("Can you give me a better price?", "能便宜一点吗？"),
        ],
    ),
    dict(
        num="07", cn="观光与问路", en="SIGHTSEEING & DIRECTIONS",
        words=[
            ("tourist information center", "游客信息中心"), ("guided tour", "导游团"),
            ("festival", "节日"), ("event", "活动"),
            ("souvenir", "纪念品"), ("ticket office", "售票处"),
            ("photo", "照片"), ("restroom", "洗手间"),
            ("traffic lights", "红绿灯"), ("around the corner", "拐角处"),
            ("across from", "在对面"), ("next to", "紧挨着"),
        ],
        sents=[
            ("Where is the visitor information center?", "游客信息中心在哪里？"),
            ("Are there any guided tours for this area?", "这个区域有导游团吗？"),
            ("Are there any rules and restrictions / taboos I should know?", "有什么需要知道的规矩或禁忌吗？"),
            ("Can you take a photo of me in front of ...?", "能帮我在……前面拍张照吗？"),
            ("Are there any events or festivals around here?", "附近有什么活动或节日吗？"),
            ("Where can I buy tickets?", "在哪里买票？"),
            ("What time does it open / close?", "几点开门 / 关门？"),
            ("Could you tell me where the restroom is?", "请问洗手间在哪里？"),
            ("Go straight, then turn left.", "直走，然后左转。"),
            ("Excuse me, where is the nearest ...?", "请问最近的……在哪里？"),
            ("Sorry, could you speak more slowly, please?", "抱歉，能说慢一点吗？"),
        ],
    ),
    dict(
        num="08", cn="沟通与应急", en="COMMUNICATION & EMERGENCIES",
        words=[
            ("help", "救命 / 帮助"), ("wallet", "钱包"),
            ("police", "警察"), ("police station", "警察局"),
            ("pharmacy / drug store", "药店"), ("hospital", "医院"),
            ("ambulance", "救护车"), ("embassy", "大使馆"),
            ("consulate", "领事馆"), ("insurance", "保险"),
            ("lost", "丢失的"), ("stolen", "被偷的"),
            ("dizzy / faint", "头晕 / 晕倒"),
        ],
        sents=[
            ("Sorry, I do not understand what you are saying.", "抱歉，我没听懂你说的话。"),
            ("I do not speak English very well.", "我英语说得不太好。"),
            ("Please speak slowly.", "请说慢一点。"),
            ("Could you say that again, please?", "能再说一遍吗？"),
            ("Could you write it down?", "能写下来吗？"),
            ("Help!", "救命！"),
            ("I have lost my wallet.", "我的钱包丢了。"),
            ("I have lost my passport.", "我的护照丢了。"),
            ("My credit card was stolen.", "我的信用卡被偷了。"),
            ("I feel dizzy / sick.", "我头晕 / 不舒服。"),
            ("I am in pain.", "我很疼。"),
            ("I need to see a doctor.", "我要看医生。"),
            ("Where is the nearest hospital / pharmacy?", "最近的医院 / 药店在哪里？"),
            ("Could you call an ambulance?", "能帮我叫救护车吗？"),
            ("Please call the police.", "请报警。"),
            ("Where is the police station?", "警察局在哪里？"),
            ("Where is the Chinese embassy / consulate?", "中国大使馆 / 领事馆在哪里？"),
            ("I'd like to file an insurance claim.", "我要报案理赔。"),
        ],
    ),
]


def build_content():
    parts = [T_cover()]
    for s in SECTIONS:
        parts.append("\\clearpage")
        parts.append(T_section(s["num"], s["cn"], s["en"]))
        parts.append(T_sub("单词", "WORDS"))
        parts.append(T_word_grid(s["words"]))
        parts.append(T_sub("句子", "SENTENCES"))
        for en, cn in s["sents"]:
            parts.append(T_sent(en, cn))
    return "\n".join(parts)


# ---------------------------------------------------------------- render
def build():
    md_out = GEN_DIR / f"{OUT_NAME}.md"
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out.write_text(build_content(), encoding="utf-8")

    pdf = PDF_DIR / f"{OUT_NAME}.pdf"
    env = dict(os.environ)
    env["PATH"] = MIKTEX_BIN + os.pathsep + env["PATH"]
    cmd = [
        PANDOC, str(md_out),
        "-f", "markdown+raw_attribute",
        "--template", str(TEMPLATE),
        "-H", str(PREAMBLE),
        "--pdf-engine=xelatex",
        "--pdf-engine-opt=--enable-installer",
        "-o", str(pdf),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, env=env)
    if r.returncode != 0:
        print("[FAIL] pandoc/xelatex")
        print(r.stderr[-4000:])
        return False
    print(f"[ok]   {pdf.name}  ({pdf.stat().st_size} bytes)")
    return True


def previews():
    pdf_path = PDF_DIR / f"{OUT_NAME}.pdf"
    PREVIEW.mkdir(exist_ok=True)
    tmp_pdf = PREVIEW / "_preview_tmp.pdf"
    tmp_pdf.write_bytes(pdf_path.read_bytes())
    tmp = PREVIEW / "_preview_tmp.py"
    code = (
        "import pypdfium2 as p\n"
        "pdf=p.PdfDocument(r'" + str(tmp_pdf) + "')\n"
        "print('pages=', len(pdf))\n"
        "for i in range(min(6, len(pdf))):\n"
        "    page=pdf[i]\n"
        "    page.render(scale=1.4).to_pil().save(r'" + str(PREVIEW / "travel_bw_") + "' + str(i) + '.png')\n"
    )
    tmp.write_text(code, encoding="utf-8")
    try:
        r = subprocess.run([str(VENV_PY), str(tmp)],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
    finally:
        for f in (tmp, tmp_pdf):
            if f.exists():
                f.unlink()
    if r.returncode != 0:
        print("[png-fail]", r.stderr.strip()[-400:])
        return
    print("[png]", r.stdout.strip())


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ok = build()
    if ok and "--png" in sys.argv:
        previews()

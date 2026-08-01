#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESLBeginner · 旅游英语实用手册 (2026 麦肯锡场景版) PDF builder
=============================================================
Source handbook:  MD/旅游英语实用手册.docx  (reviewed + reorganized)
Output:          PDF/旅游英语实用手册-2026麦肯锡场景版.pdf

Pipeline:  content (this script)  →  markdown w/ raw LaTeX  →  pandoc + xelatex
Design:    build/preamble_mck.tex  (McKinsey blue system)

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
PREAMBLE = ROOT / "build" / "preamble_mck.tex"
MIKTEX_BIN = r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"
OUT_NAME = "旅游英语实用手册-2026麦肯锡场景版"


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
    """Escape content inside a LaTeX macro argument (no braces needed)."""
    return esc(s)


# ---------------------------------------------------------------- emit
def T_cover():
    return raw(
        "\\mckcover{旅游英语实用手册}"
        "{2026 场景速查版 · 中国成年人出境游}"
        "{听得懂 · 说得出 · 够用就好\n\n"
        "按旅程场景 MECE 分类 \\textbullet{} 每节：核心提示 $\\rightarrow$ 你要说 / 对方会说 $\\rightarrow$ TIP}"
    )


def T_band(cn, en):
    return raw(f"\\mckband{{{arg(cn)}}}{{{arg(en)}}}")


def T_section(num, cn, en):
    return raw(f"\\mcksection{{{arg(num)}}}{{{arg(cn)}}}{{{arg(en)}}}")


def T_key(title, text):
    return raw(f"\\mckkey{{{arg(title)}}}{{{arg(text)}}}")


def T_h(cn, en=""):
    return raw(f"\\mckh{{{arg(cn)}}}{{{arg(en)}}}")


def T_pair(en, cn):
    return raw(f"\\mckpair{{{arg(en)}}}{{{arg(cn)}}}")


def T_note(text):
    return raw(f"\\mcknote{{{arg(text)}}}")


def T_tip(title, text):
    return raw(f"\\mcktip{{{arg(title)}}}{{{arg(text)}}}")


def T_word(en, cn):
    return raw(f"\\mckword{{{arg(en)}}}{{{arg(cn)}}}")


def T_table(headers, rows):
    """tabularx table, navy header + zebra rows; row cell = (en, cn) renders
    English bold above a muted Chinese line."""
    n = len(headers)
    colspec = "@{}" + ">{\\RaggedRight}X@{\\hspace{9pt}}" * (n - 1) + ">{\\RaggedRight}X@{}"
    lines = [
        "\\rowcolors{2}{mckpale}{white}",
        "\\par\\vspace{4pt}",
        "\\noindent\\begin{tabularx}{\\textwidth}{" + colspec + "}",
        "  \\rowcolor{mcknavy} "
        + " & ".join("{\\color{white}\\bfseries " + esc(h) + "}" for h in headers)
        + " \\\\",
        "  \\hline",
    ]
    for r in rows:
        cells = []
        for c in r:
            if isinstance(c, tuple):
                en, cn = c
                cells.append(
                    "\\RaggedRight {\\bfseries " + esc(en) + "}\\par\\vspace{1.5pt}"
                    + "{\\footnotesize " + esc(cn) + "}"
                )
            else:
                cells.append("\\RaggedRight " + esc(c))
        lines.append("  " + " & ".join(cells) + " \\\\")
        lines.append("  \\hline")
    lines.append("\\end{tabularx}\\par\\vspace{5pt}")
    return raw("\n".join(lines))


def T_journey():
    """2-row journey map: box → box → box → box."""
    row1 = ["出发前准备", "机场与飞行", "入境与海关", "市内交通"]
    row2 = ["酒店住宿", "餐饮", "购物与退税", "应急求助"]
    cell = lambda t: f"\\centering\\arraybackslash\\colorbox{{mcklight}}{{{t}}}"
    arr = "\\centering\\arraybackslash$\\rightarrow$"
    lines = [
        "\\par\\vspace{4pt}",
        "\\noindent\\begin{tabularx}{\\textwidth}{@{}"
        + "X@{\\hspace{4pt}}c@{\\hspace{4pt}}X@{\\hspace{4pt}}c@{\\hspace{4pt}}X@{\\hspace{4pt}}c@{\\hspace{4pt}}X@{}}",
    ]
    for r in (row1, row2):
        lines.append("  " + " & ".join(cell(t) for t in r[:1]) + " & " + arr + " & "
                     + " & ".join(cell(t) for t in r[1:2]) + " & " + arr + " & "
                     + " & ".join(cell(t) for t in r[2:3]) + " & " + arr + " & "
                     + " & ".join(cell(t) for t in r[3:4]) + " \\\\")
        lines.append("  \\hline")
    lines.append("\\end{tabularx}\\par\\vspace{6pt}")
    return raw("\n".join(lines))


# ---------------------------------------------------------------- content
def page_cover():
    return T_cover()


def page_howto():
    out = [T_band("使用说明", "HOW TO USE THIS HANDBOOK")]
    out.append(T_key(
        "读法：先看结论，再找句子，最后记一条 TIP。",
        "每节按“核心提示（结论）→ 你要说 / 对方会说（证据）→ TIP（细节）”三层展开，"
        "应急时只看加粗句也能把意思表达出来。"
    ))
    out.append(T_h("旅程全景图", "TRAVEL JOURNEY MAP — 8 个 MECE 场景"))
    out.append(T_journey())
    out.append(T_note("按实际行程顺序排列，遇到哪一段就翻到哪一节；每节相互独立，可单独使用。"))
    out.append(T_h("三个核心原则", "3 PRINCIPLES"))
    out.append(T_pair("Listen for key words, not whole sentences.",
                      "先听关键词，不追求听懂整句。passport / booking / gate / size / fare 出现时就抓住主线。"))
    out.append(T_pair("Short sentences are enough. Even single words work.",
                      "短句优先，单词也能救命。“Menu, please.” 和 “I'll have this.” 足够覆盖 80% 的日常。"))
    out.append(T_pair("Your phone is your second passport.",
                      "手机是第二本护照：翻译、地图、打车、支付 App 提前装好并离线可用。"))
    return "\n".join(out)


def page_insights():
    out = ["\\clearpage", T_band("2026 核心洞察", "2026 PAIN POINTS & FIXES")]
    out.append(T_key(
        "原手册底子很好，但还停在“2010 年代美国场景”；本版按 2026 年中国成年人的真实痛点做了四点升级。",
        "保留原手册全部实用句型，修正表达错误，补充数字化工具、多目的地差异与应急场景。"
    ))
    out.append(T_key(
        "痛点 1：听不懂比说不出更难。",
        "对策：每节先给“对方会说”高频句 + 关键词；听不懂用第 08 节三句万能话术接住，而不是愣住。"
    ))
    out.append(T_key(
        "痛点 2：现金时代结束，支付与退税成为新门槛。",
        "对策：信用卡 + Apple Pay / 支付宝国际版 + 少量现金组合；第 07 节专讲退税流程与单据。"
    ))
    out.append(T_key(
        "痛点 3：中国游客目的地全球化，一本“美国手册”不够。",
        "对策：新增附录 C 各国小费 / 支付 / 插座 / 卫生间用词速查，覆盖欧洲、日本、东南亚、中东。"
    ))
    out.append(T_key(
        "痛点 4：成年人最怕“出事了不会说”——生病、丢证件。",
        "对策：新增第 09 节应急场景：买药看病、报警、补护照、保险理赔，全部一句话直达。"
    ))
    return "\n".join(out)


def page_01():
    out = [T_section("01", "出发前准备", "PRE-TRIP · GET READY")]
    out.append(T_key(
        "出发前把“证件、网络、支付、确认函”四件事办妥，落地后 80% 的沟通都围绕这些信息展开。",
        "国际航班通常提前 3 小时到机场；行李额看票面 “1PC × 23kg” 或 “23kg” 字样。"
    ))
    out.append(T_h("出行清单", "CHECKLIST"))
    out.append(T_table(
        ["事项", "准备动作"],
        [
            [("Passport & visa 护照签证", "检查有效期，电子签打印或存 PDF"),
             "出发前 1 个月检查有效期，电子签下载到手机相册"],
            [("Travel insurance 旅行保险", "医疗保额建议 30–50 万，保单号存手机"),
             "先存保险公司紧急电话和保单号"],
            [("eSIM / roaming 网络", "出发前开通，落地开机即用"),
             "同时下载离线地图和离线翻译包"],
            [("Booking confirmations 确认函", "机票、酒店、车票确认函存 PDF 到相册"),
             "酒店订单上有地址和前台电话，打车直接出示"],
            [("Payment 支付", "信用卡 + 少量现金，绑定 Apple Pay / 支付宝国际版"),
             "Visa / Mastercard 优先；银联在有中国游客的地区通用"],
            [("Apps 工具", "翻译、地图、打车、订餐四件套"),
             "翻译 DeepL / Google Translate，打车 Uber / Lyft / Grab / Bolt"],
        ],
    ))
    out.append(T_h("要说的句子", "USEFUL SENTENCES"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Could you confirm my booking, please?", "请帮我确认一下预订"),
             "给客服/前台打电话开场白"],
            [("What's the baggage allowance?", "行李限额是多少？"),
             "问航司或订票平台"],
            [("What time should I be at the airport?", "我该几点到机场？"),
             "国际航班一般提前 3 小时"],
            [("I'd like to change my flight to July 10th.", "我想改签到 7 月 10 日"),
             "改签可能产生费用，先问 How much is the change fee?"],
            [("Do I need a visa for this trip?", "这次行程需要签证吗？"),
             "免签 / 落地签国家逐年增多，出行前确认"],
        ],
    ))
    out.append(T_tip("确认函存哪里？", "手机相册建一个“行程”相册，护照页、签证、保单、确认函各存一张，同时上传云端一份。"))
    return "\n".join(out)


def page_02():
    out = [T_section("02", "机场与飞行", "AIRPORT & FLIGHT")]
    out.append(T_key(
        "值机、安检、登机、机上四段，每段只有 5 个高频句；听到 baggage / gate / boarding / delayed 就是关键信息。",
        "原手册“How many luggages” 是错误的（luggage 不可数），正确问法是 How many bags are you checking in?"
    ))
    out.append(T_h("值机托运", "CHECK-IN & BAGGAGE"))
    out.append(T_table(
        ["对方会说", "你要说"],
        [
            [("May I see your passport, please?", "请出示护照"),
             ("I'd like to check in, please.", "我要办理值机")],
            [("How many bags are you checking in?", "托运几件行李？"),
             ("Two bags and one carry-on.", "两件托运，一件随身")],
            [("Do you have any carry-on?", "有随身行李吗？"),
             ("Could I have a window seat, please?", "请给我靠窗位")],
            [("Your luggage is 2 kg overweight.", "行李超重 2 公斤"),
             ("Is there an excess baggage fee?", "超重要收费吗？")],
            [("Here's your boarding pass.", "这是您的登机牌"),
             ("Which gate is my flight?", "我的航班在几号登机口？")],
        ],
    ))
    out.append(T_h("安检与登机", "SECURITY & BOARDING"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Take off your belt and shoes, please.", "请解皮带、脱鞋（安检）"),
             "液体单瓶不超过 100ml，统一放透明袋"],
            [("When does boarding start?", "几点开始登机？"),
             "登机牌上 Boarding time 通常是起飞前 30–45 分钟"],
            [("Is the flight on time?", "航班准点吗？"),
             "听到 delayed（延误）或 canceled（取消）时先问下一步"],
            [("The flight is canceled. What should I do?", "航班取消了，我该怎么办？"),
             "航司通常安排改签或住宿，问 Where can I rebook?"],
        ],
    ))
    out.append(T_h("机上", "ON BOARD"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Could I have some orange juice, please?", "请给我一杯橙汁"),
             "要毯子：May I have a blanket?"],
            [("Excuse me, could I switch seats with you?", "打扰一下，能和你换座位吗？"),
             "先说 Excuse me 再提请求，成功率更高"],
            [("I think you're in my seat.", "您好像坐了我的位置"),
             "拿出登机牌指座位号即可"],
            [("What time do we land?", "我们几点落地？"),
             "落地时间 = local time 当地时间"],
        ],
    ))
    out.append(T_tip("行李没到怎么办？",
                     "到行李转盘旁的 Baggage Claim 柜台说：My luggage didn't arrive. Here's my baggage tag. "
                     "拿一张 PIR（行李事故单）编号，凭它理赔和追踪。"))
    return "\n".join(out)


def page_03():
    out = [T_section("03", "入境与海关", "IMMIGRATION & CUSTOMS")]
    out.append(T_key(
        "边检几乎只问四件事：从哪来、来干嘛、待多久、住哪——用单词和短语回答就够，不需要完整句子。",
        "听到 Sightseeing（观光）、Business（商务）、Visiting family（探亲）这三个词就能答上 90% 的问题。"
    ))
    out.append(T_table(
        ["对方会说", "你可以答"],
        [
            [("Where did you fly from?", "从哪里飞来的？"),
             ("From China.", "中国")],
            [("What's the purpose of your visit?", "来干什么？"),
             ("Sightseeing.", "观光")],
            [("", ""),
             ("I'm here on business.", "商务出差")],
            [("", ""),
             ("Visiting my family.", "探亲")],
            [("How long will you be staying?", "打算待多久？"),
             ("Two weeks.", "两周")],
            [("", ""),
             ("Until July 20th.", "待到 7 月 20 日")],
            [("Where will you be staying?", "住哪里？"),
             ("At the Grand Hotel.", "住格兰德酒店")],
            [("Do you have anything to declare?", "有要申报的物品吗？"),
             ("No, nothing.", "没有")],
        ],
    ))
    out.append(T_h("转机与换钱", "CONNECTING FLIGHT & MONEY"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I have a connecting flight.", "我要转机"),
             "说这句，工作人员会引导你走转机通道"],
            [("Which gate is my connecting flight?", "我的转机航班在几号登机口？"),
             "转机时间紧：My connection is in 40 minutes, could you help me?"],
            [("Where can I exchange money?", "哪里能换钱？"),
             "机场汇率通常不划算，小额应急即可"],
            [("Is there an ATM nearby?", "附近有 ATM 吗？"),
             "ATM 取现按银联/国际卡当日汇率，通常优于柜台"],
        ],
    ))
    out.append(T_tip("申报单怎么填？",
                     "现金超过限额、超额烟酒、肉类水果都要申报；不确定时选 Yes，让工作人员判断，比隐瞒被罚好。"))
    return "\n".join(out)


def page_04():
    out = [T_section("04", "市内交通与问路", "GETTING AROUND")]
    out.append(T_key(
        "打车认车牌、公交听站名、问路让对方在地图上指——“听懂回答”比“说出句子”更重要。",
        "不会说地名就把手机上的目的地 / 酒店地址直接给司机看，一句话都不用讲。"
    ))
    out.append(T_h("打车与网约车", "TAXI & RIDE-HAILING"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Take me to this address, please.", "请去这个地址"),
             "出示手机上的地址或酒店名片即可"],
            [("Could you help me with my luggage?", "能帮我搬一下行李吗？"),
             "后备箱：Could you open the trunk, please?"],
            [("How much will the fare be?", "车费大概多少钱？"),
             "上车前先确认，避免绕路纠纷"],
            [("Could you turn on the meter?", "请打表计价"),
             "不打表先谈价：How much to go to ...?"],
            [("Keep the change.", "不用找了（小费）"),
             "只在美国等小费国家使用；欧洲、日本一般不适用"],
        ],
    ))
    out.append(T_note("网约车（Uber / Lyft / Grab / Bolt）：上车点在 App 里叫 pickup point；核对车牌后上车，"
                      "目的地订单里已有，通常不需要开口。"))
    out.append(T_h("公交、地铁与火车", "BUS · METRO · TRAIN"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Does this bus go to the city center?", "这趟车到市中心吗？"),
             "上车前问司机最稳妥"],
            [("How much is the fare?", "车票多少钱？"),
             "买票：One ticket, please."],
            [("Which stop should I get off at?", "我该在哪站下？"),
             "到站提醒：Could you tell me when we get there?"],
            [("I'd like a one-way ticket to …", "我要一张去……的单程票"),
             "往返：round-trip；站台：which platform"],
            [("Where can I buy a metro card?", "在哪里买地铁卡？"),
             "一日票：a one-day pass，更划算"],
        ],
    ))
    out.append(T_h("问路", "ASKING DIRECTIONS"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Excuse me, how do I get to …?", "请问去……怎么走？"),
             "问路第一句，Excuse me 必加"],
            [("Is it far from here?", "离这儿远吗？"),
             "回答可能是步行分钟数"],
            [("Could you show me on the map?", "能在地图上指给我看吗？"),
             "让对方用手机地图标点，比听口音可靠"],
            [("Go straight / Turn left / Turn right", "直走 / 左转 / 右转"),
             "方向词全表见附录 B"],
            [("It's about a 10-minute walk.", "步行大约 10 分钟"),
             "听到 minutes' walk 就知道不远"],
        ],
    ))
    out.append(T_tip("上车前确认",
                     "公交不确定对不对：Is this the right bus for …?；地铁坐反方向先看站名，多数线路有电子屏。"))
    return "\n".join(out)


def page_05():
    out = [T_section("05", "酒店住宿", "HOTEL")]
    out.append(T_key(
        "酒店 90% 的沟通是“入住、退房、要东西、报修”四类；把确认函出示给前台，名字拼写不用开口。",
        "预订名用拼音即可：I have a reservation under the name Wang. 听到 breakfast included 就确认是否含早。"
    ))
    out.append(T_h("入住与退房", "CHECK-IN & CHECK-OUT"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I have a reservation under the name Wang.", "我以 Wang 的名字订了房"),
             "出示订单确认函更快"],
            [("Could I have a room with a view?", "能给我一间景观房吗？"),
             "免费升级先问：Is there an upgrade available?"],
            [("What time is breakfast? Is it included?", "早餐几点？含在房费里吗？"),
             "听到 buffet（自助餐）就知道是自助"],
            [("What's the Wi-Fi password?", "Wi-Fi 密码是多少？"),
             "密码常印在房卡套上"],
            [("I'd like to check out, please.", "我要退房"),
             "问最晚退房：What time is check-out?"],
            [("Could I leave my luggage here until 3 p.m.?", "行李能寄存到下午 3 点吗？"),
             "寄存处一般免费；贵重物品随身带"],
        ],
    ))
    out.append(T_h("房间与服务", "ROOM & SERVICES"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("The air conditioner isn't working.", "空调坏了"),
             "万能报修句：Something is wrong with … / … isn't working"],
            [("Could you send someone to fix it?", "能派人来修一下吗？"),
             "催修：Could you send someone as soon as possible?"],
            [("Could I have an extra pillow / towel?", "能再给我一个枕头 / 毛巾吗？"),
             "吹风机：I need a hair dryer."],
            [("Could you call a taxi for me?", "能帮我叫辆出租车吗？"),
             "前台代叫更安全，上车前再次确认地址"],
            [("How do I get to the city center?", "去市中心怎么走？"),
             "要地图：Do you have a map of the city?"],
            [("Could you recommend a restaurant nearby?", "能推荐一家附近的餐厅吗？"),
             "让前台帮忙订位也可以：Could you book a table for me?"],
            [("Do you have a laundry service?", "有洗衣服务吗？"),
             "问价格：How much does it cost?"],
        ],
    ))
    out.append(T_h("晚到与延迟", "LATE ARRIVAL"))
    out.append(T_pair("I'll arrive around 9 p.m. Could I check in late?",
                      "我大约晚上 9 点到，可以晚入住吗？（提前告知，避免房间被取消）"))
    out.append(T_tip("小费怎么给？",
                     "美国等小费国家：搬行李 1–2 美元；欧洲、日本一般不强制。先看账单是否含 service charge（服务费）。"))
    return "\n".join(out)


def page_06():
    out = [T_section("06", "餐饮", "DINING OUT")]
    out.append(T_key(
        "点菜三步走——要菜单 → 指菜单 → 买单；过敏和忌口一定要说清楚，这比口音重要得多。",
        "很多餐厅扫码看菜单（QR menu），用手机拍照翻译即可；看不懂的菜直接问 What is this dish?"
    ))
    out.append(T_h("订位与入座", "RESERVATION & SEATING"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I'd like to book a table for two at 7 p.m.", "我想订今晚 7 点两人的位子"),
             "电话订位开场白"],
            [("Do you have a table for two?", "有两人桌吗？"),
             "没订位直接进店时问"],
            [("How long is the wait?", "要等多久？"),
             "排队时也可问 How many people are waiting?"],
            [("Could we sit by the window?", "能坐窗边吗？"),
             "其他要求照套：near the door / outside"],
            [("Could I see the menu, please?", "请给我菜单"),
             "没人理会时：Menu, please."],
        ],
    ))
    out.append(T_h("点餐", "ORDERING"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Are you ready to order? — I'll have the grilled chicken.", "可以点餐了吗？— 我要烤鸡"),
             "听到 Can I take your order? 是同义问法"],
            [("What do you recommend?", "你有什么推荐？"),
             "主厨推荐：chef's special"],
            [("I'll take this one, please.", "我要这个（指菜单）"),
             "指给服务员看，零词汇量也能点菜"],
            [("Could I have a few more minutes?", "我再看看菜单"),
             "还没想好时的标准回答"],
            [("Water, please. / Could I have a glass of water?", "请给我水"),
             "不要冰：No ice, please."],
            [("Could I change the fries to a salad?", "薯条能换成沙拉吗？"),
             "快餐店换配菜句型"],
        ],
    ))
    out.append(T_h("熟度、忌口与过敏", "DONENESS · DIET · ALLERGIES"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Rare / Medium rare / Medium / Well done", "一分 / 三分 / 五分 / 全熟"),
             "点牛排时必用，说错熟度无法补救"],
            [("I'm allergic to peanuts.", "我对花生过敏"),
             "过敏原要主动说，尤其是坚果 nuts、海鲜 seafood、乳制品 dairy"],
            [("Is this vegetarian?", "这是素食吗？"),
             "纯素：vegan；清真：halal"],
            [("No onions, please.", "不要洋葱"),
             "去掉某配料统一句式：No …, please."],
        ],
    ))
    out.append(T_h("买单与打包", "BILL & TO-GO"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Could I have the bill, please?", "买单，谢谢"),
             "美式说法 check，英式说法 bill，都懂"],
            [("Is service included?", "含服务费吗？"),
             "含了就不用再给消费（小费），给不给看附录 C"],
            [("We'd like to pay separately.", "我们分开付（AA）"),
             "一起付：We'd like to pay together."],
            [("Could I get this to go?", "这个帮我打包"),
             "快餐店：For here or to go?"],
            [("Could I have a bag / box for this?", "给我一个袋子 / 盒子"),
             "要餐具：Could I have some napkins, please?"],
        ],
    ))
    out.append(T_tip("上错菜 / 算错账",
                     "上错了：I didn't order this.（我没点这个）；账不对：What's this charge for?（这笔是什么费用？）"))
    return "\n".join(out)


def page_07():
    out = [T_section("07", "购物与退税", "SHOPPING & TAX REFUND")]
    out.append(T_key(
        "购物三件事：尺码、价格、退税。尺码报数字（US 6 / EU 38），退税留好小票和退税单。",
        "试衣间 fitting room、打折 on sale、退税 tax refund 三个词记住，购物基本无障碍。"
    ))
    out.append(T_h("试穿与尺码", "FITTING & SIZES"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I'm just looking, thanks.", "我随便看看"),
             "店员问 Can I help you? 时的标准回答"],
            [("Can I try this on?", "能试穿吗？"),
             "问试衣间：Where is the fitting room?"],
            [("Do you have a smaller / larger size?", "有小一码 / 大一码的吗？"),
             "颜色：Do you have this in blue?"],
            [("What size is this?", "这是几码？"),
             "欧美尺码和国内不同，直接报数字最稳"],
            [("Could you take my measurements?", "能帮我量一下尺寸吗？"),
             "原手册提示：不知道自己尺码时用这句"],
        ],
    ))
    out.append(T_h("价格与付款", "PRICE & PAYMENT"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("How much is this?", "这个多少钱？"),
             "明码标价的商店也可不问直接看标签"],
            [("Is this on sale? / Do you have any discounts?", "这个打折吗？ / 有折扣吗？"),
             "黑色星期五、季末折扣是购物季"],
            [("It's a little pricey.", "有点贵"),
             "砍价：Can you give me a better price?"],
            [("Can I pay by card?", "能刷卡吗？"),
             "Apple Pay / 支付宝：Do you accept Apple Pay / Alipay?"],
        ],
    ))
    out.append(T_h("退换与退税", "RETURNS & TAX REFUND"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I'd like to return this.", "我想退货"),
             "换货：Could I exchange this for a larger size?"],
            [("Could I get a receipt?", "请给我小票"),
             "小票 = receipt，退税和退货都要"],
            [("Is this tax-free?", "这个是免税的吗？"),
             "免税店：duty-free；退税：tax refund"],
            [("Could I get a tax refund form?", "请给我退税单"),
             "问门槛：What's the minimum for tax refund?"],
            [("Disposable / single-use items", "一次性用品（如一次性雨衣、剃须刀）"),
             "Do you sell disposable raincoats? 就能买到"],
        ],
    ))
    out.append(T_tip("退税流程",
                     "欧盟、日本等多国需离境时在机场出示商品 + 小票 + 退税单；商品吊牌先别拆，单据拍照存档。"))
    return "\n".join(out)


def page_08():
    out = [T_section("08", "沟通与求助", "COMMUNICATION & HELP")]
    out.append(T_key(
        "听不懂是常态，不是失败。三句万能话术 + 手机翻译，能让任何对话继续下去。",
        "原手册建议“I am not good at English”——不必自我贬低，直接说 Could you speak more slowly? 效果更好。"
    ))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Sorry? / Pardon?", "请再说一遍（用疑问语气）"),
             "最常用的救场句"],
            [("Could you say that again, please?", "能再说一遍吗？"),
             "比 Sorry 更礼貌完整"],
            [("Could you speak more slowly, please?", "能说慢一点吗？"),
             "对方语速快了就用这句"],
            [("Could you write it down?", "能写下来吗？"),
             "地名、号码听不懂就请对方写"],
            [("Could you show me on the map?", "能在地图上指给我看吗？"),
             "把手机地图打开给对方看"],
            [("What does … mean?", "……是什么意思？"),
             "填入不认识的词：What does “gate” mean?"],
            [("Do you mean …?", "您是说……吗？"),
             "确认理解：Do you mean Gate 3?"],
            [("Excuse me, could you help me?", "请问能帮我一下吗？"),
             "万能求助开场白"],
            [("Thank you so much!", "非常感谢！"),
             "礼貌收尾，好感翻倍"],
        ],
    ))
    out.append(T_tip("翻译 App 的正确用法",
                     "打开翻译 App 说 Listen（听我说话），或直接请对方对着手机说话，可实时双向翻译；"
                     "配合手势和表情，比纠结语法更高效。"))
    return "\n".join(out)


def page_09():
    out = [T_section("09", "应急场景", "EMERGENCIES")]
    out.append(T_key(
        "应急时先保证安全和信息：报警电话、使领馆电话、保险电话提前存在手机里，出事按顺序打。",
        "中国外交部全球领事保护与服务应急热线 12308（海外 +86-10-12308）存进通讯录。"
    ))
    out.append(T_h("生病与买药", "SICKNESS & MEDICINE"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I don't feel well.", "我不舒服"),
             "描述症状：I have a fever（发烧）/ headache（头痛）/ stomachache（肚子痛）"],
            [("Where's the nearest pharmacy?", "最近的药店在哪里？"),
             "药店招牌 Pharmacy / Chemist's"],
            [("I need to see a doctor.", "我要看医生"),
             "急诊：emergency room（美国 ER / 英国 A&E）"],
            [("Could you call an ambulance?", "能帮我叫救护车吗？"),
             "当地急救电话：911（美国）/ 999（英国）/ 112（欧盟）"],
            [("Do you have medicine for a cold?", "有感冒药吗？"),
             "把症状词 + medicine for 套用即可"],
        ],
    ))
    out.append(T_h("遗失与失窃", "LOST & STOLEN"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I lost my passport.", "我的护照丢了"),
             "补办流程：报警拿回执 → 去中国使领馆办旅行证"],
            [("Where is the police station?", "派出所在哪里？"),
             "I need a police report. 报警回执是理赔和补证必需"],
            [("My credit card was stolen.", "我的信用卡被偷了"),
             "马上打银行电话冻结：Please block my card."],
            [("Could I use your phone?", "能用一下您的电话吗？"),
             "手机也丢了的备用方案"],
        ],
    ))
    out.append(T_h("保险与使领馆", "INSURANCE & EMBASSY"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("I'd like to file an insurance claim.", "我要报案理赔"),
             "先打保单上的紧急电话，再按指引就医并保留单据"],
            [("Here's my insurance policy number.", "这是我的保单号"),
             "保单号提前存在手机里"],
            [("Where is the Chinese embassy / consulate?", "中国大使馆 / 领事馆在哪里？"),
             "使领馆电话提前存好，紧急时直接拨"],
        ],
    ))
    out.append(T_tip("出发前的备份",
                     "护照页、签证、保单、信用卡背面电话各拍一张，存手机相册 + 云端 + 微信文件传输助手三处。"))
    return "\n".join(out)


def page_app_a():
    out = [T_section("A", "附录 A · 万能句型", "5 FORMULAS THAT ALWAYS WORK")]
    out.append(T_key(
        "五个句式覆盖 80% 的日常请求，把名词换掉就能用。",
        "记不住整句时，用“关键词 + 手势”也能达到目的；重点是敢开口。"
    ))
    out.append(T_table(
        ["公式", "例句"],
        [
            [("Could I + have / ask …?", "Could I have the menu, please?"),
             "请求句式，最礼貌通用"],
            [("Can you + help / tell / show …?", "Can you help me?"),
             "向任何人求助的万能句"],
            [("I'd like + 名词 / to 动词", "I'd like to check out."),
             "表达需求：I'd like a taxi."],
            [("Where is + 名词?", "Where is the restroom?"),
             "问地点，最常用"],
            [("How much + is / are …?", "How much is this?"),
             "问价格，购物必用"],
        ],
    ))
    out.append(T_h("三句万能救场", "IF YOU GET STUCK"))
    out.append(T_pair("Could you say that again, please?", "请再说一遍"))
    out.append(T_pair("Could you speak more slowly, please?", "请说慢一点"))
    out.append(T_pair("Excuse me, I need help.", "不好意思，我需要帮助"))
    return "\n".join(out)


def page_app_b():
    out = [T_section("B", "附录 B · 数字、时间与方向", "NUMBERS · TIME · DIRECTIONS")]
    out.append(T_key(
        "数字和时间是订票、问价、约时间的共同底座，听错一个数就可能误事。",
        "重点掌握 13/30、14/40 这类易混读音：-teen 重音在后，-ty 重音在前。"
    ))
    out.append(T_h("数字速记", "NUMBERS"))
    out.append(T_table(
        ["数字", "读法"],
        [
            [("0–10", "zero, one, two, three, four, five, six, seven, eight, nine, ten"),
             "0 读 zero，美国人常读 oh"],
            [("11–19", "eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen"),
             "-teen 重音在最后"],
            [("20–90", "twenty, thirty, forty, fifty, sixty, seventy, eighty, ninety"),
             "-ty 重音在前；forty 无 u"],
            [("100 / 1,000", "one hundred / one thousand"),
             "价格：$15.99 = fifteen ninety-nine"],
        ],
    ))
    out.append(T_h("时间与日期", "TIME & DATES"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("What time is it?", "现在几点？"),
             "回答：It's three thirty.（3:30）"],
            [("a.m. / p.m.", "上午 / 下午"),
             "3 p.m. = 下午三点；欧洲常用 15:00（fifteen hundred）"],
            [("July 20th / the 20th of July", "7 月 20 日"),
             "订票时把日期说清楚：on the twentieth of July"],
            [("Until July 20th.", "待到 7 月 20 日"),
             "边检、酒店都常用"],
        ],
    ))
    out.append(T_h("方向词", "DIRECTIONS"))
    out.append(T_table(
        ["English", "中文"],
        [
            [("Go straight / straight ahead", "直走"),
             "问路回答第一句"],
            [("Turn left / Turn right", "左转 / 右转"),
             "At the traffic lights 在红绿灯处"],
            [("On your left / right", "在您的左手边 / 右手边"),
             "It's on your left. 就是“在左边”"],
            [("Next to / across from", "紧挨着 / 在对面"),
             "描述地标位置"],
            [("Around the corner", "拐角处"),
             "很近的表示"],
            [("About a 10-minute walk", "步行约 10 分钟"),
             "代替距离单位"],
        ],
    ))
    return "\n".join(out)


def page_app_c():
    out = [T_section("C", "附录 C · 目的地差异速查", "DESTINATION QUICK REFERENCE")]
    out.append(T_key(
        "小费、支付、插座、卫生间用词因国而异，出发前查一眼就能避免尴尬。",
        "下表为简化参考，实际以当地最新习惯为准；账单含 service charge 时通常无需再给小费。"
    ))
    out.append(T_table(
        ["目的地", "小费", "支付习惯", "插座 / 电压", "卫生间用词"],
        [
            ["美国", "餐馆 15–20%，打车 10–15%", "信用卡 / Apple Pay 为主", "A/B 两脚扁 · 110V", "restroom"],
            ["英国", "餐馆 10–12.5%（常已含服务费）", "银行卡 / 非接触支付", "G 三脚 · 230V", "toilet / WC"],
            ["欧洲大陆", "通常含服务费，可留 0–10%", "刷卡为主，现金零钱备用", "C/F 两脚圆 · 230V", "WC / toilet"],
            ["日本", "无小费", "现金 + IC 卡 + 扫码并存", "A/B 两脚扁 · 100V", "トイレ / toilet"],
            ["泰国等东南亚", "可留零钱或不给", "现金 + 扫码支付", "A/C 两脚 · 220V", "toilet"],
            ["中东（阿联酋等）", "部分含服务费，可留约 10%", "信用卡为主", "C/G · 220V", "WC"],
        ],
    ))
    out.append(T_h("转换插头怎么看", "ADAPTERS"))
    out.append(T_pair("A/B = 北美（美加日）；C/F = 欧洲大陆；G = 英标（英国、新加坡、香港）",
                      "看插头字母买转换器；手机充电器一般支持 100–240V 宽电压，无需变压器。"))
    out.append(T_tip("出行前 3 分钟",
                     "把目的地 小费习惯、急救电话、插座类型 三件事查好存备忘录，落地不慌。"))
    return "\n".join(out)


# ---------------------------------------------------------------- render
def build():
    parts = [
        page_cover(),
        page_howto(),
        page_insights(),
        page_01(),
        page_02(),
        page_03(),
        page_04(),
        page_05(),
        page_06(),
        page_07(),
        page_08(),
        page_09(),
        page_app_a(),
        page_app_b(),
        page_app_c(),
    ]
    md_out = GEN_DIR / f"{OUT_NAME}.md"
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out.write_text("\n".join(parts), encoding="utf-8")

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
        "    page.render(scale=1.4).to_pil().save(r'" + str(PREVIEW / "travel_prev_") + "' + str(i) + '.png')\n"
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

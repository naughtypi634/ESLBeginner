"""Generate the Travel English Phrases handbook (blue, 2 pages per chapter, curated content)."""
import base64
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(r"F:\AI project\ESLBeginner\MD")
OUT_HTML = ROOT / "ESL-travel english phrases (美化版).html"
FONT_CACHE = ROOT / "_fonts_cache"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)
FAMILIES = (
    "Playfair+Display:wght@700;800"
    "&family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500"
)
CSS_URL = f"https://fonts.googleapis.com/css2?family={FAMILIES}&display=swap"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last


def cached_font(key: str, url: str) -> bytes:
    FONT_CACHE.mkdir(exist_ok=True)
    path = FONT_CACHE / f"{key}.woff2"
    if not path.exists():
        path.write_bytes(fetch(url))
    return path.read_bytes()


def font_css() -> str:
    css = fetch(CSS_URL).decode("utf-8")
    blocks = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)
    out = []
    for b in blocks:
        ur = re.search(r"unicode-range:\s*([^;]+);", b)
        if ur and "U+0000-00FF" not in ur.group(1):
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", b).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", b).group(1)
        style = re.search(r"font-style:\s*(\w+)", b).group(1)
        src = re.search(r"url\((https://[^)]+\.woff2)\)", b).group(1)
        key = f"{fam}-{weight}-{style}".replace(" ", "-")
        data = base64.b64encode(cached_font(key, src)).decode("ascii")
        out.append(
            f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
            f"font-display:swap;src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    return "\n".join(out)


CSS = """
:root{
  --ink:#1F2C34;
  --paper:#FFFFFF;
  --acc:#1D5FA8;
  --acc-deep:#12406F;
  --acc-line:rgba(29,95,168,.30);
  --line:#E5E5E0;
  --soft:#66727B;
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{background:#D8D8D2;}
body{font-family:'Inter','Segoe UI',Verdana,sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased;}

@page{size:A4;margin:12mm 12mm 13mm;}

.book{background:var(--paper);}
@media screen{
  .book{width:210mm;min-height:297mm;margin:9mm auto;padding:12mm 12mm 13mm;box-shadow:0 10px 34px rgba(45,35,20,.18);}
}
@media print{
  html,body{background:#fff;}
  .book{width:auto;min-height:0;margin:0;padding:0;box-shadow:none;}
}

/* ---------- cover ---------- */
.cover{page-break-after:always;text-align:center;}
.cover .frame{border:1.4px solid var(--ink);padding:3mm;margin-top:6mm;}
.cover .inner{border:0.5px solid var(--acc);padding:18mm 10mm 14mm;}
.cover .plane svg{width:11mm;height:11mm;stroke:var(--acc);}
.cover .kicker{font-size:8pt;letter-spacing:4.5px;text-transform:uppercase;color:var(--acc-deep);font-weight:700;margin:6mm 0 9mm;}
.cover h1{font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-weight:800;font-size:34pt;line-height:1.14;color:var(--ink);}
.cover .orn{display:flex;align-items:center;justify-content:center;gap:3.5mm;margin:10mm 0 12mm;}
.cover .orn::before,.cover .orn::after{content:"";width:17mm;height:0.4mm;background:var(--line);}
.cover .orn .d{width:1.7mm;height:1.7mm;background:var(--acc);transform:rotate(45deg);}
.cover .sub{font-size:9.5pt;font-style:italic;color:var(--soft);margin-bottom:12mm;}
.cover .foot{font-size:7.5pt;letter-spacing:3px;text-transform:uppercase;color:var(--soft);font-weight:700;}

/* ---------- contents ---------- */
.toc{page-break-after:always;}
.toc h2{font-family:'Playfair Display',Georgia,serif;font-size:20pt;text-align:center;margin:8mm 0 4mm;font-weight:700;}
.toc .note{text-align:center;font-size:9pt;font-style:italic;color:var(--soft);margin-bottom:8mm;}
.toc-list{max-width:128mm;margin:0 auto;}
.toc-item{display:flex;align-items:baseline;gap:5mm;padding:3.2mm 0;font-size:12pt;font-weight:600;}
.toc-item .n{font-family:'Playfair Display',Georgia,serif;font-weight:800;color:var(--acc);font-size:11pt;width:9mm;text-align:right;flex:none;}
.toc-item .d{margin-left:auto;font-size:8pt;letter-spacing:1.5px;text-transform:uppercase;color:var(--soft);font-weight:600;}

/* ---------- chapter pages ---------- */
.cpage{page-break-after:always;}
.chapter:last-of-type .cpage:last-of-type{page-break-after:auto;}

.ch-head{position:relative;display:flex;align-items:baseline;gap:4mm;padding-bottom:2.4mm;border-bottom:0.5px solid var(--ink);margin-bottom:5.5mm;}
.ch-head::after{content:"";position:absolute;left:0;right:0;bottom:-1.4px;height:2px;background:var(--acc);}
.ch-num{font-family:'Playfair Display',Georgia,serif;font-weight:800;font-size:20pt;color:var(--acc);line-height:1;}
.ch-title{font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:16pt;color:var(--ink);line-height:1.1;}
.ch-part{margin-left:auto;font-size:7.5pt;letter-spacing:2.4px;text-transform:uppercase;color:var(--acc-deep);font-weight:700;}

/* words & phrases page */
.wlabel{display:flex;align-items:center;gap:4mm;font-size:8pt;letter-spacing:2.5px;text-transform:uppercase;font-weight:700;color:var(--acc);
  margin:5mm 0 2.6mm;page-break-after:avoid;break-after:avoid;}
.wgrid{display:grid;grid-template-columns:1fr 1fr;column-gap:9mm;}
.witem{display:flex;align-items:baseline;justify-content:space-between;gap:3mm;
  padding:2.6mm 0;font-size:11pt;font-weight:600;page-break-inside:avoid;break-inside:avoid;}
.witem .hint{font-size:9.2pt;font-style:italic;font-weight:500;color:var(--soft);text-align:right;}

/* sentences page */
.slabel{display:flex;align-items:center;gap:4mm;font-size:8pt;letter-spacing:2.5px;text-transform:uppercase;font-weight:700;color:var(--acc);
  margin:5mm 0 2.6mm;page-break-after:avoid;break-after:avoid;}
.sgroup:first-of-type .slabel{margin-top:0;}
.sitem{display:grid;grid-template-columns:8mm 1fr;gap:2mm;padding-bottom:1.9mm;margin-bottom:1.9mm;
  page-break-inside:avoid;break-inside:avoid;}
.sno{font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:9.4pt;color:var(--acc);text-align:right;padding-top:0.8mm;}
.main{font-size:11.1pt;font-weight:600;line-height:1.45;}
.ex{font-size:9.6pt;font-style:italic;color:var(--soft);margin-top:0.9mm;line-height:1.45;}
.subs{margin:1.3mm 0 0;display:flex;flex-direction:column;gap:1.2mm;}
.subs.cols{display:grid;grid-template-columns:1fr 1fr;column-gap:6mm;}
.sub{display:flex;gap:2.2mm;font-size:10.2pt;color:#4B5760;line-height:1.45;}
.sub::before{content:"";width:1.4mm;height:1.4mm;background:var(--acc);opacity:.5;flex:none;margin-top:2mm;}
.sub .t{font-weight:600;color:var(--ink);}
.sub .e{font-style:italic;color:var(--soft);}
"""


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_words(ch) -> str:
    out = ['<div class="cpage">']
    out.append(
        f'<header class="ch-head"><span class="ch-num">{ch["num"]}</span>'
        f'<h2 class="ch-title">{esc(ch["title"])}</h2>'
        '<span class="ch-part">Words &amp; Phrases</span></header>'
    )
    for label, terms in ch["words"]:
        items = []
        for t in terms:
            if isinstance(t, tuple):
                term, hint = t
                hint_html = f'<span class="hint">{esc(hint)}</span>' if hint else ""
            else:
                term, hint_html = t, ""
            items.append(f'<div class="witem"><span>{esc(term)}</span>{hint_html}</div>')
        out.append(
            f'<div class="wgroup"><h3 class="wlabel">{esc(label)}</h3>'
            f'<div class="wgrid">{"".join(items)}</div></div>'
        )
    out.append("</div>")
    return "\n".join(out)


def render_sentences(ch) -> str:
    out = ['<div class="cpage">']
    out.append(
        f'<header class="ch-head"><span class="ch-num">{ch["num"]}</span>'
        f'<h2 class="ch-title">{esc(ch["title"])}</h2>'
        '<span class="ch-part">Useful Sentences</span></header>'
    )
    n = 0
    for label, items in ch["sentences"]:
        rows = []
        for it in items:
            n += 1
            if isinstance(it, str):
                main, subs, ex = it, None, None
            else:
                main, subs, ex = (list(it) + [None, None])[:3]
            body = f'<p class="main">{esc(main)}</p>'
            if ex:
                body += f'<p class="ex">{esc(ex)}</p>'
            if subs:
                def sub_html(s):
                    if isinstance(s, tuple):
                        return (f'<div class="sub"><span class="t">{esc(s[0])}</span>'
                                f'<span class="e">{esc(s[1])}</span></div>')
                    return f'<div class="sub"><span>{esc(s)}</span></div>'
                sub_rows = "".join(sub_html(s) for s in subs)
                cls = "subs cols" if len(subs) >= 5 else "subs"
                body += f'<div class="{cls}">{sub_rows}</div>'
            rows.append(f'<div class="sitem"><span class="sno">{n:02d}</span><div>{body}</div></div>')
        out.append(
            f'<div class="sgroup"><h3 class="slabel">{esc(label)}</h3>{"".join(rows)}</div>'
        )
    out.append("</div>")
    return "\n".join(out)


CHAPTERS = [
    dict(num="01", title="At the Airport",
        words=[
            ("Check-in & documents", ["check in", "boarding pass", "boarding gate",
                                      "passport", "visa", "flight number", "identification (ID)",
                                      "book (a ticket)"]),
            ("Baggage", ["luggage", "carry-on bag", "checked bag", "baggage claim", "luggage cart",
                         "fragile", "liquids", "overweight"]),
            ("Airport places", ["terminal", "gate", "departures", "arrivals", "duty-free shop",
                                "tax refund", "currency exchange", "restroom", "information desk"]),
            ("People & services", ["flight attendant", "pilot", "security check",
                                   "travel agency"]),
            ("Flight status", ["airline", "flight", "on time", "delayed", "canceled",
                               "layover / stopover", "connecting flight"]),
        ],
        sentences=[
            ("Asking for help", [
                ("Excuse me, how do I…?", [("Check in.", "How do I get to the check-in counter?")]),
                ("Where is the…?", ["Information desk / center.", "Boarding gate.",
                                    ("Restroom.", "Also called a bathroom, washroom, men’s room, lady’s room."),
                                    "Duty-free shop.", "Charging station.",
                                    "Restaurant / Coffee shop / Café / Cafeteria.",
                                    "Convenience store.", "Supermarket.", "Tax refund."]),
                "How do I get to…?",
                "Could you say that again, please?",
            ]),
            ("Check-in & baggage", [
                "What time is my flight?",
                "Is this the right line for check-in?",
                "How much luggage am I allowed to carry on?",
                "Can I take this bag on the plane?",
                "Do I need to check this bag in?",
                "I’d like a window seat, please.",
                "Is my baggage overweight?",
            ]),
            ("Flight information", [
                "Which terminal does my flight leave from?",
                "Where is the boarding gate for flight …?",
                "What time does boarding start?",
                "Is my flight on time? / Has my flight been delayed?",
                "How long is the layover?",
                "Are meals included?",
            ]),
        ]),

    dict(num="02", title="On the Airplane",
        words=[
            ("Seat & cabin", ["seat", "seat belt", "window seat", "aisle seat", "recline button",
                              "charging port", "blanket", "pillow", "headphones", "aisle",
                              "lavatory / restroom", "overhead bin", "emergency exit", "boarding"]),
            ("Food & drink", ["meal", "snack", "beverage / drink", "water", "coffee", "tea"]),
            ("The journey", ["takeoff", "landing", "flight attendant", "captain", "crew", "in-flight"]),
            ("Tickets & seats", ["first class", "business class", "economy class", "upgrade"]),
            ("Feelings", ["airsick", "dizzy", "sick", "pain", "medicine", "sick bag"]),
        ],
        sentences=[
            ("Getting settled", [
                "Excuse me, can you please help me put my luggage away?",
                "Can you help me with my luggage?",
                "Can I please change my seat? / Can we swap / switch seats?",
                "Where is my seat? / Which seat is mine?",
                "Could you help me fasten my seat belt?",
                ("Does my seat have…?", ["a charging port", "a recline button"]),
            ]),
            ("Making requests", [
                ("I would like…, please.", None, "I would like a glass of water, please."),
                "Could I have a blanket / a pillow / a pair of headphones, please?",
                ("Excuse me, I need to…", ["use the restroom", "get off the plane"]),
                "I’d like something to drink, please.",
                "Is there Wi-Fi on this flight?",
                "Can I use my phone during the flight?",
                "Can I recline my seat?",
            ]),
            ("The journey", [
                "Could you tell me when we are landing?",
                "What time do we arrive?",
                "Could you wake me up before we land, please?",
            ]),
            ("Feeling unwell", [
                "I feel a little airsick. Do you have any medicine or a sick bag?",
            ]),
        ]),

    dict(num="03", title="Arrival & Customs",
        words=[
            ("Money", ["currency", "exchange rate", "cash", "credit card", "money change", "bank", "ATM"]),
            ("Documents", ["passport", "visa", "customs", "immigration", "declaration form",
                           "personal use", "gifts"]),
            ("At the airport", ["arrival", "baggage claim", "luggage cart", "exit", "arrivals hall",
                                "hotel shuttle", "taxi stand"]),
            ("Transport onward", ["taxi", "bus", "subway", "train", "ride", "address", "driver"]),
            ("Useful words", ["declare", "duty-free", "prohibited", "allowed", "fine", "officer"]),
        ],
        sentences=[
            ("Finding your way", [
                ("Where is the…?", ["Baggage claim area.", "Currency exchange / Money change.",
                                    "Taxi / taxi stand.", "Hotel shuttle.", "Immigration or customs."]),
                "How do I get to…?",
                "Where can I find a luggage cart?",
                "Where can I exchange money?",
                "I’d like to exchange some money, please.",
            ]),
            ("Asking for help", [
                "Sorry, I do not understand what you are saying.",
                "I do not speak English very well.",
                "Please speak slowly.",
                "Could you say that again, please?",
            ]),
            ("Immigration & customs", [
                ("I am traveling for…", ["Leisure / Pleasure / Sightseeing.", "Work / Business.",
                                         "Family.", "Study."]),
                "I will be / I am staying here for … days.",
                "I am staying at…",
                "Here is my passport.",
                "I have nothing to declare. / I have something to declare.",
                "These are for my personal use. / These are gifts.",
                "Do I need to pay tax on this?",
                "How long can I stay in the country?",
            ]),
        ]),

    dict(num="04", title="Transportation",
        words=[
            ("Public transport", ["bus", "subway / metro", "train", "tram", "ferry", "taxi",
                                  "ride-hailing app"]),
            ("Stops & tickets", ["bus stop", "subway station", "ticket", "ticket machine", "ticket office",
                                 "fare", "fare card", "transfer", "one-way", "round-trip", "platform"]),
            ("On the way", ["line / route", "get on", "get off", "change (lines)", "next stop",
                            "seat", "rush hour", "timetable / schedule", "passenger", "exit"]),
            ("Taxis & rides", ["meter", "address", "driver", "ride", "tip", "traffic", "drop off",
                               "map"]),
        ],
        sentences=[
            ("Public transport", [
                "Does this go to…?",
                "Which bus / train / line should I take to get to…?",
                "Where is the nearest bus stop / subway station?",
                "Where can I buy a ticket?",
                "One ticket to…, please.",
                "How much is the fare?",
                ("Do you accept…? / Can I use…?", ["cash", "credit card", "Alipay", "WeChat Pay"]),
                "How long does it take to get to…?",
                "Could you tell me when we get to…?",
                "Where should I get off for…?",
                "I would like to get off at the next stop.",
                "Excuse me, is this seat taken?",
                "Do I need to change buses / trains?",
            ]),
            ("Taxis & rides", [
                "Could you call me a taxi, please?",
                "Could you take me to this address, please?",
                "How much will it cost to get to…? Please turn on the meter.",
                "Please stop here. Thank you.",
                "How much do I owe you? Keep the change.",
            ]),
        ]),

    dict(num="05", title="At the Hotel",
        words=[
            ("Booking & check-in", ["reservation / booking", "check-in", "check-out",
                                    "front desk / reception", "key card", "room number",
                                    "late check-out", "cancellation", "deposit"]),
            ("Rooms", ["single room", "double room", "twin room", "suite", "floor", "elevator",
                       "view", "air conditioner", "shower"]),
            ("Room items", ["bedsheets", "pillow", "blanket", "towel", "toilet paper",
                            "fridge / mini-bar", "Wi-Fi", "TV", "hair dryer"]),
            ("Services", ["room service", "wake-up call", "laundry", "luggage storage",
                          "breakfast", "buffet", "housekeeping", "parking"]),
        ],
        sentences=[
            ("Checking in", [
                "I’m here to check in. I have a reservation / booking under the name of…",
                "Do you have a room available for tonight?",
                "What time is check-in / check-out?",
                "Could I check in early? / Could I check out late?",
                "I’d like to extend my stay for one more night.",
                "What floor am I on?",
            ]),
            ("Room needs", [
                ("Does the room have a…?", ["Fridge / mini-bar.", "Wi-Fi.", "Air conditioner."]),
                ("Can you help me with the Wi-Fi?", None,
                 "The Wi-Fi doesn’t work. / The Wi-Fi isn’t working. / What is the Wi-Fi password?"),
                ("My room needs…", ["Towels.", "Toilet paper.", "Bedsheets.", "Bottled water."]),
                "Could I please have room service?",
                "Could I have an extra key card / blanket / pillow, please?",
                "The air conditioner / TV / shower isn’t working.",
            ]),
            ("Breakfast & nearby places", [
                "Is breakfast included?",
                "What time is breakfast served?",
                "Can I leave my luggage here until checkout?",
                ("Where is the best / nearest … around here?", ["Supermarket.", "Pharmacy / Drug store.",
                                                                "Restaurant.", "Bank / ATM."]),
            ]),
        ]),

    dict(num="06", title="At a Restaurant",
        words=[
            ("The menu", ["menu", "appetizer / starter", "soup", "salad", "main course", "side dish",
                          "dessert", "drink", "special"]),
            ("Ordering", ["table", "order", "recommend", "waiter / waitress", "chef", "refill",
                          "takeaway / to go"]),
            ("Taste & food", ["spicy", "mild", "sweet", "sour", "salty", "hot", "vegetarian", "vegan"]),
            ("Allergies", ["allergy", "nuts", "seafood", "gluten", "dairy", "peanuts"]),
            ("Paying", ["bill / check", "tip", "service charge", "receipt", "cash", "credit card"]),
        ],
        sentences=[
            ("Ordering", [
                "A table for two, please.",
                "Could we sit outside / by the window, please?",
                "May I see a menu, please?",
                "I would like to order, please.",
                "Could you recommend some popular dishes?",
                "What’s your best / top-seller? / What’s your special?",
                "Do you have vegetarian options?",
                ("Can I please have…?", ["A glass of water.", "Extra sauce / salt / spice / ice.",
                                         "Appetizer / Starter.", "Dessert."]),
                "Is this dish spicy? / Could you make it less spicy?",
            ]),
            ("More requests", [
                "Can I ask for a refill? / Can I have another one?",
                "Could I order this to go / for takeaway, please?",
            ]),
            ("Allergies & special needs", [
                ("I have a food allergy. I am allergic to…", ["nuts", "seafood", "gluten", "dairy"]),
                "Could I have a menu in English / Chinese, please?",
            ]),
            ("Paying", [
                "May I have the bill / check, please?",
                "Could we split the bill?",
                "Is the tip included? / Is there a service charge?",
                "Could I pay by card?",
            ]),
        ]),

    dict(num="07", title="Shopping",
        words=[
            ("Shops & places", ["store / shop", "supermarket", "department store", "shopping mall",
                                "market", "gift shop", "pharmacy", "cashier"]),
            ("Products", ["size", "color", "price", "receipt", "refund", "exchange",
                          "fitting room", "bag"]),
            ("Buying & payment", ["buy", "pay", "cash", "credit card", "WeChat Pay", "Alipay",
                                  "discount", "sale"]),
            ("Describing", ["bigger", "smaller", "cheaper", "expensive", "in stock", "out of stock",
                            "another one"]),
            ("Clothes", ["try on", "fit", "tight", "loose"]),
        ],
        sentences=[
            ("Looking for things", [
                "Excuse me, where can I find…?",
                "Where is the fitting room?",
                "I’m just looking, thank you.",
                "Could you show me that one, please?",
            ]),
            ("Prices & discounts", [
                "Excuse me, how much is this?",
                "Is this on sale? / Do you have a sale?",
                "Can you give me a better price?",
                "Is there a discount if I buy two?",
                "Do you have this in another color / size?",
                "Does this come in a bigger / smaller size?",
            ]),
            ("Trying & buying", [
                "Can I try this on?",
                "What forms of payment do you accept?",
                "Can I pay by card? / Do you accept Alipay / WeChat Pay?",
                "Could I have a receipt, please?",
                "Could you wrap it as a gift, please?",
                "Where is the cashier?",
            ]),
            ("Returns", [
                "What is your return and exchange policy?",
                "It doesn’t fit. Could I exchange it?",
                "Is there a tax refund service here?",
            ]),
        ]),

    dict(num="08", title="Sightseeing",
        words=[
            ("Places", ["tourist information center", "museum", "gallery", "park", "temple",
                        "castle", "beach", "landmark", "viewpoint", "entrance"]),
            ("Tickets & tours", ["ticket", "entrance fee", "discount", "student", "senior", "free",
                                 "guided tour", "audio guide", "map", "city pass", "exhibition"]),
            ("Time & rules", ["open", "close", "opening hours", "rules", "restrictions", "photography"]),
            ("Activities", ["sightseeing", "festival", "event", "show", "photo", "camera",
                            "guide", "souvenir"]),
        ],
        sentences=[
            ("Information", [
                "Where is the visitor / tourist information center?",
                "Do you have a map of the city?",
                "Are there any guided tours for this area?",
                "What do you recommend seeing around here?",
            ]),
            ("Tickets & rules", [
                "Where can I buy tickets? / How much is the entrance fee?",
                "Is there a discount for students / seniors?",
                "What time does it open / close?",
                "Is photography allowed inside?",
                "Are there any rules and restrictions / taboos I should know?",
                "Is the museum free?",
            ]),
            ("Around town", [
                "Can you take a photo of me in front of…? / Could you take a photo for us, please?",
                "Are there any events or festivals around here?",
                "How far is it from here? Can I walk there?",
                "Is it safe to walk around here at night?",
                "Are there restrooms nearby?",
                "Is there an audio guide?",
                "Where can I buy a city pass?",
                "Where can I buy souvenirs?",
                "What time does the last bus leave?",
                "Can I pay by card here?",
            ]),
        ]),

    dict(num="09", title="Emergencies",
        words=[
            ("Getting help", ["help", "emergency", "emergency number", "police", "ambulance",
                              "fire", "thief", "accident", "doctor", "hospital"]),
            ("Health", ["pain", "dizzy", "faint", "sick", "injured", "allergic", "bleeding",
                        "medicine", "pharmacy / drug store"]),
            ("Lost items", ["lost", "stolen", "missing", "wallet", "passport", "phone", "keys"]),
            ("Key verbs", ["call", "stay", "find", "need", "translate", "embassy", "insurance",
                           "first aid", "hurt"]),
        ],
        sentences=[
            ("Getting help", [
                "Help!",
                "Call the police, please! / Call an ambulance, please!",
                "There has been an accident.",
                "I need a doctor. / Where is the nearest hospital?",
                "Please help me. / Please stay with me.",
                "Fire! / Thief!",
                "I was robbed. / Someone stole my bag.",
                "Please call my hotel / my family.",
            ]),
            ("Health", [
                ("I feel…", ["Dizzy / Faint.", "Sick."]),
                "I am in pain.",
                "I need some medicine. / Where is a pharmacy or drug store near here?",
                "I am allergic to… and I need medical help.",
            ]),
            ("Lost items & safety", [
                ("I have lost my…", ["Wallet.", "Passport.", "Phone.", "Keys.", "Luggage."]),
                "My passport has been stolen.",
                "I’m lost. Can you help me find this address?",
                "I can’t find my child / my friend.",
                "Where is the emergency exit?",
            ]),
        ]),
]


def build() -> str:
    parts = ['<!DOCTYPE html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             '<title>Travel English Phrases</title>', '<style>', font_css(), CSS, '</style>',
             '</head>', '<body>', '<div class="book">']

    parts.append("""
<section class="cover">
  <div class="frame">
    <div class="inner">
      <div class="plane"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg></div>
      <p class="kicker">Phrasebook</p>
      <h1>Travel English<br>Phrases</h1>
      <div class="orn"><span class="d"></span></div>
      <p class="sub">Essential phrases for your journey</p>
      <p class="foot">Travel English Phrases</p>
    </div>
  </div>
</section>
""")

    toc_items = []
    for ch in CHAPTERS:
        toc_items.append(
            f'<div class="toc-item"><span class="n">{ch["num"]}</span>'
            f'<span>{esc(ch["title"])}</span><span class="d">Words &amp; Sentences</span></div>'
        )
    parts.append(
        '<section class="toc"><h2>Contents</h2>'
        '<p class="note">Each chapter has one page of words &amp; phrases and one page of useful sentences.</p>'
        f'<div class="toc-list">{"".join(toc_items)}</div></section>'
    )

    for ch in CHAPTERS:
        parts.append("<section class=\"chapter\">")
        parts.append(render_words(ch))
        parts.append(render_sentences(ch))
        parts.append("</section>")

    parts.append("</div></body></html>")
    return "\n".join(parts)


if __name__ == "__main__":
    OUT_HTML.write_text(build(), encoding="utf-8")
    print("written:", OUT_HTML)

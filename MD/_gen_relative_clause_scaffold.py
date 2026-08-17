"""Generate Relative Clause 定语从句练习 PDF (90 complete opinion sentences).

3 themes x 30 sentences = 90, content only (no track/ladder labels).
Every sentence is complete (原因/细节写清楚), replaceable parts marked
with 下划线 (【…】). Each item shows 拆分两句 -> 合成句 + 试试换成提示.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "PDF"
MD_DIR = ROOT / "MD"
sys.path.insert(0, str(ROOT))
from build.student_copy import make_student_copy


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Render HTML to PDF with Playwright if available; else skip."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    html_content = html_path.read_text(encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.wait_for_selector(".page", state="visible", timeout=10000)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(pdf_path),
            width="210mm",
            height="297mm",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()
    return True

# ═══════════════════════════════════════════════════════════════════════
#  CONTENT: (cn_with_hl, split_two_sentences, en_with_hl)
#  {…}  = relative clause (粗体)
#  【…】 = replaceable part (下划线), may nest inside {…}
# ═══════════════════════════════════════════════════════════════════════

TRACKS = [
    {
        "tag": "TRACK A",
        "title": "我想要的 · What I Want",
        "subtitle": "说说你想要的老板、伴侣、工作与生活",
        "task": "表达任务：把下划线部分换成你自己的版本，用同一句式说出口：I want a … who / that …",
        "ladders": {
            "L1": [
                (
                    "我想要一个【{靠谱、有耐心、肯带人}】的老板。",
                    "我想要一个老板。他要靠谱、有耐心、肯带人。",
                    "I want a boss {who is 【reliable, patient, and willing to teach】}.",
                ),
                (
                    "我理想中的另一半，是{【愿意主动沟通、而不是让我猜】}的人。",
                    "我理想中的另一半是这样的人。他愿意主动沟通，而不是让我猜。",
                    "My ideal partner is someone {who 【communicates instead of making me guess】}.",
                ),
                (
                    "我想要一个{【能一起吃饭、也能安静各干各的】}室友。",
                    "我想要一个室友。他能一起吃饭，也能安静各干各的。",
                    "I want a roommate {who 【can share meals but also respects my quiet time】}.",
                ),
                (
                    "我理想的工作，是{【不用让我装模作样】}的那种。",
                    "我理想的工作是这样的。它不用让我装模作样。",
                    "My ideal job is one {that 【doesn't make me pretend】}.",
                ),
                (
                    "我想要一个{【说话直接、不拐弯抹角】}的朋友。",
                    "我想要一个朋友。他说话直接，不拐弯抹角。",
                    "I want a friend {who 【speaks directly and doesn't beat around the bush】}.",
                ),
                (
                    "我理想的健身教练，是{【把动作讲清楚、不推销课】}的那种。",
                    "我理想的健身教练是这样的。他把动作讲清楚，不推销课。",
                    "My ideal trainer is one {who 【explains moves clearly and never pushes courses】}.",
                ),
                (
                    "我想要一台{【开机不卡、能再用五年】}的电脑。",
                    "我想要一台电脑。它开机不卡，能再用五年。",
                    "I want a computer {that 【starts fast and lasts another five years】}.",
                ),
                (
                    "我理想中的邻居，是{【见面点头、互不打扰】}的那种。",
                    "我理想中的邻居是这样的。见面点头，互不打扰。",
                    "My ideal neighbor is one {who 【says hi but never bothers me】}.",
                ),
                (
                    "我想要一个{【可以睡到自然醒】}的周末早晨。",
                    "我想要一个周末早晨。它可以睡到自然醒。",
                    "I want a weekend morning {that 【lets me wake up naturally】}.",
                ),
                (
                    "我理想的城市，是{【地铁不挤、夜宵也有得吃】}的那种。",
                    "我理想的城市是这样的。它地铁不挤，夜宵也有得吃。",
                    "My ideal city is one {that 【has empty subways and late-night food】}.",
                ),
            ],
            "L2": [
                (
                    "{我在一个人身上最看重}的，是【他有没有同理心】。",
                    "我看重一个人身上的某种品质。那就是有没有同理心。",
                    "The thing {that I value most in a person} is 【whether they have empathy】.",
                ),
                (
                    "我{最愿意花钱}的地方，只有【吃和旅行】。",
                    "我愿意在某些地方花钱。那就是吃和旅行。",
                    "The things {that I'm willing to spend money on} are only 【food and travel】.",
                ),
                (
                    "我{最想去的}城市，不是风景最漂亮的，而是【东西最好吃的】。",
                    "我想去一些城市。不是风景最漂亮的。是东西最好吃的。",
                    "The city {that I want most} isn't pretty — 【its food is best】.",
                ),
                (
                    "我{做梦都想要}的工作，是【每天都能学到新东西】的那种。",
                    "我做梦都想要一种工作。它每天能让我学到新东西。",
                    "The job {that I dream about} is one 【that teaches me something new every day】.",
                ),
                (
                    "我{最怀念}的，是【小时候暑假不用定闹钟】的日子。",
                    "我怀念一种日子。那是小时候的暑假，不用定闹钟。",
                    "The days {that I miss most} are 【the alarm-free summers of my childhood】.",
                ),
                (
                    "我理想中{一定要有}的，是【晚上能一起散步】的人。",
                    "我理想中的生活一定要有一个人。晚上能一起散步。",
                    "The person {that I definitely want in my life} is someone 【I can take evening walks with】.",
                ),
                (
                    "我{最想改掉}的，是【遇事先往坏处想】的习惯。",
                    "我有一个习惯。它遇事先往坏处想。我想改掉它。",
                    "The habit {that I want to break most} is 【always expecting the worst】.",
                ),
                (
                    "我{期待了很久}的，是【今年的带薪休假】。",
                    "我期待了很久一件事。那就是今年的带薪休假。",
                    "The thing {that I've been waiting for} is 【my paid leave this year】.",
                ),
                (
                    "我{最想学会}的，是【给自己好好做一顿饭】。",
                    "我最想学会一件事。那就是给自己好好做一顿饭。",
                    "The skill {that I want to learn most} is 【cooking a proper meal for myself】.",
                ),
                (
                    "我每个月{最期待}的，是【工资到账的短信】。",
                    "我每个月最期待一件事。那就是工资到账的短信。",
                    "The message {that I look forward to each month} is 【the salary notification】.",
                ),
            ],
            "L3": [
                (
                    "我想住的，是那种{【下楼就能吃到热乎饭】}的地方。",
                    "我想住在一个地方。在那里下楼就能吃到热乎饭。",
                    "I want to live in a place {where I can 【get hot food right downstairs】}.",
                ),
                (
                    "我一天里最放松的时刻，是{【下班走出地铁站】}的那几分钟。",
                    "我下班走出地铁站。那几分钟最放松。",
                    "My most relaxing moment is {when I 【get off the subway】}.",
                ),
                (
                    "这就是{我留在这座城市}的原因——【朋友和想吃的都在这里】。",
                    "我愿意留在这座城市。我的朋友和想吃的那口饭都在这里。",
                    "This is why {I stay in this city} — 【friends and food are here】.",
                ),
                (
                    "这就是{我宁愿早起也不熬夜}的原因——【早上的时间才真正属于我自己】。",
                    "我宁愿早起也不熬夜。早上的时间才真正属于我自己。",
                    "This is why {I get up early} — 【mornings are my quiet time】.",
                ),
                (
                    "我想去的是那种{【不用拍照打卡也很好看】}的地方。",
                    "我想去一种地方。在那里不用拍照打卡也很好看。",
                    "I want to go somewhere {where 【the view is great even without photos】}.",
                ),
                (
                    "我每周最期待的时间，是{【周五下班后的那两小时】}。",
                    "我每周最期待一段时间。那是周五下班后的两小时。",
                    "The time {when I'm happiest every week} is 【the two hours after work on Friday】.",
                ),
                (
                    "这就是{我想要一个阳台}的原因——【我想种点薄荷和番茄】。",
                    "我想要一个阳台。因为我想种点薄荷和番茄。",
                    "This is the reason {why I want a balcony} — 【I want to grow mint and tomatoes】.",
                ),
                (
                    "我想住在{【离菜市场走路十分钟以内】}的地方。",
                    "我想住在一个地方。从那里走路十分钟就能到菜市场。",
                    "I want to live somewhere {where 【the wet market is a ten-minute walk away】}.",
                ),
                (
                    "这就是{我想养一只猫}的原因——【回家的时候有活物等我】。",
                    "我想养一只猫。因为回家的时候有活物等我。",
                    "This is the reason {why I want a cat} — 【something alive waits for me at home】.",
                ),
                (
                    "我最喜欢的时刻，是{【正要喝第一口咖啡】的那几秒}。",
                    "我正要喝第一口咖啡。那几秒我最喜欢。",
                    "My favorite moment is {when I'm 【about to sip my coffee】}.",
                ),
            ],
        },
    },
    {
        "tag": "TRACK B",
        "title": "我的底线 · What I Refuse",
        "subtitle": "说出你受不了的人和事",
        "task": "表达任务：把下划线部分换成你自己的版本，用同一句式说出口：I don't want … who / that …",
        "ladders": {
            "L1": [
                (
                    "我不想成为那种{【把“随便”挂在嘴边】}的人。",
                    "有些人总把“随便”挂在嘴边。我不想成为这种人。",
                    "I don't want to be the kind of person {who 【always says “whatever”】}.",
                ),
                (
                    "我不想跟一个{【遇事就沉默冷战】}的人做朋友。",
                    "有个人遇事就沉默冷战。我不想和他做朋友。",
                    "I don't want to befriend someone {who 【goes cold and silent】}.",
                ),
                (
                    "我不想成为那种{【答应帮忙、转头就忘】}的人。",
                    "有些人答应帮忙，转头就忘。我不想成为这种人。",
                    "I don't want to be the kind of person {who 【promises to help and then forgets】}.",
                ),
                (
                    "我不想跟一个{【吃饭永远低头看手机】}的人坐一起。",
                    "有个人吃饭永远低头看手机。我不想和他坐一起。",
                    "I don't want to sit with someone {who 【stares at their phone all through dinner】}.",
                ),
                (
                    "我不想成为那种{【一开口就贬低别人】}的人。",
                    "有些人一开口就贬低别人。我不想成为这种人。",
                    "I don't want to be someone {who 【puts others down as a habit】}.",
                ),
                (
                    "我不想找一个{【从不道歉】}的伴侣。",
                    "有些人从不道歉。我不想找这样的伴侣。",
                    "I don't want a partner {who 【never apologizes】}.",
                ),
                (
                    "我不想跟一个{【背后说人坏话】}的人共事。",
                    "有个人背后说人坏话。我不想和他共事。",
                    "I don't want to work with someone {who 【talks behind people's backs】}.",
                ),
                (
                    "我不想成为那种{【把加班当荣耀】}的人。",
                    "有些人把加班当荣耀。我不想成为这种人。",
                    "I don't want to be the kind of person {who 【wears overtime like a badge】}.",
                ),
                (
                    "我不想跟一个{【借钱不还、还装没事】}的人再来往。",
                    "有个人借钱不还，还装没事。我不想再和他来往。",
                    "I won't deal with someone {who 【borrows money and plays innocent】}.",
                ),
                (
                    "我不想成为那种{【见不得别人过得好】}的人。",
                    "有些人见不得别人过得好。我不想成为这种人。",
                    "I don't want to be the kind of person {who 【can't stand others doing well】}.",
                ),
            ],
            "L2": [
                (
                    "我不想过{【父母替我选好】}的人生。",
                    "父母替我选了一种人生。我不想那样过。",
                    "I don't want the life {that 【my parents chose for me】}.",
                ),
                (
                    "{我老是拖延}的，是【跟人开口谈钱】这种事。",
                    "有一件事我老是拖延。那就是跟人开口谈钱。",
                    "The thing {that I keep putting off} is 【talking about money】.",
                ),
                (
                    "{我最不能接受}的，是【答应了却不出现】。",
                    "有人答应了却不出现。我最不能接受这种事。",
                    "The thing {that I can't stand} is 【people promising to come and then not showing up】.",
                ),
                (
                    "{我后悔没早点做}的，是【开口跟爸妈说谢谢】。",
                    "有一件事我后悔没早点做。那就是开口跟爸妈说谢谢。",
                    "The thing {that I regret not doing sooner} is 【telling my parents thank you】.",
                ),
                (
                    "{我最受不了}的，是【别人替我做决定】。",
                    "有人替我做决定。我最受不了这种事。",
                    "The thing {that I hate most} is 【others making decisions for me】.",
                ),
                (
                    "{我坚决不做的}，是【拿健康换加班费】。",
                    "有人拿健康换加班费。我坚决不做这种事。",
                    "The thing {that I refuse to do} is 【trading my health for overtime pay】.",
                ),
                (
                    "{我删掉最多}的，是【手机里半年不联系】的“朋友”。",
                    "手机里有一些半年不联系的人。我删掉最多的就是他们。",
                    "The “friends” {that I delete most} are 【the ones I haven't talked to in half a year】.",
                ),
                (
                    "{我最不想听}的，是【“为你好”这三个字】。",
                    "有人总说“为你好”。我最不想听这三个字。",
                    "The words {that I hate hearing most} are 【“it's for your own good”】.",
                ),
                (
                    "{我一直在忍}的，是【楼下装修的电钻声】。",
                    "楼下装修的电钻声很吵。我一直在忍。",
                    "The noise {that I've been putting up with} is 【the drilling downstairs】.",
                ),
                (
                    "{我最不想要的}，是【表面客气、背后捅刀】的关系。",
                    "有一种关系表面客气，背后捅刀。我最不想要。",
                    "The bond {that I want least} is 【polite in front, cruel behind】.",
                ),
            ],
            "L3": [
                (
                    "这就是{我从不跟朋友借钱}的原因——【钱一沾上，友谊就变味了】。",
                    "我从不跟朋友借钱。钱一沾上，友谊就变味了。",
                    "That's why {I don't borrow from friends} — 【money ruins it】.",
                ),
                (
                    "这就是{我坚决不熬夜}的原因——【熬一次，第二天整个人都是废的】。",
                    "我坚决不熬夜。熬一次，第二天整个人都是废的。",
                    "This is the reason {why I refuse to stay up late} — 【one late night ruins my next day】.",
                ),
                (
                    "这就是{我不爱发朋友圈}的原因——【我不需要点赞来确认自己的生活】。",
                    "我不爱发朋友圈。我不需要点赞来确认自己的生活。",
                    "That's why {I don't post my life online} — 【I don't need likes】.",
                ),
                (
                    "这就是{我宁愿买贵些}的原因——【便宜的用不住，反而更贵】。",
                    "我宁愿多花钱也不买便宜货。便宜货用不住，最后反而更贵。",
                    "That's why {I'd rather pay more} — 【cheap breaks and costs more】.",
                ),
                (
                    "这就是{我不在群里说话}的原因——【一开口，就会冒出三个新任务】。",
                    "我不在群里说话。因为一开口就会冒出三个新任务。",
                    "That's why {I stay quiet in group chats} — 【messages mean work】.",
                ),
                (
                    "这就是{我宁可绕路也不走那条巷子}的原因——【巷子里的狗太凶了】。",
                    "我宁可绕路也不走那条巷子。因为巷子里的狗太凶了。",
                    "That's why {I avoid that alley} — 【its dogs are too scary】.",
                ),
                (
                    "我不想去的是那种{【不喝酒就散不了场】}的饭局。",
                    "有一种饭局不喝酒就散不了场。我不想去。",
                    "The dinners {where 【you can't leave without drinking】} are the ones I avoid.",
                ),
                (
                    "这就是{我不坐那趟早班地铁}的原因——【它总是挤到脚不沾地】。",
                    "我不坐那趟早班地铁。因为它总是挤到脚不沾地。",
                    "That's why {I skip that morning subway} — 【it's always packed】.",
                ),
                (
                    "这就是{我买菜坚持用现金}的原因——【花出去的钱才让人心疼】。",
                    "我买菜坚持用现金。因为花出去的钱才让人心疼。",
                    "That's why {I pay cash} — 【handing over money feels real】.",
                ),
                (
                    "这就是{我周末不接工作电话}的原因——【周末本来就是用来休息的】。",
                    "我周末不接工作电话。因为周末本来就是用来休息的。",
                    "That's why {I skip weekend work calls} — 【weekends are for rest】.",
                ),
            ],
        },
    },
    {
        "tag": "TRACK C",
        "title": "我的评价 · My Take",
        "subtitle": "给经历和身边的人一个真实的评价",
        "task": "表达任务：把下划线部分换成你自己的版本，用同一句式说出口：The … that / who / where …",
        "ladders": {
            "L1": [
                (
                    "就是那个{【第一次见面就跟我聊到深夜】}的人，后来成了我最好的朋友。",
                    "有个人第一次见面就跟我聊到深夜。他后来成了我最好的朋友。",
                    "He's my best friend now — the one {who 【talked till midnight】}.",
                ),
                (
                    "那部{大家都说会看哭}的电影，我【全程没感觉】。",
                    "大家都说一部电影会看哭。我全程没感觉。",
                    "The movie {that everyone said would make me cry} 【didn't move me at all】.",
                ),
                (
                    "那条{看起来平平无奇、穿上却很惊艳}的裙子，成了我【最常穿】的一件。",
                    "一条裙子看起来平平无奇。它穿上却很惊艳。",
                    "The dress {that looked plain but surprised me} is 【my most-worn one】.",
                ),
                (
                    "那个{【说话超大声、人却特别靠谱】}的同事，成了我的饭搭子。",
                    "有个同事说话超大声。他人却特别靠谱。",
                    "The coworker {who 【talks loud but is reliable】} is my lunch buddy.",
                ),
                (
                    "那道{【闻起来很奇怪、吃起来却真香】}的菜，现在是我每周必点。",
                    "一道菜闻起来很奇怪。它吃起来却很香。",
                    "The dish {that 【smells weird but tastes great】} is my weekly order.",
                ),
                (
                    "那个{【第一次来我家就把猫哄得团团转】}的人，我妈到现在还在夸。",
                    "有个人第一次来我家。他把猫哄得团团转。",
                    "The person {who 【charmed my cat】} — my mom still mentions him.",
                ),
                (
                    "那家{【说排队两小时、十分钟就进去了】}的餐厅，成了我们的秘密基地。",
                    "有家餐厅说要排队两小时。结果十分钟就进去了。",
                    "The spot {that 【said two hours but seated us in ten】} is our secret.",
                ),
                (
                    "那个{【平时话不多、关键时候站出来】}的人，是我最佩服的同事。",
                    "有个同事平时话不多。关键时候他会站出来。",
                    "The coworker {who 【says little but steps up】} is the one I respect.",
                ),
                (
                    "那本{【买回来放了半年、一翻开就停不下来】}的书，是我今年的惊喜。",
                    "一本书买回来放了半年。一翻开就停不下来。",
                    "The book {that 【sat unread but hooked me】} was my surprise this year.",
                ),
                (
                    "那家{【网上评分只有三颗星、味道却意外好】}的小店，是我私藏的。",
                    "一家小店网上评分只有三颗星。味道却意外好。",
                    "The little shop {that 【has three stars but good food】} is my gem.",
                ),
            ],
            "L2": [
                (
                    "我妈{给我安排的}那场【约会】，其实还挺可爱的。",
                    "我妈给我安排了一场约会。它其实还挺可爱的。",
                    "The 【date】 {that my mom set up for me} was actually cute.",
                ),
                (
                    "朋友{一直安利我}的那部【纪录片】，我看完确实很震撼。",
                    "朋友一直向我安利一部纪录片。我看完确实很震撼。",
                    "The 【documentary】 {that my friend kept recommending} was honestly amazing.",
                ),
                (
                    "我上周{买的}那双【鞋】，穿着走了一万步也不磨脚。",
                    "我上周买了一双鞋。它走了一万步也不磨脚。",
                    "The 【shoes】 {that I bought last week} didn't hurt even after ten thousand steps.",
                ),
                (
                    "老板临时{丢给我的}那个【项目】，做完才发现没那么可怕。",
                    "老板临时丢给我一个项目。做完才发现没那么可怕。",
                    "The 【project】 {that my boss suddenly dumped on me} turned out not so scary.",
                ),
                (
                    "我在二手平台{淘到}的那把【椅子】，比新的还结实。",
                    "我在二手平台淘到一把椅子。它比新的还结实。",
                    "The 【chair】 {that I got on a secondhand app} is sturdier than a new one.",
                ),
                (
                    "同事偷偷{放在我桌上}的那杯【咖啡】，让我撑过了整个下午。",
                    "同事偷偷放了一杯咖啡在我桌上。它让我撑过了整个下午。",
                    "The 【coffee】 {that my coworker left on my desk} got me through the afternoon.",
                ),
                (
                    "我第一次{做}的那顿【饭】，卖相难看，味道却不错。",
                    "我第一次做了一顿饭。它卖相难看，味道却不错。",
                    "The 【meal】 {that I cooked for the first time} looked bad but tasted good.",
                ),
                (
                    "我{删了又装回来}的那个【App】，最后还是卸了。",
                    "我删了一个App又装回来。最后还是卸了。",
                    "The 【app】 {that I deleted and reinstalled} got deleted again in the end.",
                ),
                (
                    "我在地铁上{让座}给的那位【阿姨】，下车前一直跟我说谢谢。",
                    "我在地铁上给一位阿姨让座。她下车前一直跟我说谢谢。",
                    "The 【lady】 {that I gave my seat to} kept thanking me until she got off.",
                ),
                (
                    "我替同事{顶}的那个【班】，换来一句“下次请你吃饭”。",
                    "我替同事顶了一个班。他跟我说下次请我吃饭。",
                    "The 【shift】 {that I covered for my coworker} earned me a “lunch is on me”.",
                ),
            ],
            "L3": [
                (
                    "这是{【我完全不用装大人】}的地方。",
                    "我有一个地方。在那里我完全不用装大人。",
                    "This is a place {where I 【don't have to act like a grown-up】}.",
                ),
                (
                    "这就是{成年人友谊难维持}的原因——【时间都被工作和生活占满了】。",
                    "成年人的友谊越来越难维持。大家的时间都被工作和生活占满了。",
                    "That's why {adult friendship fades} — 【work and life take time】.",
                ),
                (
                    "我们{第一次见面}的那家【奶茶店】，现在已经关门了。",
                    "我们在一家奶茶店第一次见面。它现在已经关门了。",
                    "The 【milk tea shop】 {where we first met} has closed down now.",
                ),
                (
                    "我每年{最期待}的日子，是【全家一起吃饭的除夕】。",
                    "我每年最期待一天。那是全家一起吃饭的除夕。",
                    "The day {when I'm most excited each year} is 【New Year's Eve with the whole family】.",
                ),
                (
                    "这就是{我宁愿多走十分钟也不坐那趟公交}的原因——【它总是绕远路】。",
                    "我宁愿多走十分钟也不坐那趟公交。因为它总是绕远路。",
                    "That's why {I'd rather walk} — 【that bus takes the long way】.",
                ),
                (
                    "我人生中最难熬的时刻，是{【等成绩】的那个下午}。",
                    "我等成绩等了一个下午。那是我人生中最难熬的时刻。",
                    "The hardest moment of my life was {when I 【waited for exam results】}.",
                ),
                (
                    "那家我们{每次聚会都去}的【烧烤店】，味道十年没变。",
                    "我们每次聚会都去一家烧烤店。它的味道十年没变。",
                    "Our 【barbecue spot】 {where we always go} still tastes the same.",
                ),
                (
                    "这就是那家店{永远在排队}的原因——【便宜又好吃】。",
                    "那家店永远在排队。因为它便宜又好吃。",
                    "This is the reason {why that shop always has a queue} — 【it's cheap and delicious】.",
                ),
                (
                    "我最喜欢的季节，是{【桂花开的九月】}。",
                    "九月桂花开了。那是我最喜欢的季节。",
                    "My favorite season is September, {when 【the osmanthus blooms】}.",
                ),
                (
                    "这就是{我一直留着那件旧外套}的原因——【它是外婆买的】。",
                    "我一直留着那件旧外套。因为它是外婆买的。",
                    "This is the reason {why I keep that old coat} — 【my grandma bought it for me】.",
                ),
            ],
        },
    },
]

# ═══════════════════════════════════════════════════════════════════════
#  HINTS: one per item, 3 replacement directions for the swap part.
#  Key = track letter + "_" + ladder tag, value = 10 hint strings.
# ═══════════════════════════════════════════════════════════════════════

HINTS = {
    "A_L1": [
        "不画饼的 / 到点就下班的 / 会当面说问题的人",
        "吵架后先冷静再谈的 / 记得我说过的小事的 / 愿意一起做家务的",
        "有共同爱好的 / 厨艺好的 / 有边界感的",
        "不用打卡的 / 同事好相处的 / 下班不用回消息的",
        "愿意听我吐槽的 / 早上会叫我起床的 / 借钱会主动还的",
        "不催课的 / 动作标准的 / 会鼓励人的",
        "轻到能塞进书包的 / 电池能扛一天的 / 修起来不贵的",
        "会帮我收快递的 / 半夜不开派对的 / 见面会打招呼的",
        "不用早起的 / 阳光刚好晒到床的 / 楼下没有装修声的",
        "房租不吓人的 / 末班车很晚的 / 四季分明的",
    ],
    "A_L2": [
        "责任感 / 幽默感 / 情绪稳定",
        "书和咖啡 / 家人和朋友 / 运动和装备",
        "物价最友好的 / 有老朋友的 / 出门不用打车的",
        "不用加班的 / 成果看得见的 / 同事都靠谱的",
        "大学没有早课的 / 周末自然醒的 / 请假没人问的",
        "一起跑步的人 / 周末爬山的人 / 半夜吃夜宵的人",
        "拖到最后一刻 / 忍不住刷手机 / 报复性熬夜",
        "年终奖到账 / 准点下班 / 食堂好吃的日子",
        "游一次泳 / 写一篇日记 / 早睡一次",
        "快递到货 / 演唱会开票 / 朋友回消息",
    ],
    "A_L3": [
        "楼下就有便利店 / 走路能到公园 / 阳台能晒到太阳",
        "洗完澡躺上床 / 周五下班关电脑 / 周末早上睁眼",
        "家人在 / 工作在这 / 房租还能接受",
        "早晨脑子最清醒 / 晚上脑子停不下来 / 早起能吃上早饭",
        "能看海的 / 没什么人的 / 走路不累的",
        "午休的半小时 / 发工资的那天 / 长假的第一天",
        "一个书房 / 一台投影仪 / 一个猫爬架",
        "离地铁站五分钟 / 公司步行可达 / 楼下有公园",
        "养一只狗 / 养一盆花 / 种一片菜",
        "第一口奶茶 / 第一口西瓜 / 第一口冰可乐",
    ],
    "B_L1": [
        "知道了却不动 / 下次一定 / 都行",
        "遇事就消失 / 一吵架就翻旧账 / 生气就摔门",
        "只会说漂亮话 / 有求必应但从不兑现 / 回复永远是“在忙”",
        "开会总迟到 / 上厕所玩半小时 / 走路刷短视频",
        "把刻薄当幽默 / 聊天永远在炫耀 / 拿别人的短处开玩笑",
        "永远觉得自己对 / 道歉也像在施舍 / 错了也要争赢",
        "当面一套背后一套 / 抢功甩锅 / 打小报告",
        "把吃苦当勋章 / 把忙当价值 / 把熬夜当努力",
        "蹭饭从不主动买单 / 拿我东西不还 / 让我帮忙理所当然",
        "阴阳怪气 / 背后拆台 / 见好就眼红",
    ],
    "B_L2": [
        "别人定义的成功 / 打卡式的人生 / 为了面子过的日子",
        "拒绝别人 / 提出加薪 / 承认自己不会",
        "迟到还不解释 / 约好了又改时间 / 放鸽子连句抱歉都没有",
        "跟朋友说对不起 / 跟同事说不 / 跟自己说辛苦了",
        "被安排得明明白白 / 通知式征求意见 / 替我说“没关系”",
        "用睡眠换KPI / 用身体换年终奖 / 用假期换升职",
        "全是广告的群 / 吃灰的收藏 / 过期的好友申请",
        "“我都是为你好” / “你不懂” / “别人都行你怎么不行”",
        "楼上拖椅子的声音 / 隔壁K歌的声音 / 装修敲墙的声音",
        "只跟有钱人玩 / 有好处才出现 / 背后议论你",
    ],
    "B_L3": [
        "不跟同事吐槽 / 不跟亲戚合伙 / 不给别人担保",
        "不喝奶茶 / 不吃夜宵 / 不追深夜剧",
        "不晒娃 / 不发工资条 / 不秀恩爱",
        "不囤打折货 / 不拼单凑满减 / 不买预售款",
        "不接陌生电话 / 不评论热点 / 不参与投票",
        "不走近路 / 不坐那班车 / 不订那家店",
        "劝酒局 / 下午茶局 / 狼人杀局",
        "那趟公交 / 那班电梯 / 那条高速",
        "买菜不用手机 / 出门不带卡 / 花钱只记账",
        "晚上不看工作群 / 休假不接客户电话 / 下班不回消息",
    ],
    "C_L1": [
        "第一次见面就请我吃火锅 / 帮我搬了两次家 / 借我书还写了笔记",
        "评分9.9的餐厅 / 排队两小时的网红店 / 都说必买的护肤品",
        "便宜但好用的耳机 / 丑但舒服的鞋 / 普通但耐用的包",
        "毒舌但护短的朋友 / 嘴硬心软的室友 / 挑剔但专业的师傅",
        "长得丑但甜的瓜 / 名字怪但好吃的面 / 包装土但香的酱",
        "把小孩哄睡的人 / 让老人笑的人 / 能让场面不冷的人",
        "号称等一个月却提前发货的 / 说好不排队却挤爆的 / 评论说难吃却超好吃的",
        "平时嘻嘻哈哈但关键很稳的 / 看着懒散实际靠谱的 / 爱开玩笑但从不越界的",
        "借来很久却舍不得还的 / 被安利好多次才看的 / 随手翻开就放不下的",
        "装修很破但好吃的 / 服务一般但实在的 / 位置偏但安静的",
    ],
    "C_L2": [
        "相亲 / 饭局 / 旅行",
        "书 / 剧 / 播客",
        "耳机 / 雨伞 / 保温杯",
        "报告 / 汇报 / 出差",
        "桌子 / 台灯 / 锅",
        "面包 / 便当 / 充电线",
        "菜 / 汤 / 蛋糕",
        "游戏 / 表情包 / 歌单",
        "大叔 / 小孩 / 孕妇",
        "加班 / 夜班 / 值班",
    ],
    "C_L3": [
        "不用想工作 / 不用社交 / 不用说话",
        "见面越来越少 / 共同话题变少 / 大家都在赶路",
        "咖啡店 / 书店 / 面馆",
        "发工资 / 放暑假 / 见老友",
        "快递永远送错 / 外卖永远迟到 / 电梯永远检修",
        "等面试通知 / 等体检报告 / 等快递派送",
        "面馆 / 糖水铺 / 大排档",
        "下雨天爆单 / 周末才营业 / 老板做得慢",
        "梧桐的秋天 / 银杏的十一月 / 栀子的六月",
        "旧手机 / 旧书 / 旧照片",
    ],
}


# ═══════════════════════════════════════════════════════════════════════
#  HTML / CSS — black & white, clean scaffold worksheet
# ═══════════════════════════════════════════════════════════════════════

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    width: 210mm;
    background: #ffffff;
    color: #000000;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    line-height: 1.55;
    font-size: 14px;
}

.page {
    width: 210mm;
    height: 297mm;
    padding: 12mm 16mm 12mm 16mm;
    position: relative;
    overflow: hidden;
    background: #ffffff;
}

.page-break { page-break-before: always !important; break-before: always !important; }

/* ── Title ── */
.title-area {
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 3px solid #000000;
}
.main-title { font-size: 31px; font-weight: 800; color: #000000; letter-spacing: -0.3px; }
.sub-title { font-size: 14px; color: #000000; margin-top: 3px; }

/* ── Track task ── */
.track-task {
    display: block;
    font-size: 14px;
    font-weight: 700;
    color: #000000;
    margin: 10px 0 8px 4px;
}

/* ── Item ── */
.q-item {
    padding: 18px 0 18px 6px;
    font-size: 20px;
    color: #000000;
}
.cn { color: #000000; }
.split {
    display: block;
    color: #000000;
    font-size: 15.5px;
    line-height: 1.55;
    padding-left: 21px;
}
.en {
    display: block;
    color: #000000;
    font-size: 16.5px;
    line-height: 1.55;
    padding-left: 21px;
}
.hint {
    display: block;
    color: #000000;
    font-size: 14px;
    line-height: 1.55;
    padding-left: 21px;
}
.hl { font-weight: 800; color: #000000; }
.swap { color: #000000; text-decoration: underline; }

/* ── Footer ── */
.footer {
    position: absolute;
    bottom: 6mm;
    right: 16mm;
    font-size: 10px;
    color: #000000;
    font-weight: 600;
    letter-spacing: 0.5px;
}
"""


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _highlight(text: str) -> str:
    t = _escape_html(text)
    t = re.sub(r"【(.+?)】", r'<span class="swap">\1</span>', t)
    t = re.sub(r"\{(.+?)\}", r'<span class="hl">\1</span>', t)
    return t


def _page_open(page_num: int, main_title: str, sub_title: str) -> str:
    cls = "page page-break" if page_num > 1 else "page"
    sub = (
        f'    <div class="sub-title">{_escape_html(sub_title)}</div>\n'
        if sub_title
        else ""
    )
    return (
        f'<div class="{cls}">\n'
        '  <div class="title-area">\n'
        f'    <div class="main-title">{_escape_html(main_title)}</div>\n'
        f"{sub}"
        "  </div>\n"
    )


def _page_close(page_num: int, total: int) -> str:
    return f'  <div class="footer">{page_num}/{total}</div>\n</div>\n'


def _build_content_page(
    page_num: int, total: int, track: dict, track_key: str, ladder_tag: str, items: list,
    continued: bool,
) -> str:
    sub_title = f"{track['title']} · 续" if continued else track["title"]
    if track["tag"] == "TRACK A":
        # 去掉“我想要的 · What I Want”标题文字，内容保留。
        sub_title = ""
    html = _page_open(
        page_num,
        "Relative Clause",
        sub_title,
    )
    html += f'  <div class="track-task">{_escape_html(track["task"])}</div>\n'

    hints = HINTS[f"{track_key}_{ladder_tag}"]
    for i, (cn, split, en) in enumerate(items):
        html += (
            f'  <div class="q-item">'
            f'<span class="cn">{_highlight(cn)}</span>'
            f'<span class="split">拆分：{_escape_html(split)}</span>'
            f'<span class="en">({_highlight(en)})</span>'
            f'<span class="hint">试试换成：{_escape_html(hints[i])}</span>'
            f"</div>\n"
        )

    html += _page_close(page_num, total)
    return html


def build_html() -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        "<title>Relative Clause</title>",
        "<style>",
        CSS,
        "</style>",
        "</head>",
        "<body>",
    ]
    # 3 tracks × 3 ladders, each ladder split across 2 pages.
    total = len(TRACKS) * 3 * 2
    page_num = 1
    for track in TRACKS:
        track_key = track["tag"].split()[-1]
        for ladder_tag in ("L1", "L2", "L3"):
            items = track["ladders"][ladder_tag]
            for part_idx, chunk in enumerate((items[:5], items[5:])):
                parts.append(
                    _build_content_page(
                        page_num, total, track, track_key, ladder_tag, chunk,
                        continued=part_idx > 0,
                    )
                )
                page_num += 1
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


def main():
    pdf_path = PDF_DIR / "08-Relative Clause 渐进式脚手架练习.pdf"
    html_path = MD_DIR / "_relative_clause_scaffold.html"

    print("Generating HTML...")
    html_path.write_text(build_html(), encoding="utf-8")
    print(f"  HTML written to {html_path}")

    print("Exporting PDF (this may take a few seconds)...")
    if export_pdf(html_path, pdf_path):
        print(f"  PDF saved to {pdf_path}")
        sp = make_student_copy(pdf_path)
        if sp:
            print(f"  student copy saved to {sp}")
    else:
        print("  Playwright not available: PDF skipped (HTML is ready).")
    print("Done.")


if __name__ == "__main__":
    main()

# ESLBeginner

## 文档修订规则

- 文档只保留标题、表格、练习和讨论问题本身。
- 不出现课程介绍、每节引导句、说明性标签或过渡文字（如“先认识……”“用这些句型开头”“你的版本”“完整示范”）。
- 这一规则适用于所有文档的生成、修订和重排版，任何时候都不得添加这类内容。
- 不得擅自添加用户未要求的副标题、工作表标签、说明性标签、宣传语或其他元话术；文档只呈现用户要求的标题和教学内容。

## 内容原则

- **受众与时代定位**：所有内容面向 **2026 年的中国成年英语学习者（A1-A2）**。例句、讨论题、练习场景必须贴近当代中国成年人生活（外卖、地铁通勤、加班、面试、租房、微信等），不用过时或陌生场景。
- **习语必须当代、真实在用**：只选 2020 年代英语口语中真实高频的习语/俚语，避免教科书式、老套、过时的表达（如 over the moon、raining cats and dogs、down in the dumps 之类）。拿不准就先查证再写。
- **例句要有具体画面**：每条例句必须包含具体场景、人物和动作，让读者能立刻在脑中成像并代入（如 "I'm in a good mood — my coffee was free today."），禁止写干巴巴的通用例句（如 "I'm happy today."）。
- **内容要求不得明文标注**：用户给出的选题或措辞要求（如“无关痛痒”“不敏感”“轻松有趣”）只作为生成准则，禁止原样写进文档标题、正文或引导句（如不要写 “Some common, harmless examples:” 这类给作者看的说明文字）。

## 语言标准

- **英文一律用美式英语（American English）**：拼写、词汇、语法、日期数字格式都用美式，禁止英式。
- 高频替换：colour→color、centre→center、favourite→favorite、realise→realize、travelling→traveling、cancelled→canceled、programme→program、licence→license、grey→gray、tyre→tire、learnt→learned；flat→apartment、lift→elevator、queue→line、rubbish→trash、pavement→sidewalk、car park→parking lot、zebra crossing→crosswalk、underground/tube/metro→subway、holiday→vacation、lorry→truck、mobile→cell phone、cinema→movie theater、biscuits→cookies、chips→fries、maths→math、football→soccer、petrol→gas、parcel→package、autumn→fall、chemist→pharmacy、postcode→zip code、takeaway→takeout、shop（商店/商家）→store、put my phone on charge→put my phone on the charger。
- 语法也用美式：`Do you have…?`（不用 `Have you got…?`）、`on the weekend`（不用 `at the weekend`）、`different from`（不用 `different to`）、`I've gotten used to…`、集合名词用单数（`The team is…`）。
- 日期数字：`September 12, 2026`、`1,500`（不用 `12 September 2026`、`1.500`）。
- 例外：公制单位（米、公里、摄氏度）保留；中国地铁官方英文名（如 Shanghai Metro）保留。
- 交付前自检：`.venv/bin/python build/check_bre.py <改动文件…>`，要求 **FIX = 0**，REVIEW 项逐条人工判断。完整词表见用户级 `ESL-content.instructions.md`。

## 视觉设计

- 外观 / UI 生成遵循 [DESIGN.md](DESIGN.md) 的设计语言体系（awesome-design-md）；内容与视觉分离，AGENTS.md 不写视觉规则。

## 排版硬规则

- 讲义表格中的英文、中文、例句和问题默认保持单行，不人为插入换行；需要控制长度时，优先改短句子或调整列宽、字号，并在 PDF 中检查实际渲染结果。

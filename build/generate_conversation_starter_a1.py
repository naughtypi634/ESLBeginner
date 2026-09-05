#!/usr/bin/env python3
"""Generate A1 conversation-starter source files for Units 2-10."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "MD" / "conversation starter" / "A1"

UNITS = [
    (2, "HOME AND NEIGHBORHOOD", ["Homes", "Neighborhoods", "Museums", "Parks", "Cafes and restaurants"]),
    (3, "ENTERTAINMENT", ["Movies and TV shows", "Books", "Music", "Video and mobile games", "Childhood games"]),
    (4, "HEALTH AND WELLNESS", ["Exercise", "Nutrition", "Dealing with stress", "Hospitals and illnesses", "Home remedies and treatments"]),
    (5, "WORK AND CAREER", ["Jobs and careers", "Workplace and colleagues", "Interesting jobs", "Leadership at work", "Problems at work"]),
    (6, "SOCIAL MEDIA AND THE INTERNET", ["Online shopping", "Social media", "Online safety", "News online", "Streaming services"]),
    (7, "SPORTS", ["Popular sports", "Team and individual sports", "The Olympics", "Youth sports", "Extreme sports"]),
    (8, "MONEY AND FINANCE", ["Saving money", "Extra income", "Budgeting and spending", "Retirement", "Lottery"]),
    (9, "TRAVELING AND CULTURE", ["Traveling", "Festivals", "International food", "Medical travel", "Landmarks and history"]),
    (10, "SCIENCE AND TECHNOLOGY", ["Artificial intelligence", "Space exploration", "Clean energy", "Electric vehicles", "Virtual reality"]),
]

VOCABULARY = {
    "Homes": ["apartment", "room", "kitchen", "bedroom", "rent", "move in", "clean", "quiet", "window", "comfortable"],
    "Neighborhoods": ["neighborhood", "street", "shop", "market", "park", "safe", "near", "cross", "walk", "community"],
    "Museums": ["museum", "ticket", "painting", "history", "room", "guide", "learn", "free", "visit", "interesting"],
    "Parks": ["park", "path", "tree", "bench", "exercise", "run", "walk", "fresh", "relax", "weekend"],
    "Cafes and restaurants": ["cafe", "restaurant", "menu", "order", "dish", "waiter", "taste", "bill", "spicy", "book"],
}

DEFAULT_VOCAB = ["time", "place", "people", "work", "plan", "learn", "help", "share", "try", "enjoy"]

REGIONAL_LABELS = {
    "apartment": "apartment [AmE] / flat [BrE]",
    "metro station": "metro [BrE] / subway [AmE] station",
    "vacation": "vacation [AmE] / holiday [BrE]",
    "elevator": "elevator [AmE] / lift [BrE]",
    "line": "line [AmE] / queue [BrE]",
}

TOPIC_VOCAB = {
    "Movies and TV shows": ["movie", "show", "actor", "story", "funny", "watch", "episode", "screen", "recommend", "relax"],
    "Books": ["book", "novel", "writer", "page", "library", "read", "story", "character", "borrow", "favorite"],
    "Music": ["music", "song", "singer", "concert", "band", "listen", "dance", "headphones", "quiet", "popular"],
    "Video and mobile games": ["game", "phone", "level", "player", "win", "lose", "screen", "team", "online", "time"],
    "Childhood games": ["childhood", "game", "toy", "team", "play", "outside", "friend", "rule", "laugh", "memory"],
    "Exercise": ["exercise", "walk", "stretch", "strong", "body", "gym", "run", "habit", "energy", "rest"],
    "Nutrition": ["healthy", "meal", "vegetable", "fruit", "rice", "water", "sugar", "fresh", "cook", "breakfast"],
    "Dealing with stress": ["stress", "busy", "worry", "rest", "breathe", "sleep", "break", "music", "talk", "calm"],
    "Hospitals and illnesses": ["hospital", "doctor", "nurse", "patient", "fever", "pain", "medicine", "appointment", "test", "better"],
    "Home remedies and treatments": ["remedy", "tea", "honey", "warm", "cold", "cough", "rest", "care", "treatment", "recover"],
    "Jobs and careers": ["job", "career", "office", "worker", "skill", "apply", "salary", "learn", "future", "busy"],
    "Workplace and colleagues": ["colleague", "team", "meeting", "desk", "email", "help", "share", "friendly", "project", "break"],
    "Interesting jobs": ["job", "driver", "chef", "designer", "teacher", "work", "people", "place", "skill", "interesting"],
    "Leadership at work": ["leader", "manager", "team", "plan", "listen", "decide", "help", "goal", "fair", "trust"],
    "Problems at work": ["problem", "late", "mistake", "busy", "deadline", "talk", "fix", "sorry", "plan", "solution"],
    "Online shopping": ["online", "shop", "order", "price", "review", "delivery", "package", "return", "pay", "choice"],
    "Social media": ["social media", "post", "photo", "message", "follow", "friend", "share", "video", "comment", "private"],
    "Online safety": ["safe", "password", "account", "message", "stranger", "block", "report", "careful", "personal", "help"],
    "News online": ["news", "website", "fact", "photo", "read", "check", "source", "share", "true", "report"],
    "Streaming services": ["stream", "video", "show", "movie", "app", "watch", "episode", "screen", "cancel", "monthly"],
    "Popular sports": ["sport", "football", "basketball", "player", "team", "match", "watch", "train", "win", "fan"],
    "Team and individual sports": ["team", "individual", "partner", "coach", "practice", "share", "goal", "alone", "together", "skill"],
    "The Olympics": ["Olympics", "athlete", "country", "race", "medal", "train", "fast", "win", "watch", "dream"],
    "Youth sports": ["youth", "child", "school", "coach", "practice", "team", "healthy", "learn", "game", "fun"],
    "Extreme sports": ["extreme", "climb", "ride", "mountain", "water", "helmet", "safe", "brave", "risk", "try"],
    "Saving money": ["save", "money", "bank", "goal", "plan", "spend", "income", "month", "careful", "future"],
    "Extra income": ["income", "work", "skill", "sell", "teach", "online", "time", "pay", "weekend", "extra"],
    "Budgeting and spending": ["budget", "spend", "need", "want", "bill", "rent", "food", "list", "price", "plan"],
    "Retirement": ["retire", "future", "work", "save", "age", "plan", "family", "time", "health", "life"],
    "Lottery": ["lottery", "ticket", "number", "luck", "prize", "money", "dream", "buy", "share", "plan"],
    "Traveling": ["travel", "trip", "train", "hotel", "ticket", "bag", "map", "book", "arrive", "return"],
    "Festivals": ["festival", "holiday", "music", "food", "dance", "people", "traditional", "visit", "street", "celebrate"],
    "International food": ["food", "dish", "restaurant", "taste", "spicy", "noodle", "rice", "cook", "try", "favorite"],
    "Medical travel": ["doctor", "hospital", "travel", "treatment", "patient", "hotel", "appointment", "care", "country", "health"],
    "Landmarks and history": ["landmark", "old", "history", "building", "city", "visit", "photo", "guide", "famous", "learn"],
    "Artificial intelligence": ["technology", "computer", "AI", "answer", "work", "learn", "tool", "write", "help", "careful"],
    "Space exploration": ["space", "star", "planet", "moon", "rocket", "science", "study", "earth", "future", "dream"],
    "Clean energy": ["energy", "clean", "sun", "wind", "power", "city", "save", "air", "change", "future"],
    "Electric vehicles": ["electric", "car", "battery", "charge", "drive", "station", "bus", "quiet", "cost", "travel"],
    "Virtual reality": ["virtual", "reality", "headset", "game", "screen", "room", "learn", "real", "try", "careful"],
}

SCENARIOS = {
    "Homes": ("renting a small apartment", "checked the kitchen light and fixed a loose door handle", "The landlord answered a message quickly", "the first night was noisy", "a quiet home helped Sophia sleep well", "homes"),
    "Neighborhoods": ("a new street near a metro station", "found a fruit shop, a pharmacy, and a small park", "an old neighbor showed Liu Yang a short walking path", "the busy road was hard to cross", "the area felt easier after one week", "neighborhoods"),
    "Museums": ("a free museum afternoon", "looked at old train tickets and city photos", "a guide explained a simple story about the city", "the English signs were difficult", "a phone photo helped Li Na remember new words", "museums"),
    "Parks": ("an evening walk in a city park", "walked three rounds and stretched near a tree", "Wang Wei left his phone in his bag", "he wanted to stop after one round", "fresh air gave him more energy", "parks"),
    "Cafes and restaurants": ("a noodle shop near an office", "ordered a small bowl and asked for less spice", "the waiter showed Chen Yu a picture menu", "the first dish was too hot", "the second dish was comfortable to eat", "cafes and restaurants"),
    "Movies and TV shows": ("a film night at home", "chose a short comedy with English subtitles", "Noah wrote down three useful phrases", "some actors spoke too fast", "the story was easier after one more scene", "movies and TV shows"),
    "Books": ("a library visit after work", "borrowed a short book about cooking", "Mia read five pages on the metro", "one chapter had many new words", "a small reading habit felt possible", "books"),
    "Music": ("a live music night in a small cafe", "listened to a local singer and clapped with the audience", "Emma sent one song to her sister", "the room was very crowded", "the music made the long week feel lighter", "music"),
    "Video and mobile games": ("a short mobile game after dinner", "played one level with a colleague", "Liam stopped when the timer rang", "he wanted to play all night", "a clear time limit made the game fun", "video and mobile games"),
    "Childhood games": ("a weekend game with old classmates", "played cards and a simple outdoor game", "Olivia taught the rules to two new players", "one player forgot the rules", "everyone laughed and played again", "childhood games"),
    "Exercise": ("a ten-minute exercise plan", "walked from the office to the next metro station", "Sophia used a step counter", "her legs felt tired after work", "a short walk became a daily habit", "exercise"),
    "Nutrition": ("a quick weekday dinner", "cooked rice, eggs, tomatoes, and green vegetables", "Noah prepared the vegetables before work", "he wanted to order fried food", "the home meal cost less and felt fresh", "nutrition"),
    "Dealing with stress": ("a busy Monday at work", "closed the laptop and took five slow breaths", "Emma talked with a friend during a short break", "many messages arrived at once", "a clear list made the evening calmer", "dealing with stress"),
    "Hospitals and illnesses": ("a doctor appointment for a high fever", "showed her health card and described the pain", "Mia wrote the medicine time in her phone", "she felt nervous in the waiting room", "she rested at home and slowly felt better", "hospitals and illnesses"),
    "Home remedies and treatments": ("a cold at home", "made warm water with honey and called her mother", "Liu Yang checked the medicine label", "the cough made sleep difficult", "rest and medical advice helped him recover", "home remedies and treatments"),
    "Jobs and careers": ("a first job interview", "prepared three answers and checked the bus route", "Jack wore a clean shirt and arrived early", "he forgot one English word", "he stayed calm and finished the interview", "jobs and careers"),
    "Workplace and colleagues": ("a new project at an office", "shared a task list with two colleagues", "Mia sent the final file before lunch", "one email had the wrong attachment", "the team checked the file together", "workplace and colleagues"),
    "Interesting jobs": ("a food delivery worker's morning", "picked up three orders and checked each address", "Ethan called a customer before arriving", "heavy rain slowed the bike", "careful planning kept the orders safe", "interesting jobs"),
    "Leadership at work": ("a small team meeting", "asked each person for one idea before making a plan", "Olivia wrote the goal on a whiteboard", "two colleagues wanted different dates", "the team chose a fair date together", "leadership at work"),
    "Problems at work": ("a missed work deadline", "told the manager the truth and made a new plan", "Noah asked a colleague to check the numbers", "the first report had a mistake", "the corrected report arrived that afternoon", "problems at work"),
    "Online shopping": ("buying a desk lamp online", "read three reviews and checked the delivery date", "Sophia measured her desk before ordering", "the first color was not available", "the new lamp arrived on time", "online shopping"),
    "Social media": ("a family photo in a WeChat group", "asked everyone before posting the photo", "Emma changed the privacy setting", "one relative did not want the photo online", "the family agreed on a safer post", "social media"),
    "Online safety": ("a strange message on a phone", "did not open the link and blocked the account", "Liam told his sister and changed his password", "the message looked like a delivery notice", "checking first kept the account safe", "online safety"),
    "News online": ("a surprising health story online", "checked the date and read the original source", "Jack compared the story with a trusted news site", "many friends had already shared it", "he did not share it before checking", "news online"),
    "Streaming services": ("choosing a monthly video service", "watched one episode and checked the price", "Mia put a reminder in her calendar", "the free trial was ending", "she cancelled it before paying", "streaming services"),
    "Popular sports": ("watching a football match after work", "watched the first half with two colleagues", "Ethan explained one rule to a new fan", "the match ended in a draw", "the group still enjoyed the evening", "popular sports"),
    "Team and individual sports": ("choosing a sport for the weekend", "tried badminton with a friend instead of playing alone", "Olivia practiced one simple serve", "the first shots went into the net", "practice made the game more fun", "team and individual sports"),
    "The Olympics": ("watching an Olympic race", "read about the athlete's long training plan", "Noah talked about the race with his daughter", "the result was very close", "the athletes' effort was inspiring", "the Olympics"),
    "Youth sports": ("a school basketball practice", "helped a child learn how to pass the ball", "Sophia praised effort instead of only points", "one child felt shy", "the child joined the next game", "youth sports"),
    "Extreme sports": ("an indoor climbing class", "put on a helmet and climbed a low wall", "Liam listened to the coach before moving", "the top looked higher than expected", "he stopped safely and tried again later", "extreme sports"),
    "Saving money": ("saving for a new laptop", "moved a small amount into a bank account each payday", "Emma used a simple phone note to track it", "an online sale made her want to spend", "waiting one day helped her choose carefully", "saving money"),
    "Extra income": ("teaching English online at weekends", "prepared a short lesson for two adult learners", "Mia used pictures and easy questions", "the first class started late", "the extra work paid for a train ticket", "extra income"),
    "Budgeting and spending": ("planning the monthly bills", "listed rent, food, transport, and phone costs", "Jack checked the list with his partner", "a takeaway order was not in the plan", "they cooked at home on Sunday", "budgeting and spending"),
    "Retirement": ("talking with a parent about the future", "looked at work, health, and family plans together", "Olivia wrote down three questions for the bank", "the choices felt difficult", "a small first plan made the future clearer", "retirement"),
    "Lottery": ("a small lottery ticket at a shop", "bought one ticket but kept the normal weekly budget", "Noah said a prize would not solve every problem", "his friend wanted to buy many tickets", "they chose to save the extra money", "the lottery"),
    "Traveling": ("a weekend train trip", "booked a seat and packed one small bag", "Ethan saved the hotel address offline", "the train left from a different platform", "checking the sign helped him arrive on time", "traveling"),
    "Festivals": ("a city festival in autumn", "watched a dance and tried local food", "Sophia asked a performer about the costume", "the street was very crowded", "meeting local people made the day special", "festivals"),
    "International food": ("trying a Thai restaurant", "ordered noodles and asked the waiter about the sauce", "Liu Yang shared the dish with a friend", "the sauce was hotter than expected", "the next bite was easier with less sauce", "international food"),
    "Medical travel": ("planning a hospital visit in another city", "checked the appointment, train, and hotel details", "Emma kept the medical documents in one folder", "the travel plan felt stressful", "a clear list helped the visit go smoothly", "medical travel"),
    "Landmarks and history": ("a visit to an old city wall", "read a short history note before taking photos", "Liam asked a guide about the gate", "the hot afternoon made the walk slow", "a short rest helped him continue", "landmarks and history"),
    "Artificial intelligence": ("using an AI tool at work", "asked it to make a simple meeting list", "Jack checked every answer before sending it", "one answer was not correct", "checking the tool was more important than saving time", "artificial intelligence"),
    "Space exploration": ("a science event at a library", "looked at a model rocket and watched a moon video", "Mia asked why astronauts need special clothes", "some science words were new", "the pictures helped her understand", "space exploration"),
    "Clean energy": ("a clean-energy talk at a community center", "learned how solar panels make power", "Noah asked about panels on apartment buildings", "the first explanation was difficult", "a simple picture made it clear", "clean energy"),
    "Electric vehicles": ("trying an electric bus", "checked the battery sign before getting on", "Olivia talked with the driver about charging", "the bus waited at a busy station", "the quiet ride was comfortable", "electric vehicles"),
    "Virtual reality": ("a virtual-reality class", "used a headset to visit a museum online", "Ethan took the headset off after ten minutes", "his eyes felt tired", "short sessions felt better than a long game", "virtual reality"),
}


def story_body(title, unit, number):
    people = ["Emma", "Liam", "Olivia", "Sophia", "Noah"]
    person = people[(unit + number) % len(people)]
    city = ["Beijing", "Shanghai", "Chengdu", "Hangzhou", "Shenzhen"][(unit * number) % 5]
    _, action, detail, problem, result, topic = SCENARIOS[title]
    old_names = ["Li Na", "Wang Wei", "Chen Yu", "Zhang Min", "Liu Yang", "Emma", "Liam", "Olivia", "Sophia", "Noah", "Ethan", "Jack", "Mia"]
    personal = [action, detail, problem, result]
    for old_name in old_names:
        personal = [text.replace(old_name, person) for text in personal]
    action, detail, problem, result = [
        text.replace(" his ", " their ").replace(" her ", " their ")
        for text in personal
    ]
    detail = detail[:1].upper() + detail[1:]
    result = result[:1].upper() + result[1:]
    return (f"{person} lives in {city} and was thinking about {topic}. "
            f"One Saturday, {person} visited a place or joined an activity about {topic}. "
            f"{person} {action}. {detail}.\n\n"
            f"The plan was useful, but {problem}. {person} did not give up. Instead, {person} asked a question, checked a message, "
            f"or made a small change. This helped {person} understand the situation better.\n\n"
            f"At the end of the day, {result}. {person} learned that a clear plan and one small step can make daily life easier.")


def questions(title):
    _, action, detail, problem, result, topic = SCENARIOS[title]
    return [
        f"What did the person do on Saturday?",
        f"What did the person do?",
        f"What useful detail did the person notice?",
        f"Who helped or talked with the person?",
        f"What was difficult about the day?",
        f"What small change did the person make?",
        f"What did the person learn about {topic}?",
        f"How would you handle the same problem?",
        f"What part of this story is familiar to you?",
        f"What would you like to try next about {topic}?",
    ]


def render(unit_number, unit_title, stories):
    lines = ["# CONVERSATION STARTER: A1", "", f"## UNIT {unit_number}: {unit_title}", ""]
    for number, title in enumerate(stories, 1):
        vocabulary = [REGIONAL_LABELS.get(word, word) for word in VOCABULARY.get(title, TOPIC_VOCAB.get(title, DEFAULT_VOCAB))]
        story = story_body(title, unit_number, number).replace("metro station", "metro [BrE] / subway [AmE] station")
        lines += [f"### STORY {number:02d}: {title.upper()}", "", "**Key Vocabulary**", ""]
        lines += [f"{i}. {word}" for i, word in enumerate(vocabulary, 1)]
        lines += ["", "**Story**", "", story, "", "**Conversation Questions**", ""]
        lines += [f"{i}. {question}" for i, question in enumerate(questions(title), 1)]
        lines.append("")
    return "\n".join(lines)


def main():
    for unit_number, unit_title, stories in UNITS:
        path = OUT / f"ConversationStarter.A1.Unit{unit_number}.md"
        path.write_text(render(unit_number, unit_title, stories), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
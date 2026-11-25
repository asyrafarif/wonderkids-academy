import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import hashlib
import random
import json
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & CARTOON THEME STYLING
# ==========================================
st.set_page_config(
    page_title="WonderKids Academy 🚀",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Fredoka', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #FFF8E7 0%, #E0F7FA 50%, #F3E5F5 100%);
}

/* Big Toddler-Friendly Buttons */
div.stButton > button {
    border-radius: 24px !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    padding: 0.85rem 1.4rem !important;
    border: 4px solid #FFD54F !important;
    background: linear-gradient(180deg, #FFFFFF 0%, #FFF9C4 100%) !important;
    color: #2D3436 !important;
    box-shadow: 0 6px 0 #FBC02D !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease !important;
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    border-color: #FF7043 !important;
    box-shadow: 0 9px 0 #E64A19 !important;
    background: linear-gradient(180deg, #FFFDE7 0%, #FFE082 100%) !important;
}

div.stButton > button:active {
    transform: translateY(3px) !important;
    box-shadow: 0 2px 0 #FBC02D !important;
}

/* Question Stage Card */
.stage-card {
    background: #FFFFFF;
    border-radius: 32px;
    padding: 28px;
    border: 6px solid #4FC3F7;
    box-shadow: 0 12px 24px rgba(0,0,0,0.08);
    text-align: center;
    margin-bottom: 20px;
}

.visual-stage {
    font-size: 4.2rem;
    letter-spacing: 10px;
    margin: 18px 0;
    padding: 18px;
    background: #F1F8E9;
    border-radius: 24px;
    border: 3px dashed #81C784;
}

.fact-box {
    background: linear-gradient(135deg, #E8F5E9 0%, #FFFDE7 100%);
    border-left: 8px solid #66BB6A;
    border-radius: 20px;
    padding: 18px 22px;
    font-size: 1.2rem;
    color: #1B5E20;
    margin-top: 16px;
    box-shadow: 0 6px 14px rgba(0,0,0,0.06);
}

.badge-pill {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 1rem;
    background: #FFE082;
    color: #E65100;
    margin: 4px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 2. PERSISTENT SQLITE DATABASE (IN-APP LOGIN & PROGRESS)
# ==========================================
DB_PATH = "wonderkids.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            child_name TEXT NOT NULL,
            age_group INTEGER NOT NULL,
            avatar TEXT NOT NULL,
            stars INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            stickers TEXT DEFAULT '["🌟"]',
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            mode TEXT NOT NULL,
            level INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, child_name, age_group, avatar):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO users (username, password_hash, child_name, age_group, avatar, stars, streak, stickers, created_at)
               VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?)""",
            (username.lower().strip(), hash_pw(password), child_name.strip(), age_group, avatar, json.dumps(["🌟"]), datetime.now().isoformat())
        )
        conn.commit()
        return True, "Account created! Let's play!"
    except sqlite3.IntegrityError:
        return False, "That username is already taken! Try another fun name."
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, username, child_name, age_group, avatar, stars, streak, stickers FROM users WHERE username=? AND password_hash=?",
        (username.lower().strip(), hash_pw(password))
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "child_name": row[2],
            "age_group": row[3],
            "avatar": row[4],
            "stars": row[5],
            "streak": row[6],
            "stickers": json.loads(row[7])
        }
    return None

def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, child_name, age_group, avatar, stars, streak, stickers FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "username": row[1], "child_name": row[2],
            "age_group": row[3], "avatar": row[4], "stars": row[5],
            "streak": row[6], "stickers": json.loads(row[7])
        }
    return None

STICKER_POOL = ["🦄", "🦖", "🚀", "🌈", "🐬", "🐼", "🦋", "🍓", "🎨", "🏆", "🐢", "🦊", "🐘", "🪐", "🐙", "🦁"]

def record_attempt(user_id, subject, mode, level, is_correct):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO progress_log (user_id, subject, mode, level, is_correct, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, subject, mode, level, 1 if is_correct else 0, datetime.now().isoformat())
    )
    c.execute("SELECT stars, streak, stickers FROM users WHERE id=?", (user_id,))
    stars, streak, stickers_json = c.fetchone()
    stickers = json.loads(stickers_json)

    new_sticker = None
    if is_correct:
        stars += 1
        streak += 1
        if stars % 3 == 0:
            available = [s for s in STICKER_POOL if s not in stickers]
            if available:
                new_sticker = random.choice(available)
                stickers.append(new_sticker)
    else:
        streak = 0

    c.execute(
        "UPDATE users SET stars=?, streak=?, stickers=? WHERE id=?",
        (stars, streak, json.dumps(stickers), user_id)
    )
    conn.commit()
    conn.close()
    return new_sticker

def get_progress_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT subject, mode, level, is_correct, timestamp FROM progress_log WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# ==========================================
# 3. ENERGETIC & PLAYFUL VOICE + SFX ENGINE
# ==========================================
def speak_energetic(text: str, sfx: str = "none", trigger_id: str = "0"):
    """
    Uses browser Web Speech API with high pitch & lively cadence + Web Audio celebratory chimes.
    """
    safe_text = text.replace('"', "'").replace("\n", " ")
    js_code = f"""
    <script>
    (function() {{
        const msgText = "{safe_text}";
        const sfxType = "{sfx}";

        // Play playful Web Audio chimes
        try {{
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {{
                const ctx = new AudioCtx();
                const playTone = (freq, start, dur, type='triangle') => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = type;
                    osc.frequency.setValueAtTime(freq, ctx.currentTime + start);
                    gain.gain.setValueAtTime(0.18, ctx.currentTime + start);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + dur);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(ctx.currentTime + start);
                    osc.stop(ctx.currentTime + start + dur);
                }};
                if (sfxType === "win") {{
                    playTone(523.25, 0.00, 0.15);
                    playTone(659.25, 0.12, 0.15);
                    playTone(783.99, 0.24, 0.18);
                    playTone(1046.50, 0.38, 0.35);
                }} else if (sfxType === "oops") {{
                    playTone(330, 0.00, 0.18, 'sine');
                    playTone(293.66, 0.18, 0.25, 'sine');
                }} else if (sfxType === "pop") {{
                    playTone(680, 0.00, 0.09, 'sine');
                }}
            }}
        }} catch(e) {{}}

        // Energetic, bubbly kid-host speech synthesis
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(msgText);
            const voices = window.speechSynthesis.getVoices();
            const preferred = voices.find(v =>
                /Google US English|Samantha|Victoria|Zira|Karen|Moira|Female/i.test(v.name)
            );
            if (preferred) utter.voice = preferred;
            utter.pitch = 1.38;   // Bright, playful cartoon pitch!
            utter.rate = 1.07;    // Lively, enthusiastic tempo!
            utter.volume = 1.0;
            window.speechSynthesis.speak(utter);
        }}
    }})();
    </script>
    <div style="display:none;">{trigger_id}</div>
    """
    components.html(js_code, height=0)

# ==========================================
# 4. RICH EXERCISE BANK (4 WORLDS x 4 LEVELS x 3 MODES)
# ==========================================
LEVEL_NAMES = {
    1: "🌱 Level 1: Tiny Sprout (Age 3)",
    2: "🐥 Level 2: Curious Explorer (Age 4)",
    3: "🦊 Level 3: Super Adventurer (Age 5)",
    4: "🚀 Level 4: Brainy Champion (Age 6)"
}

MODES = {
    "🎈 Adventure Mode": "Learn at your own pace with fun facts & cheering!",
    "⚡ Lightning Pop": "Quick-thinking rounds to build a mega star streak!",
    "🧩 Brainy Pattern & Logic": "Solve puzzles, sequences, and tricky riddles!"
}

def generate_question(subject: str, level: int, mode: str):
    """Generates dynamic, age-calibrated exercises with kid-friendly facts."""

    # ---------------- MATH KINGDOM ----------------
    if subject == "🔢 Math Kingdom":
        if mode == "🧩 Brainy Pattern & Logic":
            patterns = [
                ("🍎 🍌 🍎 🍌 🍎 ❓", "What fruit comes next in the yummy pattern?", "🍌 Banana", ["🍌 Banana", "🍎 Apple", "🍇 Grapes", "🍓 Strawberry"],
                 "Patterns repeat in a special order! Spot the pattern and you can predict the future!"),
                ("2️⃣ , 4️⃣ , 6️⃣ , ❓", "Count by twos! Which number jumps in next?", "8️⃣ Eight", ["7️⃣ Seven", "8️⃣ Eight", "9️⃣ Nine", "5️⃣ Five"],
                 "Skip-counting by 2s is like hopping on every second stepping stone!"),
                ("🐶 🐱 🐭 🐶 🐱 ❓", "Who completes the animal parade?", "🐭 Mouse", ["🐶 Dog", "🐱 Cat", "🐭 Mouse", "🐰 Rabbit"],
                 "Our brains love patterns—music beats and dance steps are made of math patterns too!"),
                ("10 , 9 , 8 , ❓", "Rocket countdown! What number comes next?", "7️⃣ Seven", ["6️⃣ Six", "7️⃣ Seven", "9️⃣ Nine", "5️⃣ Five"],
                 "Astronauts count backward to zero before blasting off into outer space!")
            ]
            vis, q, ans, opts, fact = random.choice(patterns)
            return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                    "voice": f"Ooh, puzzle time! {q}"}

        if level == 1:
            n = random.randint(1, 5)
            emoji = random.choice(["🍎", "🦆", "⭐", "🍓", "🐢"])
            opts = random.sample([str(i) for i in range(1, 6)], 3)
            if str(n) not in opts:
                opts[0] = str(n)
            random.shuffle(opts)
            return {
                "visual": " ".join([emoji] * n),
                "question": f"Count them out loud! How many {emoji} do you see?",
                "answer": str(n),
                "options": opts,
                "fact": f"Awesome counting! You have {n} fingers on one hand if you count all the way to 5!",
                "voice": f"Yay! Let's count together! How many {emoji} are bouncing on the screen?"
            }
        elif level == 2:
            a, b = random.sample(range(1, 8), 2)
            more = max(a, b)
            return {
                "visual": f"Group A: {'🐶'*a}   🆚   Group B: {'🐱'*b}",
                "question": "Which group has MORE furry friends?",
                "answer": f"Group A ({a})" if a > b else f"Group B ({b})",
                "options": [f"Group A ({a})", f"Group B ({b})", "Both Equal!"],
                "fact": "Comparing groups helps your brain measure size and quantity super fast!",
                "voice": "Look closely! Which group has more furry friends?"
            }
        elif level == 3:
            a, b = random.randint(1, 5), random.randint(1, 5)
            ans = a + b
            opts = list({str(ans), str(ans + 1), str(max(1, ans - 1)), str(ans + 2)})[:4]
            random.shuffle(opts)
            return {
                "visual": f"{'🍪'*a}  ➕  {'🍪'*b}",
                "question": f"Yum! {a} cookies plus {b} cookies equals how many?",
                "answer": str(ans),
                "options": opts,
                "fact": f"{a} + {b} = {ans}! Putting groups together is called addition!",
                "voice": f"Yummy math! If you have {a} cookies and get {b} more, how many cookies do you have?"
            }
        else:  # Level 4
            a = random.randint(5, 10)
            b = random.randint(1, 4)
            ans = a - b
            opts = list({str(ans), str(ans + 1), str(max(0, ans - 1)), str(a)})[:4]
            random.shuffle(opts)
            return {
                "visual": f"{'🎈'*a}  ➖  ({b} popped!)",
                "question": f"You had {a} balloons and {b} floated away! How many are left?",
                "answer": str(ans),
                "options": opts,
                "fact": f"{a} take away {b} leaves {ans}! That's called subtraction!",
                "voice": f"Pop pop! You had {a} balloons and {b} floated up to the clouds! How many are left?"
            }

    # ---------------- ALPHABET JUNGLE ----------------
    elif subject == "🔤 Alphabet Jungle":
        if mode == "🧩 Brainy Pattern & Logic":
            riddles = [
                ("🐱  🎩  🦇", "Which word RHYMES with CAT?", "🎩 HAT", ["🎩 HAT", "🐶 DOG", "☀️ SUN", "🐟 FISH"],
                 "Rhyming words end with the exact same sound—just like songs and poems!"),
                ("A ➔ B ➔ C ➔ ❓", "Sing the ABC song! Which letter marches next?", "🇩 D", ["🇩 D", "🇫 F", "🇿 Z", "🇲 M"],
                 "There are 26 letters in the English alphabet, and every word you read is built from them!"),
                ("🐝  🌳  🔑", "Which word RHYMES with BEE?", "🌳 TREE", ["🌳 TREE", "🚗 CAR", "🍎 APPLE", "🌙 MOON"],
                 "Bee, tree, and key all end with the happy 'EE' sound!")
            ]
            vis, q, ans, opts, fact = random.choice(riddles)
            return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                    "voice": f"Listen with your super ears! {q}"}

        bank = {
            1: [
                ("🦁", "ROAR! What letter does LION start with?", "L", ["L", "B", "S", "M"], "Lions are big cats whose mighty roar can be heard 5 miles away!"),
                ("🍎", "Crunch! What letter does APPLE start with?", "A", ["A", "P", "T", "D"], "Apples float in water because they are 25% air inside!"),
                ("🐸", "Ribbit! What letter does FROG start with?", "F", ["F", "G", "R", "K"], "Frogs drink water right through their skin—no cup needed!")
            ],
            2: [
                ("🐘", "Stomp stomp! Which animal starts with the letter E?", "🐘 Elephant", ["🐘 Elephant", "🐯 Tiger", "🐵 Monkey", "🐻 Bear"],
                 "Elephants use their long trunks like a nose, a hand, and even a snorkel!"),
                ("🚀", "Zoom! Which picture starts with the letter R?", "🚀 Rocket", ["🚀 Rocket", "⛵ Boat", "🚲 Bike", "🚂 Train"],
                 "Rockets travel faster than 17,000 miles per hour to reach space!")
            ],
            3: [
                ("☀️  _ U N", "Spell the bright yellow star in the sky! Missing letter?", "S (SUN)", ["S (SUN)", "B (BUN)", "R (RUN)", "F (FUN)"],
                 "The Sun is actually a giant, glowing star that keeps Earth warm!"),
                ("🐱  _ A T", "Meow! Which letter completes the word _ A T?", "C (CAT)", ["C (CAT)", "D (DAT)", "P (PAT)", "M (MAT)"],
                 "Cats use their whiskers to measure if they can squeeze through tight spaces!")
            ],
            4: [
                ("🦋", "Which word is the OPPOSITE of 'BIG'?", "🐜 TINY", ["🐜 TINY", "🐘 HUGE", "🦒 TALL", "🐳 GIANT"],
                 "Opposites are word pairs that are totally different—like hot & cold, or big & tiny!"),
                ("📚", "Which word is an ACTION word (verb)?", "🏃 JUMP", ["🏃 JUMP", "🪑 CHAIR", "🔵 BLUE", "🍎 APPLE"],
                 "Action words tell us what someone or something is doing!")
            ]
        }
        vis, q, ans, opts, fact = random.choice(bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Welcome to Alphabet Jungle! {q}"}

    # ---------------- DISCOVERY LAB (SCIENCE) ----------------
    elif subject == "🔬 Discovery Lab":
        science_bank = {
            1: [
                ("🐄  🥛", "Moo! Which friendly farm animal gives us milk?", "🐄 Cow", ["🐄 Cow", "🐔 Chicken", "🐷 Pig", "🦆 Duck"],
                 "Cows have four stomach compartments to help them digest yummy grass!"),
                ("🌧️  ☀️", "When sunshine shines through raindrops, what appears in the sky?", "🌈 Rainbow", ["🌈 Rainbow", "⛄ Snowman", "🌙 Moon", "🪨 Rock"],
                 "Sunlight is made of 7 rainbow colors hiding together inside white light!")
            ],
            2: [
                ("🐛  ➔  💤  ➔  ❓", "A hungry caterpillar goes to sleep in a chrysalis and wakes up as a...", "🦋 Butterfly", ["🦋 Butterfly", "🐸 Frog", "🐟 Fish", "🐦 Bird"],
                 "Butterflies taste flowers using tiny sensors on their FEET!"),
                ("🌱  ☀️  💧", "What does a tiny seed need to grow into a tall flower?", "☀️ Sun & Water", ["☀️ Sun & Water", "🍕 Pizza", "🧸 Teddy Bear", "❄️ Ice Cubes"],
                 "Plants drink water through their roots like straws and make food from sunshine!")
            ],
            3: [
                ("🪐  🌍  ☀️", "Which planet do WE live on?", "🌍 Earth", ["🌍 Earth", "🪐 Saturn", "🔴 Mars", "☀️ The Sun"],
                 "Earth is the only known planet with liquid oceans on its surface and living creatures!"),
                ("🧲  📎", "Which object will stick to a super magnet?", "📎 Metal Paperclip", ["📎 Metal Paperclip", "🍌 Banana", "🧸 Plush Toy", "🖍️ Crayon"],
                 "Magnets have invisible force fields that pull on iron and steel!")
            ],
            4: [
                ("🧊  🔥  💧", "When warm sunshine heats up an ice cube, it melts into...", "💧 Liquid Water", ["💧 Liquid Water", "🪨 Solid Rock", "🪵 Wood", "🏖️ Sand"],
                 "Water is a shape-shifter! It can be solid ice, liquid water, or invisible steam!"),
                ("🦉  🦇  🌙", "Animals that sleep all day and wake up at night are called...", "🦉 Nocturnal", ["🦉 Nocturnal", "🐠 Aquatic", "🦖 Extinct", "🐧 Arctic"],
                 "Owls have giant eyes that capture tiny bits of moonlight so they can see in the dark!")
            ]
        }
        vis, q, ans, opts, fact = random.choice(science_bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Put on your scientist goggles! {q}"}

    # ---------------- SHAPE & COLOR ISLAND ----------------
    else:
        shape_bank = {
            1: [
                ("🍕  📐", "How many pointy corners does a TRIANGLE have?", "3 Corners", ["3 Corners", "4 Corners", "0 Corners", "5 Corners"],
                 "Tri means THREE! Tricycles have 3 wheels and triangles have 3 sides!"),
                ("🌕  ⚽  🍪", "Which shape is completely round with ZERO corners?", "⭕ Circle", ["⭕ Circle", "⬛ Square", "🔺 Triangle", "⭐ Star"],
                 "Wheels are circles because round shapes roll smoothly without bumping!")
            ],
            2: [
                ("🔴  ➕  🟡  =  ❓", "Mix RED paint and YELLOW paint together! What magic color do you get?", "🟠 Orange", ["🟠 Orange", "🟢 Green", "🟣 Purple", "🔵 Blue"],
                 "Red, Yellow, and Blue are Primary Colors—you can mix them to create a whole rainbow!"),
                ("🔵  ➕  🟡  =  ❓", "Swirl BLUE and YELLOW paint together! Which color appears?", "🟢 Green", ["🟢 Green", "🟠 Orange", "🟣 Purple", "🩷 Pink"],
                 "Leaves look green because of chlorophyll, which catches sunlight for trees!")
            ],
            3: [
                ("🐝  🍯", "What 6-sided shape do busy bees build inside their honeycomb?", "⬡ Hexagon", ["⬡ Hexagon", "⭕ Circle", "🔺 Triangle", "⬛ Square"],
                 "Hexagons fit together with zero wasted space—bees are tiny math geniuses!"),
                ("🟥  🟦  ❓  🟥  🟦", "Complete the rainbow color pattern!", "🟨 Yellow", ["🟨 Yellow", "⬛ Black", "⬜ White", "🟫 Brown"],
                 "Artists use color patterns to make paintings feel joyful and lively!")
            ],
            4: [
                ("🎲  📦", "A 3D square box shape with 6 flat faces is called a...", "🧊 Cube", ["🧊 Cube", "⚽ Sphere", "🍦 Cone", "🥫 Cylinder"],
                 "2D shapes are flat like paper, while 3D shapes pop out so you can hold them!"),
                ("🍦  🎉", "A party hat and an ice cream waffle share which 3D shape?", "🔺 Cone", ["🔺 Cone", "🧊 Cube", "⚽ Sphere", "📦 Box"],
                 "Cones have a round circle on one end and a sharp point on the other!")
            ]
        }
        vis, q, ans, opts, fact = random.choice(shape_bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Ahoy, explorer! {q}"}

# ==========================================
# 5. SESSION STATE INITIALIZATION
# ==========================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "Play"
if "subject" not in st.session_state:
    st.session_state.subject = "🔢 Math Kingdom"
if "mode" not in st.session_state:
    st.session_state.mode = "🎈 Adventure Mode"
if "level" not in st.session_state:
    st.session_state.level = 1
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "new_sticker" not in st.session_state:
    st.session_state.new_sticker = None
if "speech_payload" not in st.session_state:
    st.session_state.speech_payload = None

# ==========================================
# 6. IN-APP LOGIN & SIGN-UP GATEWAY
# ==========================================
if st.session_state.user_id is None:
    st.markdown("""
    <div class="stage-card">
        <h1 style="font-size:3rem; color:#FF6F00; margin-bottom:4px;">🦁 WonderKids Academy 🚀</h1>
        <p style="font-size:1.3rem; color:#455A64;">Fun Cartoon Learning for Little Explorers (Ages 3 – 6)</p>
        <span class="badge-pill">🔢 Math</span>
        <span class="badge-pill">🔤 English</span>
        <span class="badge-pill">🔬 Science</span>
        <span class="badge-pill">🎨 Shapes & Colors</span>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.subheader("🔑 Log In to Your Explorer Profile")
        with st.form("login_form"):
            login_user = st.text_input("Explorer Username", placeholder="e.g., leo_dino")
            login_pw = st.text_input("Secret Passcode", type="password", placeholder="••••••")
            submitted_login = st.form_submit_button("🚀 Start Playing!")
            if submitted_login:
                user = authenticate_user(login_user, login_pw)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.level = max(1, min(4, user["age_group"] - 2))
                    st.session_state.current_q = generate_question(st.session_state.subject, st.session_state.level, st.session_state.mode)
                    st.session_state.speech_payload = (
                        f"Woohoo! Welcome back, {user['child_name']}! Let's play and earn shiny stars!",
                        "win",
                        str(random.random())
                    )
                    st.rerun()
                else:
                    st.error("Oops! Check your username or secret passcode and try again.")

    with col_right:
        st.subheader("✨ New Explorer? Create Profile (Saved Inside App!)")
        with st.form("signup_form"):
            new_child = st.text_input("Child's First Name", placeholder="e.g., Maya")
            new_user = st.text_input("Choose a Username", placeholder="e.g., maya_star")
            new_pw = st.text_input("Create a Passcode", type="password", placeholder="e.g., 1234")
            age = st.selectbox("Child's Age", [3, 4, 5, 6], format_func=lambda a: f"🎂 {a} Years Old")
            avatar = st.selectbox("Pick a Cartoon Buddy Avatar", ["🦁 Leo the Lion", "🦄 Sparkle Unicorn", "🦖 Rexy Dino", "🐼 Bamboo Panda", "🚀 Astro Fox"])
            submitted_signup = st.form_submit_button("🎉 Create Profile & Jump In!")
            if submitted_signup:
                if not new_child or not new_user or not new_pw:
                    st.warning("Please fill in your name, username, and passcode!")
                else:
                    ok, msg = create_user(new_user, new_pw, new_child, age, avatar.split()[0])
                    if ok:
                        user = authenticate_user(new_user, new_pw)
                        st.session_state.user_id = user["id"]
                        st.session_state.level = max(1, min(4, age - 2))
                        st.session_state.current_q = generate_question(st.session_state.subject, st.session_state.level, st.session_state.mode)
                        st.session_state.speech_payload = (
                            f"Hooray! Welcome to WonderKids Academy, {new_child}! You are ready for an awesome adventure!",
                            "win",
                            str(random.random())
                        )
                        st.rerun()
                    else:
                        st.error(msg)
    st.stop()

# ==========================================
# 7. AUTHENTICATED APP SHELL & SIDEBAR
# ==========================================
user = get_user_by_id(st.session_state.user_id)

with st.sidebar:
    st.markdown(f"""
    <div style="background:#FFF9C4; padding:16px; border-radius:20px; border:3px solid #FBC02D; text-align:center;">
        <div style="font-size:3.2rem;">{user['avatar']}</div>
        <h3 style="margin:4px 0; color:#E65100;">{user['child_name']} (Age {user['age_group']})</h3>
        <div style="font-size:1.2rem; font-weight:700;">⭐ {user['stars']} Stars  |  🔥 {user['streak']} Streak</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Navigation")
    nav_choice = st.radio(
        "Go to:",
        ["🎮 Play Learning Games", "🏆 My Sticker Book", "📊 Parent Progress Dashboard"],
        label_visibility="collapsed"
    )

    st.markdown("### 🌍 Choose Learning World")
    selected_subject = st.selectbox(
        "World",
        ["🔢 Math Kingdom", "🔤 Alphabet Jungle", "🔬 Discovery Lab", "🎨 Shape & Color Island"],
        index=["🔢 Math Kingdom", "🔤 Alphabet Jungle", "🔬 Discovery Lab", "🎨 Shape & Color Island"].index(st.session_state.subject)
    )

    st.markdown("### 🎯 Choose Game Mode")
    selected_mode = st.selectbox(
        "Mode",
        list(MODES.keys()),
        index=list(MODES.keys()).index(st.session_state.mode)
    )

    st.markdown("### 📈 Difficulty Level")
    selected_level = st.selectbox(
        "Level",
        [1, 2, 3, 4],
        index=st.session_state.level - 1,
        format_func=lambda l: LEVEL_NAMES[l]
    )

    if (selected_subject != st.session_state.subject or
        selected_mode != st.session_state.mode or
        selected_level != st.session_state.level):
        st.session_state.subject = selected_subject
        st.session_state.mode = selected_mode
        st.session_state.level = selected_level
        st.session_state.current_q = generate_question(selected_subject, selected_level, selected_mode)
        st.session_state.answered = False
        st.session_state.last_result = None
        st.session_state.speech_payload = (st.session_state.current_q["voice"], "pop", str(random.random()))
        st.rerun()

    st.divider()
    if st.button("🚪 Switch Explorer / Log Out"):
        st.session_state.user_id = None
        st.session_state.current_q = None
        st.rerun()

# Trigger voice narration if queued
if st.session_state.speech_payload:
    txt, sfx, tid = st.session_state.speech_payload
    speak_energetic(txt, sfx, tid)
    st.session_state.speech_payload = None

# ==========================================
# 8. VIEW 1: PLAY LEARNING GAMES
# ==========================================
if nav_choice == "🎮 Play Learning Games":
    if st.session_state.current_q is None:
        st.session_state.current_q = generate_question(st.session_state.subject, st.session_state.level, st.session_state.mode)

    q_data = st.session_state.current_q

    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.markdown(f"## {st.session_state.subject} • {st.session_state.mode}")
        st.caption(f"{LEVEL_NAMES[st.session_state.level]} — {MODES[st.session_state.mode]}")
    with top_c2:
        if st.button("🔊 Read Aloud Again!"):
            speak_energetic(q_data["voice"], "pop", str(random.random()))

    st.markdown(f"""
    <div class="stage-card">
        <div class="visual-stage">{q_data['visual']}</div>
        <h2 style="color:#1A237E; font-size:1.85rem;">{q_data['question']}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Answer Buttons Grid
    cols = st.columns(len(q_data["options"]))
    for idx, opt in enumerate(q_data["options"]):
        with cols[idx]:
            if st.button(opt, key=f"opt_{idx}", disabled=st.session_state.answered):
                is_right = (opt == q_data["answer"])
                st.session_state.answered = True
                st.session_state.last_result = is_right
                unlocked = record_attempt(
                    user["id"],
                    st.session_state.subject,
                    st.session_state.mode,
                    st.session_state.level,
                    is_right
                )
                st.session_state.new_sticker = unlocked
                if is_right:
                    cheer = random.choice([
                        f"Woohoo! You nailed it, {user['child_name']}!",
                        f"Superstar! {opt} is right! You're so smart!",
                        f"Yippee! High five, {user['child_name']}! That's awesome!"
                    ])
                    st.session_state.speech_payload = (f"{cheer} Did you know? {q_data['fact']}", "win", str(random.random()))
                else:
                    st.session_state.speech_payload = (
                        f"Good try, {user['child_name']}! The right answer is {q_data['answer']}. Let's learn why! {q_data['fact']}",
                        "oops",
                        str(random.random())
                    )
                st.rerun()

    # Feedback & Fun Fact Card
    if st.session_state.answered:
        if st.session_state.last_result:
            st.balloons()
            st.success(f"🎉 AMAZING JOB, {user['child_name'].upper()}! You earned a ⭐ Star!")
            if st.session_state.new_sticker:
                st.info(f"🎁 NEW STICKER UNLOCKED: {st.session_state.new_sticker} Check your Sticker Book!")
        else:
            st.warning(f"💛 Almost! The right answer was **{q_data['answer']}** — you're getting smarter every try!")

        st.markdown(f"""
        <div class="fact-box">
            <strong>💡 Fun Fact for Little Scientists:</strong><br>{q_data['fact']}
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("➡️ Next Super Challenge!"):
            st.session_state.current_q = generate_question(st.session_state.subject, st.session_state.level, st.session_state.mode)
            st.session_state.answered = False
            st.session_state.last_result = None
            st.session_state.new_sticker = None
            st.session_state.speech_payload = (st.session_state.current_q["voice"], "pop", str(random.random()))
            st.rerun()

# ==========================================
# 9. VIEW 2: STICKER BOOK
# ==========================================
elif nav_choice == "🏆 My Sticker Book":
    st.markdown(f"## 🏆 {user['child_name']}'s Magical Sticker Album")
    st.write("Earn **1 new sticker** for every **3 stars** you collect!")

    all_stickers = ["🌟"] + STICKER_POOL
    grid = st.columns(6)
    for idx, sticker in enumerate(all_stickers):
        unlocked = sticker in user["stickers"]
        with grid[idx % 6]:
            st.markdown(f"""
            <div style="background:{'#FFFDE7' if unlocked else '#ECEFF1'};
                        border:3px solid {'#FFD54F' if unlocked else '#CFD8DC'};
                        border-radius:20px; padding:18px; text-align:center; margin-bottom:12px;">
                <div style="font-size:3rem; opacity:{'1' if unlocked else '0.25'};">{sticker}</div>
                <div style="font-size:0.85rem; font-weight:700; color:#546E7A;">
                    {'Unlocked!' if unlocked else 'Locked'}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 10. VIEW 3: PARENT PROGRESS DASHBOARD
# ==========================================
else:
    st.markdown(f"## 📊 Parent & Teacher Development Report: {user['child_name']}")
    rows = get_progress_stats(user["id"])

    if not rows:
        st.info("No exercises completed yet! Head over to **Play Learning Games** to start tracking progress.")
    else:
        import pandas as pd
        df = pd.DataFrame(rows, columns=["Subject", "Mode", "Level", "Correct", "Timestamp"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⭐ Total Stars", user["stars"])
        m2.metric("📝 Exercises Played", len(df))
        m3.metric("🎯 Overall Accuracy", f"{df['Correct'].mean() * 100:.0f}%")
        m4.metric("🏆 Stickers Earned", f"{len(user['stickers'])} / {len(STICKER_POOL) + 1}")

        st.markdown("### 📚 Mastery by Learning World")
        subj_summary = df.groupby("Subject").agg(
            Questions=("Correct", "count"),
            Correct_Answers=("Correct", "sum")
        ).reset_index()
        subj_summary["Accuracy (%)"] = (subj_summary["Correct_Answers"] / subj_summary["Questions"] * 100).round(1)
        st.dataframe(subj_summary, use_container_width=True, hide_index=True)

        st.markdown("### 📈 Progress by Difficulty Level")
        lvl_summary = df.groupby("Level").agg(
            Attempts=("Correct", "count"),
            Accuracy_Pct=("Correct", lambda s: round(s.mean() * 100, 1))
        ).reset_index()
        lvl_summary["Level Name"] = lvl_summary["Level"].map(LEVEL_NAMES)
        st.bar_chart(lvl_summary.set_index("Level Name")["Accuracy_Pct"])

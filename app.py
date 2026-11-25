import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import psycopg2
import hashlib
import random
import json
import os
import re
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & HIGH-CONTRAST SYMMETRICAL THEME
# ==========================================
st.set_page_config(
    page_title="WonderKids Academy 🌈",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Fredoka', sans-serif !important;
    color: #102A43 !important;
}

/* Soft, Calm Sky-Mint Background for High Foreground Contrast */
.stApp {
    background: linear-gradient(160deg, #E0F2FE 0%, #FEF9C3 50%, #DCFCE7 100%);
    background-attachment: fixed;
}

/* High-Contrast Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 4px solid #38BDF8 !important;
}

section[data-testid="stSidebar"] * {
    color: #102A43 !important;
}

/* Form Inputs & Labels High Contrast */
label, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #102A43 !important;
}

div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background-color: #F8FAFC !important;
    border: 2px solid #0284C7 !important;
    border-radius: 14px !important;
    color: #0F172A !important;
}

input {
    color: #0F172A !important;
    font-weight: 600 !important;
}

/* Symmetrical, High-Contrast 3D Candy Buttons */
div.stButton > button {
    border-radius: 22px !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    min-height: 68px !important;
    padding: 0.85rem 1.2rem !important;
    border: 3px solid #0284C7 !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
    box-shadow: 0 6px 0 #0284C7, 0 8px 16px rgba(15, 23, 42, 0.10) !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease !important;
    width: 100% !important;
}

div.stButton > button:hover {
    transform: translateY(-3px) !important;
    border-color: #D97706 !important;
    background: #FEF08A !important;
    color: #0F172A !important;
    box-shadow: 0 9px 0 #D97706, 0 12px 20px rgba(15, 23, 42, 0.15) !important;
}

div.stButton > button:active {
    transform: translateY(3px) !important;
    box-shadow: 0 2px 0 #0284C7 !important;
}

div.stButton > button:disabled {
    background: #E2E8F0 !important;
    border-color: #94A3B8 !important;
    color: #475569 !important;
    box-shadow: none !important;
}

/* Form Submit Buttons */
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 20px !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    min-height: 58px !important;
    border: 3px solid #15803D !important;
    background: #22C55E !important;
    color: #FFFFFF !important;
    box-shadow: 0 6px 0 #15803D !important;
    width: 100% !important;
}

div[data-testid="stFormSubmitButton"] > button:hover {
    background: #16A34A !important;
    color: #FFFFFF !important;
}

/* Rainbow Banner Header */
.rainbow-banner {
    background: linear-gradient(90deg, #EF4444, #F59E0B, #10B981, #0EA5E9, #8B5CF6);
    padding: 5px;
    border-radius: 30px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
    margin-bottom: 22px;
}

.banner-inner {
    background: #FFFFFF;
    border-radius: 26px;
    padding: 24px 28px;
    text-align: center;
}

/* Symmetrical Auth Panel Card */
.auth-card {
    background: #FFFFFF;
    border-radius: 26px;
    padding: 22px 24px;
    border: 4px solid #38BDF8;
    box-shadow: 0 8px 0 #0284C7;
    margin-bottom: 12px;
}

/* Top 4-Card Symmetrical HUD */
.hud-card {
    background: #FFFFFF;
    border: 3px solid #38BDF8;
    border-radius: 20px;
    padding: 14px 12px;
    text-align: center;
    box-shadow: 0 5px 0 #0284C7;
    height: 100%;
}

.hud-label {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #0369A1 !important;
}

.hud-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F172A !important;
    margin-top: 4px;
}

/* Main Centered Question Stage */
.stage-card {
    background: #FFFFFF;
    border-radius: 32px;
    padding: 28px 32px;
    border: 5px solid #0284C7;
    box-shadow: 0 10px 0 #0369A1, 0 16px 32px rgba(15, 23, 42, 0.12);
    text-align: center;
    margin: 18px 0 22px 0;
}

@keyframes gentleBob {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
}

.mascot-pill {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: #FEF3C7;
    border: 3px solid #D97706;
    border-radius: 999px;
    padding: 8px 22px;
    margin-bottom: 16px;
}

.mascot-avatar {
    font-size: 2.3rem;
    animation: gentleBob 2.2s ease-in-out infinite;
}

.visual-stage {
    font-size: 4rem;
    letter-spacing: 12px;
    margin: 14px auto;
    padding: 22px 18px;
    background: #F0F9FF;
    border-radius: 24px;
    border: 3px dashed #0284C7;
    color: #0F172A !important;
}

.question-title {
    color: #0F172A !important;
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    line-height: 1.35 !important;
    margin: 14px 0 4px 0 !important;
}

.fact-box {
    background: #ECFDF5;
    border: 3px solid #059669;
    border-left: 12px solid #047857;
    border-radius: 22px;
    padding: 20px 24px;
    font-size: 1.2rem;
    color: #064E3B !important;
    margin-top: 16px;
    box-shadow: 0 6px 0 #047857;
}

.badge-pill {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 1rem;
    background: #FEF08A;
    border: 2px solid #CA8A04;
    color: #713F12 !important;
    margin: 4px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 2. RESILIENT CLOUD DATABASE (NEON POSTGRESQL + SQLITE FALLBACK)
# ==========================================
def get_db_connection():
    db_url = None
    try:
        db_url = st.secrets.get("DATABASE_URL")
    except Exception:
        db_url = os.environ.get("DATABASE_URL")

    if db_url:
        clean_url = str(db_url).strip()
        if clean_url.startswith("psql "):
            clean_url = clean_url[5:].strip()
        clean_url = clean_url.strip("'\"")

        if "channel_binding=" in clean_url:
            parts = clean_url.split("?")
            if len(parts) == 2:
                params = [p for p in parts[1].split("&") if not p.startswith("channel_binding=")]
                clean_url = parts[0] + ("?" + "&".join(params) if params else "")

        if "sslmode=" not in clean_url:
            sep = "&" if "?" in clean_url else "?"
            clean_url += f"{sep}sslmode=require"

        # Auto-inject endpoint ID option if an ep-* host is present (prevents SNI errors)
        ep_match = re.search(r"@(ep-[a-z0-9-]+)", clean_url)
        if ep_match and "options=" not in clean_url:
            ep_id = ep_match.group(1).replace("-pooler", "")
            sep = "&" if "?" in clean_url else "?"
            clean_url += f"{sep}options=endpoint%3D{ep_id}"

        try:
            return psycopg2.connect(clean_url, connect_timeout=10), "postgres"
        except Exception as e:
            st.warning(f"⚠️ Cloud DB Error ({type(e).__name__}): {e} — Using local storage.")

    return sqlite3.connect("wonderkids.db"), "sqlite"

def init_db():
    conn, db_type = get_db_connection()
    c = conn.cursor()
    if db_type == "postgres":
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                subject TEXT NOT NULL,
                mode TEXT NOT NULL,
                level INTEGER NOT NULL,
                is_correct INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
    else:
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
                timestamp TEXT NOT NULL
            )
        """)
    conn.commit()
    conn.close()

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, child_name, age_group, avatar):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    try:
        c.execute(
            f"""INSERT INTO users (username, password_hash, child_name, age_group, avatar, stars, streak, stickers, created_at)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, 0, 0, {ph}, {ph})""",
            (username.lower().strip(), hash_pw(password), child_name.strip(), age_group, avatar, json.dumps(["🌟"]), datetime.now().isoformat())
        )
        conn.commit()
        return True, "Account created! Let's play!"
    except Exception:
        conn.rollback()
        return False, "That username is already taken! Try another fun name."
    finally:
        conn.close()

def authenticate_user(username, password):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    c.execute(
        f"SELECT id, username, child_name, age_group, avatar, stars, streak, stickers FROM users WHERE username={ph} AND password_hash={ph}",
        (username.lower().strip(), hash_pw(password))
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "username": row[1], "child_name": row[2],
            "age_group": row[3], "avatar": row[4], "stars": row[5],
            "streak": row[6], "stickers": json.loads(row[7])
        }
    return None

def get_user_by_id(user_id):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    c.execute(f"SELECT id, username, child_name, age_group, avatar, stars, streak, stickers FROM users WHERE id={ph}", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "username": row[1], "child_name": row[2],
            "age_group": row[3], "avatar": row[4], "stars": row[5],
            "streak": row[6], "stickers": json.loads(row[7])
        }
    return None

STICKER_POOL = ["🦄", "🦖", "🚀", "🌈", "🐬", "🐼", "🦋", "🍓", "🎨", "🏆", "🐢", "🦊", "🐘", "🪐", "🐙", "🦁", "🍦", "🚂", "🦕"]

def record_attempt(user_id, subject, mode, level, is_correct):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    c.execute(
        f"INSERT INTO progress_log (user_id, subject, mode, level, is_correct, timestamp) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
        (user_id, subject, mode, level, 1 if is_correct else 0, datetime.now().isoformat())
    )
    c.execute(f"SELECT stars, streak, stickers FROM users WHERE id={ph}", (user_id,))
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
        f"UPDATE users SET stars={ph}, streak={ph}, stickers={ph} WHERE id={ph}",
        (stars, streak, json.dumps(stickers), user_id)
    )
    conn.commit()
    conn.close()
    return new_sticker

def get_progress_stats(user_id):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    c.execute(f"SELECT subject, mode, level, is_correct, timestamp FROM progress_log WHERE user_id={ph}", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# ==========================================
# 3. ENERGETIC CHILD VOICE + XYLOPHONE SFX ENGINE
# ==========================================
def speak_child_voice(text: str, sfx: str = "none", trigger_id: str = "0"):
    safe_text = text.replace('"', "'").replace("\n", " ")
    js_code = f"""
    <script>
    (function() {{
        const msgText = "{safe_text}";
        const sfxType = "{sfx}";

        try {{
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {{
                const ctx = new AudioCtx();
                const playXylophone = (freq, start, dur, wave='sine') => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = wave;
                    osc.frequency.setValueAtTime(freq, ctx.currentTime + start);
                    gain.gain.setValueAtTime(0.22, ctx.currentTime + start);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + dur);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(ctx.currentTime + start);
                    osc.stop(ctx.currentTime + start + dur);
                }};
                if (sfxType === "win") {{
                    playXylophone(587.33, 0.00, 0.12);
                    playXylophone(739.99, 0.10, 0.12);
                    playXylophone(880.00, 0.20, 0.14);
                    playXylophone(1174.66, 0.32, 0.35);
                }} else if (sfxType === "oops") {{
                    playXylophone(392.00, 0.00, 0.16, 'triangle');
                    playXylophone(349.23, 0.16, 0.24, 'triangle');
                }} else if (sfxType === "pop") {{
                    playXylophone(880.00, 0.00, 0.08, 'sine');
                    playXylophone(1046.50, 0.07, 0.10, 'sine');
                }}
            }}
        }} catch(e) {{}}

        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(msgText);
            const voices = window.speechSynthesis.getVoices();
            const childFriendly = voices.find(v =>
                /Google UK English Female|Google US English|Samantha|Victoria|Zira|Tessa|Karen/i.test(v.name)
            );
            if (childFriendly) utter.voice = childFriendly;
            utter.pitch = 1.58;
            utter.rate = 1.12;
            utter.volume = 1.0;
            window.speechSynthesis.speak(utter);
        }}
    }})();
    </script>
    <div style="display:none;">{trigger_id}</div>
    """
    components.html(js_code, height=0)

# ==========================================
# 4. INTERACTIVE TAP-TO-COUNT / TAP-TO-HEAR PLAYGROUND
# ==========================================
def render_interactive_toys(items: list, label_hint: str = "Tap each picture to count & pop!"):
    items_json = json.dumps(items)
    html_widget = f"""
    <div style="text-align:center; font-family:'Fredoka',sans-serif; padding:6px;">
      <div style="font-size:1.05rem; font-weight:700; color:#0F172A; margin-bottom:10px;">👆 {label_hint}</div>
      <div id="toy-box" style="display:flex; flex-wrap:wrap; justify-content:center; gap:12px;"></div>
      <div id="tap-readout" style="margin-top:8px; font-size:1.35rem; font-weight:700; color:#B45309; min-height:28px;"></div>
    </div>
    <script>
      const toys = {items_json};
      const box = document.getElementById('toy-box');
      const readout = document.getElementById('tap-readout');
      let count = 0;

      toys.forEach((item) => {{
        const btn = document.createElement('button');
        btn.innerText = item;
        btn.style.cssText = `
          font-size: 3rem; background: #FFFFFF; border: 4px solid #0284C7;
          border-radius: 20px; padding: 10px 18px; cursor: pointer;
          box-shadow: 0 5px 0 #0369A1; transition: transform 0.15s;
        `;
        btn.onclick = () => {{
          if (!btn.dataset.tapped) {{
            btn.dataset.tapped = "1";
            count++;
            btn.style.background = "#BBF7D0";
            btn.style.borderColor = "#15803D";
            btn.style.boxShadow = "0 5px 0 #15803D";
            btn.style.transform = "scale(1.12)";
            readout.innerText = "⭐ Counted: " + count + "!";
            if ('speechSynthesis' in window) {{
              window.speechSynthesis.cancel();
              const u = new SpeechSynthesisUtterance(String(count));
              u.pitch = 1.6; u.rate = 1.15;
              window.speechSynthesis.speak(u);
            }}
          }}
        }};
        box.appendChild(btn);
      }});
    </script>
    """
    components.html(html_widget, height=170)

# ==========================================
# 5. EXPANDED EXERCISE BANK (ALWAYS 4 SYMMETRICAL OPTIONS)
# ==========================================
LEVEL_NAMES = {
    1: "🌱 Level 1: Tiny Sprout (Age 3)",
    2: "🐥 Level 2: Curious Explorer (Age 4)",
    3: "🦊 Level 3: Super Adventurer (Age 5)",
    4: "🚀 Level 4: Brainy Champion (Age 6)"
}

MODES = {
    "🎈 Adventure Mode": "Playful learning with fun facts & cheering!",
    "⚡ Lightning Pop": "Fast-paced rounds to build a mega star streak!",
    "🧩 Brainy Pattern & Logic": "Solve patterns, riddles, and brain teasers!"
}

def generate_question(subject: str, level: int, mode: str):
    if subject == "🔢 Math Kingdom":
        if mode == "🧩 Brainy Pattern & Logic":
            patterns = [
                ("🍎 🍌 🍎 🍌 🍎 ❓", "What fruit comes next in the yummy pattern?", "🍌 Banana", ["🍌 Banana", "🍎 Apple", "🍇 Grapes", "🍓 Strawberry"],
                 "Patterns repeat in a special order! Spot the pattern and you can predict what comes next!", []),
                ("2️⃣ ➔ 4️⃣ ➔ 6️⃣ ➔ ❓", "Skip-count by 2s! Which number jumps in next?", "8️⃣ Eight", ["7️⃣ Seven", "8️⃣ Eight", "9️⃣ Nine", "5️⃣ Five"],
                 "Counting by 2s is like hopping over every second stone across a river!", []),
                ("5️⃣ ➔ 10 ➔ 15 ➔ ❓", "Count by 5s! High five! What number is next?", "20 Twenty", ["16 Sixteen", "20 Twenty", "18 Eighteen", "25 Twenty-Five"],
                 "You have 5 fingers on each hand—two hands make 10, and four hands make 20!", []),
                ("10 ➔ 9 ➔ 8 ➔ ❓", "Rocket countdown! Which number blasts off next?", "7️⃣ Seven", ["6️⃣ Six", "7️⃣ Seven", "9️⃣ Nine", "5️⃣ Five"],
                 "Astronauts count backward to zero before launching rockets into space!", [])
            ]
            vis, q, ans, opts, fact, toys = random.choice(patterns)
            return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                    "voice": f"Ooh, puzzle time! {q}", "toys": toys}

        if level == 1:
            n = random.randint(1, 5)
            emoji = random.choice(["🍎", "🦆", "⭐", "🍓", "🐢", "🧁"])
            opts = random.sample([str(i) for i in range(1, 6)], 4)
            if str(n) not in opts:
                opts[0] = str(n)
            random.shuffle(opts)
            return {
                "visual": " ".join([emoji] * n),
                "question": f"Tap and count! How many {emoji} are here?",
                "answer": str(n),
                "options": opts,
                "fact": f"Super counting! {n} is one of our magic counting numbers!",
                "voice": f"Yay! Tap each picture to count! How many {emoji} do you see?",
                "toys": [emoji] * n
            }

        elif level == 2:
            if random.choice([True, False]):
                n = random.randint(6, 10)
                emoji = random.choice(["🐠", "🦋", "🎈", "🍪", "🚗"])
                pool = {str(n), str(n - 1), str(min(10, n + 1)), str(n - 2), str(max(1, n - 3))}
                opts = list(pool)[:4]
                random.shuffle(opts)
                return {
                    "visual": " ".join([emoji] * n),
                    "question": f"Big counting challenge! How many {emoji} are swimming?",
                    "answer": str(n),
                    "options": opts,
                    "fact": f"Awesome! Counting all the way to {n} makes your math brain super strong!",
                    "voice": f"Whoa, look at all those {emoji}! Can you count how many there are?",
                    "toys": [emoji] * n
                }
            else:
                a, b = random.sample(range(2, 9), 2)
                ans = f"Basket A ({a})" if a > b else f"Basket B ({b})"
                opts = [f"Basket A ({a})", f"Basket B ({b})", "Both Equal!", "Zero Fruit"]
                random.shuffle(opts)
                return {
                    "visual": f"Basket A: {'🍓'*a}   🆚   Basket B: {'🍊'*b}",
                    "question": "Which basket has MORE yummy fruit?",
                    "answer": ans,
                    "options": opts,
                    "fact": "Comparing groups helps us tell which pile is bigger or smaller!",
                    "voice": "Yum! Look at the two fruit baskets! Which basket has more fruit?",
                    "toys": []
                }

        elif level == 3:
            a, b = random.randint(1, 5), random.randint(1, 5)
            ans = a + b
            pool = {str(ans), str(ans + 1), str(max(1, ans - 1)), str(ans + 2), str(max(0, ans - 2))}
            opts = list(pool)[:4]
            random.shuffle(opts)
            return {
                "visual": f"{'🦖'*a}  ➕  {'🦖'*b}",
                "question": f"{a} dinosaurs meet {b} more dinosaurs! How many altogether?",
                "answer": str(ans),
                "options": opts,
                "fact": f"{a} + {b} = {ans}! Putting two groups together is called ADDITION!",
                "voice": f"Roar! {a} friendly dinosaurs meet {b} more dinosaurs! How many dinosaurs altogether?",
                "toys": ["🦖"] * (a + b)
            }

        else:
            q_type = random.choice(["sub", "time", "missing"])
            if q_type == "sub":
                a = random.randint(6, 12)
                b = random.randint(2, 5)
                ans = a - b
                pool = {str(ans), str(ans + 1), str(max(0, ans - 1)), str(a), str(ans + 2)}
                opts = list(pool)[:4]
                random.shuffle(opts)
                return {
                    "visual": f"{'🎈'*a}  ➖  ({b} popped!)",
                    "question": f"You had {a} party balloons and {b} popped! How many are left?",
                    "answer": str(ans),
                    "options": opts,
                    "fact": f"{a} take away {b} equals {ans}! That's subtraction in action!",
                    "voice": f"Pop pop! You had {a} party balloons and {b} floated away! How many are left?",
                    "toys": []
                }
            elif q_type == "time":
                clocks = [
                    ("🕒", "3:00 (3 O'Clock)", ["3:00 (3 O'Clock)", "6:00 (6 O'Clock)", "12:00 (12 O'Clock)", "9:00 (9 O'Clock)"]),
                    ("🕕", "6:00 (6 O'Clock)", ["6:00 (6 O'Clock)", "3:00 (3 O'Clock)", "1:00 (1 O'Clock)", "10:00 (10 O'Clock)"]),
                    ("🕘", "9:00 (9 O'Clock)", ["9:00 (9 O'Clock)", "3:00 (3 O'Clock)", "6:00 (6 O'Clock)", "12:00 (12 O'Clock)"])
                ]
                clk, ans, opts = random.choice(clocks)
                random.shuffle(opts)
                return {
                    "visual": f"⏰  {clk}  ⏰",
                    "question": "Look at the clock hands! What time is it?",
                    "answer": ans,
                    "options": opts,
                    "fact": "The short hand points to the hour, and when the long hand points straight up to 12, it's O'Clock!",
                    "voice": "Tick tock! Look at the clock! What time does it show?",
                    "toys": []
                }
            else:
                total = random.randint(7, 10)
                part = random.randint(2, 5)
                missing = total - part
                pool = {str(missing), str(missing + 1), str(max(1, missing - 1)), str(total), str(missing + 2)}
                opts = list(pool)[:4]
                random.shuffle(opts)
                return {
                    "visual": f"{part}  ➕  ❓  =  {total}",
                    "question": f"Mystery number! {part} plus WHAT equals {total}?",
                    "answer": str(missing),
                    "options": opts,
                    "fact": f"{part} + {missing} = {total}! You solved an algebra mystery like a real mathematician!",
                    "voice": f"Detective math! {part} plus what secret number equals {total}?",
                    "toys": []
                }

    elif subject == "🔤 Alphabet Jungle":
        if mode == "🧩 Brainy Pattern & Logic":
            riddles = [
                ("🐱  🎩  🦇", "Which word RHYMES with CAT?", "🎩 HAT", ["🎩 HAT", "🐶 DOG", "☀️ SUN", "🐟 FISH"],
                 "Rhyming words end with the exact same sound—just like songs and poems!"),
                ("A ➔ B ➔ C ➔ ❓", "Sing the ABC song! Which letter marches next?", "🇩 D", ["🇩 D", "🇫 F", "🇿 Z", "🇲 M"],
                 "There are 26 letters in the English alphabet, and every book is written with them!"),
                ("🐸  🪵  🐶", "Which word RHYMES with FROG?", "🪵 LOG", ["🪵 LOG", "🚗 CAR", "🍎 APPLE", "🌙 MOON"],
                 "Frog and log both end with the 'OG' sound!")
            ]
            vis, q, ans, opts, fact = random.choice(riddles)
            return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                    "voice": f"Listen closely! {q}", "toys": []}

        bank = {
            1: [
                ("🦁", "ROAR! What letter does LION start with?", "L", ["L", "B", "S", "M"],
                 "Lions are big cats whose mighty roar can be heard 5 miles away!"),
                ("🍎", "Crunch! What letter does APPLE start with?", "A", ["A", "P", "T", "D"],
                 "Apples float in water because they are 25% air inside!"),
                ("🐸", "Ribbit! What letter does FROG start with?", "F", ["F", "G", "R", "K"],
                 "Frogs drink water right through their skin—no cup needed!")
            ],
            2: [
                ("🐘", "Stomp stomp! Which animal starts with the 'Eh' sound (Letter E)?", "🐘 Elephant", ["🐘 Elephant", "🐯 Tiger", "🐵 Monkey", "🐻 Bear"],
                 "Elephants use their long trunks like a nose, a hand, and even a snorkel!"),
                ("🚀", "Zoom! Which picture starts with the 'Rrr' sound (Letter R)?", "🚀 Rocket", ["🚀 Rocket", "⛵ Boat", "🚲 Bike", "🚂 Train"],
                 "Rockets travel faster than 17,000 miles per hour to reach space!"),
                ("🐢", "Which slow-and-steady friend starts with the letter T?", "🐢 Turtle", ["🐢 Turtle", "🦆 Duck", "🐷 Pig", "🐝 Bee"],
                 "Turtles carry their cozy shell homes right on their backs!")
            ],
            3: [
                ("☀️  _ U N", "Spell the bright yellow star in the sky! Missing letter?", "S (SUN)", ["S (SUN)", "B (BUN)", "R (RUN)", "F (FUN)"],
                 "The Sun is actually a giant, glowing star that keeps Earth warm!"),
                ("🐱  _ A T", "Meow! Which letter completes the word _ A T?", "C (CAT)", ["C (CAT)", "D (DAT)", "P (PAT)", "M (MAT)"],
                 "Cats use their whiskers to measure if they can squeeze through tight spaces!"),
                ("🐷  P _ G", "Oink oink! Which vowel goes in the middle of P _ G?", "I (PIG)", ["I (PIG)", "A (PAG)", "O (POG)", "E (PEG)"],
                 "A, E, I, O, U are the 5 superstar vowels—almost every word needs one!")
            ],
            4: [
                ("🦈  🚢  🐑", "Which sound do SHARK, SHIP, and SHEEP all start with?", "SH", ["SH", "CH", "TH", "ST"],
                 "When S and H team up together, they make the quiet 'SHHH' sound!"),
                ("🦋  🐜", "Which word is the OPPOSITE of 'BIG'?", "🐜 TINY", ["🐜 TINY", "🐘 HUGE", "🦒 TALL", "🐳 GIANT"],
                 "Opposites are word pairs that mean totally different things—like hot & cold, or big & tiny!"),
                ("🍎 ➔ 🍎🍎🍎", "One apple, many ______! How do we spell more than one apple?", "Apples", ["Apples", "Apple", "Appling", "Appled"],
                 "Adding the letter 'S' to the end of most words turns ONE into MANY!"),
                ("📚", "Which word is an ACTION word (verb)?", "🏃 JUMP", ["🏃 JUMP", "🪑 CHAIR", "🔵 BLUE", "🍎 APPLE"],
                 "Action words tell us what someone or something is doing!")
            ]
        }
        vis, q, ans, opts, fact = random.choice(bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Welcome to Alphabet Jungle! {q}", "toys": []}

    elif subject == "🔬 Discovery Lab":
        science_bank = {
            1: [
                ("🐄  🥛", "Moo! Which friendly farm animal gives us milk?", "🐄 Cow", ["🐄 Cow", "🐔 Chicken", "🐷 Pig", "🦆 Duck"],
                 "Cows have four stomach compartments to help them digest yummy grass!"),
                ("🌧️  ☀️", "When sunshine shines through raindrops, what appears in the sky?", "🌈 Rainbow", ["🌈 Rainbow", "⛄ Snowman", "🌙 Moon", "🪨 Rock"],
                 "Sunlight is made of 7 rainbow colors hiding together inside white light!"),
                ("👃  🌸", "Which part of your body do you use to smell a yummy flower?", "👃 Nose", ["👃 Nose", "👂 Ear", "👀 Eyes", "🦶 Foot"],
                 "Your nose can recognize thousands of different smells—like cookies baking!")
            ],
            2: [
                ("🐛  ➔  💤  ➔  ❓", "A hungry caterpillar sleeps in a chrysalis and wakes up as a...", "🦋 Butterfly", ["🦋 Butterfly", "🐸 Frog", "🐟 Fish", "🐦 Bird"],
                 "Butterflies taste flowers using tiny sensors on their FEET!"),
                ("🌱  ☀️  💧", "What does a tiny seed need to grow into a tall flower?", "☀️ Sun & Water", ["☀️ Sun & Water", "🍕 Pizza", "🧸 Teddy Bear", "❄️ Ice Cubes"],
                 "Plants drink water through their roots like straws and make food from sunshine!")
            ],
            3: [
                ("🪐  🌍  ☀️", "Which planet do WE live on?", "🌍 Earth", ["🌍 Earth", "🪐 Saturn", "🔴 Mars", "☀️ The Sun"],
                 "Earth is the only known planet with liquid oceans and living creatures!"),
                ("🧲  📎", "Which object will stick to a super magnet?", "📎 Metal Paperclip", ["📎 Metal Paperclip", "🍌 Banana", "🧸 Plush Toy", "🖍️ Crayon"],
                 "Magnets have invisible force fields that pull on iron and steel!"),
                ("🐧  ❄️", "Where does a fluffy penguin live?", "❄️ Icy Antarctica", ["❄️ Icy Antarctica", "🌵 Hot Desert", "🌴 Tropical Jungle", "🌋 Volcano"],
                 "Penguins have thick waterproof feathers that keep them cozy in freezing water!")
            ],
            4: [
                ("🧊  🔥  💧", "When warm sunshine heats up an ice cube, it melts into...", "💧 Liquid Water", ["💧 Liquid Water", "🪨 Solid Rock", "🪵 Wood", "🏖️ Sand"],
                 "Water is a shape-shifter! It can be solid ice, liquid water, or invisible steam!"),
                ("🦉  🦇  🌙", "Animals that sleep all day and wake up at night are called...", "🦉 Nocturnal", ["🦉 Nocturnal", "🐠 Aquatic", "🦖 Extinct", "🐧 Arctic"],
                 "Owls have giant eyes that capture tiny bits of moonlight so they can see in the dark!"),
                ("🫀  💓", "Which muscle inside your chest pumps blood all around your body?", "❤️ Your Heart", ["❤️ Your Heart", "🧠 Your Brain", "🦴 Your Bones", "💪 Your Biceps"],
                 "Your heart is about the size of your fist and beats around 100,000 times every single day!"),
                ("🦕  🦴", "Animals like T-Rex that lived millions of years ago and are no longer alive are...", "🦖 Extinct", ["🦖 Extinct", "Hibernating", "Nocturnal", "Amphibians"],
                 "Scientists called paleontologists dig up dinosaur fossils to learn how they lived!")
            ]
        }
        vis, q, ans, opts, fact = random.choice(science_bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Put on your scientist goggles! {q}", "toys": []}

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
                 "Red, Yellow, and Blue are Primary Colors—you can mix them to make a rainbow!"),
                ("🔵  ➕  🟡  =  ❓", "Swirl BLUE and YELLOW paint together! Which color appears?", "🟢 Green", ["🟢 Green", "🟠 Orange", "🟣 Purple", "🩷 Pink"],
                 "Leaves look green because of chlorophyll, which catches sunlight for trees!"),
                ("🔴  ➕  🔵  =  ❓", "Mix RED and BLUE paint! Which royal color pops out?", "🟣 Purple", ["🟣 Purple", "🟢 Green", "🟠 Orange", "🟡 Yellow"],
                 "Purple was once so rare that only kings and queens could wear purple clothes!")
            ],
            3: [
                ("🐝  🍯", "What 6-sided shape do busy bees build inside their honeycomb?", "⬡ Hexagon", ["⬡ Hexagon", "⭕ Circle", "🔺 Triangle", "⬛ Square"],
                 "Hexagons fit together with zero wasted space—bees are tiny math geniuses!"),
                ("🛑", "How many sides does a red STOP sign (Octagon) have?", "8 Sides", ["8 Sides", "6 Sides", "4 Sides", "3 Sides"],
                 "Octo means EIGHT—just like an octopus with 8 arms and an octagon with 8 sides!")
            ],
            4: [
                ("🎲  📦", "A 3D square box shape with 6 flat faces is called a...", "🧊 Cube", ["🧊 Cube", "⚽ Sphere", "🍦 Cone", "🥫 Cylinder"],
                 "2D shapes are flat like paper, while 3D shapes pop out so you can hold them!"),
                ("🍦  🎉", "A party hat and an ice cream waffle share which 3D shape?", "🔺 Cone", ["🔺 Cone", "🧊 Cube", "⚽ Sphere", "📦 Box"],
                 "Cones have a round circle on one end and a sharp point on the other!"),
                ("🍕  ✂️  🍕", "If you cut 1 whole pizza into 2 EQUAL slices, each slice is called...", "½ One Half", ["½ One Half", "¼ One Quarter", "2 Wholes", "Zero"],
                 "Halves must be the exact same size so everyone gets a fair share!")
            ]
        }
        vis, q, ans, opts, fact = random.choice(shape_bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Ahoy, explorer! {q}", "toys": []}

# ==========================================
# 6. SESSION STATE INITIALIZATION
# ==========================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
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
# 7. SYMMETRICAL LOGIN & SIGN-UP GATEWAY
# ==========================================
if st.session_state.user_id is None:
    st.markdown("""
    <div class="rainbow-banner">
      <div class="banner-inner">
        <div style="font-size:3.2rem; margin-bottom:6px;">🦁 🦄 🦖 🚀 🌈</div>
        <h1 style="font-size:3rem; color:#0F172A; margin:0;">WonderKids Academy</h1>
        <p style="font-size:1.3rem; color:#334155; margin:8px 0 14px 0;">
            High-Contrast Cartoon Learning World for Little Explorers (Ages 3 – 6)
        </p>
        <span class="badge-pill">🔢 Math Kingdom</span>
        <span class="badge-pill">🔤 Alphabet Jungle</span>
        <span class="badge-pill">🔬 Discovery Lab</span>
        <span class="badge-pill">🎨 Shape & Color Island</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("""
        <div class="auth-card">
            <h3 style="margin:0; text-align:center; color:#0369A1;">🔑 Returning Explorer Log In</h3>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            login_user = st.text_input("Explorer Username", placeholder="e.g., leo_dino")
            login_pw = st.text_input("Secret Passcode", type="password", placeholder="••••••")
            st.write("")
            submitted_login = st.form_submit_button("🚀 Jump Into the Playground!")
            if submitted_login:
                user = authenticate_user(login_user, login_pw)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.level = max(1, min(4, user["age_group"] - 2))
                    st.session_state.current_q = generate_question(st.session_state.subject, st.session_state.level, st.session_state.mode)
                    st.session_state.speech_payload = (
                        f"Yay! Welcome back {user['child_name']}! Let's play and collect super stars!",
                        "win",
                        str(random.random())
                    )
                    st.rerun()
                else:
                    st.error("Oopsie! Check your username or secret passcode and try again.")

    with col_right:
        st.markdown("""
        <div class="auth-card">
            <h3 style="margin:0; text-align:center; color:#15803D;">✨ New Explorer Sign Up</h3>
        </div>
        """, unsafe_allow_html=True)
        with st.form("signup_form"):
            new_child = st.text_input("Child's First Name", placeholder="e.g., Maya")
            new_user = st.text_input("Choose a Fun Username", placeholder="e.g., maya_star")
            new_pw = st.text_input("Create a Secret Passcode", type="password", placeholder="e.g., 1234")
            r_c1, r_c2 = st.columns(2)
            with r_c1:
                age = st.selectbox("Child's Age", [3, 4, 5, 6], format_func=lambda a: f"🎂 {a} Years Old")
            with r_c2:
                avatar = st.selectbox("Cartoon Buddy", ["🦁 Leo", "🦄 Sparkle", "🦖 Rexy", "🐼 Bamboo", "🚀 Astro"])
            submitted_signup = st.form_submit_button("🎉 Create My Profile & Play!")
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
                            f"Hooray! Hi {new_child}! Welcome to WonderKids Academy! Let's have super fun!",
                            "win",
                            str(random.random())
                        )
                        st.rerun()
                    else:
                        st.error(msg)
    st.stop()

# ==========================================
# 8. AUTHENTICATED APP SHELL & SIDEBAR
# ==========================================
user = get_user_by_id(st.session_state.user_id)

with st.sidebar:
    st.markdown(f"""
    <div style="background:#FEF9C3; padding:16px; border-radius:22px; border:3px solid #D97706; text-align:center; box-shadow:0 5px 0 #B45309; margin-bottom:14px;">
        <div style="font-size:3.2rem;">{user['avatar']}</div>
        <h3 style="margin:4px 0; color:#0F172A;">{user['child_name']} • Age {user['age_group']}</h3>
        <div style="font-size:1.15rem; font-weight:700; color:#0369A1;">⭐ {user['stars']} Stars  |  🔥 {user['streak']} Streak</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Playground Map")
    nav_choice = st.radio(
        "Go to:",
        ["🎮 Play Learning Games", "🏆 My Sticker Book", "📊 Parent Progress Report"],
        label_visibility="collapsed"
    )

    st.markdown("### 🌍 Learning World")
    selected_subject = st.selectbox(
        "World",
        ["🔢 Math Kingdom", "🔤 Alphabet Jungle", "🔬 Discovery Lab", "🎨 Shape & Color Island"],
        index=["🔢 Math Kingdom", "🔤 Alphabet Jungle", "🔬 Discovery Lab", "🎨 Shape & Color Island"].index(st.session_state.subject)
    )

    st.markdown("### 🎯 Game Mode")
    selected_mode = st.selectbox(
        "Mode",
        list(MODES.keys()),
        index=list(MODES.keys()).index(st.session_state.mode)
    )

    st.markdown("### 📈 Age & Skill Level")
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
    if st.button("🚪 Switch Kid / Log Out"):
        st.session_state.user_id = None
        st.session_state.current_q = None
        st.rerun()

if st.session_state.speech_payload:
    txt, sfx, tid = st.session_state.speech_payload
    speak_child_voice(txt, sfx, tid)
    st.session_state.speech_payload = None

# ==========================================
# 9. VIEW 1: SYMMETRICAL GAME ARENA
# ==========================================
if nav_choice == "🎮 Play Learning Games":
    if st.session_state.current_q is None:
        st.session_state.current_q = generate_question(st.session_state.subject, st.session_state.level, st.session_state.mode)

    q_data = st.session_state.current_q

    # Symmetrical 4-Column Top HUD Bar
    h1, h2, h3, h4 = st.columns(4, gap="medium")
    with h1:
        st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">🌍 Learning World</div>
            <div class="hud-value">{st.session_state.subject}</div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">🎯 Game Mode</div>
            <div class="hud-value">{st.session_state.mode}</div>
        </div>
        """, unsafe_allow_html=True)
    with h3:
        st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">⭐ Score & Streak</div>
            <div class="hud-value">⭐ {user['stars']}  •  🔥 {user['streak']}</div>
        </div>
        """, unsafe_allow_html=True)
    with h4:
        if st.button("🔊 Hear Question"):
            speak_child_voice(q_data["voice"], "pop", str(random.random()))

    # Centered Question Stage Card
    st.markdown(f"""
    <div class="stage-card">
        <div class="mascot-pill">
            <span class="mascot-avatar">{user['avatar']}</span>
            <span style="font-size:1.15rem; font-weight:700; color:#78350F;">
                "{user['child_name']}, pick the right answer card below!"
            </span>
        </div>
        <div class="visual-stage">{q_data['visual']}</div>
        <div class="question-title">{q_data['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if q_data.get("toys"):
        render_interactive_toys(q_data["toys"])

    # Strict 2x2 Symmetrical Answer Grid (Equal Width & Height)
    options = q_data["options"]
    row1 = st.columns(2, gap="large")
    row2 = st.columns(2, gap="large")
    grid_slots = [row1[0], row1[1], row2[0], row2[1]]

    for idx, opt in enumerate(options[:4]):
        with grid_slots[idx]:
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
                        f"Woohoo! You did it, {user['child_name']}!",
                        f"Yippee! {opt} is right! You're a superstar!",
                        f"Yay! High five, {user['child_name']}! Super smart!"
                    ])
                    st.session_state.speech_payload = (f"{cheer} Fun fact! {q_data['fact']}", "win", str(random.random()))
                else:
                    st.session_state.speech_payload = (
                        f"Nice try, {user['child_name']}! The answer is {q_data['answer']}. Here is a cool fact! {q_data['fact']}",
                        "oops",
                        str(random.random())
                    )
                st.rerun()

    if st.session_state.answered:
        st.write("")
        if st.session_state.last_result:
            st.balloons()
            st.success(f"🎉 WOOHOO, {user['child_name'].upper()}! You won a shiny ⭐ Star!")
            if st.session_state.new_sticker:
                st.info(f"🎁 NEW STICKER UNLOCKED: {st.session_state.new_sticker} Check your Sticker Book!")
        else:
            st.warning(f"💛 Good try! The right answer was **{q_data['answer']}** — let's keep learning!")

        st.markdown(f"""
        <div class="fact-box">
            <strong>💡 Did You Know? (Fun Kid Fact):</strong><br>{q_data['fact']}
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        _, center_btn, _ = st.columns([1, 2, 1])
        with center_btn:
            if st.button("➡️ Next Fun Challenge!"):
                st.session_state.current_q = generate_question(st.session_state.subject, st.session_state.level, st.session_state.mode)
                st.session_state.answered = False
                st.session_state.last_result = None
                st.session_state.new_sticker = None
                st.session_state.speech_payload = (st.session_state.current_q["voice"], "pop", str(random.random()))
                st.rerun()

# ==========================================
# 10. VIEW 2: SYMMETRICAL 5x4 STICKER BOOK
# ==========================================
elif nav_choice == "🏆 My Sticker Book":
    st.markdown(f"## 🏆 {user['child_name']}'s Magical Sticker Album")
    st.write("Collect **1 new cartoon sticker** for every **3 stars** you win!")

    all_stickers = ["🌟"] + STICKER_POOL  # 20 stickers = exact 5 columns x 4 rows
    grid = st.columns(5, gap="medium")
    for idx, sticker in enumerate(all_stickers):
        unlocked = sticker in user["stickers"]
        with grid[idx % 5]:
            st.markdown(f"""
            <div style="background:{'#FFFFFF' if unlocked else '#E2E8F0'};
                        border:3px solid {'#D97706' if unlocked else '#94A3B8'};
                        border-radius:22px; padding:18px 10px; text-align:center; margin-bottom:14px;
                        box-shadow:0 5px 0 {'#B45309' if unlocked else '#64748B'};">
                <div style="font-size:3.2rem; opacity:{'1' if unlocked else '0.30'};">{sticker}</div>
                <div style="font-size:0.95rem; font-weight:700; color:{'#0F172A' if unlocked else '#475569'}; margin-top:4px;">
                    {'Unlocked!' if unlocked else 'Locked'}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 11. VIEW 3: SYMMETRICAL PARENT PROGRESS REPORT
# ==========================================
else:
    st.markdown(f"## 📊 Parent & Teacher Development Report: {user['child_name']}")
    rows = get_progress_stats(user["id"])

    if not rows:
        st.info("No exercises completed yet! Head over to **Play Learning Games** to start tracking progress.")
    else:
        import pandas as pd
        df = pd.DataFrame(rows, columns=["Subject", "Mode", "Level", "Correct", "Timestamp"])

        m1, m2, m3, m4 = st.columns(4, gap="medium")
        metrics = [
            ("⭐ Total Stars", str(user["stars"])),
            ("📝 Exercises Played", str(len(df))),
            ("🎯 Overall Accuracy", f"{df['Correct'].mean() * 100:.0f}%"),
            ("🏆 Stickers Earned", f"{len(user['stickers'])} / {len(STICKER_POOL) + 1}")
        ]
        for col, (lbl, val) in zip([m1, m2, m3, m4], metrics):
            with col:
                st.markdown(f"""
                <div class="hud-card">
                    <div class="hud-label">{lbl}</div>
                    <div class="hud-value" style="font-size:1.6rem;">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.write("")
        c_left, c_right = st.columns(2, gap="large")
        with c_left:
            st.markdown("### 📚 Mastery by Learning World")
            subj_summary = df.groupby("Subject").agg(
                Questions=("Correct", "count"),
                Correct_Answers=("Correct", "sum")
            ).reset_index()
            subj_summary["Accuracy (%)"] = (subj_summary["Correct_Answers"] / subj_summary["Questions"] * 100).round(1)
            st.dataframe(subj_summary, use_container_width=True, hide_index=True)

        with c_right:
            st.markdown("### 📈 Progress by Age / Skill Level")
            lvl_summary = df.groupby("Level").agg(
                Attempts=("Correct", "count"),
                Accuracy_Pct=("Correct", lambda s: round(s.mean() * 100, 1))
            ).reset_index()
            lvl_summary["Level Name"] = lvl_summary["Level"].map(LEVEL_NAMES)
            st.bar_chart(lvl_summary.set_index("Level Name")["Accuracy_Pct"])

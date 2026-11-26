"""
WonderKids Academy — Mission Control Edition
Streamlit app · Neon Postgres (SQLite fallback) · browser voice + synth SFX
"""
import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import psycopg2
import hashlib
import hmac
import random
import json
import os
import re
import time
from html import escape
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & MISSION-CONTROL THEME
# ==========================================
st.set_page_config(
    page_title="WonderKids Academy · Mission Control",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

MISSION_LENGTH = 5      # questions per mission
WARP_WINDOW_SEC = 10    # answer inside this window in Warp Speed for a bonus star

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Exo+2:wght@500;600;700&display=swap');

:root{
  --bg:#050816; --panel:rgba(11,19,43,.80); --panel-solid:#0B132B;
  --line:rgba(34,211,238,.38); --line-soft:rgba(148,169,204,.22);
  --cyan:#22D3EE; --violet:#8B5CF6; --amber:#FBBF24; --mint:#34D399; --rose:#FB7185;
  --text:#E6F0FF; --muted:#9FB3D6;
}

.stApp{
  font-family:'Exo 2',sans-serif;
  color:var(--text);
  background:
    radial-gradient(circle at 12% 8%, rgba(139,92,246,.28), transparent 38%),
    radial-gradient(circle at 88% 92%, rgba(34,211,238,.20), transparent 42%),
    linear-gradient(rgba(34,211,238,.045) 1px, transparent 1px) 0 0/44px 44px,
    linear-gradient(90deg, rgba(34,211,238,.045) 1px, transparent 1px) 0 0/44px 44px,
    var(--bg);
  background-attachment:fixed;
}
.stApp::before{            /* twinkling star layer */
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    radial-gradient(1.5px 1.5px at 8% 22%, #fff, transparent),
    radial-gradient(1px 1px at 22% 68%, #cfe9ff, transparent),
    radial-gradient(1.5px 1.5px at 37% 12%, #fff, transparent),
    radial-gradient(1px 1px at 51% 82%, #fff, transparent),
    radial-gradient(1.5px 1.5px at 66% 35%, #bde9ff, transparent),
    radial-gradient(1px 1px at 79% 58%, #fff, transparent),
    radial-gradient(1.5px 1.5px at 92% 18%, #fff, transparent),
    radial-gradient(1px 1px at 14% 90%, #fff, transparent),
    radial-gradient(1px 1px at 59% 6%, #cfe9ff, transparent);
  animation:twinkle 6s ease-in-out infinite alternate;
}
@keyframes twinkle{from{opacity:.55}to{opacity:1}}

footer{visibility:hidden}
.stApp p, .stApp label, .stApp li, .stMarkdown{color:var(--text)}
h1,h2,h3{font-family:'Orbitron',sans-serif !important; color:var(--text) !important; letter-spacing:.5px}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#070D22,#0A1230) !important;
  border-right:1px solid var(--line) !important;
}
section[data-testid="stSidebar"] *{color:var(--text)}

/* ---------- Inputs ---------- */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div{
  background:#0A1430 !important; border:1px solid var(--line) !important;
  border-radius:12px !important; color:var(--text) !important;
}
input{color:var(--text) !important; font-weight:600 !important}
div[data-baseweb="popover"] ul{background:#0A1430 !important}
div[data-baseweb="popover"] li{color:var(--text) !important}
div[data-baseweb="popover"] li:hover{background:rgba(34,211,238,.18) !important}

/* ---------- Buttons (answer keys & tools) ---------- */
div.stButton > button{
  width:100% !important; min-height:72px !important; padding:.8rem 1.1rem !important;
  font-family:'Exo 2',sans-serif !important; font-size:1.3rem !important; font-weight:700 !important;
  color:var(--text) !important;
  background:linear-gradient(180deg, rgba(34,211,238,.14), rgba(11,19,43,.9)) !important;
  border:1px solid var(--line) !important; border-radius:16px !important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.04), 0 0 0 rgba(34,211,238,0) !important;
  transition:transform .12s ease, box-shadow .15s ease, border-color .15s ease !important;
}
div.stButton > button:hover{
  transform:translateY(-2px) !important; border-color:var(--cyan) !important;
  box-shadow:0 0 22px rgba(34,211,238,.45), inset 0 0 14px rgba(34,211,238,.18) !important;
  color:#fff !important;
}
div.stButton > button:active{transform:translateY(1px) scale(.99) !important}
div.stButton > button:focus-visible{outline:3px solid var(--amber) !important; outline-offset:3px}
div.stButton > button:disabled{
  opacity:.55; border-color:var(--line-soft) !important; box-shadow:none !important;
  color:var(--muted) !important; background:rgba(11,19,43,.7) !important;
}
div[data-testid="stFormSubmitButton"] > button{
  min-height:60px !important; font-size:1.2rem !important; font-weight:800 !important; width:100% !important;
  color:#04121c !important; border:0 !important; border-radius:14px !important;
  background:linear-gradient(90deg,var(--cyan),#7DD3FC) !important;
  box-shadow:0 0 24px rgba(34,211,238,.45) !important;
}
div[data-testid="stFormSubmitButton"] > button:hover{filter:brightness(1.1); color:#04121c !important}

/* ---------- Panels with HUD corner brackets ---------- */
.panel{
  position:relative; background:var(--panel); border:1px solid var(--line-soft);
  border-radius:14px; padding:20px 24px; backdrop-filter:blur(6px);
  box-shadow:0 12px 40px rgba(0,0,0,.35);
}
.panel::before,.panel::after{
  content:""; position:absolute; width:22px; height:22px; pointer-events:none;
  border:2px solid var(--cyan); opacity:.9;
}
.panel::before{top:-1px; left:-1px; border-right:0; border-bottom:0; border-top-left-radius:14px}
.panel::after{bottom:-1px; right:-1px; border-left:0; border-top:0; border-bottom-right-radius:14px}
.panel h3{margin:0 0 4px 0; font-size:1.15rem}

/* ---------- Hero + boot log ---------- */
.hero{display:flex; flex-wrap:wrap; gap:28px; align-items:center; justify-content:space-between; margin-bottom:18px}
.hero-main{flex:1 1 380px}
.hero-title{font-family:'Orbitron',sans-serif; font-weight:800; font-size:clamp(2rem,5vw,3.4rem); line-height:1.1;
  color:#fff; text-shadow:0 0 28px rgba(34,211,238,.55)}
.hero-sub{font-size:1.2rem; color:var(--muted); margin:10px 0 16px 0}
.chip{display:inline-block; padding:5px 14px; margin:3px 6px 3px 0; border-radius:999px;
  border:1px solid var(--line); background:rgba(34,211,238,.08); font-weight:700; font-size:.95rem}
.boot{flex:1 1 320px; font-family:'Exo 2',monospace; font-size:.98rem; color:var(--mint);
  background:rgba(2,8,23,.7); border:1px solid var(--line-soft); border-radius:12px; padding:14px 16px}
.boot-line{opacity:0; animation:bootIn .01s forwards; animation-delay:var(--d)}
.boot-line b{color:var(--amber)}
@keyframes bootIn{to{opacity:1}}

/* ---------- Crew card (sidebar) ---------- */
.crew{text-align:center; padding:16px 12px; border:1px solid var(--line); border-radius:16px;
  background:rgba(34,211,238,.06); margin-bottom:14px}
.orbit{position:relative; width:92px; height:92px; margin:0 auto 8px auto; display:flex; align-items:center; justify-content:center;
  font-size:2.8rem; border-radius:50%; border:2px dashed var(--cyan); animation:spin 18s linear infinite}
.orbit > span{animation:spin 18s linear infinite reverse; display:block}
@keyframes spin{to{transform:rotate(360deg)}}
.crew-name{font-family:'Orbitron',sans-serif; font-size:1.05rem; margin:2px 0}
.rank{color:var(--amber); font-weight:700}
.bar{height:10px; border-radius:99px; background:rgba(148,169,204,.2); overflow:hidden; margin-top:8px}
.bar > div{height:100%; border-radius:99px; background:linear-gradient(90deg,var(--cyan),var(--violet))}
.tiny{font-size:.85rem; color:var(--muted); margin-top:4px}

/* ---------- HUD cards ---------- */
.hud{border:1px solid var(--line-soft); border-radius:14px; padding:12px 14px; background:var(--panel); height:100%}
.hud-label{font-size:.85rem; color:var(--muted); font-weight:600}
.hud-value{font-family:'Orbitron',sans-serif; font-size:1.05rem; margin-top:4px; color:#fff}

/* ---------- Mission route ---------- */
.route{display:flex; align-items:center; margin:14px 4px 4px 4px}
.route .link{flex:1; height:2px; background:linear-gradient(90deg,var(--line),var(--line-soft))}
.node{width:44px; height:44px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:1.25rem; border:2px solid var(--line-soft); background:var(--panel-solid); flex:0 0 auto}
.node.ok{border-color:var(--mint); box-shadow:0 0 16px rgba(52,211,153,.55); color:var(--mint)}
.node.bad{border-color:var(--rose); box-shadow:0 0 14px rgba(251,113,133,.45); color:var(--rose)}
.node.now{border-color:var(--cyan); box-shadow:0 0 20px rgba(34,211,238,.7); animation:pulse 1.8s ease-in-out infinite}
@keyframes pulse{50%{transform:scale(1.1)}}
.route-cap{font-size:.9rem; color:var(--muted); margin:2px 4px 10px 4px}

/* ---------- Question stage ---------- */
.stage{text-align:center; margin:12px 0 18px 0; border-color:var(--line)}
.nova{display:inline-flex; align-items:center; gap:12px; padding:6px 18px; border-radius:999px;
  border:1px solid var(--amber); background:rgba(251,191,36,.10); margin-bottom:6px}
.nova-av{font-size:2rem}
.nova-say{font-weight:700; color:var(--amber); overflow:hidden; white-space:nowrap; max-width:0;
  border-right:2px solid var(--amber); animation:typing 1.8s steps(40) .2s forwards}
@keyframes typing{to{max-width:48ch; border-right-color:transparent}}
.holo{position:relative; overflow:hidden; margin:12px auto; padding:22px 16px;
  font-size:clamp(2rem,5vw,3.6rem); letter-spacing:8px; line-height:1.35; word-break:break-word;
  border:1px solid var(--line); border-radius:18px;
  background:linear-gradient(180deg,rgba(34,211,238,.12),rgba(139,92,246,.10));
  text-shadow:0 0 18px rgba(34,211,238,.55)}
.holo::after{content:""; position:absolute; inset:0; pointer-events:none;
  background:repeating-linear-gradient(0deg, rgba(255,255,255,.045) 0 1px, transparent 1px 4px)}
.holo::before{content:""; position:absolute; left:0; right:0; top:-35%; height:35%; pointer-events:none;
  background:linear-gradient(180deg,transparent,rgba(34,211,238,.25),transparent); animation:sweep 5s linear infinite}
@keyframes sweep{to{top:110%}}
.q{font-size:clamp(1.3rem,3vw,1.9rem); font-weight:700; line-height:1.35; color:#fff; margin-top:6px}

/* ---------- Result / debrief ---------- */
.result{border-radius:14px; padding:16px 20px; margin-top:10px; font-size:1.2rem; font-weight:700}
.result.ok{border:1px solid var(--mint); background:rgba(52,211,153,.12); box-shadow:0 0 24px rgba(52,211,153,.25)}
.result.bad{border:1px solid var(--amber); background:rgba(251,191,36,.10)}
.result small{display:block; font-weight:600; color:var(--muted); margin-top:4px; font-size:.95rem}
.fact{margin-top:12px; padding:16px 20px; border-radius:14px; border:1px solid var(--line);
  border-left:8px solid var(--cyan); background:rgba(34,211,238,.08); font-size:1.15rem}
.debrief{text-align:center; margin-top:16px}
.debrief .big{font-family:'Orbitron',sans-serif; font-size:2rem; color:var(--amber); text-shadow:0 0 20px rgba(251,191,36,.5)}
.rankup{margin-top:10px; padding:14px; text-align:center; border-radius:14px; border:1px solid var(--violet);
  background:rgba(139,92,246,.18); font-family:'Orbitron',sans-serif; font-size:1.1rem}

/* ---------- Vault ---------- */
.artifact{border-radius:16px; padding:16px 8px; text-align:center; margin-bottom:14px; border:1px solid var(--line-soft); background:var(--panel)}
.artifact.on{border-color:var(--amber); box-shadow:0 0 20px rgba(251,191,36,.35)}
.artifact .em{font-size:3rem}
.artifact.off .em{filter:grayscale(1) brightness(.35)}
.artifact .st{font-size:.9rem; font-weight:700; margin-top:4px; color:var(--muted)}
.artifact.on .st{color:var(--amber)}

@media (prefers-reduced-motion: reduce){
  .stApp::before,.orbit,.orbit>span,.node.now,.holo::before{animation:none !important}
  .nova-say{animation:none !important; max-width:none; border-right:0}
  .boot-line{animation:none !important; opacity:1}
}
@media (max-width:640px){ div.stButton > button{font-size:1.1rem !important; min-height:64px !important} }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def ui(markup: str):
    """Render HTML safely through markdown (no blank lines / indentation = no code-block surprises)."""
    cleaned = "\n".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


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
            if not st.session_state.get("_db_warned"):
                st.session_state["_db_warned"] = True
                st.warning(f"⚠️ Cloud database unreachable ({type(e).__name__}). Running on local storage.")

    return sqlite3.connect("wonderkids.db"), "sqlite"


@st.cache_resource(show_spinner=False)
def init_db():
    conn, db_type = get_db_connection()
    c = conn.cursor()
    pk = "SERIAL PRIMARY KEY" if db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {pk},
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
    ref = " REFERENCES users(id)" if db_type == "postgres" else ""
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS progress_log (
            id {pk},
            user_id INTEGER NOT NULL{ref},
            subject TEXT NOT NULL,
            mode TEXT NOT NULL,
            level INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    return True


# --- Passwords: salted PBKDF2. Legacy unsalted SHA-256 hashes still work and are upgraded on next login.
def hash_pw(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"pbkdf2${salt.hex()}${dk.hex()}"


def verify_pw(password: str, stored: str) -> bool:
    if stored.startswith("pbkdf2$"):
        try:
            _, salt_hex, dk_hex = stored.split("$")
            dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)
            return hmac.compare_digest(dk.hex(), dk_hex)
        except Exception:
            return False
    legacy = hashlib.sha256(password.encode()).hexdigest()
    return hmac.compare_digest(legacy, stored)


USER_COLS = "id, username, child_name, age_group, avatar, stars, streak, stickers"


def _row_to_user(row):
    return {
        "id": row[0], "username": row[1], "child_name": row[2],
        "age_group": row[3], "avatar": row[4], "stars": row[5],
        "streak": row[6], "stickers": json.loads(row[7]),
    }


def create_user(username, password, child_name, age_group, avatar):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    try:
        c.execute(
            f"""INSERT INTO users (username, password_hash, child_name, age_group, avatar, stars, streak, stickers, created_at)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, 0, 0, {ph}, {ph})""",
            (username.lower().strip(), hash_pw(password), child_name.strip(), age_group, avatar,
             json.dumps(["🌟"]), datetime.now().isoformat()),
        )
        conn.commit()
        return True, "Account created."
    except Exception:
        conn.rollback()
        return False, "That username is taken. Pick a different explorer name."
    finally:
        conn.close()


def authenticate_user(username, password):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    c.execute(f"SELECT {USER_COLS}, password_hash FROM users WHERE username={ph}", (username.lower().strip(),))
    row = c.fetchone()
    user = None
    if row and verify_pw(password, row[8]):
        user = _row_to_user(row[:8])
        if not row[8].startswith("pbkdf2$"):      # silent upgrade of legacy hash
            c.execute(f"UPDATE users SET password_hash={ph} WHERE id={ph}", (hash_pw(password), user["id"]))
            conn.commit()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    c.execute(f"SELECT {USER_COLS} FROM users WHERE id={ph}", (user_id,))
    row = c.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


STICKER_POOL = ["🦄", "🦖", "🚀", "🌈", "🐬", "🐼", "🦋", "🍓", "🎨", "🏆", "🐢", "🦊", "🐘", "🪐", "🐙", "🦁", "🍦", "🚂", "🦕"]


def record_attempt(user_id, subject, mode, level, is_correct, fast=False, clean=False):
    """Logs the attempt, updates stars/streak/stickers. Returns dict(sticker, gained, notes)."""
    conn, db_type = get_db_connection()
    ph = "%s" if db_type == "postgres" else "?"
    c = conn.cursor()
    c.execute(
        f"INSERT INTO progress_log (user_id, subject, mode, level, is_correct, timestamp) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
        (user_id, subject, mode, level, 1 if is_correct else 0, datetime.now().isoformat()),
    )
    c.execute(f"SELECT stars, streak, stickers FROM users WHERE id={ph}", (user_id,))
    stars, streak, stickers_json = c.fetchone()
    stickers = json.loads(stickers_json)

    gained, notes, new_sticker = 0, [], None
    if is_correct:
        streak += 1
        gained = 1
        if clean and fast:
            gained += 1
            notes.append("⚡ Warp bonus +1")
        if clean and streak % 5 == 0:
            gained += 1
            notes.append(f"🔥 {streak}-in-a-row bonus +1")
        before = stars
        stars += gained
        if stars // 3 > before // 3:
            available = [s for s in STICKER_POOL if s not in stickers]
            if available:
                new_sticker = random.choice(available)
                stickers.append(new_sticker)
    else:
        streak = 0

    c.execute(
        f"UPDATE users SET stars={ph}, streak={ph}, stickers={ph} WHERE id={ph}",
        (stars, streak, json.dumps(stickers), user_id),
    )
    conn.commit()
    conn.close()
    return {"sticker": new_sticker, "gained": gained, "notes": notes}


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
# 3. RANKS & DISPLAY NAMES
# ==========================================
RANKS = [(0, "Cadet", "🛰️"), (10, "Pilot", "🧑‍🚀"), (25, "Navigator", "🧭"),
         (50, "Captain", "🎖️"), (100, "Commander", "🛡️"), (200, "Admiral", "👑")]


def rank_info(stars: int):
    idx = max(i for i, (t, _, _) in enumerate(RANKS) if stars >= t)
    cur = RANKS[idx]
    nxt = RANKS[idx + 1] if idx + 1 < len(RANKS) else None
    pct = 100 if not nxt else int((stars - cur[0]) / (nxt[0] - cur[0]) * 100)
    return {"idx": idx, "name": cur[1], "icon": cur[2], "next": nxt, "pct": pct,
            "to_go": (nxt[0] - stars) if nxt else 0}


# Keys stay identical to the old app so existing progress data keeps working; only the labels changed.
SECTOR_NAMES = {
    "🔢 Math Kingdom": "🔢 Number Nebula",
    "🔤 Alphabet Jungle": "🔤 Letter Galaxy",
    "🔬 Discovery Lab": "🔬 Science Station",
    "🎨 Shape & Color Island": "🎨 Shape & Color Moon",
}
MODES = {
    "🎈 Adventure Mode": ("🎈 Explorer Mission", "Relaxed learning with fun facts."),
    "⚡ Lightning Pop": ("⚡ Warp Speed", f"Answer within {WARP_WINDOW_SEC}s for a bonus star."),
    "🧩 Brainy Pattern & Logic": ("🧩 Logic Core", "Patterns, rhymes and brain teasers."),
}
LEVEL_NAMES = {
    1: "🌱 Level 1 · Rookie Orbit (Age 3)",
    2: "🐥 Level 2 · Star Scout (Age 4)",
    3: "🦊 Level 3 · Deep Space Pilot (Age 5)",
    4: "🚀 Level 4 · Galaxy Captain (Age 6)",
}

# ==========================================
# 4. VOICE + SYNTH SFX ENGINE (respects the Sound toggle)
# ==========================================
SPEAK_JS = """
<script>
(function(){
  const msg = __MSG__;
  const sfx = __SFX__;
  try {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) {
      const ctx = new AC();
      const tone = (f, s, d, w='sine', v=0.2) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = w; o.frequency.setValueAtTime(f, ctx.currentTime + s);
        g.gain.setValueAtTime(v, ctx.currentTime + s);
        g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + s + d);
        o.connect(g); g.connect(ctx.destination);
        o.start(ctx.currentTime + s); o.stop(ctx.currentTime + s + d);
      };
      const sweep = (f1, f2, s, d) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = 'sawtooth'; o.frequency.setValueAtTime(f1, ctx.currentTime + s);
        o.frequency.exponentialRampToValueAtTime(f2, ctx.currentTime + s + d);
        g.gain.setValueAtTime(0.07, ctx.currentTime + s);
        g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + s + d);
        o.connect(g); g.connect(ctx.destination);
        o.start(ctx.currentTime + s); o.stop(ctx.currentTime + s + d);
      };
      if (sfx === 'win')   { [587.33, 739.99, 880, 1174.66].forEach((f,i)=>tone(f, i*0.1, i===3?0.35:0.12)); }
      if (sfx === 'oops')  { tone(392, 0, 0.16, 'triangle'); tone(349.23, 0.16, 0.24, 'triangle'); }
      if (sfx === 'pop')   { tone(880, 0, 0.08); tone(1046.5, 0.07, 0.10); }
      if (sfx === 'scan')  { sweep(300, 1500, 0, 0.55); tone(1500, 0.55, 0.12, 'sine', 0.15); }
      if (sfx === 'boot')  { [262,330,392,523,659].forEach((f,i)=>tone(f, i*0.09, 0.14, 'square', 0.07)); }
      if (sfx === 'level') { [523,659,784,1047,1319,1568].forEach((f,i)=>tone(f, i*0.1, 0.22, 'triangle', 0.2)); }
    }
  } catch(e) {}
  if (msg && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(msg);
    const voices = window.speechSynthesis.getVoices();
    const v = voices.find(x => /Google UK English Female|Google US English|Samantha|Victoria|Zira|Tessa|Karen/i.test(x.name));
    if (v) u.voice = v;
    u.pitch = 1.5; u.rate = 1.08; u.volume = 1.0;
    window.speechSynthesis.speak(u);
  }
})();
</script>
<div style="display:none">__TID__</div>
"""


def speak(text: str, sfx: str = "none", trigger_id: str = "0"):
    if not st.session_state.get("sound_on", True):
        return
    js = (SPEAK_JS.replace("__MSG__", json.dumps(text))
                  .replace("__SFX__", json.dumps(sfx))
                  .replace("__TID__", escape(str(trigger_id))))
    components.html(js, height=0)


# ==========================================
# 5. INTERACTIVE OBJECT SCANNER (tap-to-count, pitch rises with each tap)
# ==========================================
SCANNER_HTML = """
<!-- __QID__ -->
<div style="text-align:center;font-family:'Exo 2',sans-serif;color:#E6F0FF;padding:4px">
  <div style="font-size:1.05rem;font-weight:700;color:#9FB3D6;margin-bottom:10px">📡 Tap each object to scan it</div>
  <div id="box" style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px"></div>
  <div id="out" style="margin-top:10px;font-size:1.35rem;font-weight:700;color:#FBBF24;min-height:30px"></div>
</div>
<script>
  const items = __ITEMS__;
  const sound = __SOUND__;
  const box = document.getElementById('box'), out = document.getElementById('out');
  let n = 0, ctx = null;
  const beep = (f) => {
    try {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.2, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.18);
      o.connect(g); g.connect(ctx.destination); o.start(); o.stop(ctx.currentTime + 0.2);
    } catch(e) {}
  };
  items.forEach((it) => {
    const b = document.createElement('button');
    b.textContent = it;
    b.style.cssText = "font-size:2.6rem;padding:8px 16px;border-radius:16px;cursor:pointer;color:#fff;" +
      "background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.45);transition:all .15s";
    b.onmouseenter = () => { if (!b.dataset.t) b.style.boxShadow = "0 0 18px rgba(34,211,238,.5)"; };
    b.onmouseleave = () => { if (!b.dataset.t) b.style.boxShadow = "none"; };
    b.onclick = () => {
      if (b.dataset.t) return;
      b.dataset.t = "1"; n++;
      b.style.background = "rgba(52,211,153,.2)";
      b.style.borderColor = "#34D399";
      b.style.boxShadow = "0 0 20px rgba(52,211,153,.6)";
      b.style.transform = "scale(1.12)";
      out.textContent = "🛰️ Objects scanned: " + n;
      if (sound) {
        beep(440 * Math.pow(2, n / 6));
        if ('speechSynthesis' in window) {
          window.speechSynthesis.cancel();
          const u = new SpeechSynthesisUtterance(String(n));
          u.pitch = 1.6; u.rate = 1.15; window.speechSynthesis.speak(u);
        }
      }
    };
    box.appendChild(b);
  });
</script>
"""


def render_scanner(items, qid):
    html_widget = (SCANNER_HTML.replace("__ITEMS__", json.dumps(items))
                               .replace("__SOUND__", "true" if st.session_state.get("sound_on", True) else "false")
                               .replace("__QID__", str(qid)))
    components.html(html_widget, height=210)


TIMER_HTML = """
<!-- __QID__ -->
<div style="font-family:'Exo 2',sans-serif;color:#E6F0FF">
  <div id="lab" style="font-weight:700;margin-bottom:6px">⚡ Warp bonus window: <span id="t" style="color:#FBBF24">__SEC__</span>s</div>
  <div style="height:12px;border-radius:99px;background:rgba(148,169,204,.2);overflow:hidden">
    <div id="b" style="height:100%;width:100%;background:linear-gradient(90deg,#22D3EE,#FBBF24);transition:width __SEC__s linear"></div>
  </div>
</div>
<script>
  let t = __SEC__;
  const lab = document.getElementById('lab'), el = document.getElementById('t'), bar = document.getElementById('b');
  requestAnimationFrame(() => requestAnimationFrame(() => { bar.style.width = '0%'; }));
  const iv = setInterval(() => {
    t--; el.textContent = t;
    if (t <= 0) { clearInterval(iv); lab.textContent = '⏱ Bonus window closed — you can still earn a star!'; }
  }, 1000);
</script>
"""


def render_warp_timer(qid):
    components.html(TIMER_HTML.replace("__SEC__", str(WARP_WINDOW_SEC)).replace("__QID__", str(qid)), height=58)


# ==========================================
# 6. EXERCISE BANK (always 4 options; answer is guaranteed to be among them)
# ==========================================
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
                 "Astronauts count backward to zero before launching rockets into space!", []),
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
                "answer": str(n), "options": opts,
                "fact": f"Super counting! {n} is one of our magic counting numbers!",
                "voice": f"Yay! Tap each picture to count! How many {emoji} do you see?",
                "toys": [emoji] * n,
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
                    "question": f"Big counting challenge! How many {emoji} can you find?",
                    "answer": str(n), "options": opts,
                    "fact": f"Awesome! Counting all the way to {n} makes your math brain super strong!",
                    "voice": f"Whoa, look at all those {emoji}! Can you count how many there are?",
                    "toys": [emoji] * n,
                }
            else:
                a, b = random.sample(range(2, 9), 2)
                ans = f"Basket A ({a})" if a > b else f"Basket B ({b})"
                opts = [f"Basket A ({a})", f"Basket B ({b})", "Both Equal!", "Zero Fruit"]
                random.shuffle(opts)
                return {
                    "visual": f"Basket A: {'🍓'*a}   🆚   Basket B: {'🍊'*b}",
                    "question": "Which basket has MORE yummy fruit?",
                    "answer": ans, "options": opts,
                    "fact": "Comparing groups helps us tell which pile is bigger or smaller!",
                    "voice": "Yum! Look at the two fruit baskets! Which basket has more fruit?",
                    "toys": [],
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
                "answer": str(ans), "options": opts,
                "fact": f"{a} + {b} = {ans}! Putting two groups together is called ADDITION!",
                "voice": f"Roar! {a} friendly dinosaurs meet {b} more dinosaurs! How many dinosaurs altogether?",
                "toys": ["🦖"] * (a + b),
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
                    "answer": str(ans), "options": opts,
                    "fact": f"{a} take away {b} equals {ans}! That's subtraction in action!",
                    "voice": f"Pop pop! You had {a} party balloons and {b} floated away! How many are left?",
                    "toys": [],
                }
            elif q_type == "time":
                clocks = [
                    ("🕒", "3:00 (3 O'Clock)", ["3:00 (3 O'Clock)", "6:00 (6 O'Clock)", "12:00 (12 O'Clock)", "9:00 (9 O'Clock)"]),
                    ("🕕", "6:00 (6 O'Clock)", ["6:00 (6 O'Clock)", "3:00 (3 O'Clock)", "1:00 (1 O'Clock)", "10:00 (10 O'Clock)"]),
                    ("🕘", "9:00 (9 O'Clock)", ["9:00 (9 O'Clock)", "3:00 (3 O'Clock)", "6:00 (6 O'Clock)", "12:00 (12 O'Clock)"]),
                ]
                clk, ans, opts = random.choice(clocks)
                random.shuffle(opts)
                return {
                    "visual": f"⏰  {clk}  ⏰",
                    "question": "Look at the clock hands! What time is it?",
                    "answer": ans, "options": opts,
                    "fact": "The short hand points to the hour, and when the long hand points straight up to 12, it's O'Clock!",
                    "voice": "Tick tock! Look at the clock! What time does it show?",
                    "toys": [],
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
                    "answer": str(missing), "options": opts,
                    "fact": f"{part} + {missing} = {total}! You solved an algebra mystery like a real mathematician!",
                    "voice": f"Detective math! {part} plus what secret number equals {total}?",
                    "toys": [],
                }

    elif subject == "🔤 Alphabet Jungle":
        if mode == "🧩 Brainy Pattern & Logic":
            riddles = [
                ("🐱  🎩  🦇", "Which word RHYMES with CAT?", "🎩 HAT", ["🎩 HAT", "🐶 DOG", "☀️ SUN", "🐟 FISH"],
                 "Rhyming words end with the exact same sound—just like songs and poems!"),
                ("A ➔ B ➔ C ➔ ❓", "Sing the ABC song! Which letter marches next?", "🇩 D", ["🇩 D", "🇫 F", "🇿 Z", "🇲 M"],
                 "There are 26 letters in the English alphabet, and every book is written with them!"),
                ("🐸  🪵  🐶", "Which word RHYMES with FROG?", "🪵 LOG", ["🪵 LOG", "🚗 CAR", "🍎 APPLE", "🌙 MOON"],
                 "Frog and log both end with the 'OG' sound!"),
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
                 "Frogs drink water right through their skin—no cup needed!"),
            ],
            2: [
                ("🐘", "Stomp stomp! Which animal starts with the 'Eh' sound (Letter E)?", "🐘 Elephant", ["🐘 Elephant", "🐯 Tiger", "🐵 Monkey", "🐻 Bear"],
                 "Elephants use their long trunks like a nose, a hand, and even a snorkel!"),
                ("🚀", "Zoom! Which picture starts with the 'Rrr' sound (Letter R)?", "🚀 Rocket", ["🚀 Rocket", "⛵ Boat", "🚲 Bike", "🚂 Train"],
                 "Rockets travel faster than 17,000 miles per hour to reach space!"),
                ("🐢", "Which slow-and-steady friend starts with the letter T?", "🐢 Turtle", ["🐢 Turtle", "🦆 Duck", "🐷 Pig", "🐝 Bee"],
                 "Turtles carry their cozy shell homes right on their backs!"),
            ],
            3: [
                ("☀️  _ U N", "Spell the bright yellow star in the sky! Missing letter?", "S (SUN)", ["S (SUN)", "B (BUN)", "R (RUN)", "F (FUN)"],
                 "The Sun is actually a giant, glowing star that keeps Earth warm!"),
                ("🐱  _ A T", "Meow! Which letter completes the word _ A T?", "C (CAT)", ["C (CAT)", "D (DAT)", "P (PAT)", "M (MAT)"],
                 "Cats use their whiskers to measure if they can squeeze through tight spaces!"),
                ("🐷  P _ G", "Oink oink! Which vowel goes in the middle of P _ G?", "I (PIG)", ["I (PIG)", "A (PAG)", "O (POG)", "E (PEG)"],
                 "A, E, I, O, U are the 5 superstar vowels—almost every word needs one!"),
            ],
            4: [
                ("🦈  🚢  🐑", "Which sound do SHARK, SHIP, and SHEEP all start with?", "SH", ["SH", "CH", "TH", "ST"],
                 "When S and H team up together, they make the quiet 'SHHH' sound!"),
                ("🦋  🐜", "Which word is the OPPOSITE of 'BIG'?", "🐜 TINY", ["🐜 TINY", "🐘 HUGE", "🦒 TALL", "🐳 GIANT"],
                 "Opposites are word pairs that mean totally different things—like hot & cold, or big & tiny!"),
                ("🍎 ➔ 🍎🍎🍎", "One apple, many ______! How do we spell more than one apple?", "Apples", ["Apples", "Apple", "Appling", "Appled"],
                 "Adding the letter 'S' to the end of most words turns ONE into MANY!"),
                ("📚", "Which word is an ACTION word (verb)?", "🏃 JUMP", ["🏃 JUMP", "🪑 CHAIR", "🔵 BLUE", "🍎 APPLE"],
                 "Action words tell us what someone or something is doing!"),
            ],
        }
        vis, q, ans, opts, fact = random.choice(bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Welcome to Letter Galaxy! {q}", "toys": []}

    elif subject == "🔬 Discovery Lab":
        science_bank = {
            1: [
                ("🐄  🥛", "Moo! Which friendly farm animal gives us milk?", "🐄 Cow", ["🐄 Cow", "🐔 Chicken", "🐷 Pig", "🦆 Duck"],
                 "Cows have four stomach compartments to help them digest yummy grass!"),
                ("🌧️  ☀️", "When sunshine shines through raindrops, what appears in the sky?", "🌈 Rainbow", ["🌈 Rainbow", "⛄ Snowman", "🌙 Moon", "🪨 Rock"],
                 "Sunlight is made of 7 rainbow colors hiding together inside white light!"),
                ("👃  🌸", "Which part of your body do you use to smell a yummy flower?", "👃 Nose", ["👃 Nose", "👂 Ear", "👀 Eyes", "🦶 Foot"],
                 "Your nose can recognize thousands of different smells—like cookies baking!"),
            ],
            2: [
                ("🐛  ➔  💤  ➔  ❓", "A hungry caterpillar sleeps in a chrysalis and wakes up as a...", "🦋 Butterfly", ["🦋 Butterfly", "🐸 Frog", "🐟 Fish", "🐦 Bird"],
                 "Butterflies taste flowers using tiny sensors on their FEET!"),
                ("🌱  ☀️  💧", "What does a tiny seed need to grow into a tall flower?", "☀️ Sun & Water", ["☀️ Sun & Water", "🍕 Pizza", "🧸 Teddy Bear", "❄️ Ice Cubes"],
                 "Plants drink water through their roots like straws and make food from sunshine!"),
            ],
            3: [
                ("🪐  🌍  ☀️", "Which planet do WE live on?", "🌍 Earth", ["🌍 Earth", "🪐 Saturn", "🔴 Mars", "☀️ The Sun"],
                 "Earth is the only known planet with liquid oceans and living creatures!"),
                ("🧲  📎", "Which object will stick to a super magnet?", "📎 Metal Paperclip", ["📎 Metal Paperclip", "🍌 Banana", "🧸 Plush Toy", "🖍️ Crayon"],
                 "Magnets have invisible force fields that pull on iron and steel!"),
                ("🐧  ❄️", "Where does a fluffy penguin live?", "❄️ Icy Antarctica", ["❄️ Icy Antarctica", "🌵 Hot Desert", "🌴 Tropical Jungle", "🌋 Volcano"],
                 "Penguins have thick waterproof feathers that keep them cozy in freezing water!"),
            ],
            4: [
                ("🧊  🔥  💧", "When warm sunshine heats up an ice cube, it melts into...", "💧 Liquid Water", ["💧 Liquid Water", "🪨 Solid Rock", "🪵 Wood", "🏖️ Sand"],
                 "Water is a shape-shifter! It can be solid ice, liquid water, or invisible steam!"),
                ("🦉  🦇  🌙", "Animals that sleep all day and wake up at night are called...", "🦉 Nocturnal", ["🦉 Nocturnal", "🐠 Aquatic", "🦖 Extinct", "🐧 Arctic"],
                 "Owls have giant eyes that capture tiny bits of moonlight so they can see in the dark!"),
                ("🫀  💓", "Which muscle inside your chest pumps blood all around your body?", "❤️ Your Heart", ["❤️ Your Heart", "🧠 Your Brain", "🦴 Your Bones", "💪 Your Biceps"],
                 "Your heart is about the size of your fist and beats around 100,000 times every single day!"),
                ("🦕  🦴", "Animals like T-Rex that lived millions of years ago and are no longer alive are...", "🦖 Extinct", ["🦖 Extinct", "Hibernating", "Nocturnal", "Amphibians"],
                 "Scientists called paleontologists dig up dinosaur fossils to learn how they lived!"),
            ],
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
                 "Wheels are circles because round shapes roll smoothly without bumping!"),
            ],
            2: [
                ("🔴  ➕  🟡  =  ❓", "Mix RED paint and YELLOW paint together! What magic color do you get?", "🟠 Orange", ["🟠 Orange", "🟢 Green", "🟣 Purple", "🔵 Blue"],
                 "Red, Yellow, and Blue are Primary Colors—you can mix them to make a rainbow!"),
                ("🔵  ➕  🟡  =  ❓", "Swirl BLUE and YELLOW paint together! Which color appears?", "🟢 Green", ["🟢 Green", "🟠 Orange", "🟣 Purple", "🩷 Pink"],
                 "Leaves look green because of chlorophyll, which catches sunlight for trees!"),
                ("🔴  ➕  🔵  =  ❓", "Mix RED and BLUE paint! Which royal color pops out?", "🟣 Purple", ["🟣 Purple", "🟢 Green", "🟠 Orange", "🟡 Yellow"],
                 "Purple was once so rare that only kings and queens could wear purple clothes!"),
            ],
            3: [
                ("🐝  🍯", "What 6-sided shape do busy bees build inside their honeycomb?", "⬡ Hexagon", ["⬡ Hexagon", "⭕ Circle", "🔺 Triangle", "⬛ Square"],
                 "Hexagons fit together with zero wasted space—bees are tiny math geniuses!"),
                ("🛑", "How many sides does a red STOP sign (Octagon) have?", "8 Sides", ["8 Sides", "6 Sides", "4 Sides", "3 Sides"],
                 "Octo means EIGHT—just like an octopus with 8 arms and an octagon with 8 sides!"),
            ],
            4: [
                ("🎲  📦", "A 3D square box shape with 6 flat faces is called a...", "🧊 Cube", ["🧊 Cube", "⚽ Sphere", "🍦 Cone", "🥫 Cylinder"],
                 "2D shapes are flat like paper, while 3D shapes pop out so you can hold them!"),
                ("🍦  🎉", "A party hat and an ice cream waffle share which 3D shape?", "🔺 Cone", ["🔺 Cone", "🧊 Cube", "⚽ Sphere", "📦 Box"],
                 "Cones have a round circle on one end and a sharp point on the other!"),
                ("🍕  ✂️  🍕", "If you cut 1 whole pizza into 2 EQUAL slices, each slice is called...", "½ One Half", ["½ One Half", "¼ One Quarter", "2 Wholes", "Zero"],
                 "Halves must be the exact same size so everyone gets a fair share!"),
            ],
        }
        vis, q, ans, opts, fact = random.choice(shape_bank[level])
        random.shuffle(opts)
        return {"visual": vis, "question": q, "answer": ans, "options": opts, "fact": fact,
                "voice": f"Ahoy, explorer! {q}", "toys": []}


def finalize_question(q: dict) -> dict:
    """Guarantee: unique options, answer present, exactly 4 choices."""
    seen, opts = set(), []
    for o in q["options"]:
        if o not in seen:
            seen.add(o)
            opts.append(o)
    if q["answer"] not in opts:
        opts[random.randrange(len(opts))] = q["answer"]
    others = [o for o in opts if o != q["answer"]]
    random.shuffle(others)
    opts = (others[:3] + [q["answer"]])
    while len(opts) < 4:                       # pad (very rare) so the 2x2 grid never breaks
        opts.insert(0, f"✨ Mystery {len(opts)}")
    random.shuffle(opts)
    q["options"] = opts
    return q


def make_question(subject, level, mode, avoid_text=None):
    q = None
    for _ in range(6):                         # avoid showing the same question twice in a row
        q = finalize_question(generate_question(subject, level, mode))
        if q["question"] != avoid_text:
            break
    return q

# ==========================================
# 7. SESSION STATE
# ==========================================
DEFAULTS = {
    "user_id": None, "subject": "🔢 Math Kingdom", "mode": "🎈 Adventure Mode", "level": 1,
    "current_q": None, "q_id": 0, "q_start": 0.0, "answered": False, "last_result": None,
    "chosen": None, "eliminated": [], "hint_used": False, "mission_results": [],
    "result_info": None, "rank_up": None, "speech_payload": None, "sound_on": True,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def start_question(announce=True):
    s = st.session_state
    prev = (s.current_q or {}).get("question")
    s.current_q = make_question(s.subject, s.level, s.mode, prev)
    s.q_id = time.time_ns()
    s.q_start = time.time()
    s.answered, s.last_result, s.chosen = False, None, None
    s.eliminated, s.hint_used, s.result_info, s.rank_up = [], False, None, None
    if announce:
        s.speech_payload = (s.current_q["voice"], "pop", str(s.q_id))


def begin_session(user, greeting):
    s = st.session_state
    s.user_id = user["id"]
    s.level = max(1, min(4, user["age_group"] - 2))
    s.mission_results = []
    start_question(announce=False)
    s.speech_payload = (greeting, "boot", str(random.random()))


# ==========================================
# 8. CREW CHECK-IN (LOGIN / SIGN-UP)
# ==========================================
if st.session_state.user_id is None:
    ui("""
    <div class="panel hero">
      <div class="hero-main">
        <div class="hero-title">WonderKids Academy</div>
        <div class="hero-sub">Mission Control for little explorers, ages 3 to 6. Learn, scan, level up.</div>
        <span class="chip">🔢 Number Nebula</span><span class="chip">🔤 Letter Galaxy</span>
        <span class="chip">🔬 Science Station</span><span class="chip">🎨 Shape &amp; Color Moon</span>
      </div>
      <div class="boot">
        <div class="boot-line" style="--d:.2s">▸ Waking the academy core … <b>ok</b></div>
        <div class="boot-line" style="--d:.9s">▸ Calibrating star maps … <b>ok</b></div>
        <div class="boot-line" style="--d:1.6s">▸ Loading NOVA, the ship AI … <b>ok</b></div>
        <div class="boot-line" style="--d:2.3s">▸ Crew check-in ready <b>▮</b></div>
      </div>
    </div>
    """)

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        ui('<div class="panel"><h3>🔑 Crew check-in</h3><div class="tiny">Returning explorers sign in here.</div></div>')
        with st.form("login_form"):
            login_user = st.text_input("Explorer username", placeholder="e.g., leo_dino")
            login_pw = st.text_input("Secret passcode", type="password", placeholder="••••••")
            submitted_login = st.form_submit_button("🚀 Launch")
            if submitted_login:
                user = authenticate_user(login_user, login_pw)
                if user:
                    begin_session(user, f"Welcome back, {user['child_name']}! Mission control is ready. Let's collect stars!")
                    st.rerun()
                else:
                    st.error("Check-in failed: that username and passcode don't match. Check both and try again.")

    with col_right:
        ui('<div class="panel"><h3>✨ Enlist a new cadet</h3><div class="tiny">Takes ten seconds. No email needed.</div></div>')
        with st.form("signup_form"):
            new_child = st.text_input("Child's first name", placeholder="e.g., Maya")
            new_user = st.text_input("Choose an explorer username", placeholder="e.g., maya_star")
            new_pw = st.text_input("Create a secret passcode", type="password", placeholder="e.g., 1234")
            r1, r2 = st.columns(2)
            with r1:
                age = st.selectbox("Child's age", [3, 4, 5, 6], format_func=lambda a: f"🎂 {a} years old")
            with r2:
                avatar = st.selectbox("Crew buddy", ["🦁 Leo", "🦄 Sparkle", "🦖 Rexy", "🐼 Bamboo", "🚀 Astro"])
            submitted_signup = st.form_submit_button("🎉 Enlist & launch")
            if submitted_signup:
                if not new_child.strip() or not new_user.strip() or not new_pw:
                    st.warning("Enter the child's name, a username and a passcode to continue.")
                else:
                    ok, msg = create_user(new_user, new_pw, new_child, age, avatar.split()[0])
                    if ok:
                        user = authenticate_user(new_user, new_pw)
                        begin_session(user, f"Hooray! Hi {new_child}! You are now a cadet at WonderKids Academy. Let's blast off!")
                        st.rerun()
                    else:
                        st.error(msg)
    if st.session_state.speech_payload:
        st.session_state.speech_payload = None
    st.stop()

# ==========================================
# 9. APP SHELL & SIDEBAR
# ==========================================
user = get_user_by_id(st.session_state.user_id)
if user is None:                                   # account vanished — return to check-in
    st.session_state.user_id = None
    st.rerun()

rk = rank_info(user["stars"])
safe_name = escape(user["child_name"])

with st.sidebar:
    nxt_txt = (f"{rk['to_go']} ⭐ to {rk['next'][1]}" if rk["next"] else "Top rank reached")
    ui(f"""
    <div class="crew">
      <div class="orbit"><span>{user['avatar']}</span></div>
      <div class="crew-name">{safe_name} · Age {user['age_group']}</div>
      <div class="rank">{rk['icon']} {rk['name']}</div>
      <div class="bar"><div style="width:{rk['pct']}%"></div></div>
      <div class="tiny">{nxt_txt}</div>
      <div style="margin-top:8px;font-weight:700">⭐ {user['stars']} &nbsp;·&nbsp; 🔥 {user['streak']}</div>
    </div>
    """)

    st.markdown("### 🧭 Navigation")
    nav_choice = st.radio(
        "Go to",
        ["🎮 Mission Deck", "🏆 Artifact Vault", "📊 Command Analytics"],
        label_visibility="collapsed",
    )

    st.markdown("### 🌌 Sector")
    selected_subject = st.selectbox(
        "Sector", list(SECTOR_NAMES.keys()), format_func=lambda k: SECTOR_NAMES[k],
        index=list(SECTOR_NAMES.keys()).index(st.session_state.subject), label_visibility="collapsed",
    )
    st.markdown("### 🎯 Mission type")
    selected_mode = st.selectbox(
        "Mission type", list(MODES.keys()), format_func=lambda k: MODES[k][0],
        index=list(MODES.keys()).index(st.session_state.mode), label_visibility="collapsed",
    )
    st.caption(MODES[selected_mode][1])
    st.markdown("### 📈 Difficulty")
    selected_level = st.selectbox(
        "Difficulty", [1, 2, 3, 4], index=st.session_state.level - 1,
        format_func=lambda l: LEVEL_NAMES[l], label_visibility="collapsed",
    )

    if (selected_subject != st.session_state.subject or selected_mode != st.session_state.mode
            or selected_level != st.session_state.level):
        st.session_state.subject = selected_subject
        st.session_state.mode = selected_mode
        st.session_state.level = selected_level
        st.session_state.mission_results = []
        start_question()
        st.rerun()

    st.toggle("🔊 Sound & voice", key="sound_on")
    st.divider()
    if st.button("🚪 Switch crew member"):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

if st.session_state.speech_payload:
    txt, sfx, tid = st.session_state.speech_payload
    speak(txt, sfx, tid)
    st.session_state.speech_payload = None


# ==========================================
# 10. VIEW 1 · MISSION DECK
# ==========================================
def route_html(results, total, complete):
    nodes = []
    for i in range(total):
        if i < len(results):
            cls, sym = ("ok", "★") if results[i] else ("bad", "✖")
        elif i == len(results) and not complete and not st.session_state.answered:
            cls, sym = "now", "🚀"
        else:
            cls, sym = "todo", "○"
        nodes.append(f'<div class="node {cls}">{sym}</div>')
    return '<div class="route">' + '<div class="link"></div>'.join(nodes) + "</div>"


def handle_answer(idx: int, opt: str):
    s = st.session_state
    q = s.current_q
    right = (opt == q["answer"])
    elapsed = time.time() - s.q_start
    clean = not s.hint_used
    fast = (s.mode == "⚡ Lightning Pop") and elapsed <= WARP_WINDOW_SEC

    rank_before = rank_info(user["stars"])["idx"]
    res = record_attempt(user["id"], s.subject, s.mode, s.level, right, fast=fast, clean=clean)
    rank_after = rank_info(user["stars"] + res["gained"])

    s.answered, s.last_result, s.chosen, s.result_info = True, right, idx, res
    s.mission_results = s.mission_results + [right]
    ranked_up = right and rank_after["idx"] > rank_before
    s.rank_up = f"{rank_after['icon']} {rank_after['name']}" if ranked_up else None

    if right:
        cheer = random.choice([
            f"Woohoo! You did it, {user['child_name']}!",
            f"Yippee! {opt} is right! You're a superstar!",
            f"Yay! High five, {user['child_name']}! Super smart!",
        ])
        line = f"{cheer} Fun fact! {q['fact']}"
        sfx = "level" if ranked_up else "win"
    else:
        line = f"Nice try, {user['child_name']}! The answer is {q['answer']}. Here is a cool fact! {q['fact']}"
        sfx = "oops"
    if len(s.mission_results) >= MISSION_LENGTH:
        got = sum(s.mission_results)
        line += f" Mission complete! You got {got} out of {MISSION_LENGTH}!"
    s.speech_payload = (line, sfx, str(random.random()))
    st.rerun()


if nav_choice == "🎮 Mission Deck":
    s = st.session_state
    if s.current_q is None:
        start_question()
    q_data = s.current_q
    mission_done = len(s.mission_results) >= MISSION_LENGTH

    # --- HUD ---
    h1, h2, h3, h4 = st.columns(4, gap="medium")
    with h1:
        ui(f'<div class="hud"><div class="hud-label">Sector</div><div class="hud-value">{SECTOR_NAMES[s.subject]}</div></div>')
    with h2:
        ui(f'<div class="hud"><div class="hud-label">Mission type</div><div class="hud-value">{MODES[s.mode][0]}</div></div>')
    with h3:
        ui(f'<div class="hud"><div class="hud-label">Rank</div><div class="hud-value">{rk["icon"]} {rk["name"]} · ⭐ {user["stars"]}</div>'
           f'<div class="bar"><div style="width:{rk["pct"]}%"></div></div></div>')
    with h4:
        combo = "×2 combo ready" if user["streak"] >= 4 else f"{user['streak']} in a row"
        ui(f'<div class="hud"><div class="hud-label">Streak</div><div class="hud-value">🔥 {combo}</div>'
           f'<div class="tiny">Every 5th in a row earns a bonus ⭐</div></div>')

    # --- Mission route ---
    ui(route_html(s.mission_results, MISSION_LENGTH, mission_done))
    done_n = min(len(s.mission_results), MISSION_LENGTH)
    ui(f'<div class="route-cap">Mission progress: {done_n} of {MISSION_LENGTH} waypoints reached</div>')

    # --- Question stage ---
    ui(f"""
    <div class="panel stage">
      <div class="nova"><span class="nova-av">{user['avatar']}</span>
        <span class="nova-say">{safe_name}, decode the signal!</span></div>
      <div class="holo">{escape(q_data['visual'])}</div>
      <div class="q">{escape(q_data['question'])}</div>
    </div>
    """)

    if q_data.get("toys"):
        render_scanner(q_data["toys"], s.q_id)
    if s.mode == "⚡ Lightning Pop" and not s.answered:
        render_warp_timer(s.q_id)

    # --- Tools ---
    t1, t2 = st.columns(2, gap="large")
    with t1:
        if st.button("🔊 Replay transmission"):
            speak(q_data["voice"], "pop", str(random.random()))
    with t2:
        if st.button("📡 Scan for clues (removes 2 wrong answers)", disabled=s.answered or s.hint_used):
            wrong = [i for i, o in enumerate(q_data["options"]) if o != q_data["answer"]]
            s.eliminated = random.sample(wrong, 2)
            s.hint_used = True
            s.speech_payload = ("Scanning! I scrambled two wrong answers for you.", "scan", str(random.random()))
            st.rerun()

    # --- Answer grid (strict 2x2) ---
    options = q_data["options"]
    row1 = st.columns(2, gap="large")
    row2 = st.columns(2, gap="large")
    slots = [row1[0], row1[1], row2[0], row2[1]]
    for idx, opt in enumerate(options[:4]):
        label = opt
        scrambled = idx in s.eliminated and not s.answered
        if scrambled:
            label = "🚫 Signal scrambled"
        elif s.answered and opt == q_data["answer"]:
            label = f"✅ {opt}"
        elif s.answered and idx == s.chosen:
            label = f"❌ {opt}"
        with slots[idx]:
            if st.button(label, key=f"opt_{idx}", disabled=s.answered or scrambled):
                handle_answer(idx, opt)

    # --- Result, debrief, next ---
    if s.answered:
        info = s.result_info or {"gained": 0, "notes": [], "sticker": None}
        if s.last_result:
            notes = " · ".join(info["notes"])
            extra = f"<small>{notes}</small>" if notes else ""
            ui(f'<div class="result ok">✅ Signal decoded, {safe_name}! +{info["gained"]} ⭐{extra}</div>')
            if info["sticker"]:
                ui(f'<div class="result ok">🎁 Artifact unlocked: {info["sticker"]}<small>See it in the Artifact Vault.</small></div>')
        else:
            ui(f'<div class="result bad">💛 Not quite. The answer was <b>{escape(q_data["answer"])}</b>. '
               f'<small>Your streak resets, but every try teaches your brain something new.</small></div>')

        if s.rank_up:
            st.balloons()
            ui(f'<div class="rankup">🎖️ RANK UP! {safe_name} is now {s.rank_up}</div>')

        ui(f'<div class="fact"><b>💡 NOVA\'s fun fact:</b><br>{escape(q_data["fact"])}</div>')

        if mission_done:
            got = sum(s.mission_results)
            rating = 3 if got >= 4 else (2 if got == 3 else 1)
            ui(f"""
            <div class="panel debrief">
              <div class="big">Mission complete</div>
              <div style="font-size:2.2rem;margin:6px 0">{'⭐' * rating}{'☆' * (3 - rating)}</div>
              <div style="font-size:1.2rem">{got} of {MISSION_LENGTH} waypoints cleared.
              {'Flawless flying!' if got == MISSION_LENGTH else 'Great flying, ready for the next one?'}</div>
            </div>
            """)
            if got >= 4 and not s.rank_up:
                st.balloons()

        st.write("")
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            if st.button("🚀 Launch next mission" if mission_done else "➡️ Next signal"):
                if mission_done:
                    s.mission_results = []
                start_question()
                st.rerun()

# ==========================================
# 11. VIEW 2 · ARTIFACT VAULT
# ==========================================
elif nav_choice == "🏆 Artifact Vault":
    st.markdown(f"## 🏆 {safe_name}'s Artifact Vault")
    all_stickers = ["🌟"] + STICKER_POOL           # 20 slots = 5 columns x 4 rows
    got_n = len([s_ for s_ in all_stickers if s_ in user["stickers"]])
    to_next = 3 - (user["stars"] % 3)
    ui(f"""
    <div class="panel" style="margin-bottom:16px">
      <b>{got_n} of {len(all_stickers)} artifacts recovered.</b>
      {'Earn ' + str(to_next) + ' more ⭐ to unlock the next one.' if got_n < len(all_stickers) else 'Vault complete. Legendary!'}
      <div class="bar"><div style="width:{int(got_n / len(all_stickers) * 100)}%"></div></div>
    </div>
    """)
    grid = st.columns(5, gap="medium")
    for idx, sticker in enumerate(all_stickers):
        unlocked = sticker in user["stickers"]
        with grid[idx % 5]:
            ui(f"""
            <div class="artifact {'on' if unlocked else 'off'}">
              <div class="em">{sticker}</div>
              <div class="st">{'Recovered' if unlocked else 'Sealed'}</div>
            </div>
            """)

# ==========================================
# 12. VIEW 3 · COMMAND ANALYTICS (parents & teachers)
# ==========================================
else:
    import pandas as pd

    st.markdown(f"## 📊 Command Analytics: {safe_name}")
    rows = get_progress_stats(user["id"])

    if not rows:
        st.info("No missions flown yet. Open the Mission Deck to start collecting data.")
    else:
        df = pd.DataFrame(rows, columns=["Subject", "Mode", "Level", "Correct", "Timestamp"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df = df.sort_values("Timestamp").reset_index(drop=True)
        df["Sector"] = df["Subject"].map(SECTOR_NAMES).fillna(df["Subject"])
        df["Mission type"] = df["Mode"].map(lambda m: MODES.get(m, (m,))[0])

        kpis = [
            ("⭐ Total stars", str(user["stars"])),
            ("📝 Questions answered", str(len(df))),
            ("🎯 Overall accuracy", f"{df['Correct'].mean() * 100:.0f}%"),
            ("🏆 Artifacts", f"{len(user['stickers'])} / {len(STICKER_POOL) + 1}"),
        ]
        for col, (lbl, val) in zip(st.columns(4, gap="medium"), kpis):
            with col:
                ui(f'<div class="hud"><div class="hud-label">{lbl}</div><div class="hud-value" style="font-size:1.5rem">{val}</div></div>')

        # --- Insight ---
        by_sector = df.groupby("Sector").agg(Questions=("Correct", "count"), Accuracy=("Correct", "mean")).reset_index()
        solid = by_sector[by_sector["Questions"] >= 3]
        if len(solid) >= 2:
            best, weak = solid.loc[solid["Accuracy"].idxmax()], solid.loc[solid["Accuracy"].idxmin()]
            msg = (f"<b>Strongest sector:</b> {best['Sector']} ({best['Accuracy'] * 100:.0f}%). "
                   f"<b>Needs more practice:</b> {weak['Sector']} ({weak['Accuracy'] * 100:.0f}%).")
        elif len(solid) == 1:
            msg = f"<b>{solid.iloc[0]['Sector']}</b> has enough data so far. Try another sector for a fuller picture."
        else:
            msg = "Answer at least 3 questions in a sector to unlock strength and focus insights."
        st.write("")
        ui(f'<div class="panel">💡 {msg}</div>')
        st.write("")

        c_left, c_right = st.columns(2, gap="large")
        with c_left:
            st.markdown("### 📚 Accuracy by sector")
            chart = by_sector.assign(**{"Accuracy (%)": (by_sector["Accuracy"] * 100).round(1)}).set_index("Sector")[["Accuracy (%)"]]
            st.bar_chart(chart)
        with c_right:
            st.markdown("### 📈 Accuracy trend (rolling 5)")
            trend = (df["Correct"].rolling(5, min_periods=1).mean() * 100).round(1)
            st.line_chart(pd.DataFrame({"Accuracy (%)": trend}))

        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("### 🚀 Accuracy by difficulty")
            lvl = df.groupby("Level")["Correct"].mean().mul(100).round(1)
            lvl.index = [LEVEL_NAMES.get(i, str(i)) for i in lvl.index]
            st.bar_chart(lvl.rename("Accuracy (%)"))
        with c2:
            st.markdown("### 🕒 Recent flight log")
            recent = df.tail(10).iloc[::-1].copy()
            recent["When"] = recent["Timestamp"].dt.strftime("%d %b, %H:%M")
            recent["Result"] = recent["Correct"].map({1: "✅ Correct", 0: "❌ Retry"})
            try:
                st.dataframe(recent[["When", "Sector", "Mission type", "Result"]], width="stretch", hide_index=True)
            except TypeError:   # older Streamlit versions
                st.dataframe(recent[["When", "Sector", "Mission type", "Result"]], use_container_width=True, hide_index=True)

        export = df[["Timestamp", "Sector", "Mission type", "Level", "Correct"]].to_csv(index=False)
        st.download_button("⬇️ Export report (CSV)", export, file_name=f"wonderkids_{user['username']}_report.csv", mime="text/csv")

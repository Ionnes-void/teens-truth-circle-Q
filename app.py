import streamlit as st
import random
import time
import json
from datetime import datetime, timezone
from supabase import create_client, Client

# ==========================================
# 1. PAGE & BRAND CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Truth Circle",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. SUPABASE DATABASE INITIALIZATION
# ==========================================
@st.cache_resource
def init_supabase() -> Client:
    raw_url = st.secrets["supabase"]["SUPABASE_URL"].strip()
    
    # Strip any trailing path or /rest/v1 suffixes that trigger PGRST125
    clean_url = raw_url.split("/rest/v1")[0].rstrip("/")
    key = st.secrets["supabase"]["SUPABASE_KEY"].strip()
    
    return create_client(clean_url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("⚠️ Connection error. Please check your Streamlit secrets configuration.")
    st.stop()

# ==========================================
# 3. CURATED DECK DATA (FALLBACKS & PROMPTS)
# ==========================================
FEATURED_NOTES = [
    "Sometimes I feel like I'm the friend everyone comes to when they need something, but nobody notices when I'm struggling.",
    "I feel like I'm acting like a different person depending on who I'm with, and I don't know who I actually am.",
    "I'm really worried about the future, but everyone expects me to have it all figured out already.",
    "I find it hard to ask for help when I'm overwhelmed because I don't want to burden anyone."
]

QUESTIONS = [
    "What's something you wish people understood about you?",
    "What's something you're proud of that people don't usually notice?",
    "What's something you've changed your mind about recently?",
    "What makes you feel genuinely heard?",
    "What's something you wish you could say without being judged?",
    "What's something you're still learning about yourself?",
    "Who brings out the best version of you?",
    "What's something you wish adults understood about being your age?",
    "What's one thing you want to get better at?",
    "What's something that always makes your day a little better?"
]

FINISH_PROMPTS = [
    "I've never told anyone that...",
    "I wish people knew that...",
    "Something I'm still figuring out is...",
    "I feel most like myself when...",
    "Lately I've been thinking about...",
    "I never thought I'd admit this, but...",
    "If I could say one thing without being judged, I'd say...",
    "One thing I pretend doesn't bother me is...",
    "I wish I was brave enough to...",
    "Right now, I really need..."
]

ENCOURAGEMENT_MESSAGES = [
    "No pressure. There's always another card.",
    "Passing is 100% fine. Speak up when you feel like it.",
    "No worries at all. Take a breath or peek at what others shared in the House first.",
    "Your voice matters here whenever you feel ready. Take your time."
]

# ==========================================
# 4. DATABASE HELPER FUNCTIONS
# ==========================================

def insert_private_note(content: str):
    """Inserts a community note into the private draw pool (draw_notes) ONLY."""
    try:
        data = {
            "content": content.strip(),
            "source": "community",
            "status": "available"
        }
        supabase.table("draw_notes").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error submitting note: {e}")
        return False

def draw_anonymous_note():
    """Fetches an available community note from Supabase OR falls back to a featured note."""
    try:
        res = supabase.table("draw_notes").select("*").eq("status", "available").execute()
        available_community_notes = res.data or []

        pool = []
        for note_text in FEATURED_NOTES:
            pool.append({"type": "featured", "content": note_text})
        
        for db_note in available_community_notes:
            pool.append({"type": "community", "raw": db_note, "content": db_note["content"]})

        selected = random.choice(pool)

        if selected["type"] == "community":
            db_id = selected["raw"]["id"]
            now_str = datetime.now(timezone.utc).isoformat()
            supabase.table("draw_notes").update({
                "status": "drawn",
                "drawn_at": now_str
            }).eq("id", db_id).execute()

        return selected["content"]

    except Exception as e:
        return random.choice(FEATURED_NOTES)

def create_house_post(tag: str, prompt_text: str, response_text: str = ""):
    """Inserts structured content into house_posts as JSON."""
    try:
        payload = json.dumps({
            "tag": tag,
            "prompt": prompt_text,
            "response": response_text
        })
        data = {"content": payload, "likes": 0, "comments": []}
        supabase.table("house_posts").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error sharing to House: {e}")
        return False

def fetch_house_posts():
    """Fetches public feed items from house_posts."""
    try:
        res = supabase.table("house_posts").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error loading feed: {e}")
        return []

def update_post_likes(post_id: int, new_likes: int):
    try:
        supabase.table("house_posts").update({"likes": new_likes}).eq("id", post_id).execute()
    except Exception as e:
        st.error(f"Error updating like count: {e}")

def add_post_comment(post_id: int, comments_list: list):
    try:
        supabase.table("house_posts").update({"comments": comments_list}).eq("id", post_id).execute()
    except Exception as e:
        st.error(f"Error posting comment: {e}")

def report_house_post(post: dict):
    try:
        supabase.table("reported_posts").insert({
            "content": post["content"],
            "original_post_id": post["id"]
        }).execute()
        supabase.table("house_posts").delete().eq("id", post["id"]).execute()
    except Exception as e:
        st.error(f"Error reporting post: {e}")

# ==========================================
# 5. RANDOMIZER LOGIC
# ==========================================
def pick_random_card():
    random.seed(time.time_ns())
    category = random.choice(["note", "question", "finish"])

    if category == "note":
        drawn_text = draw_anonymous_note()
        return {
            "type": "note",
            "tag": "ANONYMOUS NOTE",
            "text": drawn_text,
            "instruction": "What would you tell them?",
            "placeholder": "Give them your 2 cents...",
            "btn_label": "💬 Give your 2 cents & Share"
        }
    elif category == "question":
        return {
            "type": "question",
            "tag": "OPEN QUESTION",
            "text": random.choice(QUESTIONS),
            "instruction": "Answer it yourself, or throw it to the House.",
            "placeholder": "What's your answer?",
            "btn_label": "💬 Answer & Share"
        }
    else:
        return {
            "type": "finish",
            "tag": "FINISH THIS",
            "text": random.choice(FINISH_PROMPTS),
            "instruction": "Complete the thought however it speaks to you.",
            "placeholder": "Finish the thought...",
            "btn_label": "💬 Finish & Share"
        }

# ==========================================
# 6. GLOBAL DESIGN SYSTEM & LIGHT CSS
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }

    #MainMenu, footer, header, .stDeployButton, div[data-testid="stToolbar"] {
        visibility: hidden;
        display: none !important;
    }

    .block-container {
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .brand-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .brand-title {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #0F172A;
        margin-bottom: 2px;
    }
    .brand-sub {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
    }

    .subtle-nav {
        background: #FFFFFF;
        padding: 4px;
        border-radius: 999px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    .app-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
    }

    .draw-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 32px 24px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    .card-note { border: 1px solid #FED7AA; background: linear-gradient(180deg, #FFF7ED 0%, #FFFFFF 100%); }
    .card-question { border: 1px solid #99F6E4; background: linear-gradient(180deg, #F0FDFA 0%, #FFFFFF 100%); }
    .card-finish { border: 1px solid #DDD6FE; background: linear-gradient(180deg, #F5F3FF 0%, #FFFFFF 100%); }

    .card-tag {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 16px;
        text-transform: uppercase;
    }

    .tag-note { background: #FFEDD5; color: #C2410C; }
    .tag-question { background: #CCFBF1; color: #0F766E; }
    .tag-finish { background: #EDE9FE; color: #6D28D9; }

    .card-text {
        font-size: 1.25rem;
        font-weight: 700;
        line-height: 1.45;
        color: #0F172A;
        margin-bottom: 12px;
    }

    .card-instruction {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
    }

    /* Modern Feed Card Component Styling */
    .feed-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    .feed-tag {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        padding: 3px 10px;
        border-radius: 999px;
        background: #F1F5F9;
        color: #475569;
        margin-bottom: 12px;
        text-transform: uppercase;
    }

    .feed-prompt-box {
        background: #F8FAFC;
        border-left: 3px solid #6366F1;
        padding: 10px 14px;
        border-radius: 0 10px 10px 0;
        font-size: 0.88rem;
        color: #475569;
        margin-bottom: 14px;
        font-style: italic;
    }

    .feed-response-body {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0F172A;
        line-height: 1.5;
        white-space: pre-line;
    }

    .stTextArea textarea, .stTextInput input {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 14px !important;
        color: #0F172A !important;
        padding: 12px 14px !important;
        font-size: 0.95rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    div.stButton > button {
        width: 100% !important;
        min-height: 48px !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        border: 1px solid #E2E8F0 !important;
        background: #FFFFFF !important;
        color: #334155 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button:hover {
        background: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }

    div.stButton > button[kind="primary"] {
        background: #4F46E5 !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #4338CA !important;
    }

    .subtle-info {
        font-size: 0.78rem;
        color: #64748B;
        text-align: center;
        margin-top: 6px;
        margin-bottom: 12px;
    }

    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #64748B;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 7. SESSION STATE INITIALIZATION
# ==========================================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "current_card" not in st.session_state:
    st.session_state.current_card = None
if "current_encouragement" not in st.session_state:
    st.session_state.current_encouragement = "No pressure. There's always another card."
if "liked_posts" not in st.session_state:
    st.session_state.liked_posts = set()

# ==========================================
# 8. BRAND HEADER & NAVIGATION BAR
# ==========================================
st.markdown('''
    <div class="brand-header">
        <div class="brand-title">Truth Circle</div>
        <div class="brand-sub">Say what you mean. You can always pass.</div>
    </div>
''', unsafe_allow_html=True)

st.markdown('<div class="subtle-nav">', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("🎲 Draw", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()

with nav_col2:
    if st.button("📝 Note", use_container_width=True):
        st.session_state.view = "write_note"
        st.rerun()

with nav_col3:
    if st.button("🏠 House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 9. SCREEN CONTROLLERS
# ==========================================

# --- SCREEN 1: HOME ---
if st.session_state.view == "home":
    st.markdown('''
        <div class="app-card">
            <div style="font-size: 2rem; margin-bottom: 8px;">✨</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">Ready to draw?</div>
            <div style="font-size: 0.88rem; color: #64748B;">Draw an anonymous note from someone else, an open question, or a thought starter.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🎲 DRAW A CARD", use_container_width=True, type="primary"):
        st.session_state.current_card = pick_random_card()
        st.session_state.view = "draw_card"
        st.rerun()

    st.write("")
    if st.button("📝 Write an anonymous note", use_container_width=True):
        st.session_state.view = "write_note"
        st.rerun()

    if st.button("🏠 Explore The House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 2: DRAWN CARD EXPERIENCE ---
elif st.session_state.view == "draw_card":
    card = st.session_state.current_card
    c_type = card["type"]

    st.markdown(f'''
        <div class="draw-card card-{c_type}">
            <span class="card-tag tag-{c_type}">{card["tag"]}</span>
            <div class="card-text">"{card["text"]}"</div>
            <div class="card-instruction">{card["instruction"]}</div>
        </div>
    ''', unsafe_allow_html=True)

    user_input = st.text_area(
        label="Response Input",
        placeholder=card["placeholder"],
        key="card_input",
        label_visibility="collapsed"
    )

    st.markdown('<div class="subtle-info">🌐 Your response will be posted anonymously to The House.</div>', unsafe_allow_html=True)

    if st.button(card["btn_label"], use_container_width=True, type="primary"):
        if user_input.strip():
            if create_house_post(card["tag"], card["text"], user_input.strip()):
                st.session_state.view = "shared_confirm"
                st.rerun()
        else:
            st.warning("Write a quick thought before sharing!")

    if st.button("🏠 Throw to House", use_container_width=True):
        if create_house_post(card["tag"], card["text"], user_input.strip()):
            st.session_state.view = "shared_confirm"
            st.rerun()

    if st.button("→ Pass", use_container_width=True):
        random.seed(time.time_ns())
        st.session_state.current_encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
        st.session_state.view = "pass_encouragement"
        st.rerun()

# --- SCREEN 3: PASS ENCOURAGEMENT ---
elif st.session_state.view == "pass_encouragement":
    st.markdown(f'''
        <div class="app-card">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">🌿 No pressure.</div>
            <div style="font-size: 0.9rem; color: #64748B; line-height: 1.4;">{st.session_state.current_encouragement}</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🎲 Draw another card", use_container_width=True, type="primary"):
        st.session_state.current_card = pick_random_card()
        st.session_state.view = "draw_card"
        st.rerun()

    if st.button("🏠 Go to The House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 4: SHARED CONFIRMATION ---
elif st.session_state.view == "shared_confirm":
    st.markdown('''
        <div class="app-card">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">✨ It's in the House.</div>
            <div style="font-size: 0.9rem; color: #64748B; line-height: 1.4;">Others can now see it and add their 2 cents.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🏠 See The House", use_container_width=True, type="primary"):
        st.session_state.view = "house"
        st.rerun()

    if st.button("🎲 Draw again", use_container_width=True):
        st.session_state.current_card = pick_random_card()
        st.session_state.view = "draw_card"
        st.rerun()

# --- SCREEN 5: WRITE ANONYMOUS NOTE ---
elif st.session_state.view == "write_note":
    st.markdown("### 📝 Write an Anonymous Note")
    st.markdown("*Something you've been thinking about?*")
    st.caption("No name needed.")

    note_text = st.text_area(
        label="Note Area",
        placeholder="Type your thought, situation, or prompt here...",
        height=140,
        label_visibility="collapsed"
    )

    st.markdown('<div class="subtle-info">🔒 Your note stays private until it is drawn.<br>Please leave out names and identifying details.</div>', unsafe_allow_html=True)

    if st.button("DROP IT INTO THE CIRCLE ✨", use_container_width=True, type="primary"):
        if note_text.strip():
            if insert_private_note(note_text):
                st.session_state.view = "note_submitted_confirm"
                st.rerun()
        else:
            st.warning("Type a thought before dropping it into the Circle!")

# --- SCREEN 6: NOTE SUBMITTED CONFIRMATION ---
elif st.session_state.view == "note_submitted_confirm":
    st.markdown('''
        <div class="app-card">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">✨ Your note is in the Circle.</div>
            <div style="font-size: 0.9rem; color: #64748B; line-height: 1.4;">Someone may draw it later.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🎲 Back to the Circle", use_container_width=True, type="primary"):
        st.session_state.view = "home"
        st.rerun()

    if st.button("🏠 Visit The House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 7: THE HOUSE FEED ---
elif st.session_state.view == "house":
    st.markdown("### 🏠 THE HOUSE")
    st.caption("Public feed of drawn notes and responses.")
    st.write("")

    posts = fetch_house_posts()

    if not posts:
        st.markdown('''
            <div class="empty-state">
                <div style="font-size: 2rem; margin-bottom: 8px;">🌱</div>
                <div style="font-size: 1.05rem; font-weight: 600; color: #0F172A;">The House is quiet.</div>
                <div style="font-size: 0.88rem; margin-top: 4px; color: #64748B;">Leave something for someone else to find.</div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        for post in posts:
            post_id = post["id"]
            likes = post.get("likes", 0)
            comments = post.get("comments", [])

            # Parse post body cleanly
            try:
                data = json.loads(post["content"])
                tag = data.get("tag", "NOTE")
                prompt = data.get("prompt", "")
                response = data.get("response", "")
            except Exception:
                tag = "NOTE"
                prompt = ""
                response = post["content"]

            # Render HTML Card Component
            prompt_html = f'<div class="feed-prompt-box">&ldquo;{prompt}&rdquo;</div>' if prompt else ""
            response_html = f'<div class="feed-response-body">{response}</div>' if response else ""

            st.markdown(f'''
                <div class="feed-card">
                    <span class="feed-tag">{tag}</span>
                    {prompt_html}
                    {response_html}
                </div>
            ''', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                has_liked = post_id in st.session_state.liked_posts
                like_label = f"💖 {likes}" if has_liked else f"❤️ {likes}"
                
                if st.button(like_label, key=f"like_{post_id}"):
                    if has_liked:
                        update_post_likes(post_id, max(0, likes - 1))
                        st.session_state.liked_posts.remove(post_id)
                    else:
                        update_post_likes(post_id, likes + 1)
                        st.session_state.liked_posts.add(post_id)
                    st.rerun()

            with col2:
                if st.button("🚩 Report", key=f"rep_{post_id}"):
                    report_house_post(post)
                    st.toast("Post reported and removed.")
                    st.rerun()

            with st.expander("💬 Responses"):
                if comments:
                    for comment in comments:
                        st.write(f"• {comment}")
                else:
                    st.caption("No responses yet.")

                c_input = st.text_input(
                    label="Comment input",
                    key=f"c_in_{post_id}",
                    placeholder="Give your 2 cents...",
                    label_visibility="collapsed"
                )
                if st.button("Post response", key=f"c_btn_{post_id}"):
                    if c_input.strip():
                        comments.append(c_input.strip())
                        add_post_comment(post_id, comments)
                        st.rerun()
            st.write("---")

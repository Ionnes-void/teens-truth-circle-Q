import streamlit as st
import random
import time
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
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("⚠️ Connection error. Check your Streamlit Secrets configuration.")
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
    """Inserts a community note into the private draw pool (NOT house_posts)."""
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
        # 1. Attempt to fetch available community notes
        res = supabase.table("draw_notes").select("*").eq("status", "available").execute()
        available_community_notes = res.data or []

        # 2. Build combined pool (Featured + Available Community)
        pool = []
        for note_text in FEATURED_NOTES:
            pool.append({"type": "featured", "content": note_text})
        
        for db_note in available_community_notes:
            pool.append({"type": "community", "raw": db_note, "content": db_note["content"]})

        # 3. Randomly select one note from pool
        selected = random.choice(pool)

        # 4. Mark community note as 'drawn' in Supabase
        if selected["type"] == "community":
            db_id = selected["raw"]["id"]
            now_str = datetime.now(timezone.utc).isoformat()
            supabase.table("draw_notes").update({
                "status": "drawn",
                "drawn_at": now_str
            }).eq("id", db_id).execute()

        return selected["content"]

    except Exception as e:
        # Reliable fallback if network fails
        return random.choice(FEATURED_NOTES)

def create_house_post(post_text: str):
    """Inserts a public post into house_posts."""
    try:
        data = {"content": post_text, "likes": 0, "comments": []}
        supabase.table("house_posts").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error sharing to House: {e}")
        return False

def fetch_house_posts():
    """Fetches public posts from house_posts."""
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
# 5. RANDOMIZER LOGIC (3 CONTENT TYPES)
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
# 6. REFINED DESIGN SYSTEM & RESPONSIVE CSS
# ==========================================
st.markdown("""
    <style>
    /* Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: #111015;
        color: #ECEAF0;
    }

    /* Hide Streamlit Chrome */
    #MainMenu, footer, header, .stDeployButton, div[data-testid="stToolbar"] {
        visibility: hidden;
        display: none !important;
    }

    /* Container Constrain & Fluid Spacing */
    .block-container {
        max-width: 520px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Brand Header */
    .brand-header {
        text-align: center;
        margin-bottom: 24px;
    }
    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #FFF 0%, #A5A1B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .brand-sub {
        font-size: 0.88rem;
        color: #8E8A9F;
        font-weight: 400;
    }

    /* Minimal Floating Navigation */
    .subtle-nav {
        display: flex;
        gap: 6px;
        margin-bottom: 24px;
        background: rgba(255, 255, 255, 0.03);
        padding: 4px;
        border-radius: 100px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    /* Dynamic Draw Card Object */
    .draw-card {
        background: #18161E;
        border-radius: 24px;
        padding: 32px 24px;
        text-align: center;
        position: relative;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    /* Card Variant Accents */
    .card-note {
        border: 1px solid rgba(224, 122, 95, 0.3);
        background: linear-gradient(180deg, #1E1921 0%, #18161E 100%);
    }
    .card-question {
        border: 1px solid rgba(42, 157, 143, 0.3);
        background: linear-gradient(180deg, #151D20 0%, #18161E 100%);
    }
    .card-finish {
        border: 1px solid rgba(142, 125, 190, 0.3);
        background: linear-gradient(180deg, #1C1926 0%, #18161E 100%);
    }

    .card-tag {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 1.2px;
        padding: 4px 12px;
        border-radius: 100px;
        margin-bottom: 20px;
        text-transform: uppercase;
    }

    .tag-note { background: rgba(224, 122, 95, 0.15); color: #F29E85; border: 1px solid rgba(224, 122, 95, 0.3); }
    .tag-question { background: rgba(42, 157, 143, 0.15); color: #52D1C2; border: 1px solid rgba(42, 157, 143, 0.3); }
    .tag-finish { background: rgba(142, 125, 190, 0.15); color: #BDB2FF; border: 1px solid rgba(142, 125, 190, 0.3); }

    .card-text {
        font-size: 1.35rem;
        font-weight: 700;
        line-height: 1.45;
        color: #F5F4F8;
        margin-bottom: 16px;
    }

    .card-instruction {
        font-size: 0.88rem;
        color: #9A95AA;
        font-weight: 500;
    }

    /* Feedback & Generic Cards */
    .app-card {
        background: #18161E;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Social Feed Items */
    .feed-card {
        background: #18161E;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .feed-body {
        font-size: 1.02rem;
        line-height: 1.5;
        color: #ECEAF0;
        white-space: pre-line;
    }

    /* Form Controls & Inputs */
    .stTextArea textarea, .stTextInput input {
        background: #18161E !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 16px !important;
        color: #F5F4F8 !important;
        padding: 14px !important;
        font-size: 0.98rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #8E7DBE !important;
        box-shadow: 0 0 0 1px #8E7DBE !important;
    }

    /* Buttons System (48px Min Touch Targets) */
    div.stButton > button {
        width: 100% !important;
        min-height: 48px !important;
        border-radius: 100px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: #211E2A !important;
        color: #ECEAF0 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: #2B2737 !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* Primary CTA Override */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7B61FF 0%, #6342E8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(123, 97, 255, 0.25) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        opacity: 0.92 !important;
    }

    .subtle-info {
        font-size: 0.8rem;
        color: #7D7890;
        text-align: center;
        margin-top: 6px;
        margin-bottom: 12px;
    }

    /* Empty States */
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #7D7890;
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
        <div class="brand-title">TRUTH CIRCLE</div>
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
            <div style="font-size: 2.2rem; margin-bottom: 10px;">✨</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #F5F4F8; margin-bottom: 6px;">Ready to draw?</div>
            <div style="font-size: 0.9rem; color: #8E8A9F;">Draw an anonymous note from someone else, an open question, or a thought starter.</div>
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
            post_body = f"**{card['tag']}**\n\"{card['text']}\"\n\n**Response: {user_input.strip()}"
            if create_house_post(post_body):
                st.session_state.view = "shared_confirm"
                st.rerun()
        else:
            st.warning("Write a quick thought before sharing!")

    if st.button("🏠 Throw to House", use_container_width=True):
        post_body = f"**\n\"{card['text']}\""
        if user_input.strip():
            post_body += f"\n\n**Response:** {user_input.strip()}"
        if create_house_post(post_body):
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
            <div style="font-size: 1.15rem; font-weight: 700; color: #F5F4F8; margin-bottom: 8px;">🌿 No pressure.</div>
            <div style="font-size: 0.92rem; color: #8E8A9F; line-height: 1.4;">{st.session_state.current_encouragement}</div>
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
            <div style="font-size: 1.15rem; font-weight: 700; color: #F5F4F8; margin-bottom: 8px;">✨ It's in the House.</div>
            <div style="font-size: 0.92rem; color: #8E8A9F; line-height: 1.4;">Others can now see it and add their 2 cents.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🏠 See The House", use_container_width=True, type="primary"):
        st.session_state.view = "house"
        st.rerun()

    if st.button("🎲 Draw again", use_container_width=True):
        st.session_state.current_card = pick_random_card()
        st.session_state.view = "draw_card"
        st.rerun()

# --- SCREEN 5: WRITE ANONYMOUS NOTE (PRIVATE POOL SUBMISSION) ---
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
            <div style="font-size: 1.15rem; font-weight: 700; color: #F5F4F8; margin-bottom: 8px;">✨ Your note is in the Circle.</div>
            <div style="font-size: 0.92rem; color: #8E8A9F; line-height: 1.4;">Someone may draw it later.</div>
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
                <div style="font-size: 2rem; margin-bottom: 8px;">🌙</div>
                <div style="font-size: 1.05rem; font-weight: 600; color: #ECEAF0;">The House is quiet.</div>
                <div style="font-size: 0.88rem; margin-top: 4px;">Leave something for someone else to find.</div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        for post in posts:
            post_id = post["id"]
            likes = post.get("likes", 0)
            comments = post.get("comments", [])

            st.markdown(f'''
                <div class="feed-card">
                    <div class="feed-body">{post["content"]}</div>
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

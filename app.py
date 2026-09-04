import streamlit as st
import random
import time
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Teens Truth Circle",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- SUPABASE DATABASE CONNECTION ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("⚠️ Could not connect to Supabase. Check your Streamlit Secrets configuration.")
    st.stop()

# --- DATABASE HELPER FUNCTIONS ---
def fetch_house_posts():
    """Fetch posts from Supabase house_posts table ordered by newest first."""
    try:
        response = supabase.table("house_posts").select("*").order("created_at", desc=True).execute()
        return response.data or []
    except Exception as e:
        st.error(f"Error loading posts: {e}")
        return []

def create_house_post(content: str):
    """Insert a new post into the house_posts table."""
    try:
        data = {"content": content, "likes": 0, "comments": []}
        supabase.table("house_posts").insert(data).execute()
    except Exception as e:
        st.error(f"Error publishing post: {e}")

def update_post_likes(post_id: int, new_like_count: int):
    """Update like count for a specific post."""
    try:
        supabase.table("house_posts").update({"likes": new_like_count}).eq("id", post_id).execute()
    except Exception as e:
        st.error(f"Error updating likes: {e}")

def add_post_comment(post_id: int, comments_list: list):
    """Update comments JSONB array for a specific post."""
    try:
        supabase.table("house_posts").update({"comments": comments_list}).eq("id", post_id).execute()
    except Exception as e:
        st.error(f"Error adding comment: {e}")

def report_house_post(post: dict):
    """Move post to reported_posts table and delete from house_posts."""
    try:
        # Insert into reported_posts table
        supabase.table("reported_posts").insert({
            "content": post["content"],
            "original_post_id": post["id"]
        }).execute()
        
        # Delete from house_posts table
        supabase.table("house_posts").delete().eq("id", post["id"]).execute()
    except Exception as e:
        st.error(f"Error reporting post: {e}")

# --- RESPONSIVE & MODERN CSS DESIGN ---
st.markdown("""
    <style>
    /* Global Page Styling */
    .stApp {
        background-color: #FAF6F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #2D2A32;
    }

    /* Hide Streamlit Default UI Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {visibility: hidden;}

    /* Container Max Width for Mobile-First & Desktop Game Feel */
    .block-container {
        max-width: 580px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }

    /* Top Navigation Bar */
    .subtle-nav {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-bottom: 20px;
    }

    /* Title & Homepage Typography */
    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #3C2A4D;
        margin-bottom: 4px;
    }

    .sub-title {
        text-align: center;
        font-size: 1.02rem;
        color: #6C6377;
        margin-bottom: 6px;
        line-height: 1.4;
        font-weight: 400;
    }

    /* Clean Home Screen Hero Card */
    .home-hero-card {
        background-color: #FFFFFF;
        padding: 36px 24px;
        border-radius: 28px;
        box-shadow: 0 10px 25px rgba(60, 42, 77, 0.05);
        border: 2px solid #EFEAE2;
        text-align: center;
        margin-bottom: 24px;
    }

    .home-hero-icon {
        font-size: 2.8rem;
        margin-bottom: 12px;
    }

    .home-hero-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #3C2A4D;
        margin-bottom: 8px;
    }

    .home-hero-text {
        font-size: 0.95rem;
        color: #7D7589;
        line-height: 1.4;
    }

    /* Conversation Card Physical Styling */
    .prompt-card {
        background-color: #FFFFFF;
        padding: 32px 24px;
        border-radius: 28px;
        box-shadow: 0 12px 30px rgba(60, 42, 77, 0.07);
        margin-bottom: 20px;
        border: 2px solid #EFEAE2;
        text-align: center;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    .category-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 18px;
    }

    /* Category Styling */
    .tag-note {
        background-color: #FDF0ED;
        color: #C85A32;
        border: 1px solid #F8D7CD;
    }
    .card-note {
        border-top: 6px solid #E07A5F;
    }

    .tag-question {
        background-color: #EBF7F6;
        color: #1D786F;
        border: 1px solid #C4ECE8;
    }
    .card-question {
        border-top: 6px solid #2A9D8F;
    }

    .tag-finish {
        background-color: #F3EFFF;
        color: #5842C3;
        border: 1px solid #DDD3FF;
    }
    .card-finish {
        border-top: 6px solid #8E7DBE;
    }

    .prompt-text {
        font-size: 1.45rem;
        font-weight: 700;
        color: #2D2A32;
        line-height: 1.45;
        margin-bottom: 14px;
    }

    .prompt-instruction {
        font-size: 0.9rem;
        color: #7D7589;
        font-weight: 500;
    }

    /* Custom Message Containers */
    .feedback-card {
        background-color: #FFFFFF;
        padding: 28px 22px;
        border-radius: 24px;
        border: 1.5px solid #E2DCD5;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.03);
        text-align: center;
        margin-bottom: 22px;
    }

    .feedback-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #3C2A4D;
        margin-bottom: 8px;
    }

    .feedback-sub {
        font-size: 0.98rem;
        color: #6C6377;
        line-height: 1.45;
    }

    .house-card {
        background-color: #FFFFFF;
        padding: 22px 20px;
        border-radius: 22px;
        border: 1.5px solid #EFEAE2;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    /* Mobile-First Button Polish & Touch Targets */
    div.stButton > button {
        width: 100% !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        min-height: 48px !important;
        padding: 12px 18px !important;
        font-size: 0.98rem !important;
        border: 1.5px solid #E2DCD5 !important;
        background-color: #FFFFFF !important;
        color: #3C2A4D !important;
        transition: all 0.15s ease-in-out !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }

    div.stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Primary Hero Action Override */
    div.stButton > button[kind="primary"] {
        background-color: #5842C3 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-size: 1.08rem !important;
        box-shadow: 0 6px 16px rgba(88, 66, 195, 0.28) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #4733A9 !important;
        color: #FFFFFF !important;
    }

    /* Secondary Action Override */
    .secondary-btn button {
        background-color: #F3EFFF !important;
        border: 1.5px solid #DDD3FF !important;
        color: #5842C3 !important;
    }

    /* Navigation Buttons Override */
    .nav-btn button {
        min-height: 38px !important;
        padding: 6px 12px !important;
        font-size: 0.85rem !important;
        border-radius: 20px !important;
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #E2DCD5 !important;
        color: #6C6377 !important;
    }

    /* Input Fields Styling */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1.5px solid #E2DCD5 !important;
        padding: 14px !important;
        font-size: 1rem !important;
        background-color: #FFFFFF !important;
    }

    .stTextArea textarea:focus {
        border-color: #5842C3 !important;
        box-shadow: 0 0 0 2px rgba(88, 66, 195, 0.15) !important;
    }

    .share-notice {
        font-size: 0.82rem;
        color: #8E849B;
        text-align: center;
        margin-top: 4px;
        margin-bottom: 12px;
    }

    /* Responsive Spacing Adjustments */
    @media (max-width: 480px) {
        .main-title { font-size: 2.0rem; }
        .prompt-text { font-size: 1.22rem; }
        .prompt-card { padding: 24px 18px; }
    }
    </style>
""", unsafe_allow_html=True)

# --- OPTION B: CURATED BUILT-IN CARD DECK (CLEAN & ISOLATED) ---
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

FEATURED_NOTES = [
    "*Sometimes I feel like I'm the friend everyone comes to when they need something, but nobody notices when I'm struggling.*",
    "*I feel like I'm acting like a different person depending on who I'm with, and I don't know who I actually am.*",
    "*I'm really worried about the future, but everyone expects me to have it all figured out already.*",
    "*I find it hard to ask for help when I'm overwhelmed because I don't want to burden anyone.*"
]

ENCOURAGEMENT_MESSAGES = [
    "No pressure. There's always another card.",
    "Passing is 100% fine. Speak up when you feel like it.",
    "No worries at all. Take a breath or peek at what others shared in the House first.",
    "Your voice matters here whenever you feel ready. Take your time!"
]

# --- SESSION STATE INITIALIZATION ---
if "view" not in st.session_state:
    st.session_state.view = "home"
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = None
if "current_encouragement" not in st.session_state:
    st.session_state.current_encouragement = "No pressure. There's always another card."
if "liked_posts" not in st.session_state:
    st.session_state.liked_posts = set()

# --- HYBRID CARD RANDOMIZER ENGINE ---
def pick_random_prompt():
    random.seed(time.time_ns())
    
    choice = random.choice(["question", "finish", "note"])

    if choice == "note":
        return {
            "type": "note",
            "category": "ANONYMOUS NOTE 📝",
            "text": random.choice(FEATURED_NOTES),
            "instruction": "What would you tell this person?",
            "placeholder": "Give them your 2 cents...",
            "btn_label": "💬 Give your 2 cents & Share"
        }
    elif choice == "question":
        return {
            "type": "question",
            "category": "OPEN QUESTION 🎯",
            "text": random.choice(QUESTIONS),
            "instruction": "Answer it yourself, or throw it to the House.",
            "placeholder": "What's your answer?",
            "btn_label": "💬 Answer & Share"
        }
    else:
        return {
            "type": "finish",
            "category": "FINISH THIS... ✨",
            "text": random.choice(FINISH_PROMPTS),
            "instruction": "Complete the thought however it speaks to you.",
            "placeholder": "Finish the thought...",
            "btn_label": "💬 Finish & Share"
        }

# --- BRAND HEADER ---
st.markdown('<div class="main-title">TRUTH CIRCLE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Come as you are. Say what you mean. You can always pass.</div>', unsafe_allow_html=True)

# --- TOP NAVIGATION ---
st.markdown('<div class="subtle-nav">', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("🎲 Draw", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with nav_col2:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("📝 Note", use_container_width=True):
        st.session_state.view = "leave_note"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with nav_col3:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("🏠 House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- SCREEN 1: HOME SCREEN ---
if st.session_state.view == "home":
    st.markdown('''
        <div class="home-hero-card">
            <div class="home-hero-icon">✨</div>
            <div class="home-hero-title">Ready to jump in?</div>
            <div class="home-hero-text">Draw a question, a thought starter, or an anonymous note from someone else in the circle.</div>
        </div>
    ''', unsafe_allow_html=True)
    
    if st.button("🎲 DRAW A CARD", use_container_width=True, type="primary"):
        st.session_state.current_prompt = pick_random_prompt()
        st.session_state.view = "prompt"
        st.rerun()

    st.write("")
    
    if st.button("📝 Leave an anonymous note", use_container_width=True):
        st.session_state.view = "leave_note"
        st.rerun()

    if st.button("🏠 Explore The House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 2: PROMPT DISPLAY CARD ---
elif st.session_state.view == "prompt":
    prompt = st.session_state.current_prompt
    p_type = prompt["type"]
    
    tag_class = f"tag-{p_type}"
    card_class = f"card-{p_type}"

    st.markdown(f'''
        <div class="prompt-card {card_class}">
            <span class="category-pill {tag_class}">{prompt["category"]}</span>
            <div class="prompt-text">"{prompt["text"]}"</div>
            <div class="prompt-instruction">{prompt["instruction"]}</div>
        </div>
    ''', unsafe_allow_html=True)

    user_input = st.text_area(
        label="Response Input",
        placeholder=prompt["placeholder"],
        key="prompt_response_input",
        label_visibility="collapsed"
    )

    st.markdown('<div class="share-notice">🌐 Your response will be posted anonymously to The House.</div>', unsafe_allow_html=True)

    if st.button(prompt["btn_label"], use_container_width=True, type="primary"):
        if user_input.strip():
            post_content = f"**{prompt['category']}**\n\"{prompt['text']}\"\n\n**Response:** {user_input.strip()}"
            create_house_post(post_content)
            st.session_state.view = "thrown_confirm"
            st.rerun()
        else:
            st.warning("Write a quick thought before sharing!")

    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("🏠 Throw to House", use_container_width=True):
        post_content = f"**{prompt['category']}**\n\"{prompt['text']}\""
        if user_input.strip():
            post_content += f"\n\n**Response:** {user_input.strip()}"
        create_house_post(post_content)
        st.session_state.view = "thrown_confirm"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("→ Pass", use_container_width=True):
        random.seed(time.time_ns())
        st.session_state.current_encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
        st.session_state.view = "pass_encouragement"
        st.rerun()

# --- SCREEN 3: DYNAMIC PASS SCREEN ---
elif st.session_state.view == "pass_encouragement":
    st.markdown(f'''
        <div class="feedback-card">
            <div class="feedback-title">🌿 No pressure.</div>
            <div class="feedback-sub">{st.session_state.current_encouragement}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    if st.button("🎲 Pick something else", use_container_width=True, type="primary"):
        st.session_state.current_prompt = pick_random_prompt()
        st.session_state.view = "prompt"
        st.rerun()

    if st.button("🏠 Go to the House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 4: THROWN TO HOUSE CONFIRMATION ---
elif st.session_state.view == "thrown_confirm":
    st.markdown('''
        <div class="feedback-card">
            <div class="feedback-title">✨ It's in the House.</div>
            <div class="feedback-sub">Other people using the app can see it and add their 2 cents.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("🏠 See the House", use_container_width=True, type="primary"):
        st.session_state.view = "house"
        st.rerun()

    if st.button("🎲 Draw again", use_container_width=True):
        st.session_state.current_prompt = pick_random_prompt()
        st.session_state.view = "prompt"
        st.rerun()

# --- SCREEN 5: LEAVE ANONYMOUS NOTE ---
elif st.session_state.view == "leave_note":
    st.markdown("### 📝 Leave a note")
    st.markdown("*Something you've been thinking about? Drop it here. No name needed.*")
    
    note_input = st.text_area(
        label="Anonymous Note Input",
        placeholder="Type your thought, situation, or question here...",
        height=140,
        label_visibility="collapsed"
    )
    st.caption("🔒 *Please leave out names and identifying details.*")
    st.caption("🌐 *Anything dropped here will be visible in The House.*")
    st.write("")
    
    if st.button("DROP IT INTO THE CIRCLE ✨", type="primary", use_container_width=True):
        if note_input.strip():
            post_content = f"**ANONYMOUS NOTE 📝**\n\"*{note_input.strip()}*\""
            create_house_post(post_content)
            st.success("Note posted to The House.")
            st.session_state.view = "house"
            st.rerun()
        else:
            st.warning("Type a thought before dropping it in!")

# --- SCREEN 6: THE HOUSE FEED (SUPABASE LIVE FEED) ---
elif st.session_state.view == "house":
    st.markdown("### 🏠 THE HOUSE")
    st.caption("See what's been shared. Anything shared here is visible to other people using the app.")
    st.write("")

    if "liked_posts" not in st.session_state:
        st.session_state.liked_posts = set()

    posts = fetch_house_posts()

    if not posts:
        st.info("The house is quiet right now. Be the first to throw something in!")

    for post in posts:
        post_id = post["id"]
        likes = post.get("likes", 0)
        comments = post.get("comments", [])
        
        st.markdown(f'<div class="house-card">{post["content"]}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            has_liked = post_id in st.session_state.liked_posts
            like_icon = "💖" if has_liked else "❤️"
            
            if st.button(f"{like_icon} {likes}", key=f"like_{post_id}"):
                if has_liked:
                    # Toggle off
                    new_count = max(0, likes - 1)
                    update_post_likes(post_id, new_count)
                    st.session_state.liked_posts.remove(post_id)
                else:
                    # Toggle on
                    new_count = likes + 1
                    update_post_likes(post_id, new_count)
                    st.session_state.liked_posts.add(post_id)
                st.rerun()
        
        with c2:
            if st.button("🚩 Report", key=f"rep_{post_id}"):
                report_house_post(post)
                st.toast("Post reported and hidden.")
                st.rerun()
                
        with st.expander("💬 Give your 2 cents / View responses"):
            for comment in comments:
                st.write(f"• {comment}")
            
            new_comment = st.text_input(
                label="Add response",
                key=f"comm_in_{post_id}",
                placeholder="Give them your 2 cents...",
                label_visibility="collapsed"
            )
            if st.button("Post", key=f"comm_btn_{post_id}"):
                if new_comment.strip():
                    comments.append(new_comment.strip())
                    add_post_comment(post_id, comments)
                    st.rerun()
        st.write("---")

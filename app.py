import streamlit as st
import random
import time

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Truth Circle",
    page_icon="•",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. LOCAL MEMORY STORAGE (IN-MEMORY DB)
# ==========================================
if "draw_notes" not in st.session_state:
    st.session_state.draw_notes = [
        "Sometimes I feel like I'm the friend everyone comes to when they need something, but nobody notices when I'm struggling.",
        "I feel like I'm acting like a different person depending on who I'm with, and I don't know who I actually am.",
        "I'm really worried about the future, but everyone expects me to have it all figured out already.",
        "I find it hard to ask for help when I'm overwhelmed because I don't want to burden anyone."
    ]

if "house_posts" not in st.session_state:
    st.session_state.house_posts = [
        {
            "id": 1,
            "tag": "OPEN QUESTION",
            "prompt": "What's something you wish people understood about you?",
            "response": "That being quiet doesn't mean I'm upset—I just process things internally first.",
            "likes": 2,
            "comments": ["Felt this so deeply.", "Same here."]
        }
    ]

if "liked_posts" not in st.session_state:
    st.session_state.liked_posts = set()

# ==========================================
# 3. CURATED DECK PROMPTS
# ==========================================
QUESTIONS = [
    "What's something you wish people understood about you?",
    "What's something you're proud of that people don't usually notice?",
    "What's something you've changed your mind about recently?",
    "What makes you feel genuinely heard?",
    "What's something you wish you could say without being judged?",
    "What's something you're still learning about yourself?",
    "Who brings out the best version of you?",
    "What's one thing you want to get better at?"
]

FINISH_PROMPTS = [
    "I've never told anyone that...",
    "I wish people knew that...",
    "Something I'm still figuring out is...",
    "I feel most like myself when...",
    "Lately I've been thinking about...",
    "One thing I pretend doesn't bother me is...",
    "Right now, I really need..."
]

ENCOURAGEMENT_MESSAGES = [
    "No pressure. There's always another card.",
    "Passing is 100% fine. Speak up when you feel like it.",
    "No worries at all. Take a breath or peek at what others shared in the House first.",
    "Your voice matters here whenever you feel ready. Take your time."
]

# ==========================================
# 4. RANDOMIZER LOGIC
# ==========================================
def pick_random_card():
    random.seed(time.time_ns())
    category = random.choice(["note", "question", "finish"])

    if category == "note" and st.session_state.draw_notes:
        drawn_text = random.choice(st.session_state.draw_notes)
        return {
            "type": "note",
            "tag": "ANONYMOUS NOTE",
            "text": drawn_text,
            "instruction": "What would you tell them?",
            "placeholder": "Give your perspective...",
            "btn_label": "Share response"
        }
    elif category == "question":
        return {
            "type": "question",
            "tag": "OPEN QUESTION",
            "text": random.choice(QUESTIONS),
            "instruction": "Answer it yourself, or throw it to the House.",
            "placeholder": "What's your answer?",
            "btn_label": "Answer & Share"
        }
    else:
        return {
            "type": "finish",
            "tag": "FINISH THIS",
            "text": random.choice(FINISH_PROMPTS),
            "instruction": "Complete the thought however it speaks to you.",
            "placeholder": "Finish the thought...",
            "btn_label": "Finish & Share"
        }

def add_house_post(tag, prompt_text, response_text):
    new_post = {
        "id": int(time.time() * 1000),
        "tag": tag,
        "prompt": prompt_text,
        "response": response_text,
        "likes": 0,
        "comments": []
    }
    st.session_state.house_posts.insert(0, new_post)

# ==========================================
# 5. GLOBAL DESIGN SYSTEM & CLEAN CSS
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

    #MainMenu, footer, header, 
    div[data-testid="stToolbar"], 
    div[data-testid="stHeader"], 
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    div[data-testid="stViewerBadge"],
    .stDeployButton {
        visibility: hidden !important;
        display: none !important;
    }

    .block-container {
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
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
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
    }

    .draw-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 32px 24px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08);
        word-wrap: break-word;
    }

    .card-note { border: 1px solid #CBD5E1; background: #FFFFFF; }
    .card-question { border: 1px solid #CBD5E1; background: #FFFFFF; }
    .card-finish { border: 1px solid #CBD5E1; background: #FFFFFF; }

    .card-tag {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 16px;
        text-transform: uppercase;
        background: #F1F5F9;
        color: #475569;
    }

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

    .feed-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
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
        border-left: 3px solid #0F172A;
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

    div.stButton > button {
        width: 100% !important;
        min-height: 48px !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        border: 1px solid #E2E8F0 !important;
        background: #FFFFFF !important;
        color: #334155 !important;
    }

    div.stButton > button[kind="primary"] {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 6. SESSION CONTROLLER & NAVIGATION
# ==========================================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "current_card" not in st.session_state:
    st.session_state.current_card = None
if "current_encouragement" not in st.session_state:
    st.session_state.current_encouragement = "No pressure. There's always another card."

st.markdown('''
    <div class="brand-header">
        <div class="brand-title">Truth Circle</div>
        <div class="brand-sub">Say what you mean. You can always pass.</div>
    </div>
''', unsafe_allow_html=True)

st.markdown('<div class="subtle-nav">', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("Draw", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()

with nav_col2:
    if st.button("Note", use_container_width=True):
        st.session_state.view = "write_note"
        st.rerun()

with nav_col3:
    if st.button("House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. SCREEN CONTROLLERS
# ==========================================

# --- SCREEN 1: HOME ---
if st.session_state.view == "home":
    st.markdown('''
        <div class="app-card">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">Ready to draw?</div>
            <div style="font-size: 0.88rem; color: #64748B;">Draw an anonymous note, an open question, or a thought starter.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("Draw a card", use_container_width=True, type="primary"):
        st.session_state.current_card = pick_random_card()
        st.session_state.view = "draw_card"
        st.rerun()

    st.write("")
    if st.button("Write an anonymous note", use_container_width=True):
        st.session_state.view = "write_note"
        st.rerun()

    if st.button("Explore The House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 2: DRAWN CARD EXPERIENCE ---
elif st.session_state.view == "draw_card":
    card = st.session_state.current_card
    c_type = card["type"]

    st.markdown(f'''
        <div class="draw-card card-{c_type}">
            <span class="card-tag">{card["tag"]}</span>
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

    if st.button(card["btn_label"], use_container_width=True, type="primary"):
        if user_input.strip():
            add_house_post(card["tag"], card["text"], user_input.strip())
            st.session_state.view = "shared_confirm"
            st.rerun()
        else:
            st.warning("Write a quick thought before sharing.")

    if st.button("Pass →", use_container_width=True):
        st.session_state.current_encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
        st.session_state.view = "pass_encouragement"
        st.rerun()

# --- SCREEN 3: PASS ENCOURAGEMENT ---
elif st.session_state.view == "pass_encouragement":
    st.markdown(f'''
        <div class="app-card">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">No pressure</div>
            <div style="font-size: 0.9rem; color: #64748B; line-height: 1.4;">{st.session_state.current_encouragement}</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("Draw another card", use_container_width=True, type="primary"):
        st.session_state.current_card = pick_random_card()
        st.session_state.view = "draw_card"
        st.rerun()

    if st.button("Go to The House", use_container_width=True):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 4: SHARED CONFIRMATION ---
elif st.session_state.view == "shared_confirm":
    st.markdown('''
        <div class="app-card">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">Added to The House</div>
            <div style="font-size: 0.9rem; color: #64748B; line-height: 1.4;">Others can now see it and share their perspective.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("View in The House", use_container_width=True, type="primary"):
        st.session_state.view = "house"
        st.rerun()

# --- SCREEN 5: WRITE ANONYMOUS NOTE ---
elif st.session_state.view == "write_note":
    st.markdown("### Write an Anonymous Note")
    note_text = st.text_area(
        label="Note Area",
        placeholder="Type your thought or prompt here...",
        height=140,
        label_visibility="collapsed"
    )

    if st.button("Submit to Circle", use_container_width=True, type="primary"):
        if note_text.strip():
            st.session_state.draw_notes.append(note_text.strip())
            st.session_state.view = "note_submitted_confirm"
            st.rerun()
        else:
            st.warning("Type a thought before submitting.")

# --- SCREEN 6: NOTE SUBMITTED CONFIRMATION ---
elif st.session_state.view == "note_submitted_confirm":
    st.markdown('''
        <div class="app-card">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">Note submitted</div>
            <div style="font-size: 0.9rem; color: #64748B; line-height: 1.4;">Your note is now in rotation for others to draw.</div>
        </div>
    ''', unsafe_allow_html=True)

    if st.button("Back to main menu", use_container_width=True, type="primary"):
        st.session_state.view = "home"
        st.rerun()

# --- SCREEN 7: THE HOUSE FEED ---
elif st.session_state.view == "house":
    st.markdown("### The House")
    st.caption("Public feed of drawn notes and responses.")
    st.write("")

    posts = st.session_state.house_posts

    if not posts:
        st.markdown('<div class="app-card">The House is quiet right now.</div>', unsafe_allow_html=True)
    else:
        for idx, post in enumerate(posts):
            p_id = post["id"]
            prompt_html = f'<div class="feed-prompt-box">&ldquo;{post["prompt"]}&rdquo;</div>' if post["prompt"] else ""
            response_html = f'<div class="feed-response-body">{post["response"]}</div>' if post["response"] else ""

            st.markdown(f'''
                <div class="feed-card">
                    <span class="feed-tag">{post["tag"]}</span>
                    {prompt_html}
                    {response_html}
                </div>
            ''', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                has_liked = p_id in st.session_state.liked_posts
                like_label = f"Saved ({post['likes']})" if has_liked else f"Save ({post['likes']})"
                
                if st.button(like_label, key=f"like_{p_id}_{idx}"):
                    if has_liked:
                        post['likes'] = max(0, post['likes'] - 1)
                        st.session_state.liked_posts.remove(p_id)
                    else:
                        post['likes'] += 1
                        st.session_state.liked_posts.add(p_id)
                    st.rerun()

            with col2:
                if st.button("Remove", key=f"del_{p_id}_{idx}"):
                    st.session_state.house_posts.pop(idx)
                    st.toast("Post removed.")
                    st.rerun()

            with st.expander("Responses"):
                for comment in post["comments"]:
                    st.write(f"• {comment}")

                c_input = st.text_input(
                    label="Comment input",
                    key=f"c_in_{p_id}_{idx}",
                    placeholder="Add a comment...",
                    label_visibility="collapsed"
                )
                if st.button("Post response", key=f"c_btn_{p_id}_{idx}"):
                    if c_input.strip():
                        post["comments"].append(c_input.strip())
                        st.rerun()
            st.write("---")

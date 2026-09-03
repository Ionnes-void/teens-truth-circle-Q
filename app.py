import streamlit as st
import random
import json
import os

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Teens Truth Circle", 
    page_icon="✨", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MODERN STYLING (CSS) ---
st.markdown("""
    <style>
    /* Global background and typography */
    .stApp {
        background-color: #FAF8F5;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #2D3748;
    }
    
    /* Header typography */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    
    .sub-title {
        text-align: center;
        font-size: 1.05rem;
        color: #718096;
        margin-bottom: 30px;
        line-height: 1.5;
        font-weight: 400;
    }
    
    /* Rounded elevated cards */
    .card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        border: 1px solid #EDF2F7;
        margin-bottom: 20px;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Gentle encouragement banner */
    .encouragement-card {
        background: linear-gradient(135deg, #F3E8FF 0%, #E9D5FF 100%);
        color: #5B21B6;
        border-left: 6px solid #8B5CF6;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 25px;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    
    /* Custom button styling overrides */
    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
    }
    
    /* Hide top Streamlit menu bar for clean mobile look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- DATA STORAGE ---
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "notes": [
                "Sometimes I feel like I'm the friend everyone comes to when they need something, but nobody notices when I'm struggling."
            ],
            "house": [],
            "reports": []
        }
        with open(DATA_FILE, "w") as f:
            json.dump(default_data, f)
        return default_data
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# --- PRE-LOADED PROMPTS ---
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
    "Passing is 100% okay! Every voice matters here, including yours, whenever you're ready.",
    "No pressure at all. Sometimes reading other people's thoughts first helps build the spark!",
    "Your story and perspective are valuable. Take your time—the circle isn't going anywhere.",
    "It takes courage to open up. Remember, you can always share completely anonymously!",
    "There are no right or wrong answers here. You're safe to express whatever is on your mind."
]

# --- STATE MANAGEMENT ---
if "view" not in st.session_state:
    st.session_state.view = "home"
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = None
if "last_passed_prompt" not in st.session_state:
    st.session_state.last_passed_prompt = None

def pick_random_prompt():
    choice = random.choice(["note", "question", "finish"])
    if choice == "note" and data["notes"]:
        prompt_text = random.choice(data["notes"])
        return {"category": "ANONYMOUS NOTE 📝", "text": prompt_text}
    elif choice == "question":
        return {"category": "OPEN QUESTION 🎯", "text": random.choice(QUESTIONS)}
    else:
        return {"category": "FINISH THIS... ✨", "text": random.choice(FINISH_PROMPTS)}

# --- HEADER ---
st.markdown('<div class="main-title">TRUTH CIRCLE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Come as you are.<br>Say what you mean.<br><i>You can always pass.</i></div>', unsafe_allow_html=True)

# --- NAVIGATION CONTROLS ---
if st.session_state.view not in ["home", "pass_encouragement"]:
    if st.button("⬅️ Back to Home"):
        st.session_state.view = "home"
        st.session_state.current_prompt = None
        st.rerun()

# --- HOME SCREEN ---
if st.session_state.view == "home":
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("🎲 PICK SOMETHING", use_container_width=True, type="primary"):
            st.session_state.current_prompt = pick_random_prompt()
            st.session_state.view = "prompt"
            st.rerun()

        st.write("")
        if st.button("📝 Leave an anonymous note", use_container_width=True):
            st.session_state.view = "leave_note"
            st.rerun()

        if st.button("🏠 See what the house is saying", use_container_width=True):
            st.session_state.view = "house"
            st.rerun()

# --- PROMPT DISPLAY SCREEN ---
elif st.session_state.view == "prompt":
    prompt = st.session_state.current_prompt
    st.markdown(f"### {prompt['category']}")
    st.markdown(f'<div class="card"><b>"{prompt["text"]}"</b></div>', unsafe_allow_html=True)

    user_response = st.text_area("Your response / advice (Optional):", key="prompt_response", placeholder="Write what's on your mind...")

    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("💬 Share Response", use_container_width=True):
            if user_response.strip():
                post_text = f"**Prompt:** {prompt['text']}\n\n**Response:** {user_response}"
                data["house"].append({"id": len(data["house"]), "content": post_text, "likes": 0, "comments": []})
                save_data(data)
                st.success("Shared!")
                st.session_state.view = "home"
                st.rerun()
            else:
                st.warning("Please type something before sharing.")

    with col_b:
        if st.button("🏠 Throw to House", use_container_width=True):
            post_text = f"**Shared Prompt:** {prompt['text']}" + (f"\n\n**Note:** {user_response}" if user_response.strip() else "")
            data["house"].append({"id": len(data["house"]), "content": post_text, "likes": 0, "comments": []})
            save_data(data)
            st.success("Thrown to the house!")
            st.session_state.view = "home"
            st.rerun()

    with col_c:
        if st.button("➡️ PASS", use_container_width=True):
            st.session_state.last_passed_prompt = st.session_state.current_prompt
            st.session_state.view = "pass_encouragement"
            st.rerun()

# --- ENCOURAGEMENT SCREEN (ON PASS) ---
elif st.session_state.view == "pass_encouragement":
    st.markdown("### 🌿 Take Your Time")
    
    encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
    st.markdown(
        f'<div class="encouragement-card">💛 <b>Remember:</b> {encouragement}</div>', 
        unsafe_allow_html=True
    )
    
    st.write("What would you like to do next?")
    
    if st.button("🎲 Try a Different Question", use_container_width=True, type="primary"):
        st.session_state.current_prompt = pick_random_prompt()
        st.session_state.view = "prompt"
        st.rerun()

    if st.session_state.last_passed_prompt:
        passed_text = st.session_state.last_passed_prompt['text']
        if st.button(f"↩️ Return to previous question (\"...{passed_text[:25]}...\")", use_container_width=True):
            st.session_state.current_prompt = st.session_state.last_passed_prompt
            st.session_state.view = "prompt"
            st.rerun()

    if st.button("🏠 Go Back to Home", use_container_width=True):
        st.session_state.view = "home"
        st.session_state.current_prompt = None
        st.rerun()

# --- LEAVE ANONYMOUS NOTE SCREEN ---
elif st.session_state.view == "leave_note":
    st.markdown("### 📝 Leave an Anonymous Note")
    st.caption("🔒 *Keep names and identifying details out of your note.*")
    
    note_text = st.text_area("What's on your mind?", height=120, placeholder="Share a thought, situation, or question...")
    
    if st.button("Submit Note", type="primary", use_container_width=True):
        if note_text.strip():
            data["notes"].append(note_text)
            save_data(data)
            st.success("Your note has been placed into the circle.")
            st.session_state.view = "home"
            st.rerun()
        else:
            st.warning("Please write something first.")

# --- THE HOUSE SCREEN ---
elif st.session_state.view == "house":
    st.markdown("### 🏠 The House Feed")
    
    if not data["house"]:
        st.info("The house is quiet right now. Be the first to throw something in!")
    
    for idx, post in enumerate(reversed(data["house"])):
        real_idx = len(data["house"]) - 1 - idx
        
        st.markdown(f'<div class="card">{post["content"]}</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button(f"❤️ {post.get('likes', 0)}", key=f"like_{real_idx}"):
                data["house"][real_idx]["likes"] = post.get("likes", 0) + 1
                save_data(data)
                st.rerun()
        
        with c3:
            if st.button("🚩 Report", key=f"rep_{real_idx}"):
                reported_item = data["house"].pop(real_idx)
                data["reports"].append(reported_item)
                save_data(data)
                st.success("Post reported and hidden.")
                st.rerun()
                
        with st.expander("💬 Give your 2 cents / View responses"):
            for comment in post.get("comments", []):
                st.write(f"• {comment}")
            
            new_comment = st.text_input("Add your 2 cents:", key=f"comm_in_{real_idx}", placeholder="Write a supportive comment...")
            if st.button("Post", key=f"comm_btn_{real_idx}"):
                if new_comment.strip():
                    if "comments" not in data["house"][real_idx]:
                        data["house"][real_idx]["comments"] = []
                    data["house"][real_idx]["comments"].append(new_comment)
                    save_data(data)
                    st.rerun()
        st.write("---")

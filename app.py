import streamlit as st
import random
import time

# Set up the page config
st.set_page_config(page_title="Memory Match Game", page_icon="🧠", layout="centered")
st.title("🧠 Memory Matching Game")
st.write("Find all the matching pairs! Click two cards to flip them.")
# Custom CSS for a beautiful, modern game look
st.markdown("""
<style>
    /* Change the main app background to a dark, sleek arcade theme */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #111119 100%);
        color: #ffffff;
    }
    
    /* Style the main title */
    h1 {
        font-family: 'Courier New', Courier, monospace;
        color: #00ffcc !important;
        text-shadow: 0px 0px 10px rgba(0, 255, 204, 0.6);
        text-align: center;
    }
    
    /* Target Streamlit buttons to turn them into game cards */
    div.stButton > button {
        background-color: #f2dd8f;
        color: #ffffff !important;
        border: 2px solid #444466;
        border-radius: 12px;
        height: 80px;
        font-size: 2rem !important; /* Make emojis big */
        transition: all 0.2s ease-in-out;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
    }
    
    /* Hover effect for unselected cards */
    div.stButton > button:hover:not(:disabled) {
        border-color: #00ffcc;
        background-color: #333352;
        transform: translateY(-3px);
        box-shadow: 0px 8px 15px rgba(0, 255, 204, 0.3);
    }
    
    /* Style disabled buttons (Matched or active cards) */
    div.stButton > button:disabled {
        background-color: #1a3a3a !important;
        border-color: #00ffcc !important;
        color: #ffffff !important;
        opacity: 1 !important; /* Prevents Streamlit's default washed-out look */
    }

    /* Style the metric/score counter */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        color: #ff007f !important;
        font-weight: bold;
        text-shadow: 0px 0px 8px rgba(255, 0, 127, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #aaaaaa !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Initialize Constants
EMOJIS = ["👾", "🕹️", "🚀", "🤖", "💿", "🔋", "📟", "🌌"]
BOARD_SIZE = len(EMOJIS) * 2  # 16 cards total (4x4 grid)

# 2. Initialize Session State Variables
if "board" not in st.session_state:
    # Duplicate emojis to make pairs and shuffle them
    cards = EMOJIS * 2
    random.shuffle(cards)
    st.session_state.board = cards
    
    # Track game states
    st.session_state.flipped = []      # Indices of currently flipped cards (max 2)
    st.session_state.matched = set()    # Indices of successfully matched cards
    st.session_state.moves = 0         # Move counter

# Reset Game Function
def reset_game():
    cards = EMOJIS * 2
    random.shuffle(cards)
    st.session_state.board = cards
    st.session_state.flipped = []
    st.session_state.matched = set()
    st.session_state.moves = 0

# 3. Game Logic for Card Selection
def handle_card_click(idx):
    # Prevent clicking already matched cards or the same card twice
    if idx in st.session_state.matched or idx in st.session_state.flipped:
        return
        
    # If two cards are already flipped from a previous mismatch, clear them first
    if len(st.session_state.flipped) == 2:
        st.session_state.flipped = []

    # Flip the clicked card
    st.session_state.flipped.append(idx)

    # Check if we just flipped the second card
    if len(st.session_state.flipped) == 2:
        st.session_state.moves += 1
        idx1, idx2 = st.session_state.flipped
        
        # Check for a match
        if st.session_state.board[idx1] == st.session_state.board[idx2]:
            st.session_state.matched.add(idx1)
            st.session_state.matched.add(idx2)
            st.session_state.flipped = [] # Clear flip state immediately on match

# 4. Render the Stats
col_score, col_reset = st.columns([3, 1])
with col_score:
    st.metric(label="Moves Made", value=st.session_state.moves)
with col_reset:
    st.button("Reset Game", on_click=reset_game, use_container_width=True)

st.write("---")

# 5. Render the 4x4 Grid
grid_cols = 4
for row in range(4):
    cols = st.columns(grid_cols)
    for col in range(grid_cols):
        idx = row * grid_cols + col
        
        # Determine what to display on the button
        if idx in st.session_state.matched:
            # Matched cards stay visible but disabled
            button_label = st.session_state.board[idx]
            is_disabled = True
        elif idx in st.session_state.flipped:
            # Currently flipped cards show their content
            button_label = st.session_state.board[idx]
            is_disabled = False
        else:
            # Face down cards
            button_label = "❓"
            is_disabled = False

        # Render the card button
        with cols[col]:
            st.button(
                button_label, 
                key=f"card_{idx}", 
                disabled=is_disabled, 
                on_click=handle_card_click, 
                args=(idx,),
                use_container_width=True
            )

# 6. Win Condition Check
if len(st.session_state.matched) == BOARD_SIZE:
    st.balloons()
    st.success(f"🎉 Congratulations! You won the game in {st.session_state.moves} moves!")

# 7. Auto-reset handling for mismatched pairs on next interaction
# If 2 cards are flipped and they don't match, we force a slight pause so the player sees them, 
# then rerun to turn them back face down.
if len(st.session_state.flipped) == 2:
    idx1, idx2 = st.session_state.flipped
    if st.session_state.board[idx1] != st.session_state.board[idx2]:
        time.sleep(1.0) # Let the user see the wrong choice for 1 second
        st.session_state.flipped = []
        st.rerun()

import streamlit as st
import chess
import chess.svg
import requests

# 1. Page Configuration
st.set_page_config(page_title="Ultimate Chess Academy", layout="centered")
st.title("♟️ Streamlit Chess Suite Pro")

# 2. Reference Maps & Difficulty Configurations
AI_LEVELS = {
    "Level 1: Strong Beginner (Elo 1000)": {"depth": 1, "bot_elo": 1000},
    "Level 2: Casual Player (Elo 1300)": {"depth": 4, "bot_elo": 1300},
    "Level 3: Intermediate (Elo 1600)": {"depth": 10, "bot_elo": 1600},
    "Level 4: Advanced (Elo 1900)": {"depth": 15, "bot_elo": 1900},
    "Level 5: Master Engine (Elo 2200)": {"depth": 18, "bot_elo": 2200},
    "Level 6: Grandmaster Bot (Elo 2500+)": {"depth": 22, "bot_elo": 2500}
}

PUZZLE_DIFFICULTIES = {
    "Beginner (Elo 800-1100)": 0, 
    "Casual Player (Elo 1200-1400)": 1,
    "Intermediate (Elo 1500-1700)": 2, 
    "Advanced (Elo 1800-2000)": 3,
    "Master (Elo 2100-2300)": 4, 
    "Grandmaster (Elo 2400-2600+)": 5
}

PUZZLE_DATA = {
    0: {"fen": "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4", "solution": "h5f7", "prompt": "White to move: Find the 1-move checkmate!", "hint": "Look at the weak f7 square protected only by the King."},
    1: {"fen": "rnbqkbnr/ppp2ppp/4p3/3p4/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 3", "solution": "c4d5", "prompt": "White to move: Find the best hanging piece capture.", "hint": "The black pawn on d5 is attacked twice but only defended once."},
    2: {"fen": "r1k4r/ppp1bqpp/2np1n2/4p1N1/4P3/2NP4/PPP2PPP/R1B1K2R w KQ - 0 10", "solution": "g5f7", "prompt": "White to move: Locate the hidden tactical fork opportunity.", "hint": "Look at the undefended black queen and f7 square setup."},
    3: {"fen": "q4rk1/5ppp/r7/1p2P3/1p6/1P4P1/P1R2P1P/3Q1RK1 b - - 0 22", "solution": "a6a2", "prompt": "Black to move: Punish White's loose queenside pawn defense structure.", "hint": "Target the a2 pawn directly using your rook."},
    4: {"fen": "r2q1rk1/pb1nbppp/1p2p3/2ppP3/3P4/2PBPN2/PP4PP/R1BQ1RK1 b - - 0 11", "solution": "f7f6", "prompt": "Black to move: Execute a precise, high-level counter-strike to shatter White's center space.", "hint": "Undermine White's central e5 e-pawn anchor point."},
    5: {"fen": "3r2k1/p4p1p/1pbr1qp1/nB2p3/Q3P3/P1R2P2/1P1NK1PP/2R5 b - - 5 24", "solution": "d6d2", "prompt": "Black to move: Unleash a deep Grandmaster calculation sequence starting with an aggressive temporary piece sacrifice.", "hint": "Sacrifice your rook down on the open d2 lane to break the defenses."
}
OPENINGS = {
    "Ruy Lopez (Spanish Opening)": ["e2e4", "e7e5", "g1f3", "b1c6", "b1c3", "f8b5"],
    "Sicilian Defense": ["e2e4", "c7c5"],
    "French Defense": ["e2e4", "e7e3"],
    "Queen's Gambit Accepted": ["d2d4", "d7d5", "c2c4", "d5c4"],
    "Caro-Kann Defense": ["e2e4", "c7c6"]
}

MIDDLEGAME_THEMES = {
    "Isolated Queen Pawn (IQP) Strategy": {
        "fen": "r1b2rk1/pp1nbppp/2n1p3/3pP3/3P4/1PNB1N2/P4PPP/R1BQ1RK1 w - - 1 11",
        "prompt": "White to move. You have an Isolated Queen Pawn on d4. Target a kingside space attack framework.",
        "best_move": "f3g5",
        "explanation": "Moving the knight to g5 sets up high-level attack patterns pointing directly at the black king's short-castle structure."
    },
    "Minority Pawn Attack Initiative": {
        "fen": "2rr2k1/pp1qbppp/2n1pn2/1N1p4/3P4/P3PN2/1P1B1PPP/2RQ1RK1 w - - 5 13",
        "prompt": "White to move. Launch a minority pawn storm on the Queenside to force entry lines.",
        "best_move": "b2b4",
        "explanation": "b4 drives the expansion layout on the queenside, preparing to create weaknesses in Black's pawn chain."
    }
}

ENDGAME_THEMES = {
    "King & Rook vs Lone King (Basic Mate)": {
        "fen": "4k3/8/4K3/8/8/8/8/5R2 w - - 0 1",
        "prompt": "White to move: Cut off the enemy King to lock in the absolute 1-move checkmate configuration.",
        "best_move": "f1f2",
        "explanation": "f1f2 is a critical waiting move or limitation cut that restricts the enemy king, forcing an immediate back-rank mate line."
    },
    "Pawn Promotion Race Navigation": {
        "fen": "k7/P7/1K6/8/8/8/8/8 w - - 0 1",
        "prompt": "White to move: Maintain positional balance to secure a clean promotion sequence without causing a stalemate.",
        "best_move": "b6a6",
        "explanation": "Moving the King to a6 locks your structural advantage without boxing out the king illegally, preserving the win."
    }
}

THEME_COLORS = {
    "Classic Light / Blue": {"light": "#f0d9b5", "dark": "#b58863"},
    "Emerald Forest / Green": {"light": "#eeeeee", "dark": "#769656"},
    "Dark Mode Charcoal": {"light": "#e2e4e6", "dark": "#3b3b3b"},
    "Luxury Premium Wood": {"light": "#f0d9b5", "dark": "#8b5a2b"}
}

# 3. Persistent Rating Storage
if "player_rating" not in st.session_state:
    if "saved_rating" in st.query_params:
        st.session_state.player_rating = int(st.query_params["saved_rating"])
    else:
        st.session_state.player_rating = 1200

def save_rating_permanently(new_rating):
    st.session_state.player_rating = new_rating
    st.query_params["saved_rating"] = str(new_rating)

# Navigation Layout Configuration
tab_game, tab_analysis, tab_puzzles, tab_openings, tab_middle, tab_endgame = st.tabs([
    "🎮 Match", "🔬 Analysis", "🧩 Puzzles", "📖 Openings", "⚔️ Middlegame", "👑 Endgame"
])

# Initialize Base States
if "board" not in st.session_state: st.session_state.board = chess.Board()
if "move_feedback" not in st.session_state: st.session_state.move_feedback = ""
if "player_color" not in st.session_state: st.session_state.player_color = "White"
if "game_resolved" not in st.session_state: st.session_state.game_resolved = False

board = st.session_state.board
# Sidebar Settings
with st.sidebar:
    st.header("🎨 Visual Theme")
    theme_choice = st.selectbox("Select Board Design:", list(THEME_COLORS.keys()), index=0)
    selected_theme = THEME_COLORS[theme_choice]
    
    st.header("⚙️ Match Options")
    chosen_color = st.selectbox("Play As:", ["White", "Black"])
    if chosen_color != st.session_state.player_color:
        st.session_state.player_color = chosen_color
        st.session_state.board = chess.Board()
        st.rerun()

    selected_level_name = st.selectbox("Select AI Strength:", list(AI_LEVELS.keys()))
    ai_config = AI_LEVELS[selected_level_name]
    st.write("---")
    st.metric(label="Your Saved Rating", value=f"⭐ {st.session_state.player_rating}")
    if st.button("Reset Game Board", type="primary"):
        st.session_state.board = chess.Board()
        st.session_state.game_resolved = False
        st.rerun()

def render_themed_board(b, size=380, flip=False):
    return chess.svg.board(
        board=b, size=size, flipped=flip,
        colors={"square light": selected_theme["light"], "square dark": selected_theme["dark"]},
        lastmove=b.peek() if b.move_stack else None, check=b.king(b.turn) if b.is_check() else None
    )

def display_sensory_feedback(b):
    """Generates visual banner alerts mimicking sensory game events."""
    if b.is_game_over():
        if b.is_checkmate():
            st.error("💥 *BOOM! CHECKMATE! GAME OVER!* 💥")
        else:
            st.warning("🤝 *TAP TAP. DRAW AGREED.* 🤝")
    elif b.is_check():
        st.error("🚨 *⚠️ WATCH OUT! CHECK! ⚠️* 🚨")
    elif b.move_stack:
        last_move = b.peek()
        if b.is_capture(last_move):
            st.success("⚔️ *CRASH! PIECE CAPTURED!* ⚔️")
        else:
            st.info("🪵 *Thud. Move Played.* 🪵")

# =========================================================================
# TAB 1 & 2 & 3: MATCH, ANALYSIS, AND PUZZLES
# =========================================================================
with tab_game:
    ai_should_play = ((st.session_state.player_color == "White" and board.turn == chess.BLACK) or (st.session_state.player_color == "Black" and board.turn == chess.WHITE))
    if ai_should_play and not board.is_game_over():
        with st.spinner("AI calculating..."):
            res = requests.get(f"https://stockfish.online{board.fen()}&depth={ai_config['depth']}", timeout=12).json()
            if res.get("success"): board.push(chess.Move.from_uci(res["bestmove"].split()))
            st.rerun()
            
    st.subheader("Your Move")
    col1, col2 = st.columns()
    with col1:
        move_input = st.text_input("UCI Format:", key="match_input", placeholder="e2e4", disabled=ai_should_play or board.is_game_over())
    with col2:
        if st.button("Play", use_container_width=True, disabled=ai_should_play or board.is_game_over()) and move_input:
            try:
                move = chess.Move.from_uci(move_input.strip().lower())
                if move in board.legal_moves:
                    board.push(move)
                    st.rerun()
                else: st.error("❌ Illegal Move!")
            except ValueError: st.error("⚠️ Formatting Error.")

    display_sensory_feedback(board)
    st.image(render_themed_board(board, flip=(st.session_state.player_color == "Black")), use_container_width=True)

with tab_analysis:
    st.subheader("🔬 Deep Move Analysis")
    if st.button("Analyze Current Board State"):
        res = requests.get(f"https://stockfish.online{board.fen()}&depth=15").json()
        if res.get("success"): st.info(f"**Best Move Line:** `{res.get('bestmove')}` (Eval Score: {res.get('evaluation')})")

with tab_puzzles:
    st.subheader("🧩 Scaled Tactics Challenge")
    p_tier = st.selectbox("Choose Puzzle Difficulty:", list(PUZZLE_DIFFICULTIES.keys()))
    curr_p = PUZZLE_DATA[PUZZLE_DIFFICULTIES[p_tier]]
    
    col_hz1, col_hz2 = st.columns()
    with col_hz1:
        p_input = st.text_input("Enter Puzzle Solution (UCI):", key="p_in_field")
    with col_hz2:
        st.write("")
        st.write("")
        show_hint = st.button("💡 Hint", key="p_hint_btn")
    
    if show_hint:
        st.info(f"💡 **Hint:** {curr_p['hint']}")
        
    if st.button("Verify Puzzle Move"):
        if p_input.strip().lower() == curr_p["solution"]: st.success("🎉 Correct solution!")
        else: st.error("❌ Incorrect move layout.")
    
    flip_puzzle = st.checkbox("Flip Perspective (View as Black)", key="flip_p")
    st.image(render_themed_board(chess.Board(curr_p["fen"]), size=350, flip=flip_puzzle), use_container_width=True)
# =========================================================================
# TAB 4: OPENING BOOK TRAINING
# =========================================================================
with tab_openings:
    st.subheader("📖 Opening Book Guide")
    op_choice = st.selectbox("Select Chess Opening Theory:", list(OPENINGS.keys()))
    op_board = chess.Board()
    for m in OPENINGS[op_choice]:
        try: op_board.push_san(m)
        except Exception: op_board.push_uci(m)
    
    flip_opening = st.checkbox("Flip Perspective (View as Black)", key="flip_op")
    st.image(render_themed_board(op_board, size=350, flip=flip_opening), use_container_width=True)


# =========================================================================
# TAB 5: MIDDLEGAME STRATEGY TRAINER
# =========================================================================
with tab_middle:
    st.subheader("⚔️ Middlegame Strategy Lab")
    mid_choice = st.selectbox("Select Positional Middlegame Setup:", list(MIDDLEGAME_THEMES.keys()))
    mid_data = MIDDLEGAME_THEMES[mid_choice]
    
    st.info(f"📋 **Strategic Objective:** {mid_data['prompt']}")
    mid_input = st.text_input("Propose the ideal strategic path move (UCI):", key="mid_move_input", placeholder="e.g. f3g5")
    
    if st.button("Evaluate Tactical Plan", key="mid_btn"):
        if mid_input.strip().lower() == mid_data["best_move"]:
            st.success(f"🏆 Strategic Match! {mid_data['explanation']}")
        else:
            st.error("❌ Alternative preferred. Review structural pressure elements again!")
            
    flip_mid = st.checkbox("Flip Perspective (View as Black)", key="flip_mid")
    st.image(render_themed_board(chess.Board(mid_data["fen"]), size=350, flip=flip_mid), use_container_width=True)


# =========================================================================
# TAB 6: ENDGAME TECHNIQUE MASTERY
# =========================================================================
with tab_endgame:
    st.subheader("👑 Endgame Technical Mastery")
    end_choice = st.selectbox("Select Technical Endgame Scenario:", list(ENDGAME_THEMES.keys()))
    end_data = ENDGAME_THEMES[end_choice]
    
    st.warning(f"🎯 **Technical Target:** {end_data['prompt']}")
    end_input = st.text_input("Enter precise conversion move (UCI):", key="end_move_input", placeholder="e.g. f1f2")
    
    if st.button("Check Conversion Accuracy", key="end_btn"):
        if end_input.strip().lower() == end_data["best_move"]:
            st.success(f"🎉 Technically Perfect! {end_data['explanation']}")
        else:
            st.error("❌ Suboptimal Track! That path risks allowing a draw or counterplay.")
            
    flip_end = st.checkbox("Flip Perspective (View as Black)", key="flip_end")
    st.image(render_themed_board(chess.Board(end_data["fen"]), size=350, flip=flip_end), use_container_width=True)
        

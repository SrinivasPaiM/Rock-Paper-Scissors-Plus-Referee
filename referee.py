import google.generativeai as genai
import json
import time
from typing import Literal
from dataclasses import dataclass, asdict
from google.api_core import exceptions

# --- Configuration ---
genai.configure(api_key="YOUR_GOOGLE_API_KEY")

@dataclass
class GameState:
    round_number: int = 1
    user_score: int = 0
    bot_score: int = 0
    user_bomb_used: bool = False
    bot_bomb_used: bool = False
    game_over: bool = False

state = GameState()

def resolve_turn(user_move: str, bot_move: str) -> str:
    global state
    if state.game_over:
        return json.dumps({"error": "Game is already over.", "state": asdict(state)})

    valid_basics = ["rock", "paper", "scissors"]
    user_move = user_move.lower().strip()
    
    is_valid = True
    if user_move == "bomb":
        if state.user_bomb_used:
            is_valid = False 
        else:
            state.user_bomb_used = True
    elif user_move not in valid_basics:
        is_valid = False

    if not is_valid:
        state.bot_score += 1
        result_msg = "Winner: Bot."
    else:
        win_map = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if user_move == bot_move:
            outcome = "draw"
        elif user_move == "bomb":
            outcome = "user"
        elif bot_move == "bomb":
            outcome = "bot"
        elif win_map.get(user_move) == bot_move:
            outcome = "user"
        else:
            outcome = "bot"

        if outcome == "user":
            state.user_score += 1
            result_msg = "Winner: User."
        elif outcome == "bot":
            state.bot_score += 1
            result_msg = "Winner: Bot."
        else:
            result_msg = "Winner: Draw."

    summary = {
        "round": state.round_number,
        "user_move": user_move,
        "bot_move": bot_move,
        "result": result_msg
    }

    if state.user_score >= 2 or state.bot_score >= 2 or state.round_number >= 3:
        state.game_over = True
    else:
        state.round_number += 1
        
    return json.dumps({"summary": summary, "state": asdict(state)})

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=[resolve_turn],
    system_instruction=(
        "You are an impartial Rock-Paper-Scissors-Plus Referee. \n"
        "For EVERY turn, you MUST explicitly indicate:\n"
        "1. Round number\n"
        "2. Moves played (User vs Bot)\n"
        "3. Round winner\n"
        "Always call 'resolve_turn' to process moves. If 'game_over' is true, announce final result."
    )
)

chat = model.start_chat(enable_automatic_function_calling=True)

def safe_send(message):
    while True:
        try:
            return chat.send_message(message)
        except exceptions.ResourceExhausted:
            print("\n[System: Quota exceeded. Pausing 10s to reset...]")
            time.sleep(10)
        except Exception as e:
            print(f"\n[System: Unexpected error: {e}]")
            return None

def play():
    print("=== Rock-Paper-Scissors-Plus Referee Bot ===")
    print("Rules: 1. Best of 3 rounds. 2. Moves: rock, paper, scissors, bomb.")
    print("3. Bomb beats all but used ONCE. 4. Invalid input loses round.")
    print("-" * 45)

    response = safe_send("I am ready for Round 1. Ask for my move.")
    if response: print(f"\nBot: {response.text}")

    while not state.game_over:
        user_input = input("You: ")
        if not user_input: continue
        
        response = safe_send(user_input)
        if response: print(f"\nBot: {response.text}")
        
        if state.game_over:
            break
    
    print("\n--- Final Result ---")
    print(f"Total Score -> You: {state.user_score} | Bot: {state.bot_score}")
    if state.user_score > state.bot_score:
        print("RESULT: User wins")
    elif state.bot_score > state.user_score:
        print("RESULT: Bot wins")
    else:
        print("RESULT: Draw")

if __name__ == "__main__":
    play()

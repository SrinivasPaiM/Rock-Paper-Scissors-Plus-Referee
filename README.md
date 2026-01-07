# Rock-Paper-Scissors-Plus Referee: Project Documentation

This project implements a minimal AI Game Referee chatbot using the Google Generative AI SDK (ADK). The agent facilitates a "Best of 3" Rock-Paper-Scissors-Plus game between a user and a bot, enforcing custom rules, tracking game state, and generating consistent responses to user input.

---

## 1. State Model

The game state is managed using a Python `GameState` dataclass.

### Reasoning

To ensure logical correctness and prevent LLM hallucinations, the source of truth for all critical data—such as scores, round count, and bomb usage—is stored in a structured Python object rather than relying on the language model’s conversational history.

### Persistence

This design ensures that game state persists reliably across turns and that rules, including the one-bomb-per-game constraint, are strictly and deterministically enforced.

---

## 2. Agent and Tool Design

The system architecture follows a clear separation of concerns to maintain clean boundaries between reasoning, logic, and presentation.

### Intent Understanding (LLM)

The Gemini language model interprets natural language user input and extracts the intended move without making any game decisions.

### Game Logic (Tool)

An explicit tool, `resolve_turn`, is defined to act as the referee. This tool validates moves, applies the win/loss matrix, enforces special rules, mutates the game state, and determines round and game outcomes.

### Response Generation (LLM)

The agent receives structured JSON output from the tool and generates the final conversational response. This ensures that all user-facing feedback is derived directly from the authoritative game state.

---

## 3. Tradeoffs and Decisions

### Rule Explanation

To comply with the requirement that rules be explained in five lines or fewer and to optimize API quota usage, the rules are hard-coded in the Python script. This guarantees compliance and reduces token consumption at the cost of flexibility in rule presentation.

### Quota Management

A `safe_send` wrapper with exponential backoff is implemented to handle HTTP 429 rate limit errors gracefully.

### Early Termination

The game implements early termination logic. In a best-of-three format, the game ends immediately when a player reaches two wins. This approach was chosen over forcing all three rounds to complete in order to provide a more intuitive user experience while maintaining logical correctness.

---

## 4. Improvements with More Time

### Session Persistence

Replacing the global in-memory dataclass with a lightweight database would allow the system to support multiple concurrent games and resume sessions after crashes.

### Advanced Bot Strategy

Instead of relying on random move selection, a dedicated strategist tool could be introduced to enable adaptive and competitive bot behavior based on user patterns and historical move data.

### Dynamic Feedback

Introducing a stricter structured output schema, such as one enforced with Pydantic, would further strengthen the boundary between the game logic tool and the response generation layer.

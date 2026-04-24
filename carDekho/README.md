# CarDekho AI Advisor

> **Note for reviewers:** Every API call has a deliberate 10-second delay due to Gemini free-tier rate limits — responses will feel slow, this is expected. Also, the first ~20 minutes of the demo recording was lost due to a system crash.

A conversational car research tool that takes a buyer from "I don't know what to buy" to a confident shortlist — entirely through natural language.

---
## Prompt
```
Problem Statement:
A car research platform has a dataset of cars — makes, models, variants, prices, specs,
mileage etc. Buyers come to the platform confused: there are
too many options and no easy way to figure out which car is right for them.
Build something that helps a car buyer go from “I don’t know what to buy” to “I’m confident
about my shortlist.”
That’s the entire brief. It’s deliberately vague. What you choose to build, what you cut, and
how you scope it — that’s the test.

Solution i taught of:
building a webapp with text to sql ai agent chatbox where user can ask ai what he want in natural language.

tech stack:
frontend: react, react query, tailwind
backend: fastapi, langchain react agents
db: sqllite db with only one table


User flow:
The ui should begin with a full screen chatbot, where user asks ai what he is looking for, once the user press enter, the chatbox should ask question if necessary and once it has all the clarity it should display car details, when displaying car details the full screen chat box should be minimized into circular button on the top right and the car details should be displayed in full screen. the user can talk to ai bot whenever he wants if he has anything to say

Backend:
use langchain react agent to acheive this, create necessary tools like get db schema, execute sql etc. the goal of the agent is to understand what the user really needs and then check the dataset and give the user expected results.

Persona of the agent: i want the agent to be an expert in indian used cars and indian car sales.

there will be only one table in sqlite

techinal:
i want two folders, one for frontend and one for backend. Write clean, extensible code.
```

## What did I build, and why?

The brief was deliberately open-ended: help a confused buyer find a car. I could have built filters, comparison tables, or a recommendation quiz. I built a chatbot instead.

The reason is simple: filters require the buyer to already know what they want. A chatbot meets them where they are. Someone who types "I want a reliable car for my family, not too expensive" should get results — not a blank filter panel.

The UI reflects this: the chat is full-screen at first. Once the agent finds matching cars, it steps aside (collapses to a floating button) and the results take over. The buyer can always pull the chat back to refine.

The agent persona — Arjun, an Indian used car expert — is intentional. The CarDekho dataset is India-specific (prices in rupees, brands like Maruti and Tata dominate). Generic LLM responses wouldn't know that "5 lakhs" means ₹5,00,000, or that mileage and resale value matter more to Indian buyers than 0-60 times.

### What I deliberately cut

- **User accounts / saved searches** — adds auth complexity with no demo value
- **Filter UI** — the whole point is that the chat replaces it
- **Car images** — the dataset doesn't have them; placeholders would look worse than nothing
- **Compare feature** — useful, but a second feature risks the first one being half-done
- **Persistent sessions** — conversations live in memory; a server restart wipes them. Fine for a prototype
- **Pagination** — agent returns up to 20 cars, which is already more than most buyers evaluate
- **Streaming responses** — would improve perceived speed significantly but added complexity

---

## Tech stack and why

| Layer | Choice | Reason |
|---|---|---|
| Frontend | React + Tailwind + React Query | I've shipped production React. Tailwind is fast for custom UI without fighting a component library. React Query handles loading/error state cleanly. |
| Backend | FastAPI | I know Python well — also use Django at work. FastAPI is lighter and async-native, which matters for LLM calls that can take 30+ seconds. |
| Agent | LangChain + Gemini | LangChain's tool-calling abstraction meant I could define `query_cars` as a function and let the model decide when and how to call it. Gemini Flash is free-tier accessible. |
| Database | SQLite | One table, 15k rows, read-only. SQLite needs zero infrastructure. The agent generates SQL directly — no ORM needed. |

The frontend/backend split is intentional even for a prototype. It keeps concerns clean and means I can swap the model or the DB without touching the UI.

---

## What I delegated to AI vs. did manually

**Delegated to AI (Claude Code):**
- All boilerplate scaffolding — FastAPI app structure, React component skeletons, Tailwind config, package.json
- The LangChain agent wiring — tool definitions, the ReAct loop, message history management
- Debugging from logs — pasting error traces and getting targeted fixes
- The `.gitignore`, requirements files, and other setup files

**Done manually / with heavy direction:**
- The core product decision: chatbot-first, not filter-first
- UI state design — the transition from chat mode to results mode, when the float chat opens/closes
- Debugging the Gemini quota issue

**Where AI tools helped most:**
Getting a working full-stack skeleton in one session instead of half a day. The LangChain agent loop, the tool calling pattern, and the FastAPI/React wiring are all things I know how to build but would have taken hours to type out. Having it generated meant I could focus on the parts that actually required judgment.

**Where they got in the way:**
- Model naming: I asked for "Gemini Flash 3" and the tool guessed `gemini-2.0-flash`, which has a free-tier quota of zero. Took a full error cycle to discover the actual model ID (`gemini-3-flash-preview`) from the logs.
- The AI didn't add logging, I had to tell it add logs for observability.
- The Gemini response format issue (`response.content` being a list instead of a string) was caught only at runtime — the tool couldn't predict model-specific response shapes.

---

## If I had another 4 hours

**Streaming responses** — the biggest UX gap right now. A 30-second wait with a spinner is rough. Token streaming would make the agent feel alive.

**Bake schema into the system prompt** — currently `get_schema` is a tool the agent calls, costing an extra API round-trip. Pre-loading it into the system prompt halves the calls per turn.

**Smarter results updates** — right now asking a follow-up replaces all results. Better behaviour: if the user says "only show automatics", filter the existing set rather than running a fresh query.

**Car card depth** — a "Why Arjun recommends this" line per card, generated by the agent alongside the SQL results. The data is there; it just needs surfacing.

**Rate limit feedback on the frontend** — when Gemini is slow, the UI just shows a spinner. A "still thinking…" message with elapsed time would be far less anxiety-inducing.

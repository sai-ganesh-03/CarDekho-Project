"""
ReAct-style tool-calling agent for Indian used car advisory.
Uses Gemini via langchain-google-genai with a tool-calling loop
(Reason -> Act with tools -> Reason -> final Answer).
"""

import json
import re
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

import config
from database import execute_select, get_schema_info
from logger import get_logger

log = get_logger("agent")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Arjun, a trusted Indian used car advisor with 15+ years of hands-on experience.
You work on CarDekho and have helped thousands of buyers across India find the right car.

YOUR EXPERTISE:
- All major Indian brands: Maruti Suzuki, Hyundai, Tata, Honda, Toyota, Kia, MG, Mahindra, Renault, Skoda, Volkswagen + premium brands
- Indian pricing in lakhs (1 lakh = ₹1,00,000). Prices in the database are raw rupees.
- Indian driving realities: bumpy city roads, long highway runs, parking in tight lanes, fuel costs
- What Indian buyers actually care about: mileage, resale value, service network, reliability, road presence
- Typical buyer profiles: first-car buyers (budget hatchbacks), family upgrade (SUVs), corporate (sedans)

YOUR APPROACH:
- Be warm and direct, like a knowledgeable friend — not a scripted bot
- If the user's intent is reasonably clear, SEARCH IMMEDIATELY — don't over-question
- If something truly critical is missing (usually budget), ask exactly ONE focused question
- Never ask multiple questions at once
- When presenting results, briefly say WHY these cars are good choices

DATABASE NOTES:
- No body_type column. Use model names to infer body type (your domain knowledge).
- vehicle_age = how many years old the car is (not the year of manufacture)
- selling_price is in Indian Rupees. Convert lakhs to rupees for SQL: 5 lakhs = 500000

RESPONSE FORMAT — CRITICAL:
Your Final Answer MUST be a single valid JSON object and nothing else.

Asking a clarifying question:
{"type": "question", "message": "your single focused question"}

Presenting car results:
{"type": "cars", "message": "short warm summary of what you found and why", "cars": [<exact array from query_cars tool>]}

No matching cars:
{"type": "no_results", "message": "what you searched, why nothing matched, 1-2 concrete suggestions"}

General info / greeting:
{"type": "message", "message": "your response"}

DO NOT wrap the JSON in markdown code blocks. Output raw JSON only."""

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def get_schema() -> str:
    """
    Returns the full database schema: column names, types, value ranges,
    available brands, fuel types, and sample rows.
    Call this once per session before writing any SQL.
    """
    return get_schema_info()


@tool
def query_cars(sql: str) -> str:
    """
    Execute a SQL SELECT query on the cardekho_dataset table.
    Returns up to 20 matching rows as JSON.
    Only SELECT statements are allowed.

    Good example:
        SELECT car_name, brand, model, vehicle_age, km_driven, fuel_type,
               transmission_type, mileage, engine, seats, selling_price
        FROM cardekho_dataset
        WHERE selling_price BETWEEN 300000 AND 700000
          AND fuel_type = 'Petrol'
        ORDER BY selling_price
        LIMIT 10
    """
    try:
        rows = execute_select(sql)
        return json.dumps({"count": len(rows), "results": rows})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Agent plumbing
# ---------------------------------------------------------------------------

_TOOLS = [get_schema, query_cars]
_TOOL_MAP = {t.name: t for t in _TOOLS}

# In-memory session store: session_id -> list[BaseMessage]
_sessions: dict[str, list] = {}


def _build_llm():
    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0.7,
    ).bind_tools(_TOOLS)


def _parse_response(content: str) -> dict:
    """Extract structured JSON from the agent's final answer."""
    if not content:
        return {"type": "message", "message": "I had trouble responding. Please try again."}

    # Strip markdown code fences if the model adds them
    content = re.sub(r"^```(?:json)?\s*", "", content.strip())
    content = re.sub(r"\s*```$", "", content.strip())

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try to extract the first {...} block
    match = re.search(r"\{[\s\S]*\}", content)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"type": "message", "message": content}


def chat(session_id: str, user_message: str) -> dict:
    """Run one conversational turn and return a structured response dict."""
    if session_id not in _sessions:
        _sessions[session_id] = []

    history = _sessions[session_id]
    llm = _build_llm()

    messages = [SystemMessage(content=SYSTEM_PROMPT), *history, HumanMessage(content=user_message)]

    # ReAct loop: reason → act (tools) → reason → … → final answer
    MAX_ITERATIONS = 10
    response: AIMessage | None = None
    for iteration in range(MAX_ITERATIONS):
        log.info("iter=%d | sleeping 10s before API call", iteration)
        time.sleep(10)
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            log.debug("iter=%d | no tool calls — final answer", iteration)
            break

        for tc in response.tool_calls:
            log.info("tool_call: %s | args: %s", tc["name"], str(tc["args"])[:200])
            fn = _TOOL_MAP.get(tc["name"])
            try:
                result = fn.invoke(tc["args"]) if fn else f"Unknown tool: {tc['name']}"
            except Exception as exc:
                result = json.dumps({"error": str(exc)})
                log.error("tool %s failed: %s", tc["name"], exc)

            log.debug("tool_result: %s | %.300s", tc["name"], str(result))
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )

    # Persist history (drop system message)
    _sessions[session_id] = messages[1:]

    raw = response.content if response else ""
    # Gemini may return a list of content parts instead of a plain string
    if isinstance(raw, list):
        raw = " ".join(p.get("text", "") for p in raw if isinstance(p, dict))
    log.debug("raw_response: %.500s", raw)
    return _parse_response(raw or "")

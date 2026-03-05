from grid_agent.llm import Provider
from grid_agent.rag import RagIndex
from grid_agent.weather import OpenMeteoClient, get_coordinates

from .state import AgentState

CLASSIFY_SYSTEM = (
    "You classify electric grid demand anomalies. Given the feature values that "
    "drove an anomaly flag, respond with exactly one label: "
    "'spike' (demand sharply above normal), 'drop' (demand sharply below normal), "
    "or 'sustained_deviation' (demand persistently off-baseline without a sharp "
    "single-hour move). Respond with only the label, nothing else."
)

EXPLAIN_SYSTEM = (
    "You are a grid reliability assistant. You explain flagged demand anomalies "
    "for human operator review. You are NOT diagnosing the cause with certainty — "
    "you are proposing a plausible hypothesis grounded in the provided reliability "
    "documentation excerpts. Always explicitly state that this is a hypothesis for "
    "human review, not a diagnosis. Do not recommend or imply any autonomous action; "
    "you only inform a human decision-maker. Cite which excerpt(s) informed your "
    "reasoning by their source filename. "
    "If real historical weather data is provided, treat it as evidence, not just "
    "another guess: explicitly say whether the actual temperature/wind chill "
    "supports or contradicts a weather-driven hypothesis, rather than assuming "
    "cold weather occurred just because the season or hour makes it plausible. "
    "If no weather data is provided, do not fabricate specific weather conditions — "
    "note that weather could not be checked and the hypothesis is unverified."
)

RECOMMEND_SYSTEM = (
    "Based on the anomaly and hypothesis already generated, recommend ONE next "
    "action for a human grid operator to take — e.g. 'flag for operator review', "
    "'verify against neighboring balancing authority data'. This is a "
    "recommendation for a human to consider, not an instruction to act "
    "autonomously. If weather data was already checked (it will be noted in the "
    "hypothesis), do not recommend checking weather again — recommend a different "
    "next step, such as verifying against neighboring BA data or reviewing "
    "generator/outage reports. Respond with a single concise recommendation "
    "(1-2 sentences)."
)


def classify_anomaly(state: AgentState, llm: Provider) -> AgentState:
    features = state["anomaly"]["contributing_features"]
    prompt = (
        f"Anomaly features: {features}. "
        f"Severity score: {state['anomaly']['severity_score']:.3f}."
    )
    response = llm.generate(prompt, system=CLASSIFY_SYSTEM, max_tokens=16)
    label = response.text.strip().lower()
    if label not in ("spike", "drop", "sustained_deviation"):
        label = "sustained_deviation"
    return {**state, "anomaly_type": label}


def fetch_weather(state: AgentState, weather_client: OpenMeteoClient) -> AgentState:
    """Look up real historical weather for the anomaly's region/timestamp, so
    the explanation step can check a weather hypothesis against actual data
    instead of only pattern-matching against RAG text. Degrades gracefully —
    if the region has no coordinate mapping or the lookup fails, the agent
    proceeds without weather context rather than failing the whole run.
    """
    anomaly = state["anomaly"]
    coords = get_coordinates(anomaly["region"])
    if coords is None:
        return {**state, "weather_summary": None}

    lat, lon = coords
    observation = weather_client.get_historical_hourly(lat, lon, anomaly["timestamp"])
    if observation is None:
        return {**state, "weather_summary": None}

    return {**state, "weather_summary": observation.summary()}


def retrieve_guidance(state: AgentState, rag_index: RagIndex, top_k: int = 3) -> AgentState:
    anomaly = state["anomaly"]
    query = (
        f"{state.get('anomaly_type', 'anomaly')} in electric grid demand: "
        f"deviation from last week {anomaly['contributing_features'].get('deviation_from_last_week', 0):.0f} MW, "
        f"severity {anomaly['severity_score']:.3f}"
    )
    chunks = rag_index.query(query, top_k=top_k)
    return {**state, "retrieved_chunks": chunks}


def generate_explanation(state: AgentState, llm: Provider) -> AgentState:
    anomaly = state["anomaly"]
    chunks = state.get("retrieved_chunks", [])
    context = "\n\n".join(f"[{c.source}] {c.text}" for c in chunks)
    weather_summary = state.get("weather_summary")
    weather_line = (
        f"Actual historical weather at this time/location: {weather_summary}\n"
        if weather_summary
        else "Historical weather could not be retrieved for this time/location.\n"
    )

    prompt = (
        f"Anomaly detected in {anomaly['region']} at {anomaly['timestamp']}.\n"
        f"Type: {state.get('anomaly_type', 'unknown')}\n"
        f"Severity: {anomaly['severity_score']:.3f}\n"
        f"Contributing features: {anomaly['contributing_features']}\n"
        f"{weather_line}\n"
        f"Relevant reliability documentation:\n{context}\n\n"
        "Explain the likely cause as a hypothesis for human review."
    )
    response = llm.generate(prompt, system=EXPLAIN_SYSTEM, max_tokens=512)
    return {**state, "explanation": response.text}


def recommend_action(state: AgentState, llm: Provider) -> AgentState:
    prompt = (
        f"Anomaly type: {state.get('anomaly_type', 'unknown')}\n"
        f"Hypothesis: {state.get('explanation', '')}\n\n"
        "Recommend one next action for a human operator."
    )
    response = llm.generate(prompt, system=RECOMMEND_SYSTEM, max_tokens=128)
    return {**state, "recommendation": response.text}


def cite_sources(state: AgentState) -> AgentState:
    chunks = state.get("retrieved_chunks", [])
    citations = {c.source for c in chunks}
    if state.get("weather_summary"):
        citations.add("Open-Meteo historical weather (archive-api.open-meteo.com)")
    return {**state, "citations": sorted(citations)}

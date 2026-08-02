from langgraph.graph import END, StateGraph

from grid_agent.llm import Provider, get_provider
from grid_agent.models import AnomalyResult
from grid_agent.rag import RagIndex

from . import nodes
from .state import AgentState


def build_graph(llm: Provider, rag_index: RagIndex):
    """Build the anomaly-explanation graph:
    classify -> retrieve -> explain -> recommend -> cite
    """
    graph = StateGraph(AgentState)

    graph.add_node("classify", lambda state: nodes.classify_anomaly(state, llm))
    graph.add_node("retrieve", lambda state: nodes.retrieve_guidance(state, rag_index))
    graph.add_node("explain", lambda state: nodes.generate_explanation(state, llm))
    graph.add_node("recommend", lambda state: nodes.recommend_action(state, llm))
    graph.add_node("cite", nodes.cite_sources)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "explain")
    graph.add_edge("explain", "recommend")
    graph.add_edge("recommend", "cite")
    graph.add_edge("cite", END)

    return graph.compile()


def analyze_anomaly(
    anomaly: AnomalyResult,
    llm: Provider | None = None,
    rag_index: RagIndex | None = None,
) -> AgentState:
    """Run the full agent graph on a single AnomalyResult and return the final state."""
    llm = llm or get_provider()
    if rag_index is None:
        rag_index = RagIndex()
        rag_index.load()

    app = build_graph(llm, rag_index)

    initial_state: AgentState = {
        "anomaly": {
            "timestamp": str(anomaly.timestamp),
            "region": anomaly.region,
            "severity_score": anomaly.severity_score,
            "contributing_features": anomaly.contributing_features,
        }
    }
    return app.invoke(initial_state)

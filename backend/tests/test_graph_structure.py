from blueprint_agents.graph import build_graph


def test_build_graph_compiles_without_an_api_key():
    # No OPENAI_API_KEY needed: llm_factory is only invoked lazily inside node bodies at
    # invoke time, never during build_graph()/compile() itself.
    graph = build_graph()
    node_names = set(graph.get_graph().nodes.keys())
    expected = {"product_agent", "ux_agent", "technical_agent", "reviewer_agent", "assemble"}
    assert expected <= node_names

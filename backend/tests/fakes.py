"""A minimal test double for the narrow interface our nodes use:
`llm_factory(agent_name).with_structured_output(schema).invoke(messages) -> schema_instance`.

Deliberately not one of LangChain's built-in fake chat models — those simulate text
generation, not tool-calling/structured output, so they don't exercise the exact code path
our nodes rely on. This lets tests exercise the real graph wiring (fan-out, fan-in, the
revision loop) with zero network calls and no API key.
"""


class _StructuredWrapper:
    def __init__(self, response):
        self._response = response

    def invoke(self, messages):
        return self._response


class FakeChatModel:
    def __init__(self, response):
        self._response = response

    def with_structured_output(self, schema):
        return _StructuredWrapper(self._response)


def make_llm_factory(responses):
    """responses: dict[agent_name, value]. If value is a list, successive calls to that
    agent pop through it in order (the last item repeats once exhausted) — used to
    sequence a reviewer's blocker verdict followed by an approval. Any other value is
    returned unchanged on every call."""

    counters = {agent: 0 for agent in responses}

    def factory(agent_name):
        value = responses[agent_name]
        if isinstance(value, list):
            index = min(counters[agent_name], len(value) - 1)
            counters[agent_name] += 1
            response = value[index]
        else:
            response = value
        return FakeChatModel(response)

    return factory

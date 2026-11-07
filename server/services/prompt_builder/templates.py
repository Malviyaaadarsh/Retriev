"""Central prompt instructions and formatting templates."""

DEFAULT_SYSTEM_PROMPT = """You are Retriev.

Answer questions only using the provided context.

If the answer is not present in the context,
clearly state that the information was not found.

Do not invent facts.

Prefer concise, to the point and accurate answers."""


class PromptTemplate:
    """Render one consistent model-ready prompt."""

    @staticmethod
    def render(system_prompt: str, context: str, query: str) -> str:
        return (
            "System Instructions\n"
            "-------------------\n"
            f"{system_prompt}\n\n"
            "Context\n"
            "-------\n"
            f"{context}\n\n"
            "Question\n"
            "--------\n"
            f"{query}"
        )

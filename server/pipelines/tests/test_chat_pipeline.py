from server.services.generation.models import Citation, GenerationResult
from server.services.prompt_builder.models import PromptContext
from server.services.retrieval.models import RetrievedChunk, RetrievalResult

from ..chat import (
    ChatPipeline,
    ChatRequest,
    ChatPipelineConfig,
    GenerationPipelineError,
    InvalidQueryError,
)


class FakeRetrieval:
    def __init__(self, result: RetrievalResult) -> None:
        self.result = result
        self.calls: list[tuple[str, str]] = []

    def retrieve(self, query: str, workspace_id: str) -> RetrievalResult:
        self.calls.append((query, workspace_id))
        return self.result


class FakePromptBuilder:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def build_prompt(self, query: str, retrieval: RetrievalResult) -> PromptContext:
        self.calls.append(query)
        return PromptContext(
            query=query,
            system_prompt="system",
            context="\n".join(chunk.content for chunk in retrieval.chunks),
            final_prompt=f"Question: {query}",
            source_metadata=[chunk.metadata for chunk in retrieval.chunks],
        )


class FakeGeneration:
    def __init__(self, result: GenerationResult | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def generate(
        self,
        prompt: PromptContext,
        provider_name: str,
        model_name: str,
    ) -> GenerationResult:
        self.calls.append((provider_name, model_name))
        if self.error:
            raise self.error
        assert self.result is not None
        return self.result


def make_result() -> RetrievalResult:
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        content="RAG combines retrieval and generation.",
        score=0.9,
        metadata={"file_name": "notes.md", "page": 2, "chunk_id": "chunk-1"},
    )
    return RetrievalResult(query="What is RAG?", total_results=1, chunks=[chunk])


def make_pipeline(
    retrieval: RetrievalResult | None = None,
    generation_error: Exception | None = None,
    config: ChatPipelineConfig | None = None,
) -> tuple[ChatPipeline, FakeRetrieval, FakePromptBuilder, FakeGeneration]:
    retrieval_service = FakeRetrieval(retrieval or make_result())
    prompt_builder = FakePromptBuilder()
    generation = FakeGeneration(
        result=GenerationResult(
            answer="RAG retrieves relevant context before generation.",
            citations=[Citation("notes.md", 2, "chunk-1")],
            provider_name="fake",
            model_name="fake-model",
            generation_time_ms=12.0,
        ),
        error=generation_error,
    )
    pipeline = ChatPipeline(
        retrieval_service,
        prompt_builder,
        generation,
        config,
    )
    return pipeline, retrieval_service, prompt_builder, generation


def request(query: str = "What is RAG?") -> ChatRequest:
    return ChatRequest(query, "workspace-1", "fake", "fake-model")


def test_runs_chat_flow_and_preserves_citations() -> None:
    pipeline, retrieval, prompt, generation = make_pipeline()

    result = pipeline.run(request())

    assert result.answer.startswith("RAG retrieves")
    assert result.retrieved_chunks == 1
    assert result.citations[0].chunk_id == "chunk-1"
    assert result.statistics is not None
    assert result.statistics.prompt_length > 0
    assert result.progress.current_stage == "Completed"
    assert result.progress.percentage == 100.0
    assert retrieval.calls == [("What is RAG?", "workspace-1")]
    assert prompt.calls == ["What is RAG?"]
    assert generation.calls == [("fake", "fake-model")]


def test_rejects_none_empty_and_whitespace_queries() -> None:
    pipeline, *_ = make_pipeline()

    for query in (None, "", "   "):
        try:
            pipeline.run(request(query))
        except InvalidQueryError:
            pass
        else:
            raise AssertionError("Expected InvalidQueryError")


def test_empty_retrieval_still_builds_prompt_and_generates() -> None:
    pipeline, retrieval, prompt, generation = make_pipeline(
        RetrievalResult("No match", 0, []),
    )

    result = pipeline.run(request("No match"))

    assert result.answer
    assert result.retrieved_chunks == 0
    assert result.citations
    assert retrieval.calls
    assert prompt.calls
    assert generation.calls


def test_empty_context_can_be_rejected_by_configuration() -> None:
    pipeline, *_ = make_pipeline(
        RetrievalResult("No match", 0, []),
        config=ChatPipelineConfig(allow_empty_context=False),
    )

    try:
        pipeline.run(request("No match"))
    except Exception as error:
        assert error.__class__.__name__ == "RetrievalPipelineError"
    else:
        raise AssertionError("Expected empty context failure")


def test_generation_failure_is_wrapped() -> None:
    pipeline, *_ = make_pipeline(generation_error=RuntimeError("provider unavailable"))

    try:
        pipeline.run(request())
    except GenerationPipelineError as error:
        assert str(error) == "Unable to generate answer"
    else:
        raise AssertionError("Expected generation pipeline failure")


def test_statistics_and_citations_can_be_disabled() -> None:
    pipeline, *_ = make_pipeline(
        config=ChatPipelineConfig(enable_statistics=False, enable_citations=False),
    )

    result = pipeline.run(request())

    assert result.statistics is None
    assert result.citations == []

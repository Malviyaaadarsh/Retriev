from server.services.generation.models import Citation, GenerationResult
from server.services.prompt_builder.models import PromptContext
from server.services.retrieval.models import RetrievedChunk, RetrievalResult

from ..chat import ChatPipeline, ChatRequest


class RetrievalDouble:
    def retrieve(self, query: str, workspace_id: str) -> RetrievalResult:
        return RetrievalResult(
            query=query,
            total_results=1,
            chunks=[
                RetrievedChunk(
                    "chunk-1",
                    "Recursive chunking splits text hierarchically.",
                    0.8,
                    {"file_name": "guide.md", "page": 4, "chunk_id": "chunk-1"},
                )
            ],
        )


class PromptDouble:
    def build_prompt(self, query: str, result: RetrievalResult) -> PromptContext:
        return PromptContext(
            query=query,
            system_prompt="Answer from context.",
            context=result.chunks[0].content,
            final_prompt=f"{query}\n{result.chunks[0].content}",
            source_metadata=[result.chunks[0].metadata],
        )


class GenerationDouble:
    def generate(
        self,
        prompt: PromptContext,
        provider_name: str,
        model_name: str,
    ) -> GenerationResult:
        return GenerationResult(
            answer="It splits text using progressively smaller separators.",
            citations=[Citation("guide.md", 4, "chunk-1")],
            provider_name=provider_name,
            model_name=model_name,
            generation_time_ms=1.0,
        )


def test_chat_pipeline_end_to_end_contract() -> None:
    pipeline = ChatPipeline(RetrievalDouble(), PromptDouble(), GenerationDouble())

    result = pipeline.run(
        ChatRequest(
            query="How does recursive chunking work?",
            workspace_id="workspace-1",
            provider_name="fake",
            model_name="fake-model",
        )
    )

    assert result.answer
    assert result.retrieved_chunks == 1
    assert result.citations == [Citation("guide.md", 4, "chunk-1")]
    assert result.provider_name == "fake"
    assert result.model_name == "fake-model"

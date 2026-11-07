"""Shared generation helpers."""

from server.services.prompt_builder.models import PromptContext

from .models import Citation


def citations_from_prompt(prompt_context: PromptContext) -> list[Citation]:
    grouped: dict[str, Citation] = {}
    for source in prompt_context.source_metadata:
        file_name = str(source.get("file_name", "Unknown"))
        citation = grouped.get(file_name)
        page = source.get("page")
        excerpt = str(source.get("excerpt", ""))
        chunk_id = str(source.get("chunk_id", ""))
        if citation is None:
            grouped[file_name] = Citation(file_name, page, chunk_id, excerpt)
            continue
        pages = [str(value) for value in (citation.page, page) if value is not None]
        grouped[file_name] = Citation(
            file_name=file_name,
            page=int(pages[0]) if pages else None,
            chunk_id=", ".join(filter(None, [citation.chunk_id, chunk_id])),
            excerpt=" ".join(filter(None, [citation.excerpt, excerpt])),
        )
    return list(grouped.values())

import { describe, expect, it } from "vitest";

describe("citation preview data", () => {
  it("preserves file, page, chunk, and excerpt metadata", () => {
    const citation = {
      file_name: "guide.pdf",
      page: 12,
      chunk_id: "chunk-1",
      excerpt: "Relevant passage",
    };
    const preview = {
      fileName: citation.file_name,
      page: citation.page,
      chunkId: citation.chunk_id,
      excerpt: citation.excerpt,
    };

    expect(preview).toEqual({
      fileName: "guide.pdf",
      page: 12,
      chunkId: "chunk-1",
      excerpt: "Relevant passage",
    });
  });
});

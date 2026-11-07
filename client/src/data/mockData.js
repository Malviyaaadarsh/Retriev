/**
 * Retriev — Mock Fixtures for Milestone 1 Frontend Shell
 * All mock data is encapsulated here so UI components do not hardcode mock entities.
 */

export const INITIAL_WORKSPACES = [
  {
    id: "ws-ai-research",
    name: "AI & RAG Research 2026",
    description: "Literature, surveys, and benchmarks on retrieval-augmented generation and vector indexes.",
    icon: "Sparkles",
    documentCount: 4,
    chatCount: 2,
    createdAt: "2026-03-15",
  },
  {
    id: "ws-engineering",
    name: "Engineering & Architecture",
    description: "Internal specifications, FastAPI architecture blueprints, and LanceDB storage guidelines.",
    icon: "Cpu",
    documentCount: 3,
    chatCount: 1,
    createdAt: "2026-04-01",
  },
  {
    id: "ws-product-policy",
    name: "Product & Privacy Guidelines",
    description: "Compliance specifications, privacy boundaries, and model provider access controls.",
    icon: "ShieldCheck",
    documentCount: 2,
    chatCount: 1,
    createdAt: "2026-04-08",
  },
];

export const INITIAL_DOCUMENTS = {
  "ws-ai-research": [
    {
      id: "doc-1",
      workspaceId: "ws-ai-research",
      title: "retrieval_augmented_generation_survey_2026.pdf",
      fileName: "retrieval_augmented_generation_survey_2026.pdf",
      fileType: "pdf",
      size: "2.4 MB",
      sizeBytes: 2516582,
      chunkCount: 84,
      status: "indexed",
      uploadedAt: "2026-04-02 14:22",
      excerpt: "Comprehensive comparison of dense vector retrieval versus hybrid BM25 reranking in production knowledge assistants. Demonstrates 18% higher citation accuracy when context window chunks are kept under 512 tokens with 64-token sliding window overlap.",
    },
    {
      id: "doc-2",
      workspaceId: "ws-ai-research",
      title: "speculative_decoding_and_chunking.pdf",
      fileName: "speculative_decoding_and_chunking.pdf",
      fileType: "pdf",
      size: "1.1 MB",
      sizeBytes: 1153433,
      chunkCount: 42,
      status: "indexed",
      uploadedAt: "2026-04-05 09:10",
      excerpt: "Explores interaction between prompt caching and document chunk boundaries in hosted transformer endpoints.",
    },
    {
      id: "doc-3",
      workspaceId: "ws-ai-research",
      title: "vector_index_benchmarks_lancedb.md",
      fileName: "vector_index_benchmarks_lancedb.md",
      fileType: "markdown",
      size: "340 KB",
      sizeBytes: 348160,
      chunkCount: 18,
      status: "indexed",
      uploadedAt: "2026-04-07 17:45",
      excerpt: "LanceDB disk-based vector storage performance across 100k embedded passages with IVF-PQ indexing on SSDs.",
    },
    {
      id: "doc-4",
      workspaceId: "ws-ai-research",
      title: "prompt_grounding_evaluation_criteria.txt",
      fileName: "prompt_grounding_evaluation_criteria.txt",
      fileType: "txt",
      size: "82 KB",
      sizeBytes: 83968,
      chunkCount: 6,
      status: "indexed",
      uploadedAt: "2026-04-09 11:30",
      excerpt: "Guidelines for preventing hallucination in knowledge extraction: requiring explicit citation brackets [Source N: file, page] and graceful fallback when evidence is lacking.",
    },
  ],
  "ws-engineering": [
    {
      id: "doc-eng-1",
      workspaceId: "ws-engineering",
      title: "retriev_fastapi_modular_monolith_spec.md",
      fileName: "retriev_fastapi_modular_monolith_spec.md",
      fileType: "markdown",
      size: "520 KB",
      sizeBytes: 532480,
      chunkCount: 26,
      status: "indexed",
      uploadedAt: "2026-04-01 10:15",
      excerpt: "Architecture specifications detailing FastAPI routers, service boundary decoupling, and SQLite document metadata tracking.",
    },
    {
      id: "doc-eng-2",
      workspaceId: "ws-engineering",
      title: "lancedb_workspace_isolation_protocol.md",
      fileName: "lancedb_workspace_isolation_protocol.md",
      fileType: "markdown",
      size: "190 KB",
      sizeBytes: 194560,
      chunkCount: 12,
      status: "indexed",
      uploadedAt: "2026-04-03 16:30",
      excerpt: "Strict workspace isolation rules: every vector retrieval query must include mandatory workspace_id filter predicates to prevent cross-tenant data contamination.",
    },
    {
      id: "doc-eng-3",
      workspaceId: "ws-engineering",
      title: "text_extraction_normalization_pipeline.txt",
      fileName: "text_extraction_normalization_pipeline.txt",
      fileType: "txt",
      size: "64 KB",
      sizeBytes: 65536,
      chunkCount: 8,
      status: "indexed",
      uploadedAt: "2026-04-06 13:00",
      excerpt: "Clean text extraction rules: stripping corrupt binary headers, preserving markdown headers for hierarchy-aware chunking.",
    },
  ],
  "ws-product-policy": [
    {
      id: "doc-pol-1",
      workspaceId: "ws-product-policy",
      title: "local_first_privacy_boundary_disclosure.md",
      fileName: "local_first_privacy_boundary_disclosure.md",
      fileType: "markdown",
      size: "140 KB",
      sizeBytes: 143360,
      chunkCount: 9,
      status: "indexed",
      uploadedAt: "2026-04-08 11:00",
      excerpt: "Privacy policy: Retriev stores documents and embeddings locally on device. When hosted API models (e.g. OpenAI / Anthropic) are enabled by the user, only the retrieved excerpts relevant to the query are transmitted for inference.",
    },
    {
      id: "doc-pol-2",
      workspaceId: "ws-product-policy",
      title: "supported_file_formats_matrix.txt",
      fileName: "supported_file_formats_matrix.txt",
      fileType: "txt",
      size: "45 KB",
      sizeBytes: 46080,
      chunkCount: 4,
      status: "indexed",
      uploadedAt: "2026-04-09 15:40",
      excerpt: "Initial MVP explicitly supports: PDF (.pdf), Markdown (.md), and Plain Text (.txt). DOCX, HTML, and audio transcription are deferred to later releases.",
    },
  ],
};

export const INITIAL_CONVERSATIONS = {
  "ws-ai-research": [
    {
      id: "conv-1",
      workspaceId: "ws-ai-research",
      title: "Chunking strategies & overlap analysis",
      updatedAt: "10 mins ago",
      messages: [
        {
          id: "msg-1",
          role: "user",
          content: "What does the research survey conclude about chunk sizes and overlap in dense vector retrieval?",
          timestamp: "10:14 AM",
        },
        {
          id: "msg-2",
          role: "assistant",
          content: "Based on the retrieved research papers in this workspace, the survey demonstrates that:\n\n1. **Optimal Chunk Window:** Semantic chunk sizes between **256 to 512 tokens** yield the best balance between semantic granularity and prompt context retention.\n2. **Sliding Overlap:** A **64-token overlap** prevents boundary clipping of complex definitions across adjacent chunks.\n3. **Citation Accuracy:** Keeping chunks under 512 tokens improved citation precision by approximately **18%** compared to larger 1024-token blocks.\n\n*(Note: This response is previewing grounded citation formatting. Full live LLM inference engine activates in Milestone 2 & 6.)*",
          timestamp: "10:14 AM",
          citations: [
            {
              sourceNumber: 1,
              fileName: "retrieval_augmented_generation_survey_2026.pdf",
              page: 14,
              excerpt: "Demonstrates 18% higher citation accuracy when context window chunks are kept under 512 tokens with 64-token sliding window overlap.",
            },
            {
              sourceNumber: 2,
              fileName: "prompt_grounding_evaluation_criteria.txt",
              page: 2,
              excerpt: "Requiring explicit citation brackets [Source N: file, page] prevents hallucination in knowledge extraction.",
            },
          ],
        },
      ],
    },
    {
      id: "conv-2",
      workspaceId: "ws-ai-research",
      title: "LanceDB disk benchmarks",
      updatedAt: "Yesterday",
      messages: [
        {
          id: "msg-3",
          role: "user",
          content: "How does LanceDB perform for local vector search on SSD storage?",
          timestamp: "Yesterday",
        },
        {
          id: "msg-4",
          role: "assistant",
          content: "According to **`vector_index_benchmarks_lancedb.md`**, LanceDB utilizes an on-disk columnar format that allows sub-millisecond approximate nearest neighbor (ANN) retrieval across 100k passages with IVF-PQ indexing, maintaining low RAM overhead on local workstations.",
          timestamp: "Yesterday",
          citations: [
            {
              sourceNumber: 1,
              fileName: "vector_index_benchmarks_lancedb.md",
              page: 1,
              excerpt: "LanceDB disk-based vector storage performance across 100k embedded passages with IVF-PQ indexing on SSDs.",
            },
          ],
        },
      ],
    },
  ],
  "ws-engineering": [
    {
      id: "conv-eng-1",
      workspaceId: "ws-engineering",
      title: "Workspace isolation architecture",
      updatedAt: "2 days ago",
      messages: [
        {
          id: "msg-eng-1",
          role: "user",
          content: "How is workspace isolation enforced in the storage layer?",
          timestamp: "2 days ago",
        },
        {
          id: "msg-eng-2",
          role: "assistant",
          content: "According to the architectural guidelines, workspace isolation is maintained through two strict layers:\n\n- **Logical separation:** Every vector retrieval query enforces a mandatory `workspace_id` predicate filter.\n- **Metadata consistency:** SQLite documents and conversation tables enforce workspace foreign key constraints, ensuring queries in Workspace A never expose data from Workspace B.",
          timestamp: "2 days ago",
          citations: [
            {
              sourceNumber: 1,
              fileName: "lancedb_workspace_isolation_protocol.md",
              page: 1,
              excerpt: "Strict workspace isolation rules: every vector retrieval query must include mandatory workspace_id filter predicates.",
            },
          ],
        },
      ],
    },
  ],
  "ws-product-policy": [
    {
      id: "conv-pol-1",
      workspaceId: "ws-product-policy",
      title: "Privacy boundary clarification",
      updatedAt: "3 days ago",
      messages: [
        {
          id: "msg-pol-1",
          role: "user",
          content: "What is Retriev's privacy boundary regarding external API providers?",
          timestamp: "3 days ago",
        },
        {
          id: "msg-pol-2",
          role: "assistant",
          content: "Retriev follows a strict local-first philosophy: documents, vector embeddings, and chat histories are stored on your local disk. If a hosted provider (e.g. OpenAI or Anthropic) is configured, only the retrieved passages directly relevant to your query are transmitted over TLS for inference, and this behavior is explicitly surfaced in the UI.",
          timestamp: "3 days ago",
          citations: [
            {
              sourceNumber: 1,
              fileName: "local_first_privacy_boundary_disclosure.md",
              page: 1,
              excerpt: "When hosted API models are enabled by the user, only the retrieved excerpts relevant to the query are transmitted for inference.",
            },
          ],
        },
      ],
    },
  ],
};

export const DEFAULT_SETTINGS = {
  llmProvider: "openai",
  modelName: "gpt-4o-mini",
  apiKey: "",
  temperature: 0.2,
  embeddingProvider: "openai",
  embeddingModel: "text-embedding-3-small",
  chunkSize: 512,
  chunkOverlap: 64,
  topK: 4,
  storagePath: "~/.retriev/data",
  localFirstMode: true,
};

export const SUGGESTED_PROMPTS = {
  "ws-ai-research": [
    "What are the recommended chunk sizes and overlap ratios?",
    "Summarize the performance characteristics of LanceDB.",
    "How does Retriev prevent hallucination in source citations?",
    "Compare dense vector search with hybrid BM25 retrieval.",
  ],
  "ws-engineering": [
    "Explain the workspace isolation protocol for vector queries.",
    "What is the modular monolith structure planned for FastAPI?",
    "What file formats are supported in the ingestion pipeline?",
    "How does SQLite handle document metadata tracking?",
  ],
  "ws-product-policy": [
    "What are the privacy boundaries when using hosted LLMs?",
    "What documents are stored locally vs sent to APIs?",
    "Which document formats are planned for initial MVP release?",
    "How can users configure local Ollama models?",
  ],
};

# RAG Interview Preparation Guide
**Project:** Local Data Governance RAG Assistant  
**Read first:** the five-minute revision sheet below. Use the remaining sections for follow-up questions.

[Project README](README.md) · [Live Q&A demo](https://pratikkumar-data-ai-portfolio.woollydog11.chatgpt.site/demos/local-governance-rag.html) · [Technology comparison](documentation/TECHNOLOGY_COMPARISON.md)

This guide describes the current repository code. It distinguishes implemented behavior, design rationale, measured checks, and future improvements. The project is independent learning work developed with AI assistance; its default documents are fictional.

## 1. Five-minute revision sheet

| Interview topic | Exact answer for the local Python RAG application |
|---|---|
| Business problem | Help users find governance guidance and answer questions using inspectable document evidence. |
| Input | TXT, Markdown, and text-based PDFs. Default: three fictional governance procedures. |
| Chunking | Fixed-size **character-window chunking**, 600 characters per window, 100-character overlap. |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2`; dense 384-dimensional vectors; CPU; normalized embeddings. |
| Vector database | Chroma, local `PersistentClient`, default directory `.rag_index`. |
| Collection | `governance_documents`. Stores vectors, chunk text, and source/page/position metadata. |
| Search metric | **Cosine distance** configured with `hnsw:space = cosine`; application similarity = `1 - distance`. |
| Retrieval defaults | Request up to 3 chunks, then retain results with similarity at least 0.25. |
| Augmentation | Add retrieved evidence with numbered source labels to the question prompt. |
| Generation | Downloaded `qwen2.5:1.5b` through local Ollama, not a paid API. |
| Prompt settings | Temperature 0; context setting 4096; output budget 400 tokens; non-streaming HTTP response. |
| UI | Streamlit for the local model application. |
| Missing evidence | If retrieval returns no hits, abstain without calling the LLM. |
| Evaluation | Expected-document hit rate and absent-question rejection; neither is answer accuracy. |
| Not implemented | Fine-tuning, production authentication, document authorization, MCP, OCR, hybrid fusion, or cross-encoder reranking. |

**Do not mix up the versions:**

| Component | Local Python RAG app | Python keyword baseline | Public browser Q&A |
|---|---|---|---|
| Main code | `rag/pipeline.py`, `app.py` | `lexical_baseline.py` | `web-demo/governance/qa-engine.js` |
| Text units | Overlapping character chunks | Same overlapping chunks | Whole documents, then complete sentences |
| Retrieval | Dense embedding search | BM25 keyword scoring | BM25-style document and sentence scoring with small lexical heuristics |
| Embedding model | MiniLM | None | None |
| Vector database | Chroma | None | None |
| Answer | Local Qwen model response | Retrieved passages only | Extracted source sentence |
| Runs where? | Computer running Python and Ollama | Computer running Python | Visitor’s browser |
| Requires your laptop online for public demo? | Local app requires its host running | Not used to serve public demo | No |
| Conversation context | Each request is independent | Each query is independent | History is displayed but not used as answer context |

## 2. A 45-second project introduction

> “I built an independent data-governance RAG learning project using fictional procedures. The local Python pipeline reads documents, splits them into overlapping character chunks, creates MiniLM embeddings, and stores them in Chroma. A question is embedded with the same model, and cosine search retrieves supporting passages. Those passages become evidence in a prompt sent to a local Qwen model through Ollama. I also added a BM25 baseline and a browser-based extractive Q&A demo so people can inspect source-supported answers without installing a model. I evaluate retrieval separately from generated-answer quality and document what remains unverified.”

Adapt this explanation to work you have reviewed and can demonstrate. Do not describe a synthetic demo as an NYSDFS deployment.

## 3. What documents are used?

The default folder is [sample_documents/](sample_documents/):

- `access_management.md`: access requests, approval roles, least privilege, and review.
- `data_issues.md`: issue records, escalation, remediation, and closure.
- `data_quality.md`: completeness, uniqueness, validity, consistency, timeliness, and address checks.

These are fictional learning procedures, not employer policies. The application reads the folder you select; it does not automatically scan your laptop. The default source collection is only these three files in `sample_documents/`. Project explanations live in `documentation/` and are not indexed by default. The older `docs/` company-information collection has been removed to keep this governance project focused.

For TXT/Markdown, page metadata is 1. PDF references use physical page numbers. Scanned image PDFs need OCR, which is not implemented.

## 4. The full sequence: ingestion → retrieval → augmentation → generation

| Stage | What actually happens | Code |
|---|---|---|
| Load | Walk the selected folder, read supported files, extract PDF text. | `load_chunks()` |
| Split | Create overlapping character windows while preserving source and page. | `split_text()` |
| Embed | Encode the chunk text using MiniLM with normalization enabled. | `LocalIndex.rebuild()` |
| Index | Store vectors, text, IDs, and metadata in persistent Chroma. | `LocalIndex.rebuild()` |
| Retrieve | Embed the question, request nearest chunks, filter by minimum similarity. | `LocalIndex.search()` |
| Augment | Construct system/user messages containing the question and labeled evidence. | `make_messages()` |
| Generate | Send those messages to local Ollama and read its answer. | `generate_answer()` |
| Inspect | Display the answer and the retrieved passages in Streamlit. | `app.py` |

**Indexing is preparation; retrieval happens for each question.** Rebuilding indexes does not train or fine-tune the language model.

## 5. Chunking: what, why, and limitations

**Method implemented:** fixed-size overlapping character windows. This is not recursive, semantic, sentence-based, or token-based chunking.

Defaults:

```python
size = 600
overlap = 100
```

Conceptual offsets in a long document:

- Chunk 1: characters `[0, 600)`.
- Chunk 2: characters `[500, 1100)`.
- Chunk 3: characters `[1000, 1600)`.

The step is `600 - 100 = 500` characters. Python slices exclude the ending offset. The last chunk may be shorter, and surrounding whitespace is stripped.

**Rationale:** a simple, inspectable starting point for short documents. Overlap can retain context spanning a boundary. The selected sizes are defaults, not an experimentally proven optimum.

**Tradeoff:** windows can cut sentences or words. More overlap creates duplicate evidence and additional storage/computation. No automatic deduplication of overlapping passages occurs during retrieval.

**Alternatives to compare:**

| Method | Why consider it? | Main tradeoff |
|---|---|---|
| Sentence/paragraph splitting | Preserves linguistic boundaries. | Units vary in length. |
| Recursive splitting | Tries headings/paragraphs/sentences before smaller units. | Requires separator and size choices. |
| Token-based splitting | Aligns size controls with a model tokenizer. | Tokenizers differ across models. |
| Semantic splitting | Chooses boundaries from changes in meaning. | More complexity and computation. |
| Structure-aware splitting | Preserves sections, lists, or tables. | Needs document-specific parsing. |

To experiment:

```bash
python ingestion_pipeline.py --chunk-size 600 --overlap 100
```

The code enforces size > 0 and 0 ≤ overlap < size.

## 6. Tokens, words, characters, and embeddings

A **character** is a text unit used by this chunker. A **word** is a linguistic unit. A **model token** may be a word, word fragment, punctuation, or another tokenizer-dependent unit. There is no exact universal words-to-tokens conversion.

MiniLM tokenizes internally when embedding text; Qwen uses its own tokenizer during generation. A 600-character chunk is **not** a 600-token chunk. The code does not count tokenizer tokens before embedding or building the prompt, so unusually token-dense inputs can still be truncated by model limits.

An **embedding** represents text as a numeric vector for comparing meaning. The local application uses the pretrained MiniLM sentence-transformer model: 384 dimensions, CPU execution, and `normalize_embeddings=True`. It does not train a new embedding model.

The **embedding model retrieves**; the **language model writes the answer**. MiniLM and Qwen have different jobs.

Rationale for this starting choice: local execution, no paid embedding API, and a compact general-purpose model. Domain-specific terminology and paraphrases still need evaluation. Alternatives include local BGE/E5-family embeddings; changing models requires re-embedding the corpus and using the matching query encoder. Equal vector dimensions alone do not make models interchangeable.

## 7. Chroma, persistence, and indexing

The local vector store is **Chroma**, not FAISS, Pinecone, or PostgreSQL.

```python
PersistentClient(path=".rag_index")
collection_name = "governance_documents"
metadata = {"hnsw:space": "cosine", "embedding_model": EMBEDDING_MODEL}
```

The application passes vectors explicitly with `embedding_function=None`; Chroma is not asked to choose its own embedding model.

Each stored chunk has:

| Item | Purpose |
|---|---|
| Vector | Semantic similarity search |
| Document text | Evidence passed to generation |
| Source | Relative filename for citation |
| Page | PDF page, or 1 for TXT/Markdown |
| Position | Chunk position within its page |
| ID | SHA-256 of source, page, position, and text |

Chroma’s single-node indexing uses HNSW for approximate nearest-neighbor retrieval. **HNSW is an index/search approach; cosine is the distance metric.** The project does not tune HNSW parameters or prove exact nearest-neighbor recall.

**Important rebuild behavior:** it computes embeddings, deletes the old collection, creates a replacement, and inserts batches of 128. This replaces the index; it does not append incrementally. It is not a transactional swap—an insertion failure after deletion can leave an incomplete index.

Rationale: Chroma bundles local persistence, vectors, text, and metadata without provisioning a separate database service. For another project, FAISS could provide a vector-search index with additional application-managed storage; pgvector could fit an existing PostgreSQL environment. Neither is implemented here.

## 8. Similarity search: cosine, top-k, and threshold

Cosine similarity compares vector direction:

```text
cosine_similarity(a, b) = dot(a, b) / (norm(a) × norm(b))
```

For the configured Chroma cosine metric:

```python
similarity = 1 - distance
```

The local defaults are **top-k = 3** and **minimum similarity = 0.25**. The application requests at most `min(top_k, collection_count)` candidates and then filters them. It does not keep searching farther down the index to refill rejected slots.

Example: candidate similarities `0.70, 0.31, 0.18` produce two retained passages at threshold 0.25.

**A similarity of 0.70 is not 70% answer confidence.** Threshold 0.25 is provisional and specific to this setup; it should be calibrated with relevant and irrelevant questions.

- Higher k can improve coverage but also add irrelevant/redundant context.
- A higher threshold can reduce weak matches but reject answerable questions.
- A lower threshold can improve coverage while increasing unsupported context.

Other metrics include Euclidean distance and inner product. Selection depends on the embedding model and normalization. The current application explicitly chooses cosine; it does not compare all metrics.

There is no cross-encoder reranking, metadata authorization filter, or BM25/vector fusion in the local app.

## 9. Augmentation and local answer generation

The prompt contains a system instruction, the question, and numbered evidence:

```text
[1] access_management.md page 1
The Data Owner approves or rejects the request.
```

The system instruction asks the model to use only evidence, cite numbered passages, treat document content as untrusted data, and abstain if evidence cannot answer the question.

Default generation:

| Setting | Value |
|---|---|
| Runtime | Ollama |
| Downloaded model tag | `qwen2.5:1.5b` |
| Endpoint | `http://127.0.0.1:11434/api/chat` |
| Temperature | `0` |
| Context setting | `num_ctx: 4096` |
| Output budget | `num_predict: 400` |
| Streaming | `False` |
| HTTP timeout | 180 seconds |

The 1.5b tag denotes a roughly 1.5-billion-parameter model family/size, not the download size. Temperature 0 aims to reduce variation; it does not guarantee correct or perfectly reproducible answers. Context and output settings are token-oriented budgets, not character counts.

No retrieved hits means **no model call**. With weak but nonempty evidence, a model can still answer incorrectly. Citation instructions do not verify citation correctness. No automated claim-to-source verifier is implemented.

The application rejects cloud model tags, uses a fixed loopback endpoint, bypasses proxies, and blocks redirects. The README also instructs starting Ollama with `OLLAMA_NO_CLOUD=1`. Initial package/model downloads need internet access; later inference uses the local installation.

## 10. How the live browser demo differs

The public Q&A uses **BM25-style lexical scoring plus extractive sentence selection**. It has no embeddings, vector database, or language-model generation.

Its flow:

1. Load three embedded fictional documents from `web-demo/governance/corpus.js`.
2. Lowercase/tokenize words, remove stop words, and apply a small explicit alias map.
3. Reject questions containing content terms outside the normalized corpus vocabulary.
4. Rank documents using BM25-style scores: `k1 = 1.5`, `b = 0.75`.
5. Select the highest-ranked document if its score is at least 0.15.
6. Split that document into sentences, rank them, apply role-question heuristics, and return one complete source sentence.
7. Show its document citation and supporting text.

The alias map and role boosts are handcrafted heuristics, not trained semantic understanding. Suggested questions are clickable inputs, not a lookup table of stored answers. Answers are selected from the documents; an unseen wording is included in tests.

The Python `lexical_baseline.py` is another comparison: it ranks the **character chunks**, defaults to top-k 3 and score threshold 0.2, and returns passages only. Do not confuse either BM25 score with cosine similarity or a probability.

## 11. Evaluation: what can I honestly claim?

| Check | What it establishes | What it does not establish |
|---|---|---|
| Source hit rate at k | Expected filename appears in retained retrieval results. | Correct generated answer or sufficient passage. |
| Absent-question rejection | Retrieval returns no hits for selected absent questions. | Reliable rejection of every unsupported question. |
| Chunking tests | Boundary/overlap behavior and metadata handling. | Best chunk size for a domain. |
| Stubbed HTTP/UI tests | Expected application behavior under controlled responses. | Real model quality. |
| Browser-engine tests | Eleven specified answer/abstention/wording behaviors. | Full browser UI verification or broad QA accuracy. |

The repository’s [historical semantic baseline](evaluation/BASELINE.md) reports 6/6 expected-document hits and 2/2 absent-question rejections on a tiny eight-question set. The [keyword evaluation](evaluation/lexical_results.json) also records 6/6 and 2/2 on that small set. These are not independent large-scale benchmarks and do not prove one method is superior.

The [validation record](documentation/VALIDATION.md) documents earlier checks. Real Ollama answer generation, citation support, memory use, and response latency still require verification on the owner’s computer. Do not claim production deployment or a measured reduction in employer work.

Next evaluation: expand questions, add paraphrases and hard negatives, separate threshold tuning from held-out testing, and manually assess factual support, citations, abstention, and latency.

## 12. Questions an interviewer may ask

**Why RAG instead of fine-tuning?**  
The goal is answering from inspectable external documents. Retrieval supplies evidence without changing model weights. No fine-tuning comparison was performed.

**Why overlap?**  
To preserve some text around chunk boundaries. It costs extra storage and can produce repeated context.

**Why both an embedding model and an LLM?**  
The embedding model supports retrieval; the LLM conditions its answer on retrieved text.

**Why Chroma?**  
It provides a manageable local vector store with text, metadata, and persistence for a small learning application.

**Does Chroma contain the original PDF?**  
This pipeline stores extracted chunks, vectors, and metadata. The original files remain in the document folder.

**Can I change the embedding model without rebuilding?**  
No. Re-embed the documents and use the matching query encoder in a compatible new index.

**Can the model hallucinate?**  
Yes. Retrieval and prompt rules help but do not guarantee evidence-grounded answers.

**Is this an agent or MCP application?**  
No. It is a direct retrieval-and-answer pipeline. It has no autonomous tool-selection loop or implemented MCP server.

**Is it a multi-turn chatbot?**  
The public interface shows a conversation, but each answer is independent. The local prompt also contains no prior conversation memory.

**What happens when a document changes?**  
Rebuild the index. Incremental synchronization and transactional index versioning are future improvements.

**What is your strongest lesson?**  
Separate retrieval quality from answer quality, compare a simple baseline, and make limitations visible.

**What would enterprise deployment need?**  
Identity, document-level permissions enforced before retrieval, approved data handling, versioned ingestion, secure storage, evaluation, monitoring, and controlled operations. These are requirements, not completed features.

## 13. Day-before-interview practice

1. Read sections 1 and 2 aloud. Explain the local app and browser demo without mixing their technologies.
2. Trace `Who approves access to a dataset?` from source text to the cited answer.
3. Explain 600 characters / 100 overlap, MiniLM, Chroma, cosine, top-k, augmentation, and Ollama without looking.
4. Open the live demo. Show an answerable and an unsupported question, then inspect a citation.
5. Run a baseline/check you can reproduce and explain its limits.
6. Review two failure modes: a sentence split across chunks and a relevant-looking passage that does not answer the question.
7. End with the next experiment you would run and the metric you would use.

### Useful commands

From the repository root, after setting up the Python environment and local Ollama as described in the README:

```powershell
.\.venv\Scripts\python.exe ingestion_pipeline.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
.\.venv\Scripts\python.exe evaluate.py --top-k 3 --threshold 0.25
.\.venv\Scripts\python.exe evaluate.py --generate
.\.venv\Scripts\python.exe lexical_baseline.py
node --test web-demo/tests/qa-engine.test.cjs
```

`--generate` needs a working local model. Never interpret an unrun command as a passed check.

## 14. Read the implementation

| File | What to inspect |
|---|---|
| [rag/pipeline.py](rag/pipeline.py) | `split_text`, `load_chunks`, `LocalIndex`, `make_messages`, `generate_answer` |
| [ingestion_pipeline.py](ingestion_pipeline.py) | Document/index paths and chunking CLI options |
| [app.py](app.py) | Streamlit settings, search, answer, evidence display |
| [evaluate.py](evaluate.py) | Evaluation denominators and optional generation |
| [lexical_baseline.py](lexical_baseline.py) | Chunk-level BM25 comparison |
| [web-demo/governance/qa-engine.js](web-demo/governance/qa-engine.js) | Browser retrieval, vocabulary gate, sentence extraction |
| [web-demo/tests/qa-engine.test.cjs](web-demo/tests/qa-engine.test.cjs) | Browser engine behavior checks |

## 15. Primary learning references

These explain the underlying tools; repository code remains the source for what this project implements.

- [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Chroma collection configuration, metrics, and HNSW](https://docs.trychroma.com/docs/collections/configure)
- [Ollama chat API](https://docs.ollama.com/api/chat)
- [Project technology comparison](documentation/TECHNOLOGY_COMPARISON.md)
- [Project learning guide](documentation/LEARNING_GUIDE.md)

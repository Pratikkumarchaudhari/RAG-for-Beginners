# Local Data Governance RAG Assistant — interview case study

## Business question

Can a small local assistant help a data steward find relevant governance guidance, display its evidence, and decline unsupported questions?

This is independent learning work. The default documents are fictional, not NYSDFS material. The existing implementation uses MiniLM embeddings, Chroma cosine search, and Ollama generation through loopback. A Streamlit interface exposes retrieved passages and citations.

## Trace the request

1. Load Markdown, TXT, or text-based PDF documents and preserve source/page metadata.
2. Split text into 600-character windows with 100-character overlap. Characters are not tokens; a tokenizer-aware splitter would be a useful next comparison.
3. Embed and persist the chunks locally. Embed the question with the same model.
4. Retrieve up to three passages using cosine similarity and a provisional 0.25 threshold.
5. Build a prompt containing the question and labeled evidence, then call a downloaded local Ollama model.
6. Display the answer and source passages. If retrieval produces no hits, return the abstention response without calling the model.

## Added baseline

`lexical_baseline.py` provides a dependency-free BM25 retrieval comparison using the same document chunks and the same eight evaluation questions. It retrieves passages; it does not call a language model, create semantic embeddings, or generate answers.

```powershell
python lexical_baseline.py --top-k 3
python -m unittest discover -s tests -p test_pipeline.py -v
python -m unittest discover -s tests -p test_lexical_baseline.py -v
```

In the current build workspace, BM25 retrieved the expected document for 6/6 answerable questions and returned no hits for 2/2 absent questions. This tiny set cannot establish general retrieval quality. It shows why an inexpensive keyword baseline belongs in the experiment. Its score threshold is provisional, not tuned on an independent validation set. Document hits do not prove answer accuracy or passage sufficiency.

## Current verification

Six existing dependency-free pipeline tests and three added baseline tests passed. The lexical evaluation completed and its raw results are committed in `evaluation/lexical_results.json`.

The full test suite could not run in this build workspace because Streamlit and Chroma are not installed. Semantic model retrieval and Ollama generation were not rerun. Earlier repository validation records are retained as historical reports; their claims are not presented as current-session results. No claim of complete answer quality or production readiness is made.

## Interview tradeoffs

- BM25 is cheap, inspectable, and useful for exact terminology; semantic retrieval is better suited to evaluating paraphrases. Neither approach guarantees relevant evidence.
- Overlap can preserve context but adds redundant passages and index size.
- A small local model avoids paid inference APIs, but quality, memory use, and latency must be measured on the owner's hardware.
- Source labels help review; they do not prove every generated sentence is supported.
- Prompt instructions and a similarity threshold do not fully prevent prompt injection or hallucination.
- Production access controls must filter documents before retrieval, not merely hide citations afterward.

## Resume wording after review

“Extended a local document RAG learning project with cited retrieval, abstention controls, and a reproducible BM25 baseline evaluated separately from generated answer quality.”

Next experiments: expand the labeled set, include hard negatives and paraphrases, compare BM25/semantic/hybrid retrieval on held-out questions, and manually score generated claims for source support. MCP remains a future extension.

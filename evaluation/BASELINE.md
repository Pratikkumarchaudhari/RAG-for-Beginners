# Initial retrieval baseline

Run on 5 October 2026 using real `sentence-transformers/all-MiniLM-L6-v2` CPU embeddings, Chroma cosine search, and the fictional governance corpus. Ingestion produced six passages from three files with 600 character windows and 100 character overlap.

| Setting | Expected source retrieved | Absent questions rejected |
|---|---|---|
| Top-k 1, similarity threshold 0.25 | 6 of 6 answerable questions | 2 of 2 absent questions |
| Top-k 3, similarity threshold 0.25 | 6 of 6 answerable questions | 2 of 2 absent questions |

This tiny source-level evaluation is not answer accuracy, a general benchmark, or evidence of production readiness. It does not establish that the exact supporting passage was sufficient or that a generated answer was correct. Both configurations tied on this set; there is no measured basis here to claim one is better.

Commands:

```bash
python ingestion_pipeline.py
python evaluate.py --top-k 3 --threshold 0.25
python evaluate.py --top-k 1 --threshold 0.25 --output evaluation/results_k1.json
```

The labeled questions are in `questions.json`. Generated answer evaluation was not run because local Ollama was unavailable. Expand the question set, include paraphrases and difficult absent questions, and manually assess answer support before reporting broader quality metrics.

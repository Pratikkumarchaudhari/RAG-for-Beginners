# Learning guide

## Explain the pipeline

An embedding represents the meaning of a passage as numbers. A vector database compares the question vector with passage vectors. Chroma returns passages with source metadata; Ollama uses those passages to draft an answer. The UI lets a reader inspect what was retrieved.

Read `rag/pipeline.py` in this order: `load_chunks`, `split_text`, `LocalIndex.rebuild`, `LocalIndex.search`, `make_messages`, `generate_answer`. Then read the UI and evaluator. Try retrieval inspection mode first so you can see retrieval errors separately from generation errors.

## Exercises that produce meaningful commits

1. Run the initial demo and document your hardware and actual results.
2. Add a fictional governance procedure and three labeled questions.
3. Compare top-k 1 and 3 using the evaluator. Explain when additional passages help or distract.
4. Rebuild with chunk sizes 400 and 600; compare source hit rate and inspect passages.
5. Review answers to absent questions and improve the threshold based on observed evidence.
6. Add PDF extraction tests using a small generated public sample.
7. After the local RAG works, implement and test an MCP search tool.

Commit completed work with descriptive messages. Do not backdate commits or create empty activity commits. Future updates happen when actual work is completed; no unattended commit schedule is configured.

## Troubleshooting

| Symptom | Action |
|---|---|
| Python command unavailable | Install Python 3.11 or 3.12 and reopen the terminal. Use the virtual environment executable in the README. |
| Ollama connection error | Start the local server, confirm port 11434, and download the selected model. |
| Port already in use | Quit the Ollama desktop app or stop the existing local server before starting the server with cloud disabled. |
| Embedding download failure | Initial model downloads need internet access. Retry on your own computer if this environment blocks the model host. |
| Scanned PDF returns no text | Use text based PDFs for version 1; OCR is not included. |
| Wrong document appears | Inspect passages, compare top-k, verify your corpus, and rebuild after edits. |
| Slow answers or memory pressure | Close other programs or choose a smaller downloaded model. Do not buy hardware for this project. |
| Answer has unsupported claims | Check source support. Tune retrieval and prompts, and document the failure. Citations alone are not validation. |

## Resume and interview use

Describe this as a personal learning project, not a production employer deployment. Review and understand AI assisted code. Do not claim measured accuracy, deployed users, MCP implementation, or independent authorship without evidence.

After you have run and verified it, a possible bullet is: “Implemented and tested a local RAG prototype for sample data governance documents using Python, Sentence Transformers, Chroma, Streamlit, and Ollama, with source references and a retrieval evaluation set.” Add metrics only after measuring them.

In an interview explain why embeddings and generation are separate, how overlapping passages affect retrieval, how source metadata is preserved, what happens when evidence is missing, and what your evaluation does not measure.

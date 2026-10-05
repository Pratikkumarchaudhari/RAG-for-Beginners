# Data Governance RAG Assistant

A beginner portfolio project that retrieves evidence from documents and uses a **local language model** to answer questions with source references. Built with Python, Streamlit, Sentence Transformers, Chroma, and Ollama. No paid APIs, cloud inference, or hosting are required.

**Status:** implementation added; see [validation](documentation/VALIDATION.md) for checks actually completed. Local model generation must be verified on the computer running Ollama. MCP is a future extension, not an implemented feature.

## What you can learn

- Read TXT, Markdown, and text based PDFs; preserve source and page metadata.
- Split documents into overlapping passages and create local embeddings.
- Persist vectors and perform semantic retrieval with Chroma.
- Send retrieved evidence to a local model and display supporting passages.
- Evaluate retrieval separately from generated answer quality.

The default corpus contains **fictional governance procedures**, not DFS documents. Your original company examples remain in `docs/`; use `--documents docs` to index them instead. Review their accuracy and redistribution rights before using those examples in a portfolio demo.

## Requirements

Python 3.11 or 3.12, Git, and [Ollama](https://ollama.com/download). VS Code is optional. Allow several GB of disk space for packages and models. Memory and response speed depend on the model and your computer; a GPU is optional for this small demo. No plugin installation or billing account is needed.

## Quick start on Windows PowerShell

```powershell
git clone https://github.com/Pratikkumarchaudhari/RAG-for-Beginners.git
cd RAG-for-Beginners
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install Ollama from its official website, then **quit the running Ollama app**. In a separate PowerShell terminal start a local only server:

```powershell
$env:OLLAMA_NO_CLOUD="1"
ollama serve
```

Leave that terminal running. In your project terminal:

```powershell
ollama pull qwen2.5:1.5b
.\.venv\Scripts\python.exe ingestion_pipeline.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open the local URL shown by Streamlit. Ask **Who approves access to a dataset?** Review both the answer and the retrieved evidence. The Qwen model is a small starter choice; test it on your hardware before making quality claims.

## macOS or Linux

After installing Ollama, stop any existing Ollama server before starting this one:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
OLLAMA_NO_CLOUD=1 ollama serve
```

In another terminal:

```bash
ollama pull qwen2.5:1.5b
.venv/bin/python ingestion_pipeline.py
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

On Linux, if pip attempts to install large CUDA packages, install a compatible CPU build of PyTorch first using the command from [PyTorch's official installation selector](https://pytorch.org/get-started/locally/), then install this project's requirements. CUDA is unnecessary for the current embedding code.

## Using your own documents

Put public or fictional documents in a local folder, then select that folder in the sidebar and choose **Build or replace local index**. Or run:

```bash
python ingestion_pipeline.py --documents local_documents
```

Rebuilding replaces the index; it does not append to it. Rebuild after changing source files. `local_documents/` and the index are ignored by Git. TXT and Markdown use page 1; PDF references use physical page numbers. Scanned PDFs need OCR and are not supported in version 1.

## Evaluation and tests

```bash
python -m unittest discover -s tests -v
python evaluate.py --top-k 3 --threshold 0.25
python evaluate.py --top-k 1 --threshold 0.25 --output evaluation/results_k1.json
python evaluate.py --generate
```

Evaluation assumes the default governance corpus. Source hit rate measures whether the expected document appears in retrieved results, **not answer accuracy**. Review generated claims, citation support, and abstention manually. The default similarity threshold is provisional. Compare settings before publishing metrics. Runtime reports are ignored by Git; commit a reviewed summary if you want to share results.

## Project map

| Path | Purpose |
|---|---|
| `rag/pipeline.py` | Ingestion, chunking, embeddings, vector search, local generation |
| `ingestion_pipeline.py` | Command line index builder |
| `app.py` | Streamlit interface with evidence inspection |
| `sample_documents/` | Fictional governance learning corpus |
| `evaluate.py` and `evaluation/questions.json` | Small retrieval and optional generation evaluation |
| `tests/` | Tests for chunking, metadata, abstention, and local model restrictions |
| [Technology comparison](documentation/TECHNOLOGY_COMPARISON.md) | Choices, alternatives, tradeoffs, and cost controls |
| [Learning guide](documentation/LEARNING_GUIDE.md) | Concepts, exercises, troubleshooting, and honest resume use |

## Limits and costs

Model files and Python packages are downloaded initially; inference and embeddings run locally afterward. The application only calls Ollama at `127.0.0.1`, blocks cloud model tags, and bypasses HTTP proxies. **Run Ollama with cloud features disabled**, as shown above. No remote inference endpoint can be entered in the UI. Existing computer, electricity, and internet resources are still used.

An unsupported question may retrieve a vaguely related passage. Prompting and a similarity threshold cannot guarantee factual answers or prevent every document prompt injection. This educational application has no enterprise authorization, OCR, or production deployment. Do not use private employer data in the public repository.

## References and attribution

Original implementation developed with AI assistance; repository owner should review and explain the code before claiming independent expertise. Learning references: [LangChain RAG from Scratch](https://github.com/langchain-ai/rag-from-scratch), [LlamaIndex](https://github.com/run-llama/llama_index), and official tool documentation linked in the comparison. No tutorial repository was copied or forked to represent original work.

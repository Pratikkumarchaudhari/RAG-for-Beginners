# Validation record

Checked 5 October 2026 in a Linux Python 3.12 workspace. This is implementation and retrieval validation, not a claim of complete generated answer validation.

## Completed checks

- Ten automated tests passed with `python -m unittest discover -s tests -v`.
- Python compilation and `git diff --check` passed.
- Chroma local persistence, explicit vector search, and index replacement passed. Automated storage tests use synthetic vectors; they do not assess semantic model quality.
- Streamlit initial rendering and question-to-answer flow passed through AppTest. The flow test stubs retrieval and generation.
- Real Sentence Transformers MiniLM embeddings downloaded and ran on CPU; the default three documents produced six indexed passages.
- Real semantic retrieval evaluation ran with top-k 1 and 3 and a 0.25 similarity threshold. See [baseline](../evaluation/BASELINE.md).
- Dependency consistency check passed. Direct dependency versions are recorded in `requirements.txt`.

## Runtime observations

The default PyTorch installation pulled GPU dependencies and failed to import in this environment. Installing the official CPU build resolved the import failure; the working build was `torch 2.14.1+cpu`. The environment's SOCKS proxy also needed `socksio` for model downloads. These are workspace observations, not reasons to purchase hardware or subscribe to a service.

## Not yet verified

Ollama is not installed in this workspace. Actual Qwen model generation, claim support, citation correctness, response latency, and local model memory requirements remain unverified. The HTTP request contract was tested with a stub response; this does not prove model answer quality. Follow the README on the owner's computer and run `python evaluate.py --generate` before describing the project as fully tested.

Windows setup commands are documented but have not been executed on the owner's computer. MCP, OCR, production hosting, authentication, and enterprise access controls are not implemented. No billing service or scheduled commit automation was configured.

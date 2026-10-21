# Browser governance Q&A

Open index.html. No account, paid API, model download, or server is required. Source documents are embedded in governance/corpus.js. governance/qa-engine.js implements lexical document retrieval and complete-sentence extraction; governance/qa-ui.js renders suggestions, questions, citations, and evidence using DOM textContent.

Questions are independent: conversation history is shown for convenience but is not used as model context. No generated model answer is produced. The full Python/Ollama implementation remains separate.

Run: `node --test web-demo/tests/qa-engine.test.cjs` from the repository root.

# LocalRAG — Local AI Chat + PDF RAG

LocalRAG is a local-first document assistant with two modes:

- **LLM Only:** chat with Ollama's Llama 3.2 model without retrieving document passages.
- **LLM + PDF (RAG):** upload a text-based PDF, retrieve relevant page-level chunks with MiniLM and ChromaDB, and generate an answer grounded in those passages.

The project keeps the original command-line TXT indexing workflow and adds a web UI with Flask.

## Features

- Modern dark responsive web interface.
- Switch between LLM Only and LLM + PDF (RAG).
- Select or drag-and-drop a PDF (up to 20 MB).
- Extract text page-by-page and retain page metadata.
- Sentence-aware chunking using the existing `chunker.py`.
- `sentence-transformers/all-MiniLM-L6-v2` embeddings.
- A dedicated ChromaDB collection for the active PDF, separate from the TXT collection.
- Source filename and page references in RAG responses.
- Greetings in RAG mode are answered conversationally without PDF retrieval.
- RAG requests abstain when no sufficiently relevant passages are retrieved.
- Local inference through Ollama and `llama3.2`.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend API | Python, Flask, Flask-CORS |
| Local LLM | Ollama, Llama 3.2 |
| PDF text extraction | pypdf |
| Embeddings | Sentence Transformers, all-MiniLM-L6-v2 |
| Vector database | ChromaDB |
| Existing TXT workflow | `indexer.py`, `main.py`, `vector_store.py` |

## Project structure

```text
LocalRAG_ReadyToRun/
├── app.py                    # Flask API for UI, LLM chat and PDF RAG
├── chunker.py                # Existing text chunker
├── embedding_model.py        # MiniLM model and embedding helper
├── indexer.py                # Existing TXT document indexer
├── llm.py                    # Existing context-grounded LLM helper
├── main.py                   # Existing CLI RAG application
├── retriver.py               # Existing in-memory retrieval diagnostic
├── vector_store.py            # Existing TXT ChromaDB operations
├── requirements.txt
├── setup_windows.bat
├── start_localrag.bat
├── .gitignore
├── documents/                # Sample TXT files for the CLI workflow
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## Requirements

- Windows 10/11 or another OS that supports Python and Ollama.
- Python 3.11 or 3.12 is recommended for broad ML-package compatibility. Your installed Python version may work, but the newest Python release can lag behind some ML dependency wheels.
- Ollama installed.
- The `llama3.2` model downloaded.
- Internet access on first setup to install Python packages and download model weights.
- Approximately several GB of free disk space may be needed for Python/ML dependencies and model files.

## Windows setup

### 1. Extract the ZIP

Extract the complete ZIP to a normal writable folder, for example:

```text
C:\Users\YourUser\Documents\LocalRAG_ReadyToRun
```

Avoid placing the project inside a read-only or protected system folder.

### 2. Create the environment and install dependencies

Double-click `setup_windows.bat`, or run these commands in PowerShell from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation, you can avoid activation and use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Install and start Ollama

Check whether Ollama is installed:

```powershell
ollama --version
```

Download Llama 3.2 if necessary:

```powershell
ollama pull llama3.2
```

Check that the model is available:

```powershell
ollama list
```

Ollama normally runs as a background service on `http://localhost:11434`. If it is not running, open the Ollama application first.

### 4. Start LocalRAG

Double-click `start_localrag.bat`.

It opens separate terminal windows for the Flask API and static frontend server, then opens the UI in your browser.

The web app address is:

```text
http://localhost:5500
```

The Flask API runs at:

```text
http://127.0.0.1:5000
```

To start manually instead, open two terminals at the project root.

**Terminal 1 — backend:**

```powershell
.\.venv\Scripts\python.exe app.py
```

**Terminal 2 — frontend:**

```powershell
cd frontend
python -m http.server 5500
```

Then open `http://localhost:5500`.

Keep both terminal windows running while using the app. Stop either server with `Ctrl+C` in its terminal.

## How to use the web app

### LLM Only

1. Select **LLM Only** in the sidebar.
2. Type a greeting or general question.
3. Press Enter or click Send.
4. LocalRAG sends the prompt to the local Ollama model.

### LLM + PDF (RAG)

1. Use **Upload a PDF** in the sidebar.
2. Wait for text extraction, chunking, embedding and indexing to finish.
3. Select **LLM + PDF**.
4. Ask a question that the PDF can answer.
5. Read the response and inspect the source filename and page references shown below it.

When a different PDF is uploaded, the dedicated PDF collection is cleared before the new document is indexed. The TXT collection named `localrag_documents` is not used for PDF-mode retrieval.

### Remove the current PDF

Click the `×` beside the selected PDF. The active PDF collection is cleared.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check backend, Ollama and model availability |
| `POST` | `/api/chat` | LLM Only or PDF RAG response |
| `POST` | `/api/upload` | Upload and index a PDF (`multipart/form-data`, field `file`) |
| `GET` | `/api/document` | Read active PDF metadata |
| `POST` | `/api/document/reset` | Clear the active PDF index |

## Existing command-line TXT workflow

The original TXT workflow remains available:

```powershell
.\.venv\Scripts\python.exe indexer.py
.\.venv\Scripts\python.exe main.py
```

It indexes `.txt` files from `documents/` into the existing `localrag_documents` ChromaDB collection. This is separate from the web UI's PDF collection.

## Important limitations

- **Scanned PDFs:** pypdf extracts selectable text. PDFs made only of scanned images need OCR; OCR is not included in this version.
- **PDF size:** the web upload limit is 20 MB.
- **Local privacy:** inference is sent to the Ollama service on your machine. First-time Python/model downloads require internet. Do not expose the Flask development server to an untrusted network.
- **Retrieval threshold:** the cosine-distance cutoff is experimental, not a calibrated confidence score. Relevant passages can occasionally be missed, and irrelevant passages may occasionally be retrieved.
- **Grounding:** the prompt asks the model to answer from retrieved evidence, but this cannot guarantee factual correctness.
- **Conversation history:** LLM Only mode sends a short recent history. RAG answers are grounded in the currently indexed PDF; prior chat text is not used as document evidence.
- **One active PDF:** the first version intentionally supports one active PDF at a time for a local single-user workflow.

## Troubleshooting

### “Backend unavailable”
- Start `app.py` and confirm the Flask terminal has no traceback.
- Check `http://127.0.0.1:5000/api/health`.
- Ensure port 5000 is not occupied by another process.

### “Ollama unavailable”
- Open the Ollama app or start its service.
- Verify `ollama list`.
- Check that `http://localhost:11434/api/tags` is reachable.

### “Model not found”
Run:

```powershell
ollama pull llama3.2
```

### PDF processing says no selectable text
The PDF may be scanned. Use a text-based PDF or add OCR support as a future improvement.

### Model downloads fail or Python package installation fails
Use Python 3.11 or 3.12 in a fresh virtual environment, update pip, and rerun the requirements installation. Model weights are downloaded on first use and may take time.

## Project note

This is a learning project intended to demonstrate local LLM integration, PDF ingestion, chunking, embeddings, vector search, and evidence-grounded answering. The retrieval threshold and answer quality should be evaluated on representative documents and questions before relying on it for important decisions.

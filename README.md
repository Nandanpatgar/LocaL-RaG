# LocalRAG — Local AI and PDF-Based Question Answering

LocalRAG is a locally running AI-powered document question-answering application that enables users to interact with PDF documents using natural language. It combines Large Language Models (LLMs), semantic search, vector databases, and Retrieval-Augmented Generation (RAG) to generate context-aware answers grounded in document content.

The application provides two interaction modes: **LLM Only**, for general conversational queries, and **LLM + PDF (RAG)**, for answering questions using an uploaded document as the primary source of evidence.

By running the language model locally through Ollama, LocalRAG offers a practical approach to document intelligence without requiring a cloud-based LLM API.

## Table of Contents

* [Overview](#overview)
* [Problem Statement](#problem-statement)
* [Objectives](#objectives)
* [Key Features](#key-features)
* [System Architecture](#system-architecture)
* [Technology Stack](#technology-stack)
* [How It Works](#how-it-works)
* [Project Structure](#project-structure)
* [Prerequisites](#prerequisites)
* [Installation and Setup](#installation-and-setup)
* [Running the Application](#running-the-application)
* [Application Modes](#application-modes)
* [API Endpoints](#api-endpoints)
* [Privacy and Limitations](#privacy-and-limitations)
* [Future Enhancements](#future-enhancements)
* [Author](#author)

## Overview

Reading and extracting information from lengthy documents can be time-consuming. Traditional document readers require users to manually search through pages to locate relevant information.

LocalRAG addresses this challenge by allowing users to upload a PDF and ask questions about its contents through a conversational interface.

The system extracts text from the uploaded document, divides it into smaller chunks, generates vector embeddings, and stores them in a vector database. When a question is submitted, relevant document chunks are retrieved and supplied to a locally running language model to generate a context-aware response.

The application also supports general conversations without requiring document context.

## Problem Statement

Users frequently need to retrieve specific information from lengthy documents, academic materials, reports, and reference PDFs. Manual searching is inefficient, while general-purpose language models may generate answers that are not supported by the document being examined.

A document question-answering system is needed that can retrieve relevant information, generate answers using document evidence, and operate locally to reduce dependence on external AI services.

## Objectives

* Develop a conversational interface for interacting with PDF documents.
* Enable semantic retrieval of relevant document passages.
* Generate context-aware answers using a locally running LLM.
* Provide separate modes for general conversations and document-based question answering.
* Maintain document isolation when switching between uploaded PDFs.
* Reduce dependence on cloud-based language model APIs.
* Provide a modular architecture that supports future improvements.

## Key Features

### 1. Dual Chat Modes

**LLM Only Mode**

* Supports general conversational interactions.
* Uses Llama 3.2 through Ollama.
* Does not require an uploaded PDF as context.

**LLM + PDF (RAG) Mode**

* Accepts questions about an uploaded PDF.
* Retrieves relevant passages from the indexed document.
* Uses retrieved context to generate document-grounded answers.
* Can indicate when sufficient supporting evidence is unavailable, depending on retrieval and verification behavior.

### 2. PDF Upload and Processing

* Upload PDF documents through the web interface.
* Extract text from supported, text-based PDFs.
* Divide extracted content into smaller chunks.
* Generate embeddings for semantic retrieval.
* Index document chunks for question answering.

### 3. Semantic Search

The application uses sentence embeddings to represent document passages and queries as numerical vectors. These representations allow the retrieval system to identify semantically relevant content, even when the question does not use exactly the same words as the document.

### 4. Local Language Model

Ollama provides the local inference interface for Llama 3.2. This reduces dependence on external LLM APIs and allows the application to generate responses on the local machine.

### 5. Vector Database

ChromaDB stores and retrieves vector representations of document chunks, supporting semantic search over indexed content.

### 6. Interactive Web Interface

* Dedicated chat interface.
* Mode selection between general chat and document-based chat.
* PDF upload controls.
* Conversational message display.
* Document status information.

### 7. Document Isolation

The document workflow is designed to keep the active PDF's retrieved context separate from previously uploaded PDFs. This behavior should be maintained and tested when modifying the indexing or retrieval pipeline.

## System Architecture

LocalRAG follows a modular architecture consisting of a frontend, backend, document-processing pipeline, retrieval system, vector database, and local language model.

```text
                    USER
                      |
                      v
             WEB USER INTERFACE
              HTML, CSS, JavaScript
                      |
                      v
                FLASK BACKEND
                      |
             +--------+--------+
             |                 |
             v                 v
        LLM ONLY MODE      PDF RAG MODE
             |                 |
             |                 v
             |           PDF UPLOAD
             |                 |
             |                 v
             |           TEXT EXTRACTION
             |                 |
             |                 v
             |            TEXT CHUNKING
             |                 |
             |                 v
             |          EMBEDDING GENERATION
             |                 |
             |                 v
             |             CHROMADB
             |                 |
             |                 v
             |          SEMANTIC RETRIEVAL
             |                 |
             |                 v
             +---------> OLLAMA
                           |
                           v
                      LLAMA 3.2
                           |
                           v
                    GENERATED ANSWER
                           |
                           v
                     CHAT INTERFACE
```

### Architecture Components

| Component       | Responsibility                                                                 |
| --------------- | ------------------------------------------------------------------------------ |
| Frontend        | Provides the user interface for chatting, selecting modes, and uploading PDFs. |
| Flask backend   | Handles HTTP requests and coordinates application operations.                  |
| PDF processing  | Extracts text and prepares document content for indexing.                      |
| Text chunking   | Divides extracted text into smaller, manageable passages.                      |
| Embedding model | Converts text into numerical vector representations.                           |
| ChromaDB        | Stores and retrieves vector representations of document chunks.                |
| Ollama          | Provides local access to the language model.                                   |
| Llama 3.2       | Generates conversational and context-aware responses.                          |

## Technology Stack

| Category               | Technology            | Purpose                                 |
| ---------------------- | --------------------- | --------------------------------------- |
| Frontend               | HTML5                 | Web page structure                      |
| Frontend               | CSS3                  | Layout and styling                      |
| Frontend               | JavaScript            | User interactions and API communication |
| Backend                | Python                | Application logic                       |
| Backend Framework      | Flask                 | HTTP API and backend services           |
| Cross-Origin Requests  | Flask-CORS            | Cross-origin request handling           |
| Language Model Runtime | Ollama                | Local LLM execution                     |
| Language Model         | Llama 3.2             | Natural language response generation    |
| Embeddings             | Sentence Transformers | Semantic text representation            |
| Embedding Model        | `all-MiniLM-L6-v2`    | Text embedding generation               |
| Vector Database        | ChromaDB              | Vector storage and retrieval            |
| PDF Processing         | pypdf                 | PDF text extraction                     |
| HTTP Client            | Requests              | HTTP communication                      |
| Development Tools      | VS Code, Git, GitHub  | Development and version control         |

## How It Works

### Phase 1: Document Ingestion

When a user uploads a PDF, the backend processes the document.

1. The PDF is received by the Flask application.
2. Text is extracted from the document.
3. The extracted text is divided into smaller chunks.
4. Each chunk is converted into an embedding.
5. The embeddings and associated metadata are indexed in ChromaDB.

### Phase 2: Question Processing

When the user submits a question in RAG mode:

1. The question is received by the backend.
2. The question is converted into an embedding.
3. The retrieval system searches for relevant document chunks.
4. The most relevant passages are selected according to the retrieval configuration.
5. The retrieved passages are supplied to the language model as context.

### Phase 3: Answer Generation

The language model uses the question and retrieved context to formulate a response.

The objective is to generate an answer supported by the available document evidence rather than relying exclusively on the model's general knowledge.

If the retrieved passages do not contain sufficient evidence, the system should avoid presenting an unsupported answer as a confirmed document fact.

### Phase 4: Response Delivery

The generated response is returned by the Flask backend and displayed in the frontend chat interface.

In LLM Only mode, the application uses the local language model without retrieving PDF context.

## Project Structure

The project is organized into frontend files, Python modules, configuration files, and runtime data directories.

```text
LocalRAG_ReadyToRun/
|
|-- app.py
|-- main.py
|-- chunker.py
|-- embedding_model.py
|-- indexer.py
|-- retrieval.py
|-- vector_store.py
|-- llm.py
|
|-- frontend/
|   |-- index.html
|   |-- style.css
|   |-- script.js
|
|-- documents/
|-- chroma_db/
|
|-- requirements.txt
|-- .gitignore
|-- setup_windows.bat
|-- start_localrag.bat
|-- README.md
```

*The structure above describes the intended organization. Runtime directories and additional files may vary depending on the application version.*

### Important Files

| File                  | Responsibility                                  |
| --------------------- | ----------------------------------------------- |
| `app.py`              | Flask application and API endpoints             |
| `main.py`             | Command-line RAG workflow                       |
| `chunker.py`          | Text chunking                                   |
| `embedding_model.py`  | Embedding model initialization and generation   |
| `indexer.py`          | Document indexing workflow                      |
| `retrieval.py`        | Semantic retrieval operations                   |
| `vector_store.py`     | ChromaDB operations                             |
| `llm.py`              | Local language model interaction                |
| `frontend/index.html` | Web interface structure                         |
| `frontend/style.css`  | Frontend styling                                |
| `frontend/script.js`  | Frontend interactions and backend communication |
| `requirements.txt`    | Python dependencies                             |
| `setup_windows.bat`   | Windows environment setup                       |
| `start_localrag.bat`  | Application startup script                      |

## Prerequisites

Ensure that the following software is installed:

* Python 3.11 or another Python version compatible with the installed dependencies.
* Ollama.
* Git, if cloning the repository.
* A modern web browser.
* Sufficient RAM and disk space to run the embedding model, vector database, and local LLM.

The first execution may require downloading Python packages, the embedding model, and the Llama model.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Nandanpatgar/LocaL-RaG.git
cd LocaL-RaG
```

If you are using the supplied project ZIP instead, extract it and open the extracted project directory in VS Code.

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use a Command Prompt terminal and activate the environment with:

```bat
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

With the virtual environment activated, run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install and Start Ollama

Install Ollama from its official website:

https://ollama.com/

Check whether Ollama is available:

```powershell
ollama --version
```

Download the required model:

```powershell
ollama pull llama3.2
```

Verify that the model is available:

```powershell
ollama list
```

Ensure the Ollama service is running before launching the application.

## Running the Application

### Option 1: Windows Startup Script

If the supplied startup scripts are present, run the setup script first:

```powershell
.\setup_windows.bat
```

Then start the application:

```powershell
.\start_localrag.bat
```

The startup script is intended to launch the backend and frontend separately.

Keep the server terminal windows open while using the application.

### Option 2: Run the Backend and Frontend Manually

**Terminal 1: Start Flask**

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

The backend should be available at:

```text
http://127.0.0.1:5000
```

**Terminal 2: Start the Frontend**

Open another terminal in the project root:

```powershell
cd frontend
python -m http.server 5500
```

Open the application in your browser:

```text
http://localhost:5500
```

Both servers must remain running during use.

## Application Modes

### LLM Only

Use this mode for general questions and conversational interactions.

Example:

```text
User: Hi! Introduce yourself.

Assistant: Responds conversationally using the local language model.
```

The answer does not depend on an uploaded PDF.

### LLM + PDF (RAG)

Use this mode when you want to ask questions about an uploaded document.

Example:

```text
User: Upload a PDF containing information about machine learning.

User: What is supervised learning?

Assistant: Retrieves relevant passages from the PDF and generates
an answer using the retrieved document context.
```

If the document does not contain enough information to answer a factual question, the system should indicate that sufficient evidence was not found.

The quality of the answer depends on document text extraction, chunking, retrieval quality, and language model behavior.

## API Endpoints

The Flask backend exposes HTTP endpoints for health monitoring, chat, and document operations.

| Method | Endpoint      | Purpose                                                                               |
| ------ | ------------- | ------------------------------------------------------------------------------------- |
| GET    | `/api/health` | Checks backend and Ollama status, model availability, and document-index information. |
| POST   | `/api/chat`   | Processes a chat message in the selected application mode.                            |
| POST   | `/api/upload` | Handles PDF upload and processing, if implemented in the current backend version.     |

### Health Check

Request:

```http
GET /api/health
```

Example response:

```json
{
  "backend": "online",
  "document": null,
  "indexed_chunks": 0,
  "model": "llama3.2",
  "model_available": true,
  "ollama": "online"
}
```

The document and chunk counts depend on the current application state.

### Chat Request

The chat endpoint accepts a JSON request containing the message and selected mode.

Illustrative request:

```json
{
  "message": "Explain the main topic of this document.",
  "mode": "rag"
}
```

For general conversation, the frontend should send the mode configured for LLM Only.

The exact request and response formats must match the implementation in `app.py` and `frontend/script.js`.

## Privacy and Limitations

### Privacy

* The language model runs locally through Ollama.
* Document processing and vector retrieval are intended to run on the local machine.
* Local execution reduces the need to send document content to a cloud-based LLM provider.

However, local model execution alone does not guarantee that every component is offline. Network requests, package downloads, or external retrieval services may introduce external dependencies if enabled in the implementation.

### Limitations

* Text extraction quality depends on the PDF's structure and content.
* Scanned PDFs may require OCR, which is not guaranteed to be supported.
* Retrieval may miss relevant passages or select irrelevant content.
* The language model can still produce incorrect or unsupported statements.
* Semantic similarity is not a guarantee that retrieved content supports a claim.
* Performance depends on available system resources and model size.
* Source references are useful only when the corresponding metadata is preserved and returned by the backend.
* Large documents may increase indexing time and memory usage.

LocalRAG should be evaluated using known-answer questions, unsupported questions, contradictory evidence, and ambiguous queries before being relied upon for high-stakes decisions.

## Future Enhancements

Potential improvements include:

* Support for multiple simultaneous documents.
* OCR support for scanned PDFs.
* Improved retrieval using hybrid keyword and semantic search.
* Reranking of retrieved passages.
* More precise source and page-level citations.
* Better handling of contradictory document evidence.
* Document-level and claim-level answer verification.
* Automated evaluation using a curated question-and-answer dataset.
* Support for additional file formats.
* Configurable chunk sizes and retrieval thresholds.
* Performance monitoring and retrieval diagnostics.

## Author

**Nandan Patgar**

B.E. — Artificial Intelligence and Machine Learning

Vivekananda College of Engineering and Technology (VCET), Puttur

GitHub: https://github.com/Nandanpatgar

---

## License

Add a `LICENSE` file to the repository if you intend to distribute the project under a specific open-source license.

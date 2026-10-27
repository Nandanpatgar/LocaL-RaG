const API_BASE = "http://127.0.0.1:5000";

const state = {
  mode: "llm",
  document: null,
  messages: [],
  isSending: false,
  toastTimer: null
};

const el = {
  llmModeButton: document.getElementById("llmModeButton"),
  ragModeButton: document.getElementById("ragModeButton"),
  currentModeLabel: document.getElementById("currentModeLabel"),
  welcomeTitle: document.getElementById("welcomeTitle"),
  welcomeDescription: document.getElementById("welcomeDescription"),
  welcomeScreen: document.getElementById("welcomeScreen"),
  suggestionGrid: document.getElementById("suggestionGrid"),
  pdfInput: document.getElementById("pdfInput"),
  uploadArea: document.getElementById("uploadArea"),
  uploadNote: document.getElementById("uploadNote"),
  documentCard: document.getElementById("documentCard"),
  documentName: document.getElementById("documentName"),
  documentSize: document.getElementById("documentSize"),
  documentStatus: document.getElementById("documentStatus"),
  removeDocumentButton: document.getElementById("removeDocumentButton"),
  uploadProgress: document.getElementById("uploadProgress"),
  progressText: document.getElementById("progressText"),
  newChatButton: document.getElementById("newChatButton"),
  messageInput: document.getElementById("messageInput"),
  sendButton: document.getElementById("sendButton"),
  messagesContainer: document.getElementById("messagesContainer"),
  chatWrapper: document.getElementById("chatWrapper"),
  composerModeIcon: document.getElementById("composerModeIcon"),
  composerModeText: document.getElementById("composerModeText"),
  connectionDot: document.getElementById("connectionDot"),
  connectionTitle: document.getElementById("connectionTitle"),
  connectionSubtitle: document.getElementById("connectionSubtitle"),
  topStatusDot: document.getElementById("topStatusDot"),
  topStatusText: document.getElementById("topStatusText"),
  refreshStatusButton: document.getElementById("refreshStatusButton"),
  toast: document.getElementById("toast")
};

function showToast(message, isError = false) {
  el.toast.textContent = message;
  el.toast.classList.toggle("error", isError);
  el.toast.classList.add("visible");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => el.toast.classList.remove("visible"), 4200);
}

function setMode(mode) {
  if (!["llm", "rag"].includes(mode)) return;
  state.mode = mode;

  el.llmModeButton.classList.toggle("active", mode === "llm");
  el.ragModeButton.classList.toggle("active", mode === "rag");

  if (mode === "llm") {
    el.currentModeLabel.textContent = "LLM Only";
    el.welcomeTitle.innerHTML = 'Intelligence, <span>without limits.</span>';
    el.welcomeDescription.textContent =
      "Ask questions, explore ideas, and learn something new with your local AI assistant.";
    el.composerModeIcon.className = "fa-solid fa-wand-magic-sparkles";
    el.composerModeText.textContent = "General AI conversation";
    el.messageInput.placeholder = "Ask anything…";
    el.uploadNote.textContent = state.document
      ? "PDF indexed and ready whenever you switch to LLM + PDF mode."
      : "Upload a document to ask questions about its contents.";
  } else {
    el.currentModeLabel.textContent = "LLM + PDF";
    el.welcomeTitle.innerHTML = 'Your documents, <span>understood.</span>';
    el.welcomeDescription.textContent =
      "Ask questions about your PDF and receive answers grounded in relevant document evidence.";
    el.composerModeIcon.className = "fa-solid fa-file-circle-check";
    el.composerModeText.textContent = "Document-grounded conversation";
    el.messageInput.placeholder = "Ask a question about your PDF…";
    el.uploadNote.textContent = state.document
      ? `${state.document.page_count} pages · ${state.document.chunk_count} indexed chunks.`
      : "Upload a PDF to prepare for evidence-based conversations.";
  }

  renderMessages();
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function setDocumentStatus(text, kind = "") {
  el.documentStatus.textContent = text;
  el.documentStatus.classList.toggle("ready", kind === "ready");
  el.documentStatus.classList.toggle("error", kind === "error");
}

async function handlePDFSelection(file) {
  if (!file) return;

  const isPDF = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
  if (!isPDF) {
    showToast("Please select a PDF document.", true);
    el.pdfInput.value = "";
    return;
  }

  if (file.size > 20 * 1024 * 1024) {
    showToast("This PDF is larger than the 20 MB limit.", true);
    el.pdfInput.value = "";
    return;
  }

  state.document = null;
  el.uploadArea.hidden = true;
  el.documentCard.hidden = false;
  el.documentName.textContent = file.name;
  el.documentSize.textContent = formatFileSize(file.size);
  setDocumentStatus("Uploading and indexing…");
  el.uploadProgress.hidden = false;
  el.progressText.textContent = "Extracting text and creating embeddings…";
  el.uploadNote.textContent = "Keep this page open while the PDF is processed.";

  try {
    const formData = new FormData();
    formData.append("file", file, file.name);

    const response = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData
    });
    const data = await response.json();

    if (!response.ok) throw new Error(data.error || "Could not process this PDF.");

    state.document = data.document;
    setDocumentStatus("Indexed and ready", "ready");
    el.progressText.textContent = "PDF is ready for questions.";
    el.uploadNote.textContent =
      `${data.document.page_count} pages · ${data.document.chunk_count} chunks indexed.`;
    showToast(`Indexed ${file.name} successfully.`);
    setMode(state.mode);
  } catch (error) {
    console.error("PDF upload failed:", error);
    state.document = null;
    setDocumentStatus("Processing failed", "error");
    el.progressText.textContent = error.message;
    el.uploadNote.textContent = "Check that the Flask backend is running, then try again.";
    showToast(error.message || "PDF upload failed.", true);
  } finally {
    // Keep the progress result visible until another file is selected or removed.
  }
}

async function removePDF() {
  try {
    await fetch(`${API_BASE}/api/document/reset`, { method: "POST" });
  } catch (error) {
    console.warn("Backend reset could not be reached:", error);
  }

  state.document = null;
  el.pdfInput.value = "";
  el.uploadArea.hidden = false;
  el.documentCard.hidden = true;
  el.uploadProgress.hidden = true;
  el.uploadNote.textContent = state.mode === "rag"
    ? "Upload a PDF to prepare for evidence-based conversations."
    : "Upload a document to ask questions about its contents.";
  showToast("Current PDF cleared.");
}

function createMessageElement(message) {
  const article = document.createElement("article");
  article.className = `chat-message ${message.role}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  const avatarIcon = document.createElement("i");
  avatarIcon.className = message.role === "user"
    ? "fa-solid fa-user"
    : "fa-solid fa-layer-group";
  avatar.appendChild(avatarIcon);

  const body = document.createElement("div");
  body.className = "message-body";

  const heading = document.createElement("div");
  heading.className = "message-heading";
  heading.textContent = message.role === "user" ? "You" : "LocalRAG";

  const content = document.createElement("div");
  content.className = "message-text";
  if (message.error) content.classList.add("error");
  content.textContent = message.content;

  body.append(heading, content);

  if (message.role === "assistant" && Array.isArray(message.sources) && message.sources.length) {
    const sourceBox = document.createElement("div");
    sourceBox.className = "message-sources";

    const sourceHeading = document.createElement("div");
    sourceHeading.className = "sources-heading";
    const sourceIcon = document.createElement("i");
    sourceIcon.className = "fa-solid fa-book-open";
    const sourceLabel = document.createElement("span");
    sourceLabel.textContent = "DOCUMENT SOURCES";
    sourceHeading.append(sourceIcon, sourceLabel);
    sourceBox.appendChild(sourceHeading);

    message.sources.forEach(source => {
      const item = document.createElement("div");
      item.className = "source-item";
      const icon = document.createElement("i");
      icon.className = "fa-solid fa-file-pdf";
      const label = document.createElement("span");
      const page = source.page_number ? ` · Page ${source.page_number}` : "";
      label.textContent = `${source.filename || source.source || "PDF document"}${page}`;
      item.append(icon, label);
      sourceBox.appendChild(item);
    });
    body.appendChild(sourceBox);
  }

  article.append(avatar, body);
  return article;
}

function renderMessages() {
  el.messagesContainer.replaceChildren();
  el.welcomeScreen.hidden = state.messages.length > 0;

  state.messages.forEach(message => {
    el.messagesContainer.appendChild(createMessageElement(message));
  });

  if (state.isSending) {
    const typing = document.createElement("article");
    typing.className = "chat-message assistant";
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.innerHTML = '<i class="fa-solid fa-layer-group"></i>';
    const body = document.createElement("div");
    body.className = "message-body";
    const heading = document.createElement("div");
    heading.className = "message-heading";
    heading.textContent = "LocalRAG";
    const dots = document.createElement("div");
    dots.className = "typing-indicator";
    dots.innerHTML = "<span></span><span></span><span></span>";
    body.append(heading, dots);
    typing.append(avatar, body);
    el.messagesContainer.appendChild(typing);
  }

  requestAnimationFrame(() => {
    el.chatWrapper.scrollTop = el.chatWrapper.scrollHeight;
  });
}

function addMessage(role, content, options = {}) {
  state.messages.push({
    role,
    content,
    mode: state.mode,
    sources: options.sources || [],
    error: options.error || false
  });
  renderMessages();
}

function resizeInput() {
  el.messageInput.style.height = "auto";
  el.messageInput.style.height = `${Math.min(el.messageInput.scrollHeight, 150)}px`;
}

function setSending(value) {
  state.isSending = value;
  el.sendButton.disabled = value;
  el.sendButton.innerHTML = value
    ? '<i class="fa-solid fa-spinner fa-spin"></i>'
    : '<i class="fa-solid fa-arrow-up"></i>';
  renderMessages();
}

async function sendMessage() {
  if (state.isSending) return;
  const message = el.messageInput.value.trim();
  if (!message) return;

  addMessage("user", message);
  el.messageInput.value = "";
  resizeInput();
  setSending(true);

  const history = state.messages.slice(0, -1)
    .filter(item => item.role === "user" || item.role === "assistant")
    .map(item => ({ role: item.role, content: item.content }));

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, mode: state.mode, history })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request failed.");

    addMessage("assistant", data.answer, { sources: data.sources || [] });
  } catch (error) {
    console.error("Chat request failed:", error);
    addMessage("assistant", error.message || "Could not reach the LocalRAG backend.", { error: true });
    showToast(error.message || "Could not reach the backend.", true);
  } finally {
    setSending(false);
    el.messageInput.focus();
  }
}

function startNewChat() {
  if (state.isSending) return;
  state.messages = [];
  renderMessages();
  el.messageInput.value = "";
  resizeInput();
  el.messageInput.focus();
}

async function checkHealth() {
  el.connectionTitle.textContent = "Checking local AI…";
  el.topStatusText.textContent = "Checking backend";
  try {
    const response = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
    const data = await response.json();
    const healthy = response.ok && data.ollama === "online" && data.model_available;
    el.connectionDot.classList.toggle("online", healthy);
    el.connectionDot.classList.toggle("offline", !healthy);
    el.topStatusDot.classList.toggle("online", healthy);
    el.topStatusDot.classList.toggle("offline", !healthy);

    if (healthy) {
      el.connectionTitle.textContent = "Local AI connected";
      el.connectionSubtitle.textContent = `${data.model} · Ollama online`;
      el.topStatusText.textContent = "Local model active";
    } else {
      el.connectionTitle.textContent = data.ollama === "online" ? "Model not found" : "Ollama unavailable";
      el.connectionSubtitle.textContent = data.ollama === "online"
        ? `Run: ollama pull ${data.model}`
        : "Start Ollama and retry";
      el.topStatusText.textContent = "AI offline";
    }
  } catch (error) {
    el.connectionDot.classList.remove("online");
    el.connectionDot.classList.add("offline");
    el.topStatusDot.classList.remove("online");
    el.topStatusDot.classList.add("offline");
    el.connectionTitle.textContent = "Backend unavailable";
    el.connectionSubtitle.textContent = "Start app.py on port 5000";
    el.topStatusText.textContent = "Backend offline";
  }
}

el.llmModeButton.addEventListener("click", () => setMode("llm"));
el.ragModeButton.addEventListener("click", () => setMode("rag"));
el.pdfInput.addEventListener("change", event => handlePDFSelection(event.target.files[0]));
el.removeDocumentButton.addEventListener("click", removePDF);
el.sendButton.addEventListener("click", sendMessage);
el.newChatButton.addEventListener("click", startNewChat);
el.messageInput.addEventListener("input", resizeInput);
el.messageInput.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});
el.suggestionGrid.addEventListener("click", event => {
  const button = event.target.closest("[data-prompt]");
  if (!button) return;
  el.messageInput.value = button.dataset.prompt;
  resizeInput();
  el.messageInput.focus();
});
el.refreshStatusButton.addEventListener("click", checkHealth);

el.uploadArea.addEventListener("dragover", event => {
  event.preventDefault();
  el.uploadArea.classList.add("dragging");
});
el.uploadArea.addEventListener("dragleave", () => el.uploadArea.classList.remove("dragging"));
el.uploadArea.addEventListener("drop", event => {
  event.preventDefault();
  el.uploadArea.classList.remove("dragging");
  const file = event.dataTransfer.files[0];
  if (file) handlePDFSelection(file);
});

setMode("llm");
checkHealth();
setInterval(checkHealth, 30000);
console.log("LocalRAG frontend initialized.");

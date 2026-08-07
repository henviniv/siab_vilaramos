(() => {
  const STORAGE_KEY = "siab-ai-chat-history";
  const OPEN_KEY = "siab-ai-chat-open";
  const root = document.querySelector(".siab-ai-chat");

  if (!root) return;

  const endpoint = root.dataset.aiEndpoint;
  const toggle = root.querySelector(".siab-ai-toggle");
  const panel = root.querySelector(".siab-ai-panel");
  const closeButton = root.querySelector(".siab-ai-close");
  const minimizeButton = root.querySelector(".siab-ai-minimize");
  const messages = root.querySelector(".siab-ai-messages");
  const form = root.querySelector(".siab-ai-form");
  const textarea = form.querySelector("textarea");
  const sendButton = form.querySelector("button");
  const suggestions = root.querySelectorAll(".siab-ai-suggestions button");

  const scrollToBottom = () => {
    messages.scrollTop = messages.scrollHeight;
  };

  const setOpen = (open) => {
    panel.hidden = !open;
    toggle.hidden = open;
    toggle.setAttribute("aria-expanded", String(open));
    sessionStorage.setItem(OPEN_KEY, open ? "1" : "0");
    if (open) setTimeout(() => textarea.focus(), 50);
  };

  const saveHistory = () => {
    sessionStorage.setItem(STORAGE_KEY, messages.innerHTML);
  };

  const addMessage = (text, type = "bot", save = true) => {
    const item = document.createElement("div");
    item.className = `siab-ai-message siab-ai-message--${type}`;

    if (type === "bot") {
      const avatar = document.createElement("div");
      avatar.className = "siab-ai-avatar";
      avatar.textContent = "🤖";
      item.appendChild(avatar);
    }

    const bubble = document.createElement("div");
    bubble.className = "siab-ai-bubble";
    bubble.textContent = text;
    item.appendChild(bubble);
    messages.appendChild(item);
    scrollToBottom();
    if (save) saveHistory();
    return item;
  };

  const addTyping = () => {
    const item = document.createElement("div");
    item.className = "siab-ai-message siab-ai-message--bot";
    item.innerHTML = '<div class="siab-ai-avatar">🤖</div><div class="siab-ai-bubble">Consultando banco de dados... <span class="siab-ai-typing"><span></span><span></span><span></span></span></div>';
    messages.appendChild(item);
    scrollToBottom();
    return item;
  };

  const sendQuestion = async (question) => {
    const pergunta = question.trim();
    if (!pergunta) return;

    addMessage(pergunta, "user");
    textarea.value = "";
    textarea.style.height = "auto";
    sendButton.disabled = true;
    const typing = addTyping();

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.success) {
        throw new Error(data.message || "Não foi possível consultar a IA.");
      }
      typing.remove();
      addMessage(data.resposta, "bot");
    } catch (error) {
      typing.remove();
      addMessage(error.message, "bot");
    } finally {
      sendButton.disabled = false;
      textarea.focus();
      saveHistory();
    }
  };

  const storedHistory = sessionStorage.getItem(STORAGE_KEY);
  if (storedHistory) messages.innerHTML = storedHistory;
  setOpen(sessionStorage.getItem(OPEN_KEY) === "1");
  scrollToBottom();

  toggle.addEventListener("click", () => setOpen(true));
  closeButton.addEventListener("click", () => setOpen(false));
  minimizeButton.addEventListener("click", () => setOpen(false));
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendQuestion(textarea.value);
  });

  textarea.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  });

  suggestions.forEach((button) => {
    button.addEventListener("click", () => sendQuestion(button.textContent.replace(/^\S+\s*/, "")));
  });
})();

(function() {
  const CURRENT_URL = window.location.href;

  let knowledgeBase = null;
  let isLoading = false;
  let chatHistory = [];

  // Create CSS
  const style = document.createElement('style');
  style.textContent = `
    .lic-chat-btn {
      position: fixed;
      bottom: 80px;
      right: 28px;
      z-index: 99998;
      background: #1a1a2e;
      color: white;
      border-radius: 50px;
      padding: 12px 20px;
      font-weight: bold;
      font-size: 14px;
      font-family: inherit;
      box-shadow: 0 4px 15px rgba(0,0,0,0.3);
      cursor: pointer;
      border: none;
      transition: background 0.2s, transform 0.2s;
    }
    .lic-chat-btn:hover {
      background: #2d2d4e;
      transform: scale(1.03);
    }
    
    .lic-chat-panel {
      position: fixed;
      bottom: 130px;
      right: 28px;
      width: 380px;
      max-width: 92vw;
      height: 520px;
      z-index: 99998;
      background: white;
      border-radius: 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: sans-serif;
    }

    .lic-chat-header {
      background: #1a1a2e;
      color: white;
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .lic-chat-header-info {
      display: flex;
      flex-direction: column;
    }
    .lic-chat-header-title {
      font-weight: bold;
      font-size: 15px;
      margin: 0;
    }
    .lic-chat-header-subtitle {
      font-size: 12px;
      opacity: 0.7;
      margin: 2px 0 0 0;
    }
    .lic-chat-close {
      background: none;
      border: none;
      color: white;
      font-size: 20px;
      cursor: pointer;
      padding: 0;
      line-height: 1;
    }

    .lic-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #f9fafb;
    }

    .lic-chat-msg {
      padding: 10px 14px;
      font-size: 14px;
      line-height: 1.6;
    }
    .lic-chat-user {
      align-self: flex-end;
      background: #1a1a2e;
      color: white;
      border-radius: 16px 16px 4px 16px;
      max-width: 80%;
    }
    .lic-chat-bot {
      align-self: flex-start;
      background: white;
      color: #1a1a2e;
      border: 1px solid #e5e7eb;
      border-radius: 16px 16px 16px 4px;
      max-width: 90%;
    }
    
    .lic-chat-loading-dots::after {
      content: 'Searching...';
      animation: lic-chat-dots 1.5s infinite;
    }
    @keyframes lic-chat-dots {
      0% { content: 'Searching.'; }
      33% { content: 'Searching..'; }
      66% { content: 'Searching...'; }
    }

    .lic-chat-card {
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 10px 12px;
      margin-top: 8px;
      background: #f8f9fa;
    }
    .lic-chat-card-title {
      font-weight: bold;
      color: #1a1a2e;
      font-size: 13px;
      margin-bottom: 4px;
    }
    .lic-chat-card-excerpt {
      font-size: 14px;
      color: #374151;
      margin-bottom: 6px;
    }
    .lic-chat-card-link {
      font-size: 12px;
      color: #4B110B;
      text-decoration: none;
    }
    .lic-chat-card-link:hover {
      text-decoration: underline;
    }

    .lic-chat-input-area {
      border-top: 1px solid #e5e7eb;
      padding: 12px 16px;
      display: flex;
      gap: 8px;
      background: white;
    }
    .lic-chat-input {
      flex: 1;
      border: 1px solid #d1d5db;
      border-radius: 20px;
      padding: 8px 16px;
      font-size: 14px;
      outline: none;
    }
    .lic-chat-input:focus {
      border-color: #1a1a2e;
    }
    .lic-chat-send {
      background: #1a1a2e;
      color: white;
      border: none;
      border-radius: 50%;
      width: 36px;
      height: 36px;
      cursor: pointer;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .lic-chat-send:hover {
      background: #2d2d4e;
    }
  `;
  document.head.appendChild(style);

  // Create UI Elements
  const btn = document.createElement('button');
  btn.className = 'lic-chat-btn';
  btn.innerHTML = '💬 Ask';
  document.body.appendChild(btn);

  const panel = document.createElement('div');
  panel.className = 'lic-chat-panel';
  panel.innerHTML = `
    <div class="lic-chat-header">
      <div class="lic-chat-header-info">
        <p class="lic-chat-header-title">💬 College Assistant</p>
        <p class="lic-chat-header-subtitle">Searching across all pages</p>
      </div>
      <button class="lic-chat-close">&times;</button>
    </div>
    <div class="lic-chat-messages"></div>
    <div class="lic-chat-input-area">
      <input type="text" class="lic-chat-input" placeholder="Type your question..." />
      <button class="lic-chat-send">→</button>
    </div>
  `;
  document.body.appendChild(panel);

  const messagesArea = panel.querySelector('.lic-chat-messages');
  const inputEl = panel.querySelector('.lic-chat-input');
  const sendBtn = panel.querySelector('.lic-chat-send');
  const closeBtn = panel.querySelector('.lic-chat-close');

  // Functions
  function togglePanel() {
    if (panel.style.display === 'flex') {
      panel.style.display = 'none';
    } else {
      panel.style.display = 'flex';
      inputEl.focus();
      if (!knowledgeBase) {
        loadKnowledgeBase();
      }
    }
  }

  function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  function addMessage(role, content) {
    const el = document.createElement('div');
    el.className = 'lic-chat-msg ' + (role === 'user' ? 'lic-chat-user' : 'lic-chat-bot');
    if (typeof content === 'string') {
      el.innerHTML = content.replace(/\n/g, '<br/>');
    } else {
      el.appendChild(content);
    }
    messagesArea.appendChild(el);
    scrollToBottom();
    return el;
  }

  let loadingIdCounter = 0;
  function addLoadingBubble() {
    const id = 'lic-chat-loading-' + (++loadingIdCounter);
    const el = document.createElement('div');
    el.className = 'lic-chat-msg lic-chat-bot';
    el.id = id;
    const span = document.createElement('span');
    span.className = 'lic-chat-loading-dots';
    el.appendChild(span);
    messagesArea.appendChild(el);
    scrollToBottom();
    return id;
  }

  function removeLoadingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function clearInput() {
    inputEl.value = '';
  }

  async function loadKnowledgeBase() {
    const loadingId = addLoadingBubble();
    const loadingEl = document.getElementById(loadingId);
    loadingEl.innerHTML = "Loading college data...";

    try {
      const response = await fetch("/knowledge.json");
      if (!response.ok) throw new Error("Network error");
      const data = await response.json();
      knowledgeBase = data;
      removeLoadingBubble(loadingId);

      addMessage("bot", 
`👋 Hi! I can answer questions about Lady Irwin College — programmes, admissions, facilities, research, and more.
   
Try asking:
• What programmes are offered?
• How do I apply for admission?
• What facilities does the college have?
• Tell me about the college history`);
    } catch (err) {
      removeLoadingBubble(loadingId);
      addMessage("bot", "Could not load college data. Make sure the knowledge.json file is generated.");
    }
  }

  function searchKnowledgeBase(query, pages) {
    const stopWords = new Set([
      "what", "where", "when", "how", "why",
      "who", "is", "are", "the", "a", "an",
      "in", "on", "at", "to", "for", "of",
      "and", "or", "tell", "me", "about",
      "does", "do", "can", "i", "my", "your"
    ]);

    const keywords = query
      .toLowerCase()
      .replace(/[^\w\s]/g, "")
      .split(/\s+/)
      .filter(w => w.length > 2 && !stopWords.has(w));

    if (keywords.length === 0) return [];

    const scored = pages.map(page => {
      let score = 0;
      const titleLower = (page.title || "").toLowerCase();
      const fullText = (page.full_text || "").toLowerCase();
      const summary = (page.summary || "").toLowerCase();
      const keyPoints = (page.key_points || []).join(" ").toLowerCase();
      const isCurrentPage = page.url === CURRENT_URL;

      for (const keyword of keywords) {
        // Title matches
        if (titleLower.includes(keyword)) score += 15;

        // Current page bonus
        if (isCurrentPage) score += 20;

        // Full text frequency
        const textMatches = (fullText.match(new RegExp(keyword, "gi")) || []).length;
        score += Math.min(textMatches, 20);

        // Summary matches
        if (summary.includes(keyword)) score += 8;

        // Key point matches
        const kpMatches = (keyPoints.match(new RegExp(keyword, "gi")) || []).length;
        score += kpMatches * 5;
      }

      return { page, score, keywords };
    });

    return scored
      .filter(r => r.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
  }

  function extractExcerpt(fullText, keywords, maxLength=300) {
    if (!fullText) return "";

    const sentences = fullText.match(/[^.!?]+[.!?]+/g) || [];
    
    // Score each sentence by keyword matches
    const scored = sentences.map((sentence, i) => {
      let score = 0;
      const lower = sentence.toLowerCase();
      for (const kw of keywords) {
        if (lower.includes(kw)) score += 10;
      }
      // Prefer earlier sentences slightly
      score -= i * 0.1;
      return { sentence: sentence.trim(), score };
    });

    scored.sort((a, b) => b.score - a.score);

    // Take top 3 sentences
    const selected = scored
      .slice(0, 3)
      .map(s => s.sentence)
      .join(" ");

    if (selected.length > maxLength) {
      return selected.substring(0, maxLength) + "...";
    }

    return selected || fullText.substring(0, maxLength) + "...";
  }

  function renderResults(results) {
    const container = document.createElement("div");

    const intro = document.createElement("p");
    intro.style.margin = "0 0 8px 0";
    intro.style.fontSize = "13px";
    intro.style.color = "#6b7280";
    intro.textContent = results.length === 1
      ? "Here's what I found:"
      : `Here's what I found across ${results.length} pages:`;
    container.appendChild(intro);

    results.forEach(({ page, keywords }) => {
      const excerpt = extractExcerpt(page.full_text, keywords);

      const card = document.createElement("div");
      card.className = "lic-chat-card";
      card.innerHTML = `
        <div class="lic-chat-card-title">
          📄 ${page.title || "Page"}
        </div>
        <div class="lic-chat-card-excerpt">
          ${excerpt}
        </div>
        <a href="${page.url}" class="lic-chat-card-link"
           target="_blank">
          → View page
        </a>
      `;
      container.appendChild(card);
    });

    addMessage("bot", container);
  }

  function handleQuery(query) {
    if (!query.trim() || isLoading) return;

    // Add user bubble
    addMessage("user", query);
    clearInput();

    // Show loading
    const loadingId = addLoadingBubble();
    isLoading = true;

    // Small delay for UX feel
    setTimeout(() => {
      const results = searchKnowledgeBase(query, knowledgeBase.pages);

      removeLoadingBubble(loadingId);
      isLoading = false;

      if (results.length === 0) {
        addMessage(
          "bot",
          "I couldn't find specific information about that. Try rephrasing your question or ask about admissions, programmes, facilities, or college history."
        );
        return;
      }

      // Build response
      renderResults(results);

    }, 400); // 400ms feels natural
  }

  // Events
  btn.addEventListener('click', togglePanel);
  closeBtn.addEventListener('click', togglePanel);
  
  sendBtn.addEventListener('click', () => {
    handleQuery(inputEl.value);
  });
  
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      handleQuery(inputEl.value);
    }
  });
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && panel.style.display === 'flex') {
      togglePanel();
    }
  });

})();

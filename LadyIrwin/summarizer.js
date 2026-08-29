(function() {

  // Create CSS
  const style = document.createElement('style');
  style.textContent = `
    .lic-sum-btn {
      position: fixed;
      bottom: 28px;
      right: 28px;
      z-index: 99999;
      background: #4B110B;
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
    .lic-sum-btn:not(:disabled):hover {
      background: #6B1A0F;
      transform: scale(1.03);
    }
    .lic-sum-btn:disabled {
      cursor: not-allowed;
      opacity: 0.8;
    }
    
    .lic-sum-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 100000;
      background: rgba(0,0,0,0.6);
      display: none;
      align-items: center;
      justify-content: center;
      font-family: sans-serif;
    }
    
    .lic-sum-modal {
      background: white;
      border-radius: 16px;
      max-width: 680px;
      width: 92vw;
      max-height: 82vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0,0,0,0.4);
      padding: 0;
    }

    .lic-sum-header {
      background: #4B110B;
      color: white;
      padding: 20px 24px;
      border-radius: 16px 16px 0 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .lic-sum-header h2 {
      margin: 0;
      font-weight: bold;
      font-size: 18px;
    }
    .lic-sum-close {
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 0;
      line-height: 1;
    }

    .lic-sum-loading {
      padding: 40px;
      text-align: center;
      color: #4B110B;
    }
    .lic-sum-spinner {
      border: 4px solid rgba(75, 17, 11, 0.1);
      border-left-color: #4B110B;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: lic-spin 1s linear infinite;
      margin: 0 auto 15px;
    }
    @keyframes lic-spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .lic-sum-loading h3 { margin: 0 0 5px; font-size: 16px; }
    .lic-sum-loading p { margin: 0; font-size: 13px; color: #666; }

    .lic-sum-url {
      padding: 12px 24px;
      background: #f8f4f3;
      border-bottom: 1px solid #e8e0df;
      font-size: 12px;
      color: #888;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .lic-sum-warning {
      margin: 16px 24px 0;
      background: #fff8e6;
      border: 1px solid #f0d080;
      border-radius: 8px;
      padding: 12px 16px;
      display: flex;
      gap: 10px;
      color: #7a5c00;
      font-size: 13px;
    }

    .lic-sum-section {
      padding: 20px 24px 0;
    }
    .lic-sum-label {
      font-size: 11px;
      font-weight: bold;
      letter-spacing: 1px;
      color: #4B110B;
      margin: 0;
    }
    .lic-sum-content-box {
      border-left: 4px solid #4B110B;
      background: #fdf8f8;
      padding: 14px 16px;
      border-radius: 0 8px 8px 0;
      margin-top: 10px;
      line-height: 1.7;
      color: #1a1a2e;
      font-size: 14px;
    }

    .lic-sum-kp-section {
      padding: 16px 24px;
    }
    .lic-sum-kp-list {
      list-style: none;
      padding: 0;
      margin: 10px 0 0 0;
    }
    .lic-sum-kp-item {
      display: flex;
      gap: 10px;
      margin-top: 10px;
      color: #1a1a2e;
      line-height: 1.6;
      font-size: 14px;
    }
    .lic-sum-kp-bullet {
      color: #4B110B;
      font-size: 10px;
      margin-top: 3px;
    }

    .lic-sum-footer {
      background: #f8f4f3;
      border-top: 1px solid #e8e0df;
      padding: 10px 24px;
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      font-size: 12px;
      color: #888;
      margin-top: 20px;
    }

    .lic-sum-error {
      padding: 30px 24px;
    }
    .lic-sum-error-box {
      border-left: 4px solid #dc2626;
      background: #fff5f5;
      border-radius: 8px;
      margin: 20px 24px;
      padding: 20px;
    }
    .lic-sum-error-title {
      color: #dc2626;
      font-weight: bold;
      margin: 0 0 10px 0;
      font-size: 16px;
    }
    .lic-sum-error-msg {
      color: #4b5563;
      margin: 0 0 15px 0;
      font-size: 14px;
    }
    .lic-sum-retry {
      background: #4B110B;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 8px 16px;
      cursor: pointer;
      font-size: 13px;
    }
  `;
  document.head.appendChild(style);

  // Create Button
  const btn = document.createElement('button');
  btn.className = 'lic-sum-btn';
  btn.innerHTML = '✦ Summarize This Page';
  document.body.appendChild(btn);

  // Create Modal Overlay
  const overlay = document.createElement('div');
  overlay.className = 'lic-sum-overlay';
  document.body.appendChild(overlay);

  const modal = document.createElement('div');
  modal.className = 'lic-sum-modal';
  overlay.appendChild(modal);

  // Helper to render loading state
  function renderLoading() {
    modal.innerHTML = `
      <div class="lic-sum-header">
        <h2>Page Summary</h2>
        <button class="lic-sum-close">&times;</button>
      </div>
      <div class="lic-sum-loading">
        <div class="lic-sum-spinner"></div>
        <h3>Analyzing page content...</h3>
        <p>This may take a few seconds</p>
      </div>
    `;
    modal.querySelector('.lic-sum-close').onclick = closeModal;
  }

  // Helper to render error state
  function renderError(message) {
    modal.innerHTML = `
      <div class="lic-sum-header">
        <h2>Page Summary</h2>
        <button class="lic-sum-close">&times;</button>
      </div>
      <div class="lic-sum-error">
        <div class="lic-sum-error-box">
          <h3 class="lic-sum-error-title">⚠ Summary Failed</h3>
          <p class="lic-sum-error-msg">${message}</p>
          <button class="lic-sum-retry">Try Again</button>
        </div>
      </div>
    `;
    modal.querySelector('.lic-sum-close').onclick = closeModal;
    modal.querySelector('.lic-sum-retry').onclick = handleSummarize;
  }

  // Helper to render success result
  function renderResult(data) {
    let warningHtml = '';
    if (!data.is_english) {
      warningHtml = `
        <div class="lic-sum-warning">
          <span>⚠️</span>
          <span><strong>Non-English page detected (${data.language}).</strong> Summary may be less accurate.</span>
        </div>
      `;
    }

    let keyPointsHtml = '';
    if (data.key_points && data.key_points.length > 0) {
      const items = data.key_points.map(kp => `
        <li class="lic-sum-kp-item">
          <div class="lic-sum-kp-bullet">●</div>
          <div>${kp}</div>
        </li>
      `).join('');
      keyPointsHtml = `
        <div class="lic-sum-kp-section">
          <h4 class="lic-sum-label">KEY POINTS</h4>
          <ul class="lic-sum-kp-list">
            ${items}
          </ul>
        </div>
      `;
    }

    modal.innerHTML = `
      <div class="lic-sum-header">
        <h2>Page Summary</h2>
        <button class="lic-sum-close">&times;</button>
      </div>
      <div class="lic-sum-url">${window.location.href}</div>
      ${warningHtml}
      
      <div class="lic-sum-section">
        <h4 class="lic-sum-label">SUMMARY</h4>
        <div class="lic-sum-content-box">${data.summary}</div>
      </div>
      
      ${keyPointsHtml}
      
      <div class="lic-sum-footer">
        <span>Words: ${data.word_count || 0}</span>
        <span>|</span>
        <span>Language: ${data.language || 'Unknown'}</span>
        <span>|</span>
        <span>Model: ${data.model_used || 'Unknown'}</span>
        <span>|</span>
        <span>Time: ${data.time_taken}s</span>
      </div>
    `;
    modal.querySelector('.lic-sum-close').onclick = closeModal;
  }

  function closeModal() {
    overlay.style.display = 'none';
  }

  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) {
      closeModal();
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && overlay.style.display === 'flex') {
      closeModal();
    }
  });

  async function handleSummarize() {
    overlay.style.display = 'flex';
    renderLoading();
    btn.disabled = true;
    btn.innerHTML = 'Summarizing...';

    const startTime = performance.now();
    
    // Derive JSON filename from window.location.pathname
    // e.g. /about/index.html -> about.json
    // e.g. / -> index.json
    let path = window.location.pathname.replace(/^\/|\/$/g, '');
    if (path.endsWith('index.html')) {
      path = path.replace(/\/index\.html$/, '');
    }
    path = path.replace(/^\/|\/$/g, '');
    let jsonName = "index.json";
    if (path) {
      jsonName = path.split('/').join('--') + '.json';
    }
    const JSON_URL = "/summaries/" + jsonName;

    try {
      const response = await fetch(JSON_URL);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Summary not available offline for this page.');
        }
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      if (data.success || data.summary) {
        data.time_taken = ((performance.now() - startTime) / 1000).toFixed(1);
        renderResult(data);
      } else {
        renderError(data.error || 'Unknown error occurred.');
      }
    } catch (err) {
      renderError(err.message || 'Could not load summary. Make sure the page has been pre-summarized.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '✦ Summarize This Page';
    }
  }

  btn.addEventListener('click', handleSummarize);
})();

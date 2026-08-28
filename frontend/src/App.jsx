import React, { useState } from 'react';

export default function WebsiteSummarizer() {
  const [url, setUrl] = useState("");
  const [useBrowser, setUseBrowser] = useState(false);
  const [summaryMode, setSummaryMode] = useState("sentences");
  const [summaryAmount, setSummaryAmount] = useState(3);
  const [keyPointsCount, setKeyPointsCount] = useState(6);
  const [groqApiKey, setGroqApiKey] = useState(import.meta.env.VITE_GROQ_API_KEY || "");
  const [apiKeyConfigured, setApiKeyConfigured] = useState(!!import.meta.env.VITE_GROQ_API_KEY);
  const [showApiConfig, setShowApiConfig] = useState(!import.meta.env.VITE_GROQ_API_KEY);
  
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [currentStep, setCurrentStep] = useState("");
  const [completedSteps, setCompletedSteps] = useState([]);
  
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const EXAMPLES = [
    { label: "Flat-file Database", url: "https://en.wikipedia.org/wiki/Flat-file_database" },
    { label: "Microservices", url: "https://martinfowler.com/articles/microservices.html" },
    { label: "Python Classes", url: "https://docs.python.org/3/tutorial/classes.html" }
  ];

  const handleApiKeySubmit = (e) => {
    e.preventDefault();
    if (groqApiKey.trim()) {
      setApiKeyConfigured(true);
      setShowApiConfig(false);
    }
  };

  const handleSummarize = async (e) => {
    if (e) e.preventDefault();
    if (!apiKeyConfigured || !groqApiKey.trim()) {
      setError("Please enter your Groq API key first.");
      setStatus("error");
      return;
    }
    
    let targetUrl = url.trim();
    if (!targetUrl.match(/^https?:\/\//)) {
      setError("Please enter a valid URL starting with http:// or https://");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setError(null);
    setResult(null);
    setCompletedSteps([]);
    
    const startTime = performance.now();
    
    try {
      // Step 1: Fetch using local Vite proxy
      setCurrentStep("Fetching page...");
      const CORS_PROXY = `/proxy?browser=${useBrowser}&url=`;
      const fetchResponse = await fetch(CORS_PROXY + encodeURIComponent(targetUrl));
      if (!fetchResponse.ok) throw new Error("fetch_error");
      const rawHtml = await fetchResponse.text();
      
      if (!rawHtml) throw new Error("fetch_error");
      setCompletedSteps(prev => [...prev, "Fetching page..."]);

      // Step 2: Extract & Clean
      setCurrentStep("Extracting content...");
      const parser = new DOMParser();
      const doc = parser.parseFromString(rawHtml, "text/html");
      const pageTitle = doc.querySelector("title")?.innerText?.trim() || "Unknown Title";

      setCurrentStep("Removing noise...");
      
      const tagsToRemove = ["script", "style", "nav", "header", "footer", "aside", "noscript", "iframe", "form"];
      tagsToRemove.forEach(tag => {
        doc.querySelectorAll(tag).forEach(el => el.remove());
      });

      const noiseRegex = /(^|[\s_-])(ad|ads|sidebar|cookie|popup|banner|menu|social|share|comment|related|widget|overlay|modal|newsletter)([\s_-]|$)/i;
      doc.querySelectorAll("*").forEach(el => {
        if (["html", "body", "main", "article"].includes(el.tagName.toLowerCase())) return;
        const className = (el.className || "").toString();
        const idName = (el.id || "").toString();
        if (noiseRegex.test(className) || noiseRegex.test(idName)) {
          el.remove();
        }
      });

      setCompletedSteps(prev => [...prev, "Extracting content...", "Removing noise..."]);

      // Find main content
      let contentNode = doc.querySelector("article") || doc.querySelector("main") || doc.body;
      if (!contentNode) throw new Error("no_content");

      let extractedText = contentNode.innerText || contentNode.textContent || "";
      extractedText = extractedText.replace(/\s+/g, " ").trim();
      
      if (extractedText.length < 100) {
        throw new Error("no_content");
      }

      extractedText = extractedText.substring(0, 12000);
      const wordCount = extractedText.split(/\s+/).length;

      // Step 3: Groq API
      setCurrentStep("Summarizing with AI...");
      
      const instruction = summaryMode === "words" 
          ? `approximately ${summaryAmount} words`
          : `${summaryAmount} sentences`;

      const pointsArray = Array.from({ length: keyPointsCount || 6 }, (_, i) => `"complete specific sentence ${i + 1}"`).join(",\n    ");
      
      const systemPrompt = `You are a precise webpage summarizer.
Always respond in this exact JSON format and nothing else — no markdown, no code fences:
{
  "summary": "${instruction} covering the main definition, key concepts, historical context if present, and primary examples",
  "key_points": [
    ${pointsArray}
  ],
  "title": "page title extracted from content",
  "word_count": 0
}
Rules:
- Be factual, use only the provided content
- Each key point must be a complete sentence
- Do not number the key points
- Return only valid JSON, absolutely no other text`;

      const userMessage = `Summarize this webpage.
URL: ${targetUrl}

Content:
${extractedText}`;

      const groqResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${groqApiKey}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          model: "openai/gpt-oss-20b",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userMessage }
          ],
          temperature: 0.3,
          max_tokens: 4000
        })
      });

      if (groqResponse.status === 401) throw new Error("groq_401");
      if (groqResponse.status === 429) throw new Error("groq_429");
      if (!groqResponse.ok) {
        const errorText = await groqResponse.text();
        throw new Error(`groq_error: ${groqResponse.status} - ${errorText}`);
      }

      const groqData = await groqResponse.json();
      const content = groqData.choices[0].message.content;
      
      let parsedResult;
      try {
        const cleanedContent = content.replace(/^```(?:json)?\n?/i, "").replace(/\n?```$/i, "").trim();
        parsedResult = JSON.parse(cleanedContent);
        if (!parsedResult.summary && !parsedResult.key_points) {
          parsedResult = {
            summary: cleanedContent,
            key_points: []
          };
        }
      } catch (err1) {
        parsedResult = {
          summary: content,
          key_points: []
        };
      }

      setCompletedSteps(prev => [...prev, "Summarizing with AI..."]);
      setStatus("success");
      const endTime = performance.now();
      setResult({
        ...parsedResult,
        actualTitle: pageTitle, // Fallback if AI omits
        wordCount: wordCount,
        timeTaken: ((endTime - startTime) / 1000).toFixed(1)
      });
      
    } catch (err) {
      console.error(err);
      setStatus("error");
      switch (err.message) {
        case "fetch_error":
          setError("Could not fetch this page. Some sites block external access. Try a different URL.");
          break;
        case "no_content":
          setError("No readable content found on this page. The page may require JavaScript to render.");
          break;
        case "groq_401":
          setError("Invalid API key. Please check your Groq key.");
          break;
        case "groq_429":
          setError("Rate limit reached. Please wait a moment and try again.");
          break;
        default:
          setError(`AI summarization failed: ${err.message}. Please try again.`);
          break;
      }
    }
  };

  const steps = [
    { id: "Fetching page...", label: "Fetching page..." },
    { id: "Extracting content...", label: "Extracting content..." },
    { id: "Removing noise...", label: "Removing noise..." },
    { id: "Summarizing with AI...", label: "Summarizing with AI..." }
  ];

  return (
    <div className="min-h-screen bg-white text-[#1a1a2e] font-sans p-4">
      <div className="max-w-3xl mx-auto py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Website Summarizer</h1>
          <p className="text-gray-600">Extract key insights from any webpage — Powered by AI</p>
        </div>



        {/* URL Input */}
        <form onSubmit={handleSummarize} className="mb-8 relative">
          <div className="flex flex-col sm:flex-row gap-3 mb-3">
            <input 
              type="text" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter a webpage URL..."
              disabled={status === "loading"}
              className="flex-1 border-2 border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 disabled:bg-gray-100"
            />
            <button 
              type="submit"
              disabled={status === "loading"}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-6 py-3 transition-colors disabled:opacity-50 flex items-center justify-center min-w-[140px]"
            >
              {status === "loading" ? "Processing..." : "Summarize"}
            </button>
          </div>
          <div className="flex flex-wrap items-center gap-4 px-1 mt-3">
            <div className="flex items-center gap-2">
              <input 
                type="checkbox" 
                id="useBrowser" 
                checked={useBrowser}
                onChange={(e) => setUseBrowser(e.target.checked)}
                disabled={status === "loading"}
                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
              />
              <label htmlFor="useBrowser" className="text-sm text-gray-600 select-none cursor-pointer">
                Use Browser Rendering
              </label>
            </div>
            
            <div className="flex items-center gap-2 border-l border-gray-300 pl-4">
              <label className="text-sm text-gray-600">Summary:</label>
              <input 
                type="number" 
                min="1" 
                value={summaryAmount} 
                onChange={(e) => setSummaryAmount(parseInt(e.target.value) || 1)}
                disabled={status === "loading"}
                className="w-16 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-500"
              />
              <select 
                value={summaryMode}
                onChange={(e) => setSummaryMode(e.target.value)}
                disabled={status === "loading"}
                className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-500 bg-white cursor-pointer"
              >
                <option value="sentences">sentences</option>
                <option value="words">words</option>
              </select>
            </div>

            <div className="flex items-center gap-2 border-l border-gray-300 pl-4">
              <label className="text-sm text-gray-600">Key Points:</label>
              <input 
                type="number" 
                min="1" 
                value={keyPointsCount} 
                onChange={(e) => setKeyPointsCount(parseInt(e.target.value) || 1)}
                disabled={status === "loading"}
                className="w-16 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </form>

        {/* Examples (Empty State) */}
        {status === "idle" && (
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-3">Try an example:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {EXAMPLES.map(ex => (
                <button
                  key={ex.url}
                  onClick={() => setUrl(ex.url)}
                  type="button"
                  className="rounded-full border border-blue-200 bg-blue-50 text-blue-700 text-sm px-3 py-1 cursor-pointer hover:bg-blue-100 transition-colors"
                >
                  📄 {ex.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading State */}
        {status === "loading" && (
          <div className="rounded-xl shadow-lg bg-white border border-gray-200 p-6 max-w-sm mx-auto">
            <h3 className="font-bold text-lg mb-4 text-center">Processing...</h3>
            <div className="space-y-3">
              {steps.map(step => {
                const isCompleted = completedSteps.includes(step.id);
                const isCurrent = currentStep === step.id;
                
                let icon = "○";
                let textColor = "text-gray-400";
                let text = step.label;
                
                if (isCompleted) {
                  icon = "✓";
                  textColor = "text-green-600";
                  text = step.id.replace("...", "") + " complete";
                } else if (isCurrent) {
                  icon = "⟳";
                  textColor = "text-blue-600 font-medium";
                }
                
                return (
                  <div key={step.id} className={`flex items-center gap-3 ${textColor}`}>
                    <span className={`w-5 text-center ${isCurrent ? 'animate-spin inline-block' : ''}`}>{icon}</span>
                    <span className={isCurrent ? "font-medium" : ""}>{text}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Error State */}
        {status === "error" && (
          <div className="rounded-xl shadow-lg bg-white border-l-4 border-red-500 p-6">
            <h2 className="text-xl font-bold text-red-600 flex items-center gap-2 mb-2">
              <span>⚠</span> SUMMARY FAILED
            </h2>
            {url && (
              <div className="mb-4">
                <span className="font-semibold text-gray-700">URL:</span> <span className="text-gray-600 break-all">{url}</span>
              </div>
            )}
            <div className="bg-red-50 rounded p-4 text-red-800 border border-red-100 mb-4">
              <span className="font-semibold">Error:</span> {error}
            </div>
            <button 
              onClick={() => setStatus("idle")}
              className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium rounded-lg px-4 py-2 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Results */}
        {status === "success" && result && (
          <div className="rounded-xl shadow-lg bg-white border border-gray-200 overflow-hidden">
            <div className="bg-gray-50 border-b border-gray-200 p-4">
              <h2 className="font-bold text-lg text-gray-800 mb-1">{result.title || result.actualTitle}</h2>
              <p className="text-sm text-gray-500 break-all">{url}</p>
            </div>
            
            <div className="p-6">
              <div className="mb-8">
                <h3 className="text-sm font-bold text-gray-500 tracking-wider mb-3">SUMMARY</h3>
                <div className="border-l-4 border-blue-600 bg-blue-50 p-4 rounded-r-lg">
                  <p className="text-gray-800 leading-relaxed">{result.summary}</p>
                </div>
              </div>
              
              {result.key_points && result.key_points.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-gray-500 tracking-wider mb-3">KEY POINTS</h3>
                  <ul className="space-y-3">
                    {result.key_points.map((point, idx) => (
                      <li key={idx} className="flex gap-3 text-gray-800">
                        <span className="text-green-600 text-[10px] mt-1.5">●</span>
                        <span className="leading-relaxed">{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            <div className="bg-gray-50 border-t border-gray-200 p-3 text-xs text-gray-500 text-center flex flex-wrap justify-center gap-x-4 gap-y-2">
              <span>Words: {result.wordCount || 0}</span>
              <span className="text-gray-300">|</span>
              <span>Model: openai/gpt-oss-20b</span>
              <span className="text-gray-300">|</span>
              <span>Time Taken: {result.timeTaken}s</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

import { useState, useRef, useEffect } from 'react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Send, Upload, Moon, Sun, Sparkles, BarChart3, Download } from 'lucide-react';

const API_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isDark, setIsDark] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [chartUrl, setChartUrl] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [hasPendingFile, setHasPendingFile] = useState(false);
  const [pendingFileName, setPendingFileName] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const handleSend = async () => {
    // Check if there's a pending file to process
    const pendingFile = fileInputRef.current?.pendingFile;

    // If no file and no input, do nothing
    if (!pendingFile && !input.trim()) return;

    // If there's a pending file, process it
    if (pendingFile) {
      // Show upload message NOW (when Send is clicked)
      setMessages(prev => [...prev, {
        role: 'user',
        content: `📎 Uploaded: ${pendingFileName}`
      }]);

      // Show user's request if they typed one
      const userRequest = input.trim() || 'stakeholders';  // Default to stakeholders if empty

      if (input.trim()) {
        setMessages(prev => [...prev, {
          role: 'user',
          content: input
        }]);
      }

      // Add acknowledgment message - this will be the ONLY message that grows
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Okay! I will ${userRequest === 'stakeholders' ? 'analyze all stakeholders' : userRequest} for you...`,
        type: 'consolidated'  // Mark as consolidated message
      }]);

      setInput('');

      // Clear pending file and file indicator
      fileInputRef.current.pendingFile = null;
      setHasPendingFile(false);
      setPendingFileName(null);

      setIsProcessing(true);

      try {
        // Prepare form data
        const formData = new FormData();
        formData.append('file', pendingFile);
        formData.append('request', userRequest);

        // Call backend API with streaming
        const response = await fetch(`${API_URL}/api/process`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to process document');
        }

        // Process streaming response
        await processStreamingResponse(response);

      } catch (error) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `❌ Error processing document: ${error.message}`
        }]);
        setIsProcessing(false);
      }
    } else {
      // No pending file - just show the message as a regular chat
      setMessages(prev => [...prev, {
        role: 'user',
        content: input
      }]);
      setInput('');

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Please upload a document to analyze.'
      }]);
    }
  };

  const processStreamingResponse = async (response, userRequest = null) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let consolidatedMessageIndex = -1; // Track the consolidated message index
    let accumulatedContent = ''; // Accumulate ALL content

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));

            // Find the consolidated message (the acknowledgment message we created)
            if (consolidatedMessageIndex === -1) {
              setMessages(prev => {
                // Find the last message with type 'consolidated'
                for (let i = prev.length - 1; i >= 0; i--) {
                  if (prev[i].type === 'consolidated') {
                    consolidatedMessageIndex = i;
                    accumulatedContent = prev[i].content;
                    break;
                  }
                }
                return prev;
              });
            }

            // Append ALL message types to the consolidated message
            if (data.type === 'progress' || data.type === 'thinking') {
              accumulatedContent += '\n' + data.message;
              setMessages(prev => {
                const newMessages = [...prev];
                if (consolidatedMessageIndex !== -1) {
                  newMessages[consolidatedMessageIndex] = {
                    role: 'assistant',
                    content: accumulatedContent,
                    type: 'consolidated'
                  };
                }
                return newMessages;
              });
            } else if (data.type === 'complete') {
              accumulatedContent += '\n\n' + data.message;
              setMessages(prev => {
                const newMessages = [...prev];
                if (consolidatedMessageIndex !== -1) {
                  newMessages[consolidatedMessageIndex] = {
                    role: 'assistant',
                    content: accumulatedContent,
                    type: 'consolidated'
                  };
                }
                return newMessages;
              });

              // Set chart data (HTML for viewing, PNG for downloading)
              setChartUrl(`${API_URL}${data.data.chart_url}`);
              setDownloadUrl(`${API_URL}${data.data.download_url}`);
              setChartData(data.data);
              setIsProcessing(false);
            } else if (data.type === 'error') {
              accumulatedContent += '\n\n❌ ' + data.message;
              setMessages(prev => {
                const newMessages = [...prev];
                if (consolidatedMessageIndex !== -1) {
                  newMessages[consolidatedMessageIndex] = {
                    role: 'assistant',
                    content: accumulatedContent,
                    type: 'consolidated'
                  };
                }
                return newMessages;
              });
              setIsProcessing(false);
            }
          } catch (e) {
            console.error('Error parsing SSE:', e);
          }
        }
      }
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Only accept PDFs for now
    if (file.type !== 'application/pdf') {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Please upload a PDF document.'
      }]);
      return;
    }

    // Store the file for later processing when user clicks Send
    // NO messages added here - just set indicators
    fileInputRef.current.pendingFile = file;
    setHasPendingFile(true);
    setPendingFileName(file.name);

    // Reset file input
    e.target.value = null;
  };

  const handleExport = () => {
    if (!downloadUrl) return;

    // Download the PNG chart
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = 'timeline.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Left Panel - Chat */}
      <div className="w-[400px] border-r flex flex-col bg-card">
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-base font-semibold">Hubble</h1>
              <p className="text-xs text-muted-foreground">Legal Timeline AI</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsDark(!isDark)}
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </Button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <div className="space-y-4 pt-8">
              <div className="text-center text-sm text-muted-foreground">
                <p className="mb-4">Upload a legal document to get started.</p>
                <p className="text-xs mb-3">Try these visualization types:</p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center px-2">
                {[
                  'Show executive timeline',
                  'Focus on regulatory events',
                  'Analyze all stakeholders',
                  'Show key milestones only'
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="px-3 py-1.5 text-xs rounded-full bg-muted hover:bg-muted/80 transition-colors border border-border"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-foreground whitespace-pre-wrap'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t">
          {/* File indicator - shown above input like ChatGPT */}
          {pendingFileName && (
            <div className="mb-3 flex items-center gap-2 p-3 rounded-xl bg-muted border border-border">
              <div className="w-10 h-10 rounded-lg bg-red-500 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{pendingFileName}</p>
                <p className="text-xs text-muted-foreground">PDF</p>
              </div>
              <button
                onClick={() => {
                  fileInputRef.current.pendingFile = null;
                  setHasPendingFile(false);
                  setPendingFileName(null);
                }}
                className="w-6 h-6 rounded-full hover:bg-muted-foreground/10 flex items-center justify-center flex-shrink-0"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder={hasPendingFile ? "Describe what you want to visualize (or press Send for all stakeholders)..." : "Upload a PDF to get started..."}
                className="pr-10"
                disabled={isProcessing}
              />
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
              <Button
                size="icon"
                variant="ghost"
                className="absolute right-1 top-1 h-8 w-8"
                onClick={() => fileInputRef.current?.click()}
                disabled={isProcessing}
              >
                <Upload className="w-4 h-4" />
              </Button>
            </div>
            <Button
              size="icon"
              onClick={handleSend}
              disabled={(!input.trim() && !hasPendingFile) || isProcessing}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Right Panel - Visualization */}
      <div className="flex-1 flex flex-col">
        <div className="h-14 border-b flex items-center justify-between px-6 bg-card/30">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
            <h2 className="text-sm font-medium">Timeline Visualization</h2>
          </div>
          {chartData ? (
            <div className="flex items-center gap-3">
              <p className="text-xs text-muted-foreground">
                {chartData.event_count} events • {chartData.actor_count} actors
              </p>
              <Button
                size="sm"
                variant="outline"
                onClick={handleExport}
                className="h-8 gap-2"
              >
                <Download className="w-3 h-3" />
                Download PNG
              </Button>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">No visualizations yet</p>
          )}
        </div>

        {/* Visualization Area */}
        <div className="flex-1 flex items-center justify-center p-12 overflow-auto bg-muted/20">
          {chartUrl ? (
            <div className="w-full h-full rounded-lg shadow-2xl overflow-hidden bg-white">
              {chartUrl.endsWith('.html') ? (
                <iframe
                  src={chartUrl}
                  title="Interactive Timeline Chart"
                  className="w-full h-full border-0"
                  style={{ minHeight: '600px' }}
                />
              ) : (
                <img
                  src={chartUrl}
                  alt="Timeline Chart"
                  className="max-w-full max-h-full object-contain"
                  style={{ backgroundColor: '#ffffff' }}
                />
              )}
            </div>
          ) : (
            <div className="text-center space-y-4">
              <div className="w-20 h-20 mx-auto rounded-2xl bg-muted flex items-center justify-center">
                <BarChart3 className="w-10 h-10 text-muted-foreground" />
              </div>
              <div>
                <h3 className="text-lg font-medium mb-2">No visualizations yet</h3>
                <p className="text-sm text-muted-foreground max-w-md">
                  Upload a legal document to generate a timeline visualization
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

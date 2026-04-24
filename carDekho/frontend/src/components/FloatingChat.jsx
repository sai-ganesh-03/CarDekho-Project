import { useEffect, useRef, useState } from 'react';
import ChatMessage from './ChatMessage';

function IconChat() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );
}

function IconClose() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

export default function FloatingChat({ isOpen, onToggle, messages, onSend, loading }) {
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      bottomRef.current?.scrollIntoView({ behavior: 'instant' });
    }
  }, [messages, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput('');
  };

  return (
    <>
      {/* FAB */}
      <button
        onClick={onToggle}
        className="fixed top-4 right-4 z-50 w-14 h-14 rounded-full bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/30 flex items-center justify-center transition-transform duration-150 hover:scale-105 active:scale-95"
        title={isOpen ? 'Close chat' : 'Chat with Arjun'}
      >
        {isOpen ? <IconClose /> : <IconChat />}
      </button>

      {/* Panel */}
      {isOpen && (
        <div className="fixed top-20 right-4 z-40 w-80 sm:w-96 h-[480px] bg-slate-900 rounded-2xl shadow-2xl border border-slate-700/60 flex flex-col overflow-hidden">
          {/* Panel header */}
          <div className="border-b border-slate-700/60 px-4 py-3 flex items-center gap-2 bg-slate-900">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">
              A
            </div>
            <div>
              <p className="text-white text-sm font-medium leading-none">Arjun</p>
              <p className="text-slate-400 text-xs mt-0.5">Refine your search</p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} compact />
            ))}

            {loading && (
              <div className="flex items-end gap-2">
                <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                  A
                </div>
                <div className="bg-slate-700 rounded-xl rounded-bl-sm px-3 py-2">
                  <div className="flex gap-1 items-center h-3">
                    {[0, 150, 300].map((d) => (
                      <span
                        key={d}
                        className="w-1.5 h-1.5 rounded-full bg-slate-400 block animate-bounce"
                        style={{ animationDelay: `${d}ms` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-700/60 p-3 bg-slate-900">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Refine your search…"
                className="flex-1 bg-slate-700/80 text-white placeholder-slate-400 rounded-lg px-3 py-2 text-xs outline-none focus:ring-1 focus:ring-blue-500 transition"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-lg px-3 py-2 transition text-sm font-medium"
              >
                →
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

import { useCallback, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { v4 as uuidv4 } from 'uuid';
import ChatView from './components/ChatView';
import ResultsView from './components/ResultsView';
import FloatingChat from './components/FloatingChat';
import { sendMessage } from './services/api';

const WELCOME = {
  role: 'ai',
  content:
    "Namaste! I'm Arjun, your personal used car advisor on CarDekho. Tell me what you're looking for — budget, type, purpose, anything — and I'll find the right car for you!",
};

export default function App() {
  const [sessionId] = useState(() => uuidv4());
  const [mode, setMode] = useState('chat'); // 'chat' | 'results'
  const [messages, setMessages] = useState([WELCOME]);
  const [cars, setCars] = useState([]);
  const [isFloatOpen, setIsFloatOpen] = useState(false);

  const mutation = useMutation({
    mutationFn: ({ sid, msg }) => sendMessage(sid, msg),
  });

  const handleSend = useCallback(
    async (text) => {
      if (!text.trim() || mutation.isPending) return;

      setMessages((prev) => [...prev, { role: 'user', content: text }]);

      try {
        const res = await mutation.mutateAsync({ sid: sessionId, msg: text });

        if (res.type === 'cars' && res.cars?.length > 0) {
          setCars(res.cars);
          setMessages((prev) => [...prev, { role: 'ai', content: res.message }]);
          setMode('results');
          setIsFloatOpen(false);
        } else {
          const reply = res.message || "I couldn't find a match. Could you rephrase?";
          setMessages((prev) => [...prev, { role: 'ai', content: reply }]);
        }
      } catch {
        setMessages((prev) => [
          ...prev,
          { role: 'ai', content: 'Something went wrong on my end. Please try again.' },
        ]);
      }
    },
    [sessionId, mutation],
  );

  if (mode === 'results') {
    return (
      <>
        <ResultsView cars={cars} />
        <FloatingChat
          isOpen={isFloatOpen}
          onToggle={() => setIsFloatOpen((o) => !o)}
          messages={messages}
          onSend={handleSend}
          loading={mutation.isPending}
        />
      </>
    );
  }

  return <ChatView messages={messages} onSend={handleSend} loading={mutation.isPending} />;
}

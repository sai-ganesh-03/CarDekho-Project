export default function ChatMessage({ message, compact = false }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-end gap-2 ${isUser ? 'flex-row-reverse' : ''}`}>
      {!isUser && (
        <div
          className={`rounded-full bg-blue-600 flex items-center justify-center text-white font-bold flex-shrink-0 ${
            compact ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm'
          }`}
        >
          A
        </div>
      )}
      <div
        className={`max-w-[78%] rounded-2xl ${
          compact ? 'px-3 py-2' : 'px-4 py-3'
        } ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-slate-700 text-slate-100 rounded-bl-sm'
        }`}
      >
        <p className={`leading-relaxed whitespace-pre-wrap ${compact ? 'text-xs' : 'text-sm'}`}>
          {message.content}
        </p>
      </div>
    </div>
  );
}

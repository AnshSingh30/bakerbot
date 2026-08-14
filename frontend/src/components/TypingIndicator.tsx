export default function TypingIndicator() {
  return (
    <div className="flex justify-start px-3">
      <div className="tail-in relative flex gap-1 rounded-lg rounded-tl-none bg-white px-3 py-3 shadow-sm">
        {[0, 0.18, 0.36].map((delay) => (
          <span
            key={delay}
            className="dot h-2 w-2 rounded-full bg-gray-400"
            style={{ animationDelay: `${delay}s` }}
          />
        ))}
      </div>
    </div>
  );
}

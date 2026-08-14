import { Camera, Paperclip, SendHorizontal, Smile } from "lucide-react";
import { useState } from "react";

export default function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [text, setText] = useState("");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const value = text.trim();
    if (!value || disabled) return;
    setText("");
    onSend(value);
  }

  return (
    <form onSubmit={submit} className="flex items-end gap-2 bg-[#f0f0f0] px-2 py-2">
      <div className="flex flex-1 items-center gap-2 rounded-full bg-white px-3 py-2 shadow-sm">
        <Smile size={22} className="shrink-0 text-gray-500" />
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Message"
          className="min-w-0 flex-1 bg-transparent text-[15px] outline-none placeholder:text-gray-500"
        />
        <Paperclip size={20} className="shrink-0 -rotate-45 text-gray-500" />
        <Camera size={20} className="shrink-0 text-gray-500" />
      </div>
      <button
        type="submit"
        aria-label="Send"
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-wa-teal text-white disabled:opacity-60"
        disabled={disabled}
      >
        <SendHorizontal size={20} />
      </button>
    </form>
  );
}

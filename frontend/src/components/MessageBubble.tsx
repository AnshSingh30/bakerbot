import { CheckCheck } from "lucide-react";
import type { ReactNode } from "react";
import type { Msg } from "../types";

export default function MessageBubble({ msg, children }: { msg: Msg; children?: ReactNode }) {
  const out = msg.role === "out";
  return (
    <div className={`flex px-3 ${out ? "justify-end" : "justify-start"}`}>
      <div
        className={`relative max-w-[80%] rounded-lg px-2.5 py-1.5 text-[15px] leading-snug shadow-sm ${
          out ? "tail-out rounded-tr-none bg-wa-out" : "tail-in rounded-tl-none bg-white"
        }`}
      >
        <p className="whitespace-pre-wrap break-words text-gray-900">{msg.text}</p>
        {children}
        <span className="float-right ml-2 mt-1 flex items-center gap-1 text-[11px] text-gray-500">
          {msg.time}
          {out && <CheckCheck size={14} className="text-wa-tick" />}
        </span>
      </div>
    </div>
  );
}

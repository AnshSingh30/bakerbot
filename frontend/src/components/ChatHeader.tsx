import { ArrowLeft, MoreVertical, Phone, Video } from "lucide-react";
import { useState } from "react";
import type { Business } from "../types";

export default function ChatHeader({ business }: { business: Business | null }) {
  const [broken, setBroken] = useState(false);
  const name = business?.business_name ?? "…";
  const initials = name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="flex items-center gap-3 bg-wa-dark px-2 py-2 text-white shadow">
      <ArrowLeft size={22} className="shrink-0 opacity-90" />
      {business && !broken ? (
        <img
          src={business.avatar_url}
          onError={() => setBroken(true)}
          alt=""
          className="h-10 w-10 shrink-0 rounded-full object-cover"
        />
      ) : (
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-wa-teal text-sm font-semibold">
          {initials}
        </div>
      )}
      <div className="min-w-0 flex-1 leading-tight">
        <div className="truncate font-medium">{name}</div>
        <div className="text-xs text-white/70">online</div>
      </div>
      <Video size={21} className="opacity-90" />
      <Phone size={19} className="opacity-90" />
      <MoreVertical size={20} className="opacity-90" />
    </header>
  );
}

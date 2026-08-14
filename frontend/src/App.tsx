import { X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import CatalogCarousel from "./components/CatalogCarousel";
import ChatHeader from "./components/ChatHeader";
import ChatInput from "./components/ChatInput";
import MessageBubble from "./components/MessageBubble";
import OrderCard from "./components/OrderCard";
import TypingIndicator from "./components/TypingIndicator";
import { createOrder, getBusiness, getCatalog, sendChat } from "./lib/api";
import type { Business, Catalog, Msg, OrderDraft } from "./types";

const BUSINESS_ID = new URLSearchParams(window.location.search).get("b") || "tinyd_lights";
const SESSION_ID = Math.random().toString(36).slice(2);

const now = () =>
  new Date().toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true });
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export default function App() {
  const [business, setBusiness] = useState<Business | null>(null);
  const [catalog, setCatalog] = useState<Catalog>({});
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [typing, setTyping] = useState(false);
  const [banner, setBanner] = useState(true);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getBusiness(BUSINESS_ID).then((b) => {
      setBusiness(b);
      document.title = b.business_name;
      push("in", `Hi! 👋 You're chatting with ${b.business_name}${b.location ? `, ${b.location}` : ""}. Ask me anything — prices, flavours, delivery dates.`);
    });
    getCatalog(BUSINESS_ID).then(setCatalog).catch(() => {});
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, typing]);

  function push(role: "in" | "out", text: string, draft?: OrderDraft) {
    setMsgs((m) => [
      ...m,
      { id: `${Date.now()}-${Math.random()}`, role, text, time: now(), draft },
    ]);
  }

  async function send(text: string) {
    push("out", text);
    setTyping(true);
    const started = Date.now();
    try {
      const res = await sendChat(BUSINESS_ID, SESSION_ID, text);
      // Even an instant answer waits — a reply with no pause reads as a machine.
      await sleep(Math.max(0, 600 + Math.random() * 600 - (Date.now() - started)));
      setTyping(false);
      push("in", res.reply, res.order_draft ?? undefined);
    } catch {
      setTyping(false);
      push("in", "Sorry, I couldn't reach the kitchen just now — try again in a moment.");
    }
  }

  async function confirm(draft: OrderDraft, name: string, phone: string) {
    const { order_id } = await createOrder(BUSINESS_ID, draft, name, phone);
    push("in", `Order #${order_id} confirmed, ${name}! We'll message you here once it's ready. 🎂`);
  }

  return (
    <div className="mx-auto flex h-full max-w-[430px] flex-col bg-white shadow-xl">
      {banner && (
        <div className="flex items-start gap-2 bg-[#fff4d6] px-3 py-1.5 text-[11px] leading-tight text-[#7a5c00]">
          <span className="flex-1">
            Demo — prices are standard market rates. Send your real price list and this updates in
            minutes.
          </span>
          <button onClick={() => setBanner(false)} aria-label="Dismiss">
            <X size={14} />
          </button>
        </div>
      )}

      <ChatHeader business={business} />

      {Object.keys(catalog).length > 0 && <CatalogCarousel catalog={catalog} onPick={send} />}

      <main className="wa-doodle flex-1 space-y-2 overflow-y-auto py-3">
        {msgs.map((m) => (
          <MessageBubble key={m.id} msg={m}>
            {m.draft && (
              <OrderCard draft={m.draft} onConfirm={(n, p) => confirm(m.draft!, n, p)} />
            )}
          </MessageBubble>
        ))}
        {typing && <TypingIndicator />}
        <div ref={endRef} />
      </main>

      <ChatInput onSend={send} disabled={typing} />
    </div>
  );
}

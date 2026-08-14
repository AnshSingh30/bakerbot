import { useState } from "react";
import type { OrderDraft } from "../types";

const prettyDate = (iso?: string | null) =>
  iso
    ? new Date(iso).toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" })
    : "—";

export default function OrderCard({
  draft,
  onConfirm,
}: {
  draft: OrderDraft;
  onConfirm: (name: string, phone: string) => Promise<void>;
}) {
  const [stage, setStage] = useState<"idle" | "details" | "sending" | "done">("idle");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const rows: [string, string][] = [
    ["Item", draft.item],
    ["Size", draft.size ?? "—"],
    ["Flavour", draft.flavour ?? "—"],
    ["Qty", String(draft.quantity ?? 1)],
    ["Delivery", prettyDate(draft.delivery_date)],
    ["Area", draft.area ?? "—"],
  ];

  async function place() {
    if (!name.trim() || !phone.trim()) return;
    setStage("sending");
    await onConfirm(name.trim(), phone.trim());
    setStage("done");
  }

  return (
    <div className="mt-1 w-[240px] rounded-lg border border-black/10 bg-[#f7fbf5] p-2.5">
      <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-wa-teal">
        Order summary
      </div>
      <dl className="space-y-0.5 text-[13px]">
        {rows.map(([label, value]) => (
          <div key={label} className="flex justify-between gap-2">
            <dt className="text-gray-500">{label}</dt>
            <dd className="truncate text-right text-gray-800">{value}</dd>
          </div>
        ))}
        {draft.price != null && (
          <div className="flex justify-between border-t border-black/10 pt-1 font-semibold">
            <dt>Total</dt>
            <dd>₹{draft.price}</dd>
          </div>
        )}
      </dl>

      {stage === "idle" && (
        <button
          onClick={() => setStage("details")}
          className="mt-2 w-full rounded-md bg-wa-teal py-1.5 text-[13px] font-medium text-white"
        >
          Confirm Order
        </button>
      )}

      {(stage === "details" || stage === "sending") && (
        <div className="mt-2 space-y-1.5">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            className="w-full rounded-md border border-black/10 px-2 py-1.5 text-[13px] outline-none"
          />
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Phone number"
            inputMode="tel"
            className="w-full rounded-md border border-black/10 px-2 py-1.5 text-[13px] outline-none"
          />
          <button
            onClick={place}
            disabled={stage === "sending"}
            className="w-full rounded-md bg-wa-teal py-1.5 text-[13px] font-medium text-white disabled:opacity-60"
          >
            {stage === "sending" ? "Placing…" : "Place order"}
          </button>
        </div>
      )}

      {stage === "done" && (
        <div className="mt-2 text-[13px] font-medium text-wa-teal">Order placed ✓</div>
      )}
    </div>
  );
}

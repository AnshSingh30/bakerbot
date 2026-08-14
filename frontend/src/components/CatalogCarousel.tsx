import type { Catalog, Prices } from "../types";

function priceLabel(price: Prices): string {
  if (typeof price === "number") return `₹${price}`;
  const entries = Object.entries(price);
  const [key, value] = entries[0];
  return key === "starting_at" ? `from ₹${value}` : `${key} ₹${value}`;
}

const CAKEY = ["🎂", "🧁", "🍫", "🍪", "🥮", "🍰", "🎁"];

export default function CatalogCarousel({
  catalog,
  onPick,
}: {
  catalog: Catalog;
  onPick: (message: string) => void;
}) {
  const cards = Object.entries(catalog).flatMap(([category, block], ci) =>
    Object.entries(block.items).map(([item, price]) => ({
      category: category.replace(/_/g, " "),
      item,
      price: priceLabel(price),
      lead: block.lead_time_days,
      icon: CAKEY[ci % CAKEY.length],
    })),
  );

  return (
    <div className="no-scrollbar flex gap-2 overflow-x-auto bg-[#f7f3ee] px-3 py-2">
      {cards.map((c) => (
        <button
          key={`${c.category}-${c.item}`}
          onClick={() => onPick(`Tell me about the ${c.item}`)}
          className="w-32 shrink-0 rounded-lg border border-black/5 bg-white p-2 text-left shadow-sm active:scale-[0.98]"
        >
          <div className="text-lg leading-none">{c.icon}</div>
          <div className="mt-1 text-[11px] uppercase tracking-wide text-gray-400">{c.category}</div>
          <div className="text-[13px] font-medium leading-tight text-gray-800">{c.item}</div>
          <div className="mt-1 text-[13px] text-wa-teal">{c.price}</div>
          <div className="text-[11px] text-gray-400">{c.lead}d notice</div>
        </button>
      ))}
    </div>
  );
}

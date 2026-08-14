import type { Business, Catalog, ChatResponse, OrderDraft } from "../types";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

export const getBusiness = (id: string) => json<Business>(`/api/business/${id}`);
export const getCatalog = (id: string) => json<Catalog>(`/api/catalog/${id}`);

export const sendChat = (business_id: string, session_id: string, message: string) =>
  json<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ business_id, session_id, message }),
  });

export const createOrder = (
  business_id: string,
  draft: OrderDraft,
  customer_name: string,
  customer_phone: string,
) =>
  json<{ order_id: number; status: string }>("/api/orders", {
    method: "POST",
    body: JSON.stringify({ ...draft, business_id, customer_name, customer_phone }),
  });

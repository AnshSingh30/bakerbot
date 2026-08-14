export type Business = {
  business_id: string;
  business_name: string;
  location: string;
  avatar_url: string;
  signature_items: string[];
  tagline: string;
};

export type Prices = number | Record<string, number>;

export type Catalog = Record<
  string,
  {
    unit: string;
    lead_time_days: number;
    note?: string;
    min_order_qty?: number;
    items: Record<string, Prices>;
  }
>;

export type OrderDraft = {
  item: string;
  category?: string | null;
  size?: string | null;
  flavour?: string | null;
  quantity: number;
  delivery_date?: string | null;
  area?: string | null;
  price?: number | null;
  notes?: string | null;
};

export type ChatResponse = {
  reply: string;
  order_draft: OrderDraft | null;
  grounded: boolean;
  sources: string[];
};

export type Msg = {
  id: string;
  role: "in" | "out";
  text: string;
  time: string;
  draft?: OrderDraft;
};

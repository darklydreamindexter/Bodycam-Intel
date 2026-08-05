export type Summary = {
  cases_total: number;
  cases_prioritized: number;
  agencies_total: number;
  requests_draft: number;
  requests_awaiting_approval: number;
  requests_submitted: number;
  sources_total: number;
  collection_runs_failed: number;
};

export type CollectionSource = {
  id: string;
  name: string;
  kind: "rss" | "official_rss";
  url: string;
  homepage_url?: string | null;
  default_state?: string | null;
  active: boolean;
  reliability_score: number;
  poll_interval_minutes: number;
  last_collected_at?: string | null;
  next_collection_at?: string | null;
  created_at: string;
};

export type CollectionRun = {
  id: string;
  source_id: string;
  trigger: string;
  status: string;
  documents_seen: number;
  documents_new: number;
  candidate_cases_created: number;
  error_message?: string | null;
  started_at: string;
  finished_at?: string | null;
};

export type Case = {
  id: string;
  title: string;
  summary?: string | null;
  state: string;
  city?: string | null;
  status: string;
  confidence: number;
  created_at: string;
};

export type Agency = {
  id: string;
  name: string;
  agency_type: string;
  state: string;
  city?: string | null;
  records_email?: string | null;
  records_portal_url?: string | null;
};

export type RecordsRequest = {
  id: string;
  case_id: string;
  agency_id: string;
  subject: string;
  status: string;
  requested_items: string[];
  created_at: string;
};

const apiUrl = process.env.INTERNAL_API_URL ?? "http://localhost:8000";

export async function apiFetch<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${apiUrl}/api/v1${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

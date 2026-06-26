/**
 * Typed client for the FastAPI backend. Types are generated from the backend's
 * OpenAPI schema (see api-types.ts), so the contract stays in sync end to end.
 */
import type { components } from "./api-types";

export type Opportunity = components["schemas"]["OpportunityRead"];
export type OpportunityCreate = components["schemas"]["OpportunityCreate"];
export type OpportunityStatus = Opportunity["status"];

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // body was not JSON; keep statusText
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listOpportunities: () => apiFetch<Opportunity[]>("/opportunities"),
  getOpportunity: (id: string) => apiFetch<Opportunity>(`/opportunities/${id}`),
  createOpportunity: (data: OpportunityCreate) =>
    apiFetch<Opportunity>("/opportunities", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

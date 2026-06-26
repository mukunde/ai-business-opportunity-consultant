/**
 * Typed client for the FastAPI backend. Types are generated from the backend's
 * OpenAPI schema (see api-types.ts), so the contract stays in sync end to end.
 */
import type { components } from "./api-types";

export type Opportunity = components["schemas"]["OpportunityRead"];
export type OpportunityCreate = components["schemas"]["OpportunityCreate"];
export type OpportunityStatus = Opportunity["status"];

export type InterviewTurn = components["schemas"]["InterviewTurnResponse"];
export type InterviewSession = components["schemas"]["InterviewSessionRead"];
export type Turn = components["schemas"]["TurnRead"];
export type ContextGraph = components["schemas"]["ContextGraphRead"];
export type ContextNode = components["schemas"]["NodeRead"];
export type Completeness = components["schemas"]["CompletenessRead"];

export type Score = components["schemas"]["ScoreRead"];
export type ScoreInput = components["schemas"]["ScoreInput"];
export type Recommendation = components["schemas"]["RecommendationRead"];
export type RecommendationType = Recommendation["type"];
export type ReportBundle = components["schemas"]["ReportBundle"];
export type Version = components["schemas"]["VersionRead"];
export type AssessmentSnapshot = components["schemas"]["AssessmentSnapshot"];

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

const TIMEOUT_MS = 15_000;

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new ApiError(0, "The API did not respond in time. Is the backend running?");
    }
    throw new ApiError(0, "Could not reach the API. Is the backend running?");
  } finally {
    clearTimeout(timer);
  }
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

  startInterview: (id: string, message: string) =>
    apiFetch<InterviewTurn>(`/opportunities/${id}/interview`, {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  continueInterview: (id: string, answer: string) =>
    apiFetch<InterviewTurn>(`/opportunities/${id}/continue`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    }),
  getInterview: (id: string) =>
    apiFetch<InterviewSession>(`/opportunities/${id}/interview`),
  getContext: (id: string) =>
    apiFetch<ContextGraph>(`/opportunities/${id}/context`),

  getScore: (id: string) => apiFetch<Score>(`/opportunities/${id}/score`),
  createScore: (id: string, input: ScoreInput) =>
    apiFetch<Score>(`/opportunities/${id}/score`, {
      method: "POST",
      body: JSON.stringify(input),
    }),
  getRecommendation: (id: string) =>
    apiFetch<Recommendation>(`/opportunities/${id}/recommendation`),
  createRecommendation: (id: string) =>
    apiFetch<Recommendation>(`/opportunities/${id}/recommendation`, {
      method: "POST",
    }),
  getReport: (id: string) =>
    apiFetch<ReportBundle>(`/opportunities/${id}/report`),
  createReport: (id: string) =>
    apiFetch<ReportBundle>(`/opportunities/${id}/report`, { method: "POST" }),
  // Direct link to the server-rendered PDF (a plain GET the browser downloads),
  // so it is an <a href> rather than an apiFetch JSON call.
  reportPdfUrl: (id: string) => `${API_BASE}/opportunities/${id}/report.pdf`,

  listVersions: (id: string) =>
    apiFetch<Version[]>(`/opportunities/${id}/versions`),
  createVersion: (id: string, note?: string) =>
    apiFetch<Version>(`/opportunities/${id}/versions`, {
      method: "POST",
      body: JSON.stringify({ note: note ?? null }),
    }),
};

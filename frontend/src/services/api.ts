import type { AnalyzeResponse, ReferencePreviewResponse, TransformOptions, TransformResponse } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://soulmiker.fvds.ru:8001";

async function jsonFetch<T>(url: string, init: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) }
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? "Request failed");
  }
  return res.json();
}

export const api = {
  analyze(data: unknown) {
    return jsonFetch<AnalyzeResponse>("/api/analyze", { method: "POST", body: JSON.stringify({ data }) });
  },
  transform(data: unknown, options: TransformOptions) {
    return jsonFetch<TransformResponse>("/api/transform", { method: "POST", body: JSON.stringify({ data, options }) });
  },
  previewReference(data: unknown) {
    return jsonFetch<ReferencePreviewResponse>("/api/preview/reference", { method: "POST", body: JSON.stringify({ data, preview_limit: 100 }) });
  },
  async exportCsv(rows: Record<string, unknown>[], columns: string[], delimiter: string) {
    const res = await fetch(`${API_BASE}/api/export/csv`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows, columns, delimiter, filename: "json-table" })
    });
    await downloadBlob(res, "json-table.csv");
  },
  async exportReferenceXlsx(data: unknown) {
    const res = await fetch(`${API_BASE}/api/export/xlsx-hierarchical`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data, filename: "json-table" })
    });
    await downloadBlob(res, "json-table.xlsx");
  }
};

async function downloadBlob(res: Response, filename: string) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Export failed" }));
    throw new Error(body.detail ?? "Export failed");
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

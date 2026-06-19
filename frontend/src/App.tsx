import { useMemo, useState } from "react";
import { JsonInput } from "./components/JsonInput";
import { ReferenceTable } from "./components/ReferenceTable";
import { api } from "./services/api";
import type { AnalyzeResponse, ReferencePreviewResponse } from "./types/api";
import "./styles.css";

export default function App() {
  const [rawJson, setRawJson] = useState("{");
  const [error, setError] = useState("");
  const [analyze, setAnalyze] = useState<AnalyzeResponse>();
  const [result, setResult] = useState<ReferencePreviewResponse>();
  const [showSource, setShowSource] = useState(false);
  const [loading, setLoading] = useState(false);
  const [csvDelimiter, setCsvDelimiter] = useState(",");

  const parsed = useMemo(() => {
    try { return JSON.parse(rawJson); } catch { return undefined; }
  }, [rawJson]);

  function parseOrFail() {
    try {
      setError("");
      return JSON.parse(rawJson);
    } catch (e) {
      setError(`JSON невалиден: ${(e as Error).message}`);
      return undefined;
    }
  }

  async function onAnalyze() {
    const data = parseOrFail();
    if (data === undefined) return;
    setLoading(true);
    try {
      const res = await api.analyze(data);
      setAnalyze(res);
    } catch (e) { setError((e as Error).message); } finally { setLoading(false); }
  }

  async function onPreview() {
    const data = parseOrFail();
    if (data === undefined) return;
    setLoading(true);
    try {
      setResult(await api.previewReference(data));
    } catch (e) { setError((e as Error).message); } finally { setLoading(false); }
  }

  function headerChains() {
    if (!result) return [];
    const columns: string[] = [];
    for (let col = 0; col < result.meta.column_count; col += 1) {
      const parts: string[] = [];
      for (const headerRow of result.header_rows) {
        const value = headerRow[col];
        if (value !== null && value !== undefined && String(value) !== "") parts.push(String(value));
      }
      columns.push(parts.join("."));
    }
    return columns;
  }

  async function onExportCsv() {
    if (!result) return;
    const columns = headerChains();
    const rows = result.rows.map((row) => Object.fromEntries(columns.map((col, idx) => [col || `column_${idx + 1}`, row[idx] ?? ""])));
    await api.exportCsv(rows, columns, csvDelimiter);
  }

  async function onExportXlsx() {
    const data = parseOrFail();
    if (data === undefined) return;
    setLoading(true);
    try {
      await api.exportReferenceXlsx(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <div><h1>JSON → Table / CSV / XLSX</h1><p>Конвертер JSON в табличный вид с XLSX-структурой как в референсе.</p></div>
        <button onClick={() => setShowSource(true)} disabled={!parsed}>Исходный JSON</button>
      </header>
      {error && <div className="error">{error}</div>}
      {loading && <div className="info">Выполняется обработка...</div>}
      <div className="layout single-panel">
        <JsonInput rawJson={rawJson} setRawJson={setRawJson} setError={setError} />
        <section className="card action-panel">
          <div className="actions-row">
            <button onClick={onAnalyze} disabled={loading}>Analyze</button>
            <button className="primary" onClick={onPreview} disabled={loading}>Preview first 100 rows</button>
          </div>
          {analyze && (
            <div className="summary-box">
              <div><b>Recommended root:</b> {analyze.recommended_root_path}</div>
              <div><b>Candidate roots:</b> {analyze.candidate_roots.length}</div>
              {analyze.warnings.map((w) => <div className="warn" key={w}>{w}</div>)}
            </div>
          )}
        </section>
      </div>
      {result && <section className="export card"><input value={csvDelimiter} onChange={(e) => setCsvDelimiter(e.target.value)} title="CSV delimiter" /><button onClick={onExportCsv}>Download CSV</button><button className="primary" onClick={onExportXlsx}>Download XLSX</button></section>}
      {result && <ReferenceTable result={result} />}
      {showSource && <div className="modal" onClick={() => setShowSource(false)}><pre onClick={(e) => e.stopPropagation()}>{JSON.stringify(parsed, null, 2)}</pre></div>}
    </main>
  );
}

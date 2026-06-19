import type { AnalyzeResponse, TransformOptions } from "../types/api";

type Props = {
  analyze?: AnalyzeResponse;
  options: TransformOptions;
  setOptions: (next: TransformOptions) => void;
  onAnalyze: () => void;
  onTransform: () => void;
  disabled: boolean;
};

export function OptionsPanel({ analyze, options, setOptions, onAnalyze, onTransform, disabled }: Props) {
  return (
    <section className="card options">
      <div className="actions">
        <button onClick={onAnalyze} disabled={disabled}>Analyze</button>
        <button className="primary" onClick={onTransform} disabled={disabled}>Preview first 100 rows</button>
      </div>

      <label>Root path</label>
      <select value={options.root_path ?? analyze?.recommended_root_path ?? "$"} onChange={(e) => setOptions({ ...options, root_path: e.target.value })}>
        <option value="$">$</option>
        {analyze?.candidate_roots.map((c) => <option key={c.path} value={c.path}>{c.path} · {c.kind} · {c.length ?? 0}</option>)}
      </select>

      <label>Array mode</label>
      <select value={options.array_mode} onChange={(e) => setOptions({ ...options, array_mode: e.target.value as TransformOptions["array_mode"] })}>
        <option value="explode">explode</option>
        <option value="join">join/json cell</option>
        <option value="json-stringify">json-stringify</option>
      </select>

      <label>Primitive arrays</label>
      <select value={options.primitive_array_mode} onChange={(e) => setOptions({ ...options, primitive_array_mode: e.target.value as TransformOptions["primitive_array_mode"] })}>
        <option value="join">join</option>
        <option value="index">indexed columns</option>
        <option value="json-stringify">json-stringify</option>
      </select>

      <label>CSV delimiter</label>
      <input value={options.join_delimiter} onChange={(e) => setOptions({ ...options, join_delimiter: e.target.value })} />

      {analyze && <div className="summary"><b>Рекомендовано:</b> {analyze.recommended_root_path}. Найдено roots: {analyze.candidate_roots.length}</div>}
    </section>
  );
}

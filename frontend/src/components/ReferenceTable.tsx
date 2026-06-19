import { useMemo, useState } from "react";
import type { ReferencePreviewResponse } from "../types/api";

type Props = { result: ReferencePreviewResponse };

const PAGE_SIZE = 100;

export function ReferenceTable({ result }: Props) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);

  const filteredRows = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return result.rows;
    return result.rows.filter((row) => row.some((cell) => String(cell ?? "").toLowerCase().includes(q)));
  }, [result.rows, search]);

  const pageCount = Math.max(1, Math.ceil(filteredRows.length / PAGE_SIZE));
  const visibleRows = filteredRows.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  return (
    <section className="card table-card">
      <div className="table-toolbar">
        <div><b>{result.meta.row_count}</b> rows · <b>{result.meta.column_count}</b> columns · shown {result.meta.returned_rows}</div>
        <input placeholder="Поиск по таблице" value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} />
      </div>
      <div className="table-wrap">
        <table className="reference-table">
          <thead>
            {result.header_rows.map((headerRow, rowIndex) => (
              <tr key={rowIndex}>
                {headerRow.map((cell, colIndex) => <th key={`${rowIndex}-${colIndex}`}>{String(cell ?? "")}</th>)}
              </tr>
            ))}
          </thead>
          <tbody>
            {visibleRows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, colIndex) => <td key={colIndex}>{String(cell ?? "")}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="pager">
        <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0}>Назад</button>
        <span>Page {page + 1} / {pageCount}</span>
        <button onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))} disabled={page + 1 >= pageCount}>Вперёд</button>
      </div>
    </section>
  );
}

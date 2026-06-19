import { useMemo, useState } from "react";
import { flexRender, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, getSortedRowModel, useReactTable } from "@tanstack/react-table";
import type { TransformResponse } from "../types/api";

type Props = { result: TransformResponse };

export function DataTable({ result }: Props) {
  const [globalFilter, setGlobalFilter] = useState("");
  const columns = useMemo(() => result.columns.map((c) => ({ accessorKey: c.field, header: c.headerName })), [result.columns]);
  const table = useReactTable({
    data: result.rows,
    columns,
    state: { globalFilter },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel()
  });

  return (
    <section className="card table-card">
      <div className="table-toolbar">
        <div><b>{result.meta.row_count}</b> rows · <b>{result.meta.column_count}</b> columns · shown {result.meta.returned_rows}</div>
        <input placeholder="Поиск по таблице" value={globalFilter} onChange={(e) => setGlobalFilter(e.target.value)} />
      </div>
      <div className="table-wrap">
        <table>
          <thead>{table.getHeaderGroups().map((hg) => <tr key={hg.id}>{hg.headers.map((h) => <th key={h.id} onClick={h.column.getToggleSortingHandler()}>{flexRender(h.column.columnDef.header, h.getContext())} <span>{h.column.getIsSorted() === "asc" ? "↑" : h.column.getIsSorted() === "desc" ? "↓" : ""}</span></th>)}</tr>)}</thead>
          <tbody>{table.getRowModel().rows.map((row) => <tr key={row.id}>{row.getVisibleCells().map((cell) => <td key={cell.id}>{String(cell.getValue() ?? "")}</td>)}</tr>)}</tbody>
        </table>
      </div>
      <div className="pager">
        <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>Назад</button>
        <span>Page {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}</span>
        <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>Вперёд</button>
      </div>
    </section>
  );
}

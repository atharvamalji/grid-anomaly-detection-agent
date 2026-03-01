"use client";

import { useMemo, useState } from "react";
import {
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import type { AnomalyExplanation } from "@/lib/api";
import { severityBadgeStyle } from "@/lib/severity";
import { categoricalColor } from "@/lib/colors";
import { useDarkMode } from "@/lib/useDarkMode";
import { AnomalyDetailDialog } from "@/components/AnomalyDetailDialog";

function truncate(text: string | null, length: number): string {
  if (!text) return "—";
  return text.length > length ? `${text.slice(0, length)}…` : text;
}

function SortIcon({ direction }: { direction: false | "asc" | "desc" }) {
  if (!direction) return <span style={{ color: "var(--text-muted)" }}>↕</span>;
  return <span>{direction === "asc" ? "↑" : "↓"}</span>;
}

export function AnomalyTable({ anomalies }: { anomalies: AnomalyExplanation[] }) {
  const [selected, setSelected] = useState<AnomalyExplanation | null>(null);
  const [sorting, setSorting] = useState<SortingState>([{ id: "severity_score", desc: true }]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const isDark = useDarkMode();

  // Stable alphabetical order for color assignment — color follows the region
  // identity, never its rank in the sorted/filtered display order.
  const stableRegionOrder = useMemo(
    () => Array.from(new Set(anomalies.map((a) => a.region))).sort(),
    [anomalies],
  );

  const regionOptions = stableRegionOrder;
  const typeOptions = useMemo(
    () =>
      Array.from(new Set(anomalies.map((a) => a.anomaly_type).filter((t): t is string => !!t))).sort(),
    [anomalies],
  );

  const columns = useMemo<ColumnDef<AnomalyExplanation>[]>(
    () => [
      {
        accessorKey: "region",
        header: "Region",
        filterFn: "equalsString",
        cell: ({ getValue }) => {
          const region = getValue<string>();
          return (
            <span className="inline-flex items-center gap-1.5">
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{
                  backgroundColor: categoricalColor(stableRegionOrder.indexOf(region), isDark),
                }}
              />
              <span style={{ color: "var(--text-primary)" }}>{region}</span>
            </span>
          );
        },
      },
      {
        accessorKey: "timestamp",
        header: "Timestamp",
        filterFn: "includesString",
        cell: ({ getValue }) => (
          <span className="whitespace-nowrap" style={{ color: "var(--text-primary)" }}>
            {getValue<string>()}
          </span>
        ),
      },
      {
        accessorKey: "anomaly_type",
        header: "Type",
        filterFn: "equalsString",
        cell: ({ getValue }) => (
          <span style={{ color: "var(--text-secondary)" }}>{getValue<string | null>() ?? "—"}</span>
        ),
      },
      {
        accessorKey: "explanation",
        header: "Explanation",
        enableSorting: false,
        filterFn: "includesString",
        cell: ({ getValue }) => (
          <span style={{ color: "var(--text-secondary)" }}>
            {truncate(getValue<string | null>(), 90)}
          </span>
        ),
      },
      {
        accessorKey: "severity_score",
        header: "Severity",
        filterFn: (row, columnId, filterValue: string) => {
          if (!filterValue) return true;
          const min = Number(filterValue);
          if (Number.isNaN(min)) return true;
          return row.getValue<number>(columnId) >= min;
        },
        cell: ({ getValue }) => {
          const score = getValue<number>();
          return (
            <span
              className="inline-block rounded-full px-2.5 py-0.5 text-xs font-medium"
              style={severityBadgeStyle(score)}
            >
              {score.toFixed(3)}
            </span>
          );
        },
      },
    ],
    [stableRegionOrder, isDark],
  );

  const table = useReactTable({
    data: anomalies,
    columns,
    state: { sorting, columnFilters },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 20 } },
  });

  const filteredCount = table.getFilteredRowModel().rows.length;

  return (
    <>
      <div className="mb-2 flex items-baseline justify-between">
        <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
          Flagged anomalies
        </h2>
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
          {filteredCount} of {anomalies.length}
        </span>
      </div>

      <div
        className="overflow-x-auto rounded-lg border"
        style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
      >
        <table className="w-full text-left text-sm">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b" style={{ borderColor: "var(--gridline)" }}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-2 text-xs font-medium"
                    style={{ color: "var(--text-muted)" }}
                  >
                    {header.column.getCanSort() ? (
                      <button
                        type="button"
                        onClick={header.column.getToggleSortingHandler()}
                        className="inline-flex items-center gap-1"
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        <SortIcon direction={header.column.getIsSorted()} />
                      </button>
                    ) : (
                      flexRender(header.column.columnDef.header, header.getContext())
                    )}
                  </th>
                ))}
              </tr>
            ))}
            <tr className="border-b" style={{ borderColor: "var(--gridline)" }}>
              <th className="px-4 pb-2">
                <select
                  value={(table.getColumn("region")?.getFilterValue() as string) ?? ""}
                  onChange={(e) => table.getColumn("region")?.setFilterValue(e.target.value || undefined)}
                  className="w-full rounded border px-1.5 py-1 text-xs"
                  style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)", color: "var(--text-secondary)" }}
                >
                  <option value="">All</option>
                  {regionOptions.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </th>
              <th className="px-4 pb-2">
                <input
                  type="text"
                  placeholder="Filter…"
                  value={(table.getColumn("timestamp")?.getFilterValue() as string) ?? ""}
                  onChange={(e) => table.getColumn("timestamp")?.setFilterValue(e.target.value || undefined)}
                  className="w-full rounded border px-1.5 py-1 text-xs"
                  style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)", color: "var(--text-secondary)" }}
                />
              </th>
              <th className="px-4 pb-2">
                <select
                  value={(table.getColumn("anomaly_type")?.getFilterValue() as string) ?? ""}
                  onChange={(e) => table.getColumn("anomaly_type")?.setFilterValue(e.target.value || undefined)}
                  className="w-full rounded border px-1.5 py-1 text-xs"
                  style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)", color: "var(--text-secondary)" }}
                >
                  <option value="">All</option>
                  {typeOptions.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </th>
              <th className="px-4 pb-2">
                <input
                  type="text"
                  placeholder="Search…"
                  value={(table.getColumn("explanation")?.getFilterValue() as string) ?? ""}
                  onChange={(e) => table.getColumn("explanation")?.setFilterValue(e.target.value || undefined)}
                  className="w-full rounded border px-1.5 py-1 text-xs"
                  style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)", color: "var(--text-secondary)" }}
                />
              </th>
              <th className="px-4 pb-2">
                <input
                  type="number"
                  step="0.001"
                  placeholder="Min…"
                  value={(table.getColumn("severity_score")?.getFilterValue() as string) ?? ""}
                  onChange={(e) => table.getColumn("severity_score")?.setFilterValue(e.target.value || undefined)}
                  className="w-full rounded border px-1.5 py-1 text-xs"
                  style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)", color: "var(--text-secondary)" }}
                />
              </th>
            </tr>
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={() => setSelected(row.original)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    setSelected(row.original);
                  }
                }}
                tabIndex={0}
                role="button"
                className="table-row-hover cursor-pointer border-b transition-colors last:border-b-0"
                style={{ borderColor: "var(--gridline)" }}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-2.5">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
            {table.getRowModel().rows.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-4 py-6 text-center text-sm" style={{ color: "var(--text-muted)" }}>
                  No anomalies match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs" style={{ color: "var(--text-muted)" }}>
        <span>
          Page {table.getState().pagination.pageIndex + 1} of {Math.max(table.getPageCount(), 1)}
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="rounded border px-2.5 py-1 disabled:opacity-40"
            style={{ borderColor: "var(--gridline)" }}
          >
            Previous
          </button>
          <button
            type="button"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="rounded border px-2.5 py-1 disabled:opacity-40"
            style={{ borderColor: "var(--gridline)" }}
          >
            Next
          </button>
        </div>
      </div>

      <AnomalyDetailDialog anomaly={selected} onClose={() => setSelected(null)} />
    </>
  );
}

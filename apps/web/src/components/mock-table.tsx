import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export type MockTableColumn<T> = {
  key: string;
  header: string;
  className?: string;
  render: (row: T) => ReactNode;
};

type MockTableProps<T> = {
  rows: T[];
  columns: MockTableColumn<T>[];
  getRowKey: (row: T) => string;
  emptyText?: string;
};

export function MockTable<T>({
  rows,
  columns,
  getRowKey,
  emptyText = "暂无数据",
}: MockTableProps<T>) {
  return (
    <div className="overflow-hidden rounded-xl border border-zinc-200">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead className="bg-zinc-50 text-xs font-semibold tracking-wide text-zinc-500 uppercase">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={cn("px-4 py-3", column.className)}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 bg-white">
            {rows.length > 0 ? (
              rows.map((row) => (
                <tr key={getRowKey(row)} className="hover:bg-zinc-50/70">
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={cn("px-4 py-3 align-middle", column.className)}
                    >
                      {column.render(row)}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-10 text-center text-zinc-500"
                >
                  {emptyText}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import type { SchemaResponse } from "../api/types";

export function SchemaTable({ schema }: { schema: SchemaResponse }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-stone-100 text-sm dark:divide-stone-800">
        <caption className="sr-only">
          Dataset schema: column names, inferred types, and a sample of rows
        </caption>
        <thead>
          <tr>
            {schema.columns.map((col) => (
              <th
                key={col.name}
                scope="col"
                className="px-4 py-2.5 text-left font-semibold text-stone-700 dark:text-stone-200"
              >
                {col.name}
                <span className="ml-1.5 font-mono text-xs font-normal text-stone-400 dark:text-stone-500">
                  {col.dtype}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-50 dark:divide-stone-800/60">
          {schema.sample_rows.map((row, i) => (
            <tr key={i} className="transition-colors duration-200 hover:bg-stone-50 dark:hover:bg-stone-800/40">
              {schema.columns.map((col) => (
                <td key={col.name} className="px-4 py-2 whitespace-nowrap text-stone-600 dark:text-stone-300">
                  {row[col.name] === null || row[col.name] === undefined ? (
                    <span className="text-stone-400 italic dark:text-stone-600">null</span>
                  ) : (
                    String(row[col.name])
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

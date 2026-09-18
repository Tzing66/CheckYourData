import type { SchemaResponse } from "../api/types";

export function SchemaTable({ schema }: { schema: SchemaResponse }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-100 text-sm dark:divide-gray-800">
        <caption className="sr-only">
          Dataset schema: column names, inferred types, and a sample of rows
        </caption>
        <thead>
          <tr>
            {schema.columns.map((col) => (
              <th
                key={col.name}
                scope="col"
                className="px-4 py-2.5 text-left font-semibold text-gray-700 dark:text-gray-200"
              >
                {col.name}
                <span className="ml-1.5 font-mono text-xs font-normal text-gray-400 dark:text-gray-500">
                  {col.dtype}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50 dark:divide-gray-800/60">
          {schema.sample_rows.map((row, i) => (
            <tr key={i} className="transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/40">
              {schema.columns.map((col) => (
                <td key={col.name} className="px-4 py-2 whitespace-nowrap text-gray-600 dark:text-gray-300">
                  {row[col.name] === null || row[col.name] === undefined ? (
                    <span className="text-gray-400 italic dark:text-gray-600">null</span>
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

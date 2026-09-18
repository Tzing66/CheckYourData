import { CheckCircle2, XCircle } from "lucide-react";
import { motion } from "motion/react";
import type { RunResponse } from "../api/types";

export function RunResultsPanel({ run }: { run: RunResponse }) {
  const passedCount = run.results.filter((r) => r.passed).length;
  const allPassed = passedCount === run.results.length;
  const grouped = new Map<string, typeof run.results>();
  for (const result of run.results) {
    const key = result.column ?? "Table-level";
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key)!.push(result);
  }

  return (
    <div>
      <p
        aria-live="polite"
        className={`mb-4 flex items-center gap-1.5 text-sm font-medium ${
          allPassed ? "text-green-700 dark:text-green-400" : "text-amber-700 dark:text-amber-400"
        }`}
      >
        {allPassed ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
        Run at {new Date(run.run_at).toLocaleString()} — {passedCount} of {run.results.length} checks passed
      </p>
      <div className="space-y-5">
        {[...grouped.entries()].map(([column, results]) => (
          <div key={column}>
            <h3 className="mb-1.5 text-sm font-semibold text-gray-800 dark:text-gray-200">{column}</h3>
            <ul className="space-y-1.5">
              {results.map((result, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.15, delay: i * 0.03 }}
                  className={`flex items-start gap-2.5 rounded-lg border px-3 py-2.5 text-sm ${
                    result.passed
                      ? "border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950/50"
                      : "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/50"
                  }`}
                >
                  {result.passed ? (
                    <CheckCircle2 aria-hidden className="mt-0.5 h-4 w-4 shrink-0 text-green-600 dark:text-green-400" />
                  ) : (
                    <XCircle aria-hidden className="mt-0.5 h-4 w-4 shrink-0 text-red-600 dark:text-red-400" />
                  )}
                  <div>
                    <p className="font-mono text-xs font-medium text-gray-800 dark:text-gray-200">
                      {result.check_type} — {result.passed ? "passed" : "failed"}
                    </p>
                    <p className="mt-0.5 font-mono text-xs text-gray-500 dark:text-gray-400">
                      {JSON.stringify(result.details)}
                    </p>
                  </div>
                </motion.li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

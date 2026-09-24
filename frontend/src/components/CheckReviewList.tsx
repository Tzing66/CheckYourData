import { motion } from "motion/react";
import { ListChecks, Pencil, X } from "lucide-react";
import type { CheckConfig } from "../api/types";
import { formatCheckTypeLabel } from "../lib/describeResult";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";
import { EmptyState } from "./ui/EmptyState";

interface CheckReviewListProps {
  checks: CheckConfig[];
  onEdit: (index: number) => void;
  onRemove: (index: number) => void;
}

export function CheckReviewList({ checks, onEdit, onRemove }: CheckReviewListProps) {
  if (checks.length === 0) {
    return (
      <EmptyState
        icon={ListChecks}
        title="No checks yet"
        description="Suggest some with AI or add one manually to get started."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
    <table className="min-w-full divide-y divide-stone-100 text-sm dark:divide-stone-800">
      <caption className="sr-only">Checks pending save for this dataset</caption>
      <thead>
        <tr>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-stone-700 dark:text-stone-200">
            Column
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-stone-700 dark:text-stone-200">
            Check type
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-stone-700 dark:text-stone-200">
            Params
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-stone-700 dark:text-stone-200">
            Source
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-stone-700 dark:text-stone-200">
            <span className="sr-only">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody className="divide-y divide-stone-50 dark:divide-stone-800/60">
        {checks.map((check, i) => (
          // Key is content-based (no array index) so React recognizes unchanged rows as the
          // same element across updates — only genuinely new rows animate in, not the whole list.
          <motion.tr
            key={`${check.column ?? "_"}-${check.check_type}`}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.15 }}
            className="transition-colors duration-200 hover:bg-stone-50 dark:hover:bg-stone-800/40"
          >
            <td className="px-4 py-2 text-stone-800 dark:text-stone-200">
              {check.column ?? <em className="text-stone-400 dark:text-stone-500">table-level</em>}
            </td>
            <td className="px-4 py-2 font-mono text-xs text-stone-800 dark:text-stone-200">{check.check_type}</td>
            <td className="max-w-xs truncate px-4 py-2 font-mono text-xs text-stone-500 dark:text-stone-400">
              {JSON.stringify(check.params)}
            </td>
            <td className="px-4 py-2">
              <Badge tone={check.source === "ai_suggested" ? "purple" : "stone"}>
                {check.source === "ai_suggested" ? "AI" : "manual"}
              </Badge>
            </td>
            <td className="px-4 py-2 text-right whitespace-nowrap">
              <Button
                variant="secondary"
                className="mr-1.5 !p-2"
                aria-label={`Edit ${formatCheckTypeLabel(check.check_type)} check on ${check.column ?? "table"}`}
                onClick={() => onEdit(i)}
              >
                <Pencil className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="danger"
                className="!p-2"
                aria-label={`Remove ${formatCheckTypeLabel(check.check_type)} check on ${check.column ?? "table"}`}
                onClick={() => onRemove(i)}
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            </td>
          </motion.tr>
        ))}
      </tbody>
    </table>
    </div>
  );
}

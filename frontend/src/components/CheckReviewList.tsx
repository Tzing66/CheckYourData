import { motion } from "motion/react";
import { ListChecks, Pencil, Trash2 } from "lucide-react";
import type { CheckConfig } from "../api/types";
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
    <table className="min-w-full divide-y divide-gray-100 text-sm dark:divide-gray-800">
      <caption className="sr-only">Checks pending save for this dataset</caption>
      <thead>
        <tr>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-gray-700 dark:text-gray-200">
            Column
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-gray-700 dark:text-gray-200">
            Check type
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-gray-700 dark:text-gray-200">
            Params
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-gray-700 dark:text-gray-200">
            Source
          </th>
          <th scope="col" className="px-4 py-2.5 text-left font-semibold text-gray-700 dark:text-gray-200">
            <span className="sr-only">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-50 dark:divide-gray-800/60">
        {checks.map((check, i) => (
          <motion.tr
            key={`${check.column ?? "_"}-${check.check_type}-${i}`}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.15, delay: i * 0.02 }}
            className="transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/40"
          >
            <td className="px-4 py-2 text-gray-800 dark:text-gray-200">
              {check.column ?? <em className="text-gray-400 dark:text-gray-500">table-level</em>}
            </td>
            <td className="px-4 py-2 font-mono text-xs text-gray-800 dark:text-gray-200">{check.check_type}</td>
            <td className="max-w-xs truncate px-4 py-2 font-mono text-xs text-gray-500 dark:text-gray-400">
              {JSON.stringify(check.params)}
            </td>
            <td className="px-4 py-2">
              <Badge tone={check.source === "ai_suggested" ? "purple" : "gray"}>
                {check.source === "ai_suggested" ? "AI" : "manual"}
              </Badge>
            </td>
            <td className="px-4 py-2 text-right whitespace-nowrap">
              <Button variant="secondary" className="mr-2" onClick={() => onEdit(i)}>
                <Pencil className="h-3.5 w-3.5" />
                Edit
              </Button>
              <Button variant="danger" onClick={() => onRemove(i)}>
                <Trash2 className="h-3.5 w-3.5" />
                Remove
              </Button>
            </td>
          </motion.tr>
        ))}
      </tbody>
    </table>
  );
}

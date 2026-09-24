import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-2 px-4 py-10 text-center">
      <Icon aria-hidden className="h-8 w-8 text-stone-400 dark:text-stone-600" strokeWidth={1.5} />
      <p className="text-sm font-medium text-stone-700 dark:text-stone-300">{title}</p>
      {description && <p className="max-w-sm text-sm text-stone-500 dark:text-stone-400">{description}</p>}
      {action}
    </div>
  );
}

import { AlertCircle, Database, UploadCloud } from "lucide-react";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { listDatasets } from "../api/datasets";
import { PageLayout } from "../components/layout/PageLayout";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SkeletonBlock } from "../components/ui/Skeleton";
import { useFetch } from "../hooks/useFetch";

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function DatasetsListPage() {
  const { data: datasets, loading, error } = useFetch(() => listDatasets(), []);

  return (
    <PageLayout>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-stone-900 dark:text-stone-100">My datasets</h1>
        <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
          Everything you&apos;ve uploaded from this browser.
        </p>
      </div>

      {loading && (
        <Card className="p-5">
          <SkeletonBlock rows={4} />
        </Card>
      )}

      {error && <EmptyState icon={AlertCircle} title="Couldn't load your datasets" description={error} />}

      {datasets && datasets.length === 0 && (
        <EmptyState
          icon={Database}
          title="No datasets yet"
          description="Upload a CSV to get started."
          action={
            <Link
              to="/upload"
              className="mt-2 flex items-center gap-1.5 text-sm font-medium text-amber-600 hover:underline dark:text-amber-400"
            >
              <UploadCloud className="h-4 w-4" />
              Upload a CSV
            </Link>
          }
        />
      )}

      {datasets && datasets.length > 0 && (
        <Card>
          <ul className="divide-y divide-stone-100 dark:divide-stone-800">
            {datasets.map((dataset, i) => (
              <motion.li
                key={dataset.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: Math.min(i, 8) * 0.03 }}
              >
                <Link
                  to={`/datasets/${dataset.id}`}
                  className="flex items-center justify-between gap-4 px-5 py-3.5 transition-colors duration-200 hover:bg-stone-50 dark:hover:bg-stone-800/40"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-stone-900 dark:text-stone-100">{dataset.name}</p>
                    <p className="text-sm text-stone-500 dark:text-stone-400">
                      {dataset.row_count.toLocaleString()} rows · {Object.keys(dataset.column_schema).length} columns
                    </p>
                  </div>
                  <span className="shrink-0 text-sm text-stone-400 dark:text-stone-500">
                    {timeAgo(dataset.uploaded_at)}
                  </span>
                </Link>
              </motion.li>
            ))}
          </ul>
        </Card>
      )}
    </PageLayout>
  );
}

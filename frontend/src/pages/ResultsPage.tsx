import { ArrowLeft, ClipboardList, History } from "lucide-react";
import { motion } from "motion/react";
import { Link, useParams } from "react-router-dom";
import { getHistory } from "../api/datasets";
import { PageLayout } from "../components/layout/PageLayout";
import { RunResultsPanel } from "../components/RunResultsPanel";
import { EmptyState } from "../components/ui/EmptyState";
import { SkeletonBlock } from "../components/ui/Skeleton";
import { useFetch } from "../hooks/useFetch";

export function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const datasetId = Number(id);
  const historyState = useFetch(() => getHistory(datasetId), [datasetId]);

  const latestRun = historyState.data?.at(-1) ?? null;

  return (
    <PageLayout>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-stone-900 dark:text-stone-100">Results</h1>
          <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">Here&apos;s how your data did.</p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1 text-sm">
          <Link
            to={`/datasets/${datasetId}`}
            className="flex items-center gap-1.5 font-medium text-amber-600 hover:underline dark:text-amber-400"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to checks
          </Link>
          {latestRun && (
            <Link
              to={`/datasets/${datasetId}/history`}
              className="flex items-center gap-1.5 font-medium text-stone-500 hover:underline dark:text-stone-400"
            >
              <History className="h-4 w-4" />
              View history
            </Link>
          )}
        </div>
      </div>

      {historyState.loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <SkeletonBlock rows={5} />
        </motion.div>
      )}

      {historyState.error && (
        <EmptyState icon={ClipboardList} title="Couldn't load results" description={historyState.error} />
      )}

      {historyState.data && !latestRun && (
        <EmptyState
          icon={ClipboardList}
          title="No results yet"
          description="Go back and run your saved checks to see results here."
          action={
            <Link
              to={`/datasets/${datasetId}`}
              className="mt-2 text-sm font-medium text-amber-600 hover:underline dark:text-amber-400"
            >
              Back to checks →
            </Link>
          }
        />
      )}

      {latestRun && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
          <RunResultsPanel run={latestRun} />
        </motion.div>
      )}
    </PageLayout>
  );
}

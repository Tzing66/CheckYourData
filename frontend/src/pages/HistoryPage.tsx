import { AlertCircle, ArrowLeft, LineChart } from "lucide-react";
import { motion } from "motion/react";
import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { getHistory } from "../api/datasets";
import type { CheckType } from "../api/types";
import { deriveSignal, HistoryChart, type HistoryPoint } from "../components/HistoryChart";
import { PageLayout } from "../components/layout/PageLayout";
import { EmptyState } from "../components/ui/EmptyState";
import { Skeleton } from "../components/ui/Skeleton";
import { useFetch } from "../hooks/useFetch";

interface CheckSeries {
  checkId: number;
  column: string | null;
  checkType: CheckType;
  points: HistoryPoint[];
}

export function HistoryPage() {
  const { id } = useParams<{ id: string }>();
  const datasetId = Number(id);
  const historyState = useFetch(() => getHistory(datasetId), [datasetId]);

  const series = useMemo<CheckSeries[]>(() => {
    if (!historyState.data) return [];
    const byCheck = new Map<number, CheckSeries>();
    for (const run of historyState.data) {
      for (const result of run.results) {
        if (!byCheck.has(result.check_id)) {
          byCheck.set(result.check_id, {
            checkId: result.check_id,
            column: result.column,
            checkType: result.check_type,
            points: [],
          });
        }
        byCheck.get(result.check_id)!.points.push({
          runAt: run.run_at,
          passed: result.passed,
          signal: deriveSignal(result.details, result.passed),
        });
      }
    }
    return [...byCheck.values()];
  }, [historyState.data]);

  return (
    <PageLayout>
      <div className="mb-2 flex items-start justify-between">
        <h1 className="text-xl font-semibold text-stone-900 dark:text-stone-100">History</h1>
        <Link
          to={`/datasets/${datasetId}`}
          className="flex shrink-0 items-center gap-1.5 text-sm font-medium text-amber-600 hover:underline dark:text-amber-400"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to dataset
        </Link>
      </div>
      <p className="mb-6 max-w-2xl text-sm text-stone-500 dark:text-stone-400">
        Each point is a run. Red points failed. Checks tagged <span className="font-medium">drift check</span> compare
        the current data against past runs, not just the file on its own — that's how gradual shifts (a shrinking
        row count, a creeping mean) get caught even when nothing looks wrong in isolation.
      </p>

      {historyState.loading && (
        <div className="space-y-4">
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
        </div>
      )}

      {historyState.error && (
        <EmptyState icon={AlertCircle} title="Couldn't load history" description={historyState.error} />
      )}

      {historyState.data && historyState.data.length === 0 && (
        <EmptyState
          icon={LineChart}
          title="No runs yet"
          description="Run checks from the dataset page first, then come back to see trends here."
        />
      )}

      <div className="space-y-4">
        {series.map((s, i) => (
          <motion.div
            key={s.checkId}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: i * 0.03, ease: [0.22, 1, 0.36, 1] }}
          >
            <HistoryChart column={s.column} checkType={s.checkType} points={s.points} />
          </motion.div>
        ))}
      </div>
    </PageLayout>
  );
}

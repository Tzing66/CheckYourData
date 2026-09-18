import { AlertCircle, ArrowLeft, LineChart } from "lucide-react";
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
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">History</h1>
        <Link
          to={`/datasets/${datasetId}`}
          className="flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to dataset
        </Link>
      </div>

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
        {series.map((s) => (
          <HistoryChart key={s.checkId} column={s.column} checkType={s.checkType} points={s.points} />
        ))}
      </div>
    </PageLayout>
  );
}

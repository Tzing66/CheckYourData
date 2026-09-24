import { ChevronRight, Database, ShieldCheck } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { getDataset } from "../../api/datasets";
import { useFetch } from "../../hooks/useFetch";
import { ThemeToggle } from "../ui/ThemeToggle";

export function AppHeader() {
  const location = useLocation();
  const datasetMatch = location.pathname.match(/^\/datasets\/(\d+)/);
  const datasetId = datasetMatch ? Number(datasetMatch[1]) : null;
  const isHistory = location.pathname.endsWith("/history");
  const isResults = location.pathname.endsWith("/results");

  const datasetState = useFetch(
    () => (datasetId ? getDataset(datasetId) : Promise.resolve(null)),
    [datasetId],
  );

  return (
    <header className="sticky top-0 z-40 border-b border-stone-200/80 bg-stone-50/85 backdrop-blur-md transition-colors duration-300 dark:border-stone-800/80 dark:bg-stone-950/85">
      <div className="mx-auto flex max-w-4xl items-center gap-2 px-4 py-3.5">
        <Link
          to="/"
          className="flex items-center gap-2 text-base font-semibold text-stone-900 transition-opacity hover:opacity-80 dark:text-stone-100"
        >
          <ShieldCheck className="h-5 w-5 text-amber-600 dark:text-amber-500" strokeWidth={2.25} />
          CheckYourData
        </Link>

        {datasetId && (
          <>
            <ChevronRight aria-hidden className="h-4 w-4 shrink-0 text-stone-300 dark:text-stone-700" />
            <Link
              to={`/datasets/${datasetId}`}
              className="truncate text-sm font-medium text-stone-600 transition-colors duration-200 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100"
            >
              {datasetState.data?.name ?? `Dataset #${datasetId}`}
            </Link>
          </>
        )}

        {isHistory && (
          <>
            <ChevronRight aria-hidden className="h-4 w-4 shrink-0 text-stone-300 dark:text-stone-700" />
            <span className="text-sm font-medium text-stone-600 dark:text-stone-400">History</span>
          </>
        )}

        {isResults && (
          <>
            <ChevronRight aria-hidden className="h-4 w-4 shrink-0 text-stone-300 dark:text-stone-700" />
            <span className="text-sm font-medium text-stone-600 dark:text-stone-400">Results</span>
          </>
        )}

        <div className="ml-auto flex items-center gap-4">
          <Link
            to="/datasets"
            className="flex items-center gap-1.5 text-sm font-medium text-stone-600 transition-colors duration-200 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100"
          >
            <Database className="h-4 w-4" />
            My datasets
          </Link>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}

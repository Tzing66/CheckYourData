import { ChevronRight, ShieldCheck } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { getDataset } from "../../api/datasets";
import { useFetch } from "../../hooks/useFetch";

export function AppHeader() {
  const location = useLocation();
  const datasetMatch = location.pathname.match(/^\/datasets\/(\d+)/);
  const datasetId = datasetMatch ? Number(datasetMatch[1]) : null;
  const isHistory = location.pathname.endsWith("/history");

  const datasetState = useFetch(
    () => (datasetId ? getDataset(datasetId) : Promise.resolve(null)),
    [datasetId],
  );

  return (
    <header className="sticky top-0 z-40 border-b border-gray-200/80 bg-white/85 backdrop-blur-md dark:border-gray-800/80 dark:bg-gray-950/85">
      <div className="mx-auto flex max-w-4xl items-center gap-2 px-4 py-3.5">
        <Link
          to="/"
          className="flex items-center gap-2 text-base font-semibold text-gray-900 transition-opacity hover:opacity-80 dark:text-gray-100"
        >
          <ShieldCheck className="h-5 w-5 text-blue-600 dark:text-blue-400" strokeWidth={2.25} />
          CheckYourData
        </Link>

        {datasetId && (
          <>
            <ChevronRight aria-hidden className="h-4 w-4 shrink-0 text-gray-300 dark:text-gray-700" />
            <Link
              to={`/datasets/${datasetId}`}
              className="truncate text-sm font-medium text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
            >
              {datasetState.data?.name ?? `Dataset #${datasetId}`}
            </Link>
          </>
        )}

        {isHistory && (
          <>
            <ChevronRight aria-hidden className="h-4 w-4 shrink-0 text-gray-300 dark:text-gray-700" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">History</span>
          </>
        )}
      </div>
    </header>
  );
}

import { AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { uploadDataset } from "../api/datasets";
import { PageLayout } from "../components/layout/PageLayout";
import { UploadDropzone } from "../components/UploadDropzone";
import { useAsyncAction } from "../hooks/useAsyncAction";

export function UploadPage() {
  const navigate = useNavigate();
  const { run, loading, error } = useAsyncAction(uploadDataset);

  async function handleFile(file: File) {
    const dataset = await run(file);
    if (dataset) navigate(`/datasets/${dataset.id}`);
  }

  return (
    <PageLayout>
      <div className="py-8 text-center">
        <h1 className="mb-2 text-3xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">
          Check your data before it checks you
        </h1>
        <p className="mx-auto mb-10 max-w-lg text-gray-600 dark:text-gray-400">
          Upload a CSV to get AI-suggested data quality checks, review and run them, and track results over time.
        </p>
        <div className="mx-auto max-w-lg text-left">
          <UploadDropzone onFileSelected={handleFile} disabled={loading} />
          <p aria-live="polite" className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            {loading ? "Uploading…" : null}
          </p>
          {error && (
            <div
              role="alert"
              className="mt-4 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
            >
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}

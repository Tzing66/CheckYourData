import { AlertCircle } from "lucide-react";
import { motion } from "motion/react";
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
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
        className="mx-auto max-w-lg py-16"
      >
        <div className="mb-6 text-center">
          <h1 className="mb-2 text-2xl font-semibold tracking-tight text-stone-900 dark:text-stone-100">
            Upload your CSV
          </h1>
          <p className="text-sm text-stone-500 dark:text-stone-400">
            We'll read the columns and take you straight to the next step.
          </p>
        </div>
        <UploadDropzone onFileSelected={handleFile} disabled={loading} />
        <p aria-live="polite" className="mt-4 text-sm text-stone-500 dark:text-stone-400">
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
      </motion.div>
    </PageLayout>
  );
}

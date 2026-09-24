import { AlertCircle, History, PlayCircle, Plus, Sparkles, Table2 } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getChecks, getSchema, runChecks, saveChecks, suggestChecks } from "../api/datasets";
import type { CheckConfig, CheckOut } from "../api/types";
import { CheckEditorDialog } from "../components/CheckEditorDialog";
import { CheckReviewList } from "../components/CheckReviewList";
import { PageLayout } from "../components/layout/PageLayout";
import { SchemaTable } from "../components/SchemaTable";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SkeletonBlock } from "../components/ui/Skeleton";
import { useToast } from "../components/ui/ToastProvider";
import { useAsyncAction } from "../hooks/useAsyncAction";
import { useFetch } from "../hooks/useFetch";
import { formatCheckTypeLabel } from "../lib/describeResult";

function toCheckConfig(check: CheckOut): CheckConfig {
  return { column: check.column, check_type: check.check_type, params: check.params, source: check.source, active: check.active };
}

function checkKey(check: CheckConfig): string {
  return `${check.column ?? "_"}|${check.check_type}`;
}

function mergeByKey(base: CheckConfig[], incoming: CheckConfig[]): CheckConfig[] {
  const byKey = new Map(base.map((c) => [checkKey(c), c]));
  for (const c of incoming) byKey.set(checkKey(c), c);
  return [...byKey.values()];
}

const sectionMotion = (index: number) => ({
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.25, delay: index * 0.04, ease: [0.22, 1, 0.36, 1] as const },
});

export function ChecksPage() {
  const { id } = useParams<{ id: string }>();
  const datasetId = Number(id);
  const navigate = useNavigate();
  const addToast = useToast();

  const schemaState = useFetch(() => getSchema(datasetId), [datasetId]);
  const checksState = useFetch(() => getChecks(datasetId), [datasetId]);

  const [draftChecks, setDraftChecks] = useState<CheckConfig[] | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    if (checksState.data && draftChecks === null) {
      setDraftChecks(checksState.data.map(toCheckConfig));
    }
  }, [checksState.data, draftChecks]);

  const suggest = useAsyncAction(suggestChecks);
  const save = useAsyncAction(saveChecks);
  const run = useAsyncAction(runChecks);

  // Success/error toasts fire off the hooks' state rather than inline in the handlers,
  // since useAsyncAction's error state updates a render after the awaited call resolves.
  useEffect(() => {
    if (suggest.error) addToast({ message: suggest.error, tone: "error" });
  }, [suggest.error, addToast]);

  useEffect(() => {
    if (save.error) addToast({ message: save.error, tone: "error" });
  }, [save.error, addToast]);

  useEffect(() => {
    if (run.error) addToast({ message: run.error, tone: "error" });
  }, [run.error, addToast]);

  useEffect(() => {
    if (save.data) {
      addToast({
        message: `Saved ${save.data.length} check${save.data.length === 1 ? "" : "s"}.`,
        tone: "success",
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [save.data]);

  async function handleSuggest() {
    const suggestions = await suggest.run(datasetId);
    if (suggestions) setDraftChecks((prev) => mergeByKey(prev ?? [], suggestions));
  }

  function handleRemove(index: number) {
    const removed = draftChecks?.[index];
    if (!removed) return;
    setDraftChecks((prev) => (prev ?? []).filter((_, i) => i !== index));
    addToast({
      message: `Removed ${formatCheckTypeLabel(removed.check_type)}${removed.column ? ` on ${removed.column}` : ""}.`,
      tone: "info",
      action: {
        label: "Undo",
        onClick: () => {
          setDraftChecks((prev) => {
            const copy = [...(prev ?? [])];
            copy.splice(index, 0, removed);
            return copy;
          });
        },
      },
    });
  }

  function handleEdit(index: number) {
    setEditingIndex(index);
    setDialogOpen(true);
  }

  function handleAddManual() {
    setEditingIndex(null);
    setDialogOpen(true);
  }

  function handleDialogSave(check: CheckConfig) {
    setDraftChecks((prev) => {
      const base = prev ?? [];
      if (editingIndex !== null) {
        const copy = [...base];
        copy[editingIndex] = check;
        return copy;
      }
      return mergeByKey(base, [check]);
    });
  }

  async function handleSave() {
    if (!draftChecks) return;
    const saved = await save.run(datasetId, draftChecks);
    if (saved) setDraftChecks(saved.map(toCheckConfig));
  }

  async function handleRun() {
    const result = await run.run(datasetId);
    if (result) navigate(`/datasets/${datasetId}/results`);
  }

  if (schemaState.error) {
    return (
      <PageLayout>
        <EmptyState icon={AlertCircle} title="Couldn't load this dataset" description={schemaState.error} />
      </PageLayout>
    );
  }

  const columns = schemaState.data?.columns.map((c) => c.name) ?? [];
  const hasChecks = (draftChecks ?? []).length > 0;

  return (
    <PageLayout>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-stone-900 dark:text-stone-100">Review &amp; save checks</h1>
          <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
            Explore your data&apos;s structure and let AI suggest quality checks — or add your own.
          </p>
        </div>
        <Link
          to={`/datasets/${datasetId}/history`}
          className="flex shrink-0 items-center gap-1.5 text-sm font-medium text-amber-600 hover:underline dark:text-amber-400"
        >
          <History className="h-4 w-4" />
          View history
        </Link>
      </div>

      <div className="space-y-6">
        <motion.div {...sectionMotion(0)}>
          <Card>
            <CardHeader>
              <h2 className="flex items-center gap-2 text-base font-medium text-stone-800 dark:text-stone-200">
                <Table2 className="h-4 w-4 text-stone-400" />
                Schema
              </h2>
            </CardHeader>
            <CardBody>
              <p className="mb-3 text-sm text-stone-500 dark:text-stone-400">
                Here&apos;s what we found in your file — column names, inferred types, and a preview of the first rows.
              </p>
              {schemaState.loading ? <SkeletonBlock rows={4} /> : schemaState.data && <SchemaTable schema={schemaState.data} />}
            </CardBody>
          </Card>
        </motion.div>

        <motion.div {...sectionMotion(1)}>
          <Card>
            <CardHeader>
              <h2 className="flex items-center gap-2 text-base font-medium text-stone-800 dark:text-stone-200">
                <Sparkles className="h-4 w-4 text-stone-400" />
                Checks
              </h2>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={handleAddManual}>
                  <Plus className="h-3.5 w-3.5" />
                  Add manual check
                </Button>
                <Button onClick={handleSuggest} disabled={suggest.loading}>
                  <Sparkles className="h-3.5 w-3.5" />
                  {suggest.loading ? "Asking AI…" : "Suggest checks with AI"}
                </Button>
              </div>
            </CardHeader>
            <CardBody>
              <p className="mb-3 text-sm text-stone-500 dark:text-stone-400">
                Let AI suggest checks based on your data, or add your own. Nothing runs until you save.
              </p>
              {suggest.loading && (
                <p aria-live="polite" className="mb-3 text-sm text-amber-700 dark:text-amber-400">
                  Asking AI to review {schemaState.data?.columns.length ?? "your"} columns — wider datasets can take
                  up to 30s…
                </p>
              )}

              {checksState.loading && draftChecks === null ? (
                <SkeletonBlock rows={3} />
              ) : (
                <CheckReviewList checks={draftChecks ?? []} onEdit={handleEdit} onRemove={handleRemove} />
              )}

              <div className="mt-4">
                <Button onClick={handleSave} disabled={save.loading}>
                  {save.loading ? "Saving…" : "Save checks"}
                </Button>
              </div>
            </CardBody>
          </Card>
        </motion.div>

        <motion.div {...sectionMotion(2)}>
          <Card>
            <CardBody className="flex items-center justify-between gap-4">
              <div>
                <h2 className="flex items-center gap-2 text-base font-medium text-stone-800 dark:text-stone-200">
                  <PlayCircle className="h-4 w-4 text-stone-400" />
                  Ready to check your data?
                </h2>
                <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
                  Runs your saved checks and takes you to the results.
                </p>
              </div>
              <Button onClick={handleRun} disabled={run.loading || !hasChecks} className="shrink-0">
                <PlayCircle className="h-3.5 w-3.5" />
                {run.loading ? "Running…" : "Run checks"}
              </Button>
            </CardBody>
          </Card>
        </motion.div>
      </div>

      <CheckEditorDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        columns={columns}
        initial={editingIndex !== null ? draftChecks?.[editingIndex] ?? null : null}
        onSave={handleDialogSave}
      />
    </PageLayout>
  );
}

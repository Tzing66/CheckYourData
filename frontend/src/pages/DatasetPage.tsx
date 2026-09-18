import { AlertCircle, History, PlayCircle, Plus, Sparkles, Table2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getChecks, getSchema, runChecks, saveChecks, suggestChecks } from "../api/datasets";
import type { CheckConfig, CheckOut } from "../api/types";
import { CheckEditorDialog } from "../components/CheckEditorDialog";
import { CheckReviewList } from "../components/CheckReviewList";
import { PageLayout } from "../components/layout/PageLayout";
import { RunResultsPanel } from "../components/RunResultsPanel";
import { SchemaTable } from "../components/SchemaTable";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SkeletonBlock } from "../components/ui/Skeleton";
import { useAsyncAction } from "../hooks/useAsyncAction";
import { useFetch } from "../hooks/useFetch";

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

export function DatasetPage() {
  const { id } = useParams<{ id: string }>();
  const datasetId = Number(id);

  const schemaState = useFetch(() => getSchema(datasetId), [datasetId]);
  const checksState = useFetch(() => getChecks(datasetId), [datasetId]);

  const [draftChecks, setDraftChecks] = useState<CheckConfig[] | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  useEffect(() => {
    if (checksState.data && draftChecks === null) {
      setDraftChecks(checksState.data.map(toCheckConfig));
    }
  }, [checksState.data, draftChecks]);

  const suggest = useAsyncAction(suggestChecks);
  const save = useAsyncAction(saveChecks);
  const run = useAsyncAction(runChecks);

  async function handleSuggest() {
    const suggestions = await suggest.run(datasetId);
    if (suggestions) setDraftChecks((prev) => mergeByKey(prev ?? [], suggestions));
  }

  function handleRemove(index: number) {
    setDraftChecks((prev) => (prev ?? []).filter((_, i) => i !== index));
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
    setSaveMessage(null);
    const saved = await save.run(datasetId, draftChecks);
    if (saved) {
      setDraftChecks(saved.map(toCheckConfig));
      setSaveMessage(`Saved ${saved.length} check${saved.length === 1 ? "" : "s"}.`);
    }
  }

  if (schemaState.error) {
    return (
      <PageLayout>
        <EmptyState icon={AlertCircle} title="Couldn't load this dataset" description={schemaState.error} />
      </PageLayout>
    );
  }

  const columns = schemaState.data?.columns.map((c) => c.name) ?? [];

  return (
    <PageLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Review &amp; run checks</h1>
        <Link
          to={`/datasets/${datasetId}/history`}
          className="flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
        >
          <History className="h-4 w-4" />
          View history
        </Link>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <h2 className="flex items-center gap-2 text-base font-medium text-gray-800 dark:text-gray-200">
              <Table2 className="h-4 w-4 text-gray-400" />
              Schema
            </h2>
          </CardHeader>
          <CardBody>
            {schemaState.loading ? <SkeletonBlock rows={4} /> : schemaState.data && <SchemaTable schema={schemaState.data} />}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="flex items-center gap-2 text-base font-medium text-gray-800 dark:text-gray-200">
              <Sparkles className="h-4 w-4 text-gray-400" />
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
            <p aria-live="polite" className="sr-only">
              {suggest.loading ? "Asking AI for check suggestions" : ""}
            </p>
            {suggest.error && (
              <p role="alert" className="mb-3 flex items-center gap-1.5 text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="h-4 w-4" />
                {suggest.error}
              </p>
            )}

            {checksState.loading && draftChecks === null ? (
              <SkeletonBlock rows={3} />
            ) : (
              <CheckReviewList checks={draftChecks ?? []} onEdit={handleEdit} onRemove={handleRemove} />
            )}

            <div className="mt-4 flex items-center gap-3">
              <Button onClick={handleSave} disabled={save.loading}>
                {save.loading ? "Saving…" : "Save checks"}
              </Button>
              <p aria-live="polite" className="text-sm text-green-700 dark:text-green-400">
                {saveMessage}
              </p>
              {save.error && (
                <p role="alert" className="flex items-center gap-1.5 text-sm text-red-600 dark:text-red-400">
                  <AlertCircle className="h-4 w-4" />
                  {save.error}
                </p>
              )}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="flex items-center gap-2 text-base font-medium text-gray-800 dark:text-gray-200">
              <PlayCircle className="h-4 w-4 text-gray-400" />
              Run
            </h2>
            <Button onClick={() => run.run(datasetId)} disabled={run.loading}>
              <PlayCircle className="h-3.5 w-3.5" />
              {run.loading ? "Running…" : "Run checks"}
            </Button>
          </CardHeader>
          <CardBody>
            {run.error && (
              <p role="alert" className="mb-3 flex items-center gap-1.5 text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="h-4 w-4" />
                {run.error}
              </p>
            )}
            {run.data ? (
              <RunResultsPanel run={run.data} />
            ) : (
              <EmptyState icon={PlayCircle} title="No runs yet" description="Save some checks above, then run them." />
            )}
          </CardBody>
        </Card>
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

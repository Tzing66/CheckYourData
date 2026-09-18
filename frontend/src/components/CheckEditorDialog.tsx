import { useEffect, useState } from "react";
import { CHECK_CATEGORIES, CHECK_TYPES, TABLE_LEVEL_CHECK_TYPES, type CheckConfig, type CheckType } from "../api/types";
import { Button } from "./ui/Button";
import { Dialog } from "./ui/Dialog";
import { Select } from "./ui/Select";

interface CheckEditorDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  columns: string[];
  initial: CheckConfig | null;
  onSave: (check: CheckConfig) => void;
}

const CHECK_TYPE_OPTIONS = CHECK_TYPES.map((t) => ({
  value: t,
  label: t,
  group: CHECK_CATEGORIES[t],
}));

function emptyCheck(): CheckConfig {
  return { column: null, check_type: "not_null", params: {}, source: "manual", active: true };
}

export function CheckEditorDialog({ open, onOpenChange, columns, initial, onSave }: CheckEditorDialogProps) {
  const [checkType, setCheckType] = useState<CheckType>("not_null");
  const [column, setColumn] = useState<string>("");
  const [paramsText, setParamsText] = useState("{}");
  const [paramsError, setParamsError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    const base = initial ?? emptyCheck();
    setCheckType(base.check_type);
    setColumn(base.column ?? "");
    setParamsText(JSON.stringify(base.params, null, 2));
    setParamsError(null);
  }, [open, initial]);

  const isTableLevel = TABLE_LEVEL_CHECK_TYPES.has(checkType);

  function handleSave() {
    let params: Record<string, unknown>;
    try {
      params = JSON.parse(paramsText);
    } catch {
      setParamsError("Params must be valid JSON, e.g. {\"min\": 0, \"max\": 100}");
      return;
    }
    onSave({
      column: isTableLevel ? null : column || null,
      check_type: checkType,
      params,
      source: initial?.source ?? "manual",
      active: true,
    });
    onOpenChange(false);
  }

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      title={initial ? "Edit check" : "Add manual check"}
      footer={
        <>
          <Button variant="secondary" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save check</Button>
        </>
      }
    >
      <div className="space-y-4">
        <Select
          id="check-type-select"
          label="Check type"
          value={checkType}
          onValueChange={(v) => setCheckType(v as CheckType)}
          options={CHECK_TYPE_OPTIONS}
        />

        {!isTableLevel && (
          <div>
            <label htmlFor="check-column-select" className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Column
            </label>
            <select
              id="check-column-select"
              value={column}
              onChange={(e) => setColumn(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 transition-colors
                hover:border-gray-400 focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:hover:border-gray-600"
            >
              <option value="">— choose a column —</option>
              {columns.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        )}

        <div>
          <label htmlFor="check-params-textarea" className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Params (JSON)
          </label>
          <textarea
            id="check-params-textarea"
            value={paramsText}
            onChange={(e) => {
              setParamsText(e.target.value);
              setParamsError(null);
            }}
            rows={5}
            className="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-sm text-gray-900 transition-colors
              hover:border-gray-400 focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:hover:border-gray-600"
          />
          {paramsError && (
            <p role="alert" className="mt-1 text-sm text-red-600">
              {paramsError}
            </p>
          )}
        </div>
      </div>
    </Dialog>
  );
}

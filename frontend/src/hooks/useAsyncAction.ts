import { useCallback, useState } from "react";

/** Wraps an imperative API call (button click) with loading/error/last-result state. */
export function useAsyncAction<Args extends unknown[], R>(action: (...args: Args) => Promise<R>) {
  const [data, setData] = useState<R | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (...args: Args): Promise<R | undefined> => {
      setLoading(true);
      setError(null);
      try {
        const result = await action(...args);
        setData(result);
        return result;
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        return undefined;
      } finally {
        setLoading(false);
      }
    },
    [action],
  );

  return { run, data, loading, error, clearError: () => setError(null) };
}

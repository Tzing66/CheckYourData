import { useCallback, useEffect, useState } from "react";

interface FetchState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

/** Runs `fetcher` on mount and whenever `deps` change; `refetch` re-runs it on demand. */
export function useFetch<T>(fetcher: () => Promise<T>, deps: unknown[]) {
  const [state, setState] = useState<FetchState<T>>({ data: null, error: null, loading: true });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    fetcher()
      .then((data) => {
        if (!cancelled) setState({ data, error: null, loading: false });
      })
      .catch((err: unknown) => {
        if (!cancelled) setState({ data: null, error: err instanceof Error ? err.message : String(err), loading: false });
      });
    return () => {
      cancelled = true;
    };
    // deps is caller-controlled; fetcher identity intentionally excluded to avoid re-fetch loops
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  return { ...state, refetch };
}

const STORAGE_KEY = "clientId";

let cachedId: string | null = null;

/** A per-browser anonymous id, persisted in localStorage. Used to scope "my datasets"
 * without requiring a real login — see the owner_id column on the backend.
 */
export function getClientId(): string {
  if (cachedId) return cachedId;

  try {
    const existing = localStorage.getItem(STORAGE_KEY);
    cachedId = existing ?? crypto.randomUUID();
    localStorage.setItem(STORAGE_KEY, cachedId);
  } catch {
    // localStorage unavailable (private browsing, etc.) — still cache in-memory so
    // every request in this session at least uses the same id, just not persisted
    // across reloads.
    cachedId = crypto.randomUUID();
  }
  return cachedId;
}

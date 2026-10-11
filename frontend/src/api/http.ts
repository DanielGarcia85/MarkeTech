// frontend/src/api/http.ts
//
// HTTP client — the only place where the frontend talks to the backend
// ─────────────────────────────────────────────────────────────────────────────
// Components never call the browser's fetch function themselves: they go
// through the functions of this file, so that the way requests are sent can
// change here without touching the rest of the application.

// Sends a GET request to the backend and returns its JSON answer.
// T is the shape the caller expects for that answer.
export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path, {
    headers: { Accept: "application/json" },
  });

  // fetch only fails when the server cannot be reached: an error status
  // such as 404 or 500 has to be turned into an error here
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

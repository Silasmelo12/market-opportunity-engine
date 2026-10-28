export class ApiClientError extends Error {
  status: number;
  detail: string;

  constructor(message: string, status: number, detail = "") {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.detail = detail || message;
  }
}

export async function fetchJson<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let detail = `Erro HTTP ${response.status}`;
    try {
      const errBody = await response.json();
      detail = errBody.detail || errBody.message || detail;
    } catch {
      // Fallback to status text
    }
    throw new ApiClientError(detail, response.status, detail);
  }

  return (await response.json()) as T;
}

export async function postJson<T>(
  url: string,
  payload: unknown,
  signal?: AbortSignal
): Promise<T> {
  return fetchJson<T>(url, {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export async function postMultipart<T>(
  url: string,
  formData: FormData,
  signal?: AbortSignal
): Promise<T> {
  return fetchJson<T>(url, {
    method: "POST",
    body: formData,
    signal,
  });
}

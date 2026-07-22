import { cookies } from "next/headers";

const browserBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const serverBase = process.env.INTERNAL_API_URL
  ? `http://${process.env.INTERNAL_API_URL}`
  : browserBase;

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const payload = await response.json();
      detail = payload.detail ?? detail;
    } catch {}
    throw new ApiError(response.status, detail);
  }
  return response.json() as Promise<T>;
}

export async function serverApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();
  const response = await fetch(`${serverBase}/api/v1${path}`, {
    ...options,
    cache: "no-store",
    headers: {
      Accept: "application/json",
      Cookie: cookieHeader,
      ...(options.headers ?? {})
    }
  });
  return parseResponse<T>(response);
}

function csrfToken(): string | null {
  if (typeof document === "undefined") return null;
  const item = document.cookie.split("; ").find((row) => row.startsWith("csrf_token="));
  return item ? decodeURIComponent(item.split("=")[1]) : null;
}

export async function clientApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrf = csrfToken();
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  const response = await fetch(`${browserBase}/api/v1${path}`, {
    ...options,
    credentials: "include",
    headers
  });
  return parseResponse<T>(response);
}

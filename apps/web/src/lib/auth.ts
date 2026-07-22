import { redirect } from "next/navigation";
import { ApiError, serverApi } from "./api";
import type { User } from "./types";

export async function currentUser(optional = false): Promise<User | null> {
  try {
    return await serverApi<User>("/auth/me");
  } catch (error) {
    if (optional && error instanceof ApiError && error.status === 401) return null;
    redirect("/login");
  }
}

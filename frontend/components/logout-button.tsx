"use client";

import { useRouter } from "next/navigation";

import { logout } from "../lib/api";
import { clearSessionToken } from "../lib/session";

export function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    try {
      await logout();
    } catch {
      // Clear local state even if the backend session already expired.
    } finally {
      clearSessionToken();
      router.push("/");
    }
  }

  return (
    <button className="button button-ghost" onClick={handleLogout} type="button">
      Sign out
    </button>
  );
}

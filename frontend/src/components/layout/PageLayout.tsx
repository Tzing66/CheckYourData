import type { ReactNode } from "react";

export function PageLayout({ children }: { children: ReactNode }) {
  return <div className="mx-auto max-w-4xl px-4 py-8">{children}</div>;
}

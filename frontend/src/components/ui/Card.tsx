import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-stone-200 bg-white shadow-sm shadow-stone-900/5 transition-colors duration-300 dark:border-stone-800 dark:bg-stone-900 dark:shadow-none ${className}`}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = "" }: CardProps) {
  return (
    <div className={`flex items-center justify-between gap-3 border-b border-stone-100 px-5 py-4 dark:border-stone-800 ${className}`}>
      {children}
    </div>
  );
}

export function CardBody({ children, className = "" }: CardProps) {
  return <div className={`px-5 py-4 ${className}`}>{children}</div>;
}

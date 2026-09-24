import { motion, type HTMLMotionProps } from "motion/react";

interface ButtonProps extends HTMLMotionProps<"button"> {
  variant?: "primary" | "secondary" | "danger";
}

const VARIANT_CLASSES: Record<string, string> = {
  primary:
    "bg-amber-500 text-stone-900 shadow-sm hover:bg-amber-400 disabled:bg-amber-200 disabled:text-amber-700 disabled:shadow-none dark:disabled:bg-stone-800 dark:disabled:text-stone-600",
  secondary:
    "bg-white text-stone-800 border border-stone-300 hover:bg-stone-50 disabled:text-stone-400 dark:bg-stone-800 dark:text-stone-100 dark:border-stone-700 dark:hover:bg-stone-750",
  danger:
    "bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 disabled:text-red-300 dark:bg-red-950 dark:text-red-300 dark:border-red-900",
};

export function Button({ variant = "primary", className = "", disabled, ...props }: ButtonProps) {
  return (
    <motion.button
      type="button"
      disabled={disabled}
      whileTap={disabled ? undefined : { scale: 0.97 }}
      transition={{ duration: 0.15, ease: [0.22, 1, 0.36, 1] }}
      className={`inline-flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 disabled:cursor-not-allowed ${VARIANT_CLASSES[variant]} ${className}`}
      {...props}
    />
  );
}

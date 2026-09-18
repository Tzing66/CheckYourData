import { motion, type HTMLMotionProps } from "motion/react";

interface ButtonProps extends HTMLMotionProps<"button"> {
  variant?: "primary" | "secondary" | "danger";
}

const VARIANT_CLASSES: Record<string, string> = {
  primary: "bg-blue-600 text-white shadow-sm hover:bg-blue-700 disabled:bg-blue-300 disabled:shadow-none",
  secondary:
    "bg-white text-gray-800 border border-gray-300 hover:bg-gray-50 disabled:text-gray-400 dark:bg-gray-800 dark:text-gray-100 dark:border-gray-700 dark:hover:bg-gray-750",
  danger: "bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 disabled:text-red-300 dark:bg-red-950 dark:text-red-300 dark:border-red-900",
};

export function Button({ variant = "primary", className = "", disabled, ...props }: ButtonProps) {
  return (
    <motion.button
      type="button"
      disabled={disabled}
      whileTap={disabled ? undefined : { scale: 0.97 }}
      transition={{ duration: 0.1 }}
      className={`inline-flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${VARIANT_CLASSES[variant]} ${className}`}
      {...props}
    />
  );
}

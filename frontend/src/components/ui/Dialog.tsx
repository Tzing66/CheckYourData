import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import type { ReactNode } from "react";

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function Dialog({ open, onOpenChange, title, children, footer }: DialogProps) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="dialog-overlay fixed inset-0 bg-black/40 backdrop-blur-[2px]" />
        <DialogPrimitive.Content
          className="dialog-content fixed top-1/2 left-1/2 w-full max-w-md -translate-x-1/2 -translate-y-1/2
            rounded-xl border border-stone-200 bg-white p-6 shadow-xl focus:outline-none dark:border-stone-800 dark:bg-stone-900"
        >
          <DialogPrimitive.Title className="text-lg font-semibold text-stone-900 dark:text-stone-100">
            {title}
          </DialogPrimitive.Title>
          <div className="mt-4">{children}</div>
          {footer && <div className="mt-6 flex justify-end gap-2">{footer}</div>}
          <DialogPrimitive.Close asChild>
            <button
              type="button"
              aria-label="Close dialog"
              className="absolute top-4 right-4 rounded-md p-1 text-stone-400 transition-colors duration-200 hover:bg-stone-100 hover:text-stone-600 dark:hover:bg-stone-800 dark:hover:text-stone-300"
            >
              <X className="h-4 w-4" />
            </button>
          </DialogPrimitive.Close>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

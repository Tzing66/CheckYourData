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
            rounded-xl border border-gray-200 bg-white p-6 shadow-xl focus:outline-none dark:border-gray-800 dark:bg-gray-900"
        >
          <DialogPrimitive.Title className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {title}
          </DialogPrimitive.Title>
          <div className="mt-4">{children}</div>
          {footer && <div className="mt-6 flex justify-end gap-2">{footer}</div>}
          <DialogPrimitive.Close asChild>
            <button
              type="button"
              aria-label="Close dialog"
              className="absolute top-4 right-4 rounded-md p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          </DialogPrimitive.Close>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

import * as CheckboxPrimitive from "@radix-ui/react-checkbox";
import { Check } from "lucide-react";

interface CheckboxProps {
  id: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  label: string;
}

export function Checkbox({ id, checked, onCheckedChange, label }: CheckboxProps) {
  return (
    <div className="flex items-center gap-2">
      <CheckboxPrimitive.Root
        id={id}
        checked={checked}
        onCheckedChange={(state) => onCheckedChange(state === true)}
        className="flex h-5 w-5 items-center justify-center rounded border border-stone-300 transition-colors duration-200
          data-[state=checked]:border-amber-600 data-[state=checked]:bg-amber-600 dark:border-stone-600"
      >
        <CheckboxPrimitive.Indicator>
          <Check className="h-3.5 w-3.5 text-white" />
        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Root>
      <label htmlFor={id} className="cursor-pointer text-sm text-stone-800 dark:text-stone-200">
        {label}
      </label>
    </div>
  );
}

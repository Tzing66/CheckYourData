import * as SelectPrimitive from "@radix-ui/react-select";
import { Check, ChevronDown } from "lucide-react";

export interface SelectOption {
  value: string;
  label: string;
  group?: string;
}

interface SelectProps {
  id: string;
  label: string;
  value: string;
  onValueChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
}

export function Select({ id, label, value, onValueChange, options, placeholder }: SelectProps) {
  const groups = new Map<string | undefined, SelectOption[]>();
  for (const opt of options) {
    const key = opt.group;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(opt);
  }

  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-stone-700 dark:text-stone-300">
        {label}
      </label>
      <SelectPrimitive.Root value={value} onValueChange={onValueChange}>
        <SelectPrimitive.Trigger
          id={id}
          className="flex w-full items-center justify-between rounded-md border border-stone-300 bg-white
            px-3 py-2 text-sm text-stone-900 transition-colors duration-200 hover:border-stone-400
            focus:border-amber-500 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100 dark:hover:border-stone-600"
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon aria-hidden>
            <ChevronDown className="h-4 w-4 text-stone-400" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
        <SelectPrimitive.Portal>
          <SelectPrimitive.Content
            className="z-50 max-h-72 overflow-hidden rounded-md border border-stone-200 bg-white shadow-lg
              dark:border-stone-700 dark:bg-stone-900"
          >
            <SelectPrimitive.Viewport className="p-1">
              {[...groups.entries()].map(([group, opts]) => (
                <SelectPrimitive.Group key={group ?? "_"}>
                  {group && (
                    <SelectPrimitive.Label className="px-2 py-1 text-xs font-semibold text-stone-400 uppercase">
                      {group}
                    </SelectPrimitive.Label>
                  )}
                  {opts.map((opt) => (
                    <SelectPrimitive.Item
                      key={opt.value}
                      value={opt.value}
                      className="flex cursor-pointer items-center justify-between rounded px-2 py-1.5 text-sm text-stone-900 outline-none
                        data-[highlighted]:bg-amber-50 dark:text-stone-100 dark:data-[highlighted]:bg-amber-950"
                    >
                      <SelectPrimitive.ItemText>{opt.label}</SelectPrimitive.ItemText>
                      <SelectPrimitive.ItemIndicator>
                        <Check className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
                      </SelectPrimitive.ItemIndicator>
                    </SelectPrimitive.Item>
                  ))}
                </SelectPrimitive.Group>
              ))}
            </SelectPrimitive.Viewport>
          </SelectPrimitive.Content>
        </SelectPrimitive.Portal>
      </SelectPrimitive.Root>
    </div>
  );
}

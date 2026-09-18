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
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>
      <SelectPrimitive.Root value={value} onValueChange={onValueChange}>
        <SelectPrimitive.Trigger
          id={id}
          className="flex w-full items-center justify-between rounded-md border border-gray-300 bg-white
            px-3 py-2 text-sm text-gray-900 transition-colors hover:border-gray-400
            focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:hover:border-gray-600"
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon aria-hidden>
            <ChevronDown className="h-4 w-4 text-gray-400" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
        <SelectPrimitive.Portal>
          <SelectPrimitive.Content
            className="z-50 max-h-72 overflow-hidden rounded-md border border-gray-200 bg-white shadow-lg
              dark:border-gray-700 dark:bg-gray-900"
          >
            <SelectPrimitive.Viewport className="p-1">
              {[...groups.entries()].map(([group, opts]) => (
                <SelectPrimitive.Group key={group ?? "_"}>
                  {group && (
                    <SelectPrimitive.Label className="px-2 py-1 text-xs font-semibold text-gray-400 uppercase">
                      {group}
                    </SelectPrimitive.Label>
                  )}
                  {opts.map((opt) => (
                    <SelectPrimitive.Item
                      key={opt.value}
                      value={opt.value}
                      className="flex cursor-pointer items-center justify-between rounded px-2 py-1.5 text-sm text-gray-900 outline-none
                        data-[highlighted]:bg-blue-50 dark:text-gray-100 dark:data-[highlighted]:bg-blue-950"
                    >
                      <SelectPrimitive.ItemText>{opt.label}</SelectPrimitive.ItemText>
                      <SelectPrimitive.ItemIndicator>
                        <Check className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400" />
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

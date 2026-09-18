import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

interface UploadDropzoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function UploadDropzone({ onFileSelected, disabled }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleDrop(event: React.DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) onFileSelected(file);
  }

  return (
    <label
      htmlFor="csv-upload-input"
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed
        p-14 text-center transition-all duration-200 ${
          isDragging
            ? "scale-[1.01] border-blue-500 bg-blue-50 dark:bg-blue-950/40"
            : "border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50/40 dark:border-gray-700 dark:bg-gray-900 dark:hover:border-blue-600 dark:hover:bg-blue-950/20"
        } ${disabled ? "pointer-events-none opacity-50" : ""}`}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-950">
        <UploadCloud aria-hidden className="h-6 w-6 text-blue-600 dark:text-blue-400" strokeWidth={2} />
      </div>
      <p className="mt-4 text-base font-medium text-gray-800 dark:text-gray-100">
        Drop a CSV file here, or click to choose one
      </p>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">CSV files up to 20MB</p>
      <input
        ref={inputRef}
        id="csv-upload-input"
        type="file"
        accept=".csv,text/csv"
        disabled={disabled}
        className="sr-only"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFileSelected(file);
        }}
      />
    </label>
  );
}

import { ArrowRight, LineChart, Sparkles, UploadCloud } from "lucide-react";
import { motion } from "motion/react";
import { useNavigate } from "react-router-dom";
import { PageLayout } from "../components/layout/PageLayout";
import { Button } from "../components/ui/Button";

const STEPS = [
  {
    icon: UploadCloud,
    title: "Upload a CSV",
    description: "Drop in a file. We'll infer its columns and types automatically.",
  },
  {
    icon: Sparkles,
    title: "AI suggests checks",
    description: "Claude reads your schema and proposes checks per column — you approve, edit, or add your own.",
  },
  {
    icon: LineChart,
    title: "Run & track",
    description: "See pass/fail instantly, then watch results and drift trend over every run after that.",
  },
];

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <PageLayout>
      <div className="relative py-12 text-center">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 -top-10 -z-10 h-80 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-amber-200/40 via-transparent to-transparent blur-2xl dark:from-amber-500/10"
        />

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
        >
          <h1 className="mb-3 text-4xl font-semibold tracking-tight text-stone-900 dark:text-stone-100">
            Check your data before it checks you
          </h1>
          <p className="mx-auto mb-8 max-w-lg text-stone-600 dark:text-stone-400">
            Upload a CSV to get AI-suggested data quality checks, review and run them, and track results over time —
            no config files, no setup.
          </p>
          <Button className="!px-5 !py-3 text-base" onClick={() => navigate("/upload")}>
            Get started
            <ArrowRight className="h-4 w-4" />
          </Button>
        </motion.div>

        <div className="mx-auto mt-20 grid max-w-2xl gap-10 text-center sm:grid-cols-3 sm:gap-6">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: 0.1 + i * 0.05, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col items-center"
            >
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-500/15">
                <step.icon className="h-4.5 w-4.5 text-amber-600 dark:text-amber-400" strokeWidth={2} />
              </div>
              <h3 className="mb-1 text-sm font-semibold text-stone-800 dark:text-stone-200">
                {i + 1}. {step.title}
              </h3>
              <p className="max-w-[15rem] text-sm text-stone-500 dark:text-stone-400">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </PageLayout>
  );
}

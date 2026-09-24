import { TrendingUp } from "lucide-react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { DRIFT_CHECK_TYPES, type CheckType } from "../api/types";
import { useTheme } from "../hooks/useTheme";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

// Recharts renders raw SVG attributes, which Tailwind's dark: classes can't reach —
// picked to match the stone/amber palette used everywhere else via CSS classes.
const CHART_COLORS = {
  light: { grid: "#e7e5e4", tick: "#78716c", line: "#d97706" },
  dark: { grid: "#292524", tick: "#a8a29e", line: "#f59e0b" },
};

export interface HistoryPoint {
  runAt: string;
  passed: boolean;
  signal: number;
}

const SIGNAL_KEYS = ["diff_pct", "psi", "outlier_rate", "null_pct", "uniqueness_pct"] as const;

/** Pulls a representative number out of a result's details for charting, falling back to pass/fail. */
export function deriveSignal(details: Record<string, unknown>, passed: boolean): number {
  for (const key of SIGNAL_KEYS) {
    const value = details[key];
    if (typeof value === "number") return value;
  }
  return passed ? 0 : 1;
}

function CheckDot(props: { cx?: number; cy?: number; payload?: HistoryPoint }) {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || !payload) return null;
  return <circle cx={cx} cy={cy} r={4} fill={payload.passed ? "#16a34a" : "#dc2626"} stroke="none" />;
}

interface HistoryChartProps {
  column: string | null;
  checkType: CheckType;
  points: HistoryPoint[];
}

export function HistoryChart({ column, checkType, points }: HistoryChartProps) {
  const { theme } = useTheme();
  const colors = CHART_COLORS[theme];
  const isDrift = DRIFT_CHECK_TYPES.has(checkType);
  const failCount = points.filter((p) => !p.passed).length;

  return (
    <Card className="p-4">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-stone-800 dark:text-stone-200">
          {column ?? "Table-level"} — <span className="font-mono text-xs">{checkType}</span>
          {isDrift && <Badge tone="yellow" icon={<TrendingUp className="h-3 w-3" />}>drift check</Badge>}
        </h3>
        {failCount > 0 && (
          <Badge tone="red">
            {failCount} failure{failCount === 1 ? "" : "s"}
          </Badge>
        )}
      </div>
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ top: 4, right: 8, bottom: 4, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
            <XAxis
              dataKey="runAt"
              tickFormatter={(v: string) => new Date(v).toLocaleDateString()}
              tick={{ fontSize: 11, fill: colors.tick }}
            />
            <YAxis tick={{ fontSize: 11, fill: colors.tick }} width={40} />
            <Tooltip
              formatter={(value, _name, item) => {
                const payload = item?.payload as HistoryPoint | undefined;
                return [String(value), payload?.passed ? "passed" : "failed"];
              }}
              labelFormatter={(label) => (typeof label === "string" ? new Date(label).toLocaleString() : String(label))}
              contentStyle={{
                backgroundColor: theme === "dark" ? "#1c1917" : "#ffffff",
                borderColor: colors.grid,
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Line type="monotone" dataKey="signal" stroke={colors.line} strokeWidth={2} dot={<CheckDot />} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

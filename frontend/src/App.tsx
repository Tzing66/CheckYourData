import { AnimatePresence, motion } from "motion/react";
import { lazy, Suspense, useRef } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { AppHeader } from "./components/layout/AppHeader";
import { ToastProvider } from "./components/ui/ToastProvider";

const LandingPage = lazy(() => import("./pages/LandingPage").then((m) => ({ default: m.LandingPage })));
const UploadPage = lazy(() => import("./pages/UploadPage").then((m) => ({ default: m.UploadPage })));
const ChecksPage = lazy(() => import("./pages/ChecksPage").then((m) => ({ default: m.ChecksPage })));
const ResultsPage = lazy(() => import("./pages/ResultsPage").then((m) => ({ default: m.ResultsPage })));
const HistoryPage = lazy(() => import("./pages/HistoryPage").then((m) => ({ default: m.HistoryPage })));
const DatasetsListPage = lazy(() =>
  import("./pages/DatasetsListPage").then((m) => ({ default: m.DatasetsListPage })),
);

/** Where each route sits in the guided flow, used to pick a slide direction. */
function stepIndex(pathname: string): number {
  if (pathname === "/") return 0;
  if (pathname === "/upload" || pathname === "/datasets") return 1;
  if (/\/results$/.test(pathname)) return 3;
  if (/\/history$/.test(pathname)) return 2;
  if (/^\/datasets\/\d+$/.test(pathname)) return 2;
  return 0;
}

const SLIDE_DISTANCE = 56;

const slideVariants = {
  enter: (direction: number) => ({ opacity: 0, x: direction >= 0 ? SLIDE_DISTANCE : -SLIDE_DISTANCE }),
  center: { opacity: 1, x: 0 },
  exit: (direction: number) => ({ opacity: 0, x: direction >= 0 ? -SLIDE_DISTANCE : SLIDE_DISTANCE }),
};

function PageTransition({ children, direction }: { children: React.ReactNode; direction: number }) {
  return (
    <motion.div
      custom={direction}
      variants={slideVariants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
    >
      <Suspense fallback={<div className="min-h-[50vh]" />}>{children}</Suspense>
    </motion.div>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  const currentIndex = stepIndex(location.pathname);
  const prevIndexRef = useRef(currentIndex);
  const direction = currentIndex >= prevIndexRef.current ? 1 : -1;
  prevIndexRef.current = currentIndex;

  return (
    <AnimatePresence mode="wait" initial={false} custom={direction}>
      <Routes location={location} key={location.pathname}>
        <Route
          path="/"
          element={
            <PageTransition direction={direction}>
              <LandingPage />
            </PageTransition>
          }
        />
        <Route
          path="/upload"
          element={
            <PageTransition direction={direction}>
              <UploadPage />
            </PageTransition>
          }
        />
        <Route
          path="/datasets"
          element={
            <PageTransition direction={direction}>
              <DatasetsListPage />
            </PageTransition>
          }
        />
        <Route
          path="/datasets/:id"
          element={
            <PageTransition direction={direction}>
              <ChecksPage />
            </PageTransition>
          }
        />
        <Route
          path="/datasets/:id/results"
          element={
            <PageTransition direction={direction}>
              <ResultsPage />
            </PageTransition>
          }
        />
        <Route
          path="/datasets/:id/history"
          element={
            <PageTransition direction={direction}>
              <HistoryPage />
            </PageTransition>
          }
        />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <div className="min-h-screen overflow-x-hidden bg-stone-50 transition-colors duration-300 dark:bg-stone-950">
          <AppHeader />
          <AnimatedRoutes />
        </div>
      </ToastProvider>
    </BrowserRouter>
  );
}

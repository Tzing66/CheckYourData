import { AnimatePresence, motion } from "motion/react";
import type { ReactNode } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { AppHeader } from "./components/layout/AppHeader";
import { DatasetPage } from "./pages/DatasetPage";
import { HistoryPage } from "./pages/HistoryPage";
import { UploadPage } from "./pages/UploadPage";

function PageTransition({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.22, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait" initial={false}>
      <Routes location={location} key={location.pathname}>
        <Route
          path="/"
          element={
            <PageTransition>
              <UploadPage />
            </PageTransition>
          }
        />
        <Route
          path="/datasets/:id"
          element={
            <PageTransition>
              <DatasetPage />
            </PageTransition>
          }
        />
        <Route
          path="/datasets/:id/history"
          element={
            <PageTransition>
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
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <AppHeader />
        <AnimatedRoutes />
      </div>
    </BrowserRouter>
  );
}

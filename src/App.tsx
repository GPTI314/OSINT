import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useThemeStore, useAuthStore } from './store';
import { lightTheme, darkTheme } from './theme';

// Layouts
import { AppLayout } from './layouts/AppLayout';

// Pages
import { Login } from './pages/auth/Login';
import { Dashboard } from './pages/dashboard/Dashboard';
import { InvestigationsList } from './pages/investigations/InvestigationsList';
import { InvestigationDetail } from './pages/investigations/InvestigationDetail';
import { TargetsList } from './pages/targets/TargetsList';
import { ScrapingJobs } from './pages/scraping/ScrapingJobs';
import { CrawlingSessions } from './pages/crawling/CrawlingSessions';
import { Intelligence } from './pages/intelligence/Intelligence';
import { AnalysisView } from './pages/analysis/AnalysisView';
import { FindingsList } from './pages/findings/FindingsList';
import { ReportsList } from './pages/reports/ReportsList';
import { Settings } from './pages/settings/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  const { mode } = useThemeStore();

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={mode === 'light' ? lightTheme : darkTheme}>
        <CssBaseline />
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />

            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />

              <Route path="investigations">
                <Route index element={<InvestigationsList />} />
                <Route path=":id" element={<InvestigationDetail />} />
              </Route>

              <Route path="targets">
                <Route index element={<TargetsList />} />
              </Route>

              <Route path="scraping">
                <Route index element={<ScrapingJobs />} />
              </Route>

              <Route path="crawling">
                <Route index element={<CrawlingSessions />} />
              </Route>

              <Route path="intelligence">
                <Route index element={<Intelligence />} />
              </Route>

              <Route path="analysis">
                <Route index element={<AnalysisView />} />
              </Route>

              <Route path="findings">
                <Route index element={<FindingsList />} />
              </Route>

              <Route path="reports">
                <Route index element={<ReportsList />} />
              </Route>

              <Route path="settings">
                <Route index element={<Settings />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

import { Navigate, Route, Routes } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import AdminPage from '../pages/admin/AdminPage';
import ContractDetailPage from '../pages/ContractDetailPage';
import ContractListPage from '../pages/ContractListPage';
import ContractUploadPage from '../pages/ContractUploadPage';
import DashboardPage from '../pages/DashboardPage';
import LoginPage from '../pages/LoginPage';
import ParseResultPage from '../pages/ParseResultPage';
import RegisterPage from '../pages/RegisterPage';
import ReportPage from '../pages/ReportPage';
import ReviewProgressPage from '../pages/ReviewProgressPage';
import RiskAnalysisPage from '../pages/RiskAnalysisPage';
import SuggestionPage from '../pages/SuggestionPage';

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="contracts" element={<ContractListPage />} />
        <Route path="contracts/upload" element={<ContractUploadPage />} />
        <Route path="contracts/:id" element={<ContractDetailPage />} />
        <Route path="contracts/:id/parse-result" element={<ParseResultPage />} />
        <Route path="review-tasks/:taskId/progress" element={<ReviewProgressPage />} />
        <Route path="review-tasks/:taskId/risks" element={<RiskAnalysisPage />} />
        <Route path="review-tasks/:taskId/suggestions" element={<SuggestionPage />} />
        <Route path="reports/:taskId" element={<ReportPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Routes>
  );
}

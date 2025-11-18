import axios, { AxiosInstance } from 'axios';
import {
  ApiResponse,
  PaginatedResponse,
  Investigation,
  Target,
  ScrapingJob,
  CrawlingSession,
  IntelligenceData,
  Finding,
  Report,
  Statistics,
  SearchFilters,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle response errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Dashboard
  async getStatistics(): Promise<Statistics> {
    const response = await this.client.get<ApiResponse<Statistics>>('/dashboard/statistics');
    return response.data.data;
  }

  async getRecentActivity(): Promise<any[]> {
    const response = await this.client.get<ApiResponse<any[]>>('/dashboard/recent-activity');
    return response.data.data;
  }

  // Investigations
  async getInvestigations(filters?: SearchFilters): Promise<PaginatedResponse<Investigation>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Investigation>>>(
      '/investigations',
      { params: filters }
    );
    return response.data.data;
  }

  async getInvestigation(id: string): Promise<Investigation> {
    const response = await this.client.get<ApiResponse<Investigation>>(`/investigations/${id}`);
    return response.data.data;
  }

  async createInvestigation(data: Partial<Investigation>): Promise<Investigation> {
    const response = await this.client.post<ApiResponse<Investigation>>('/investigations', data);
    return response.data.data;
  }

  async updateInvestigation(id: string, data: Partial<Investigation>): Promise<Investigation> {
    const response = await this.client.put<ApiResponse<Investigation>>(`/investigations/${id}`, data);
    return response.data.data;
  }

  async deleteInvestigation(id: string): Promise<void> {
    await this.client.delete(`/investigations/${id}`);
  }

  // Targets
  async getTargets(investigationId?: string, filters?: SearchFilters): Promise<PaginatedResponse<Target>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Target>>>('/targets', {
      params: { investigationId, ...filters },
    });
    return response.data.data;
  }

  async getTarget(id: string): Promise<Target> {
    const response = await this.client.get<ApiResponse<Target>>(`/targets/${id}`);
    return response.data.data;
  }

  async createTarget(data: Partial<Target>): Promise<Target> {
    const response = await this.client.post<ApiResponse<Target>>('/targets', data);
    return response.data.data;
  }

  async updateTarget(id: string, data: Partial<Target>): Promise<Target> {
    const response = await this.client.put<ApiResponse<Target>>(`/targets/${id}`, data);
    return response.data.data;
  }

  async deleteTarget(id: string): Promise<void> {
    await this.client.delete(`/targets/${id}`);
  }

  // Scraping
  async getScrapingJobs(filters?: SearchFilters): Promise<PaginatedResponse<ScrapingJob>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<ScrapingJob>>>('/scraping/jobs', {
      params: filters,
    });
    return response.data.data;
  }

  async getScrapingJob(id: string): Promise<ScrapingJob> {
    const response = await this.client.get<ApiResponse<ScrapingJob>>(`/scraping/jobs/${id}`);
    return response.data.data;
  }

  async createScrapingJob(data: Partial<ScrapingJob>): Promise<ScrapingJob> {
    const response = await this.client.post<ApiResponse<ScrapingJob>>('/scraping/jobs', data);
    return response.data.data;
  }

  async pauseScrapingJob(id: string): Promise<void> {
    await this.client.post(`/scraping/jobs/${id}/pause`);
  }

  async resumeScrapingJob(id: string): Promise<void> {
    await this.client.post(`/scraping/jobs/${id}/resume`);
  }

  async cancelScrapingJob(id: string): Promise<void> {
    await this.client.post(`/scraping/jobs/${id}/cancel`);
  }

  // Crawling
  async getCrawlingSessions(filters?: SearchFilters): Promise<PaginatedResponse<CrawlingSession>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<CrawlingSession>>>(
      '/crawling/sessions',
      { params: filters }
    );
    return response.data.data;
  }

  async getCrawlingSession(id: string): Promise<CrawlingSession> {
    const response = await this.client.get<ApiResponse<CrawlingSession>>(`/crawling/sessions/${id}`);
    return response.data.data;
  }

  async createCrawlingSession(data: Partial<CrawlingSession>): Promise<CrawlingSession> {
    const response = await this.client.post<ApiResponse<CrawlingSession>>('/crawling/sessions', data);
    return response.data.data;
  }

  async pauseCrawlingSession(id: string): Promise<void> {
    await this.client.post(`/crawling/sessions/${id}/pause`);
  }

  async resumeCrawlingSession(id: string): Promise<void> {
    await this.client.post(`/crawling/sessions/${id}/resume`);
  }

  async cancelCrawlingSession(id: string): Promise<void> {
    await this.client.post(`/crawling/sessions/${id}/cancel`);
  }

  // Intelligence
  async getIntelligenceData(filters?: SearchFilters): Promise<PaginatedResponse<IntelligenceData>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<IntelligenceData>>>(
      '/intelligence',
      { params: filters }
    );
    return response.data.data;
  }

  async enrichTarget(targetId: string, enrichmentType: string): Promise<IntelligenceData> {
    const response = await this.client.post<ApiResponse<IntelligenceData>>(
      `/intelligence/enrich/${targetId}`,
      { type: enrichmentType }
    );
    return response.data.data;
  }

  // Findings
  async getFindings(investigationId?: string, filters?: SearchFilters): Promise<PaginatedResponse<Finding>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Finding>>>('/findings', {
      params: { investigationId, ...filters },
    });
    return response.data.data;
  }

  async getFinding(id: string): Promise<Finding> {
    const response = await this.client.get<ApiResponse<Finding>>(`/findings/${id}`);
    return response.data.data;
  }

  async createFinding(data: Partial<Finding>): Promise<Finding> {
    const response = await this.client.post<ApiResponse<Finding>>('/findings', data);
    return response.data.data;
  }

  async updateFinding(id: string, data: Partial<Finding>): Promise<Finding> {
    const response = await this.client.put<ApiResponse<Finding>>(`/findings/${id}`, data);
    return response.data.data;
  }

  async deleteFinding(id: string): Promise<void> {
    await this.client.delete(`/findings/${id}`);
  }

  // Reports
  async getReports(investigationId?: string): Promise<PaginatedResponse<Report>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Report>>>('/reports', {
      params: { investigationId },
    });
    return response.data.data;
  }

  async getReport(id: string): Promise<Report> {
    const response = await this.client.get<ApiResponse<Report>>(`/reports/${id}`);
    return response.data.data;
  }

  async createReport(data: Partial<Report>): Promise<Report> {
    const response = await this.client.post<ApiResponse<Report>>('/reports', data);
    return response.data.data;
  }

  async updateReport(id: string, data: Partial<Report>): Promise<Report> {
    const response = await this.client.put<ApiResponse<Report>>(`/reports/${id}`, data);
    return response.data.data;
  }

  async exportReport(id: string, format: 'pdf' | 'docx' | 'html'): Promise<Blob> {
    const response = await this.client.get(`/reports/${id}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  // Analysis
  async getCorrelationGraph(investigationId: string): Promise<any> {
    const response = await this.client.get(`/analysis/correlation/${investigationId}`);
    return response.data.data;
  }

  async getTimeline(investigationId: string): Promise<any[]> {
    const response = await this.client.get(`/analysis/timeline/${investigationId}`);
    return response.data.data;
  }

  async getThreatAnalysis(targetId: string): Promise<any> {
    const response = await this.client.get(`/analysis/threat/${targetId}`);
    return response.data.data;
  }

  // Search
  async search(query: string, type?: string): Promise<any[]> {
    const response = await this.client.get('/search', {
      params: { query, type },
    });
    return response.data.data;
  }

  // Export
  async exportData(type: string, filters: any, format: 'csv' | 'json' | 'xlsx'): Promise<Blob> {
    const response = await this.client.post(
      '/export',
      { type, filters, format },
      { responseType: 'blob' }
    );
    return response.data;
  }
}

export const api = new ApiService();

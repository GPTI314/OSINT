import { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  Assignment,
  Person,
  BugReport,
  Warning,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../../services/api';
import { Statistics } from '../../types';
import { formatRelativeTime, getSeverityColor } from '../../utils/helpers';

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  trend?: number;
}

const StatCard = ({ title, value, icon, color, trend }: StatCardProps) => (
  <Card>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4">{value}</Typography>
          {trend !== undefined && (
            <Box display="flex" alignItems="center" mt={1}>
              <TrendingUp fontSize="small" color={trend >= 0 ? 'success' : 'error'} />
              <Typography
                variant="body2"
                color={trend >= 0 ? 'success.main' : 'error.main'}
                ml={0.5}
              >
                {trend >= 0 ? '+' : ''}{trend}%
              </Typography>
            </Box>
          )}
        </Box>
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: '50%',
            p: 2,
            color: 'white',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

export const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, activityData] = await Promise.all([
        api.getStatistics(),
        api.getRecentActivity(),
      ]);
      setStats(statsData);
      setRecentActivity(activityData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const findingsData = stats?.findings.bySeverity
    ? Object.entries(stats.findings.bySeverity).map(([name, value]) => ({
        name,
        value,
        color: getSeverityColor(name as any),
      }))
    : [];

  const targetsData = stats?.targets.byType
    ? Object.entries(stats.targets.byType).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Investigations"
            value={stats?.investigations.active || 0}
            icon={<Assignment />}
            color="#1976d2"
            trend={12}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Targets"
            value={stats?.targets.total || 0}
            icon={<Person />}
            color="#2e7d32"
            trend={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Findings"
            value={stats?.findings.total || 0}
            icon={<BugReport />}
            color="#ed6c02"
            trend={-3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Data Collected"
            value={`${(stats?.dataCollected.totalRecords || 0) / 1000}K`}
            icon={<Warning />}
            color="#9c27b0"
            trend={25}
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Findings by Severity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={findingsData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {findingsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Targets by Type
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={targetsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        <List>
          {recentActivity.map((activity, index) => (
            <ListItem key={index} divider={index < recentActivity.length - 1}>
              <ListItemText
                primary={activity.title}
                secondary={
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="body2" color="textSecondary">
                      {formatRelativeTime(activity.timestamp)}
                    </Typography>
                    <Chip label={activity.type} size="small" />
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

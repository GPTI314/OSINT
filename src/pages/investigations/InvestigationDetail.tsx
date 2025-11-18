import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Tab,
  Tabs,
  CircularProgress,
  Stack,
} from '@mui/material';
import { ArrowBack, Edit } from '@mui/icons-material';
import { api } from '../../services/api';
import { Investigation, Target, Finding } from '../../types';
import { formatDate, getStatusColor } from '../../utils/helpers';
import { DataTable } from '../../components/common/DataTable';
import { GridColDef } from '@mui/x-data-grid';

export const InvestigationDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [targets, setTargets] = useState<Target[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (id) {
      loadInvestigationData(id);
    }
  }, [id]);

  const loadInvestigationData = async (investigationId: string) => {
    setLoading(true);
    try {
      const [investigationData, targetsData, findingsData] = await Promise.all([
        api.getInvestigation(investigationId),
        api.getTargets(investigationId),
        api.getFindings(investigationId),
      ]);
      setInvestigation(investigationData);
      setTargets(targetsData.items);
      setFindings(findingsData.items);
    } catch (error) {
      console.error('Failed to load investigation data:', error);
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

  if (!investigation) {
    return (
      <Box>
        <Typography variant="h5">Investigation not found</Typography>
      </Box>
    );
  }

  const targetColumns: GridColDef[] = [
    { field: 'type', headerName: 'Type', width: 120 },
    { field: 'value', headerName: 'Value', flex: 1 },
    { field: 'label', headerName: 'Label', width: 150 },
    {
      field: 'riskScore',
      headerName: 'Risk Score',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value || 'N/A'}
          size="small"
          color={params.value > 70 ? 'error' : params.value > 40 ? 'warning' : 'success'}
        />
      ),
    },
  ];

  const findingColumns: GridColDef[] = [
    { field: 'title', headerName: 'Title', flex: 1 },
    {
      field: 'severity',
      headerName: 'Severity',
      width: 120,
      renderCell: (params) => (
        <Chip label={params.value} size="small" color="error" />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip label={params.value} size="small" />
      ),
    },
    { field: 'category', headerName: 'Category', width: 150 },
  ];

  return (
    <Box>
      <Stack direction="row" spacing={2} alignItems="center" mb={3}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/investigations')}>
          Back
        </Button>
        <Typography variant="h4" sx={{ flexGrow: 1 }}>
          {investigation.name}
        </Typography>
        <Button variant="contained" startIcon={<Edit />}>
          Edit
        </Button>
      </Stack>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Status
              </Typography>
              <Chip
                label={investigation.status}
                sx={{
                  backgroundColor: getStatusColor(investigation.status),
                  color: 'white',
                }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Priority
              </Typography>
              <Chip
                label={investigation.priority}
                color={
                  investigation.priority === 'critical'
                    ? 'error'
                    : investigation.priority === 'high'
                    ? 'warning'
                    : 'default'
                }
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Targets
              </Typography>
              <Typography variant="h4">{investigation.targetCount}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Findings
              </Typography>
              <Typography variant="h4">{investigation.findingCount}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Description
          </Typography>
          <Typography color="textSecondary" paragraph>
            {investigation.description}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="textSecondary">
                Created: {formatDate(investigation.createdAt)}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="textSecondary">
                Updated: {formatDate(investigation.updatedAt)}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="Targets" />
          <Tab label="Findings" />
          <Tab label="Activity" />
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <DataTable columns={targetColumns} rows={targets} exportFilename="targets.csv" />
      )}
      {tabValue === 1 && (
        <DataTable columns={findingColumns} rows={findings} exportFilename="findings.csv" />
      )}
      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Typography>Activity timeline will be displayed here</Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

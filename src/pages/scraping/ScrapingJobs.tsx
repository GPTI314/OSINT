import { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Stack,
  IconButton,
} from '@mui/material';
import { Add, Pause, PlayArrow, Stop } from '@mui/icons-material';
import { GridColDef } from '@mui/x-data-grid';
import { DataTable } from '../../components/common/DataTable';
import { api } from '../../services/api';
import { ScrapingJob } from '../../types';
import { formatDate, getStatusColor } from '../../utils/helpers';
import { websocket } from '../../services/websocket';

export const ScrapingJobs = () => {
  const [jobs, setJobs] = useState<ScrapingJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newJob, setNewJob] = useState({
    name: '',
    url: '',
    type: 'single',
    targetId: '',
    config: {
      maxDepth: 3,
      maxPages: 100,
      timeout: 30,
    },
  });

  useEffect(() => {
    loadJobs();
    websocket.connect();

    // Listen for job updates
    websocket.on('scraping:update', (data) => {
      setJobs((prevJobs) =>
        prevJobs.map((job) => (job.id === data.jobId ? { ...job, ...data.updates } : job))
      );
    });

    return () => {
      websocket.off('scraping:update');
    };
  }, []);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const response = await api.getScrapingJobs();
      setJobs(response.items);
    } catch (error) {
      console.error('Failed to load scraping jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.createScrapingJob(newJob);
      setDialogOpen(false);
      setNewJob({
        name: '',
        url: '',
        type: 'single',
        targetId: '',
        config: { maxDepth: 3, maxPages: 100, timeout: 30 },
      });
      loadJobs();
    } catch (error) {
      console.error('Failed to create job:', error);
    }
  };

  const handlePause = async (id: string) => {
    try {
      await api.pauseScrapingJob(id);
      loadJobs();
    } catch (error) {
      console.error('Failed to pause job:', error);
    }
  };

  const handleResume = async (id: string) => {
    try {
      await api.resumeScrapingJob(id);
      loadJobs();
    } catch (error) {
      console.error('Failed to resume job:', error);
    }
  };

  const handleCancel = async (id: string) => {
    try {
      await api.cancelScrapingJob(id);
      loadJobs();
    } catch (error) {
      console.error('Failed to cancel job:', error);
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Name',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'type',
      headerName: 'Type',
      width: 100,
      renderCell: (params) => <Chip label={params.value} size="small" />,
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          sx={{
            backgroundColor: getStatusColor(params.value),
            color: 'white',
          }}
        />
      ),
    },
    {
      field: 'progress',
      headerName: 'Progress',
      width: 150,
      renderCell: (params) => (
        <Box width="100%">
          <LinearProgress variant="determinate" value={params.value} />
          <Typography variant="caption">{params.value}%</Typography>
        </Box>
      ),
    },
    {
      field: 'itemsCollected',
      headerName: 'Items',
      width: 100,
    },
    {
      field: 'startedAt',
      headerName: 'Started',
      width: 180,
      valueFormatter: (params) => (params ? formatDate(params as string) : 'N/A'),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      sortable: false,
      renderCell: (params) => (
        <Box>
          {params.row.status === 'running' && (
            <IconButton size="small" onClick={() => handlePause(params.row.id)}>
              <Pause />
            </IconButton>
          )}
          {params.row.status === 'paused' && (
            <IconButton size="small" onClick={() => handleResume(params.row.id)}>
              <PlayArrow />
            </IconButton>
          )}
          {(params.row.status === 'running' || params.row.status === 'paused') && (
            <IconButton size="small" color="error" onClick={() => handleCancel(params.row.id)}>
              <Stop />
            </IconButton>
          )}
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Scraping Jobs</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
        >
          New Job
        </Button>
      </Box>

      <DataTable
        columns={columns}
        rows={jobs}
        loading={loading}
        exportFilename="scraping-jobs.csv"
      />

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Scraping Job</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Job Name"
              fullWidth
              value={newJob.name}
              onChange={(e) => setNewJob({ ...newJob, name: e.target.value })}
            />
            <TextField
              label="URL"
              fullWidth
              value={newJob.url}
              onChange={(e) => setNewJob({ ...newJob, url: e.target.value })}
              placeholder="https://example.com"
            />
            <TextField
              select
              label="Type"
              fullWidth
              value={newJob.type}
              onChange={(e) => setNewJob({ ...newJob, type: e.target.value })}
            >
              <MenuItem value="single">Single Page</MenuItem>
              <MenuItem value="list">List Scraping</MenuItem>
              <MenuItem value="sitemap">Sitemap</MenuItem>
            </TextField>
            <TextField
              label="Max Pages"
              type="number"
              fullWidth
              value={newJob.config.maxPages}
              onChange={(e) =>
                setNewJob({
                  ...newJob,
                  config: { ...newJob.config, maxPages: parseInt(e.target.value) },
                })
              }
            />
            <TextField
              label="Max Depth"
              type="number"
              fullWidth
              value={newJob.config.maxDepth}
              onChange={(e) =>
                setNewJob({
                  ...newJob,
                  config: { ...newJob.config, maxDepth: parseInt(e.target.value) },
                })
              }
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

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
  FormControlLabel,
  Switch,
} from '@mui/material';
import { Add, Pause, PlayArrow, Stop } from '@mui/icons-material';
import { GridColDef } from '@mui/x-data-grid';
import { DataTable } from '../../components/common/DataTable';
import { api } from '../../services/api';
import { CrawlingSession } from '../../types';
import { formatDate, getStatusColor } from '../../utils/helpers';
import { websocket } from '../../services/websocket';

export const CrawlingSessions = () => {
  const [sessions, setSessions] = useState<CrawlingSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newSession, setNewSession] = useState({
    name: '',
    seedUrl: '',
    targetId: '',
    config: {
      maxDepth: 3,
      maxPages: 1000,
      followExternal: false,
      respectRobots: true,
    },
  });

  useEffect(() => {
    loadSessions();
    websocket.connect();

    websocket.on('crawling:update', (data) => {
      setSessions((prev) =>
        prev.map((session) =>
          session.id === data.sessionId ? { ...session, ...data.updates } : session
        )
      );
    });

    return () => {
      websocket.off('crawling:update');
    };
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const response = await api.getCrawlingSessions();
      setSessions(response.items);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.createCrawlingSession(newSession);
      setDialogOpen(false);
      setNewSession({
        name: '',
        seedUrl: '',
        targetId: '',
        config: { maxDepth: 3, maxPages: 1000, followExternal: false, respectRobots: true },
      });
      loadSessions();
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const columns: GridColDef[] = [
    { field: 'name', headerName: 'Name', flex: 1, minWidth: 200 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          sx={{ backgroundColor: getStatusColor(params.value), color: 'white' }}
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
    { field: 'pagesDiscovered', headerName: 'Discovered', width: 120 },
    { field: 'pagesCrawled', headerName: 'Crawled', width: 100 },
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
            <IconButton
              size="small"
              onClick={() => api.pauseCrawlingSession(params.row.id).then(loadSessions)}
            >
              <Pause />
            </IconButton>
          )}
          {params.row.status === 'paused' && (
            <IconButton
              size="small"
              onClick={() => api.resumeCrawlingSession(params.row.id).then(loadSessions)}
            >
              <PlayArrow />
            </IconButton>
          )}
          {(params.row.status === 'running' || params.row.status === 'paused') && (
            <IconButton
              size="small"
              color="error"
              onClick={() => api.cancelCrawlingSession(params.row.id).then(loadSessions)}
            >
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
        <Typography variant="h4">Crawling Sessions</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>
          New Session
        </Button>
      </Box>

      <DataTable columns={columns} rows={sessions} loading={loading} exportFilename="crawling-sessions.csv" />

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Crawling Session</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Session Name"
              fullWidth
              value={newSession.name}
              onChange={(e) => setNewSession({ ...newSession, name: e.target.value })}
            />
            <TextField
              label="Seed URL"
              fullWidth
              value={newSession.seedUrl}
              onChange={(e) => setNewSession({ ...newSession, seedUrl: e.target.value })}
              placeholder="https://example.com"
            />
            <TextField
              label="Max Pages"
              type="number"
              fullWidth
              value={newSession.config.maxPages}
              onChange={(e) =>
                setNewSession({
                  ...newSession,
                  config: { ...newSession.config, maxPages: parseInt(e.target.value) },
                })
              }
            />
            <TextField
              label="Max Depth"
              type="number"
              fullWidth
              value={newSession.config.maxDepth}
              onChange={(e) =>
                setNewSession({
                  ...newSession,
                  config: { ...newSession.config, maxDepth: parseInt(e.target.value) },
                })
              }
            />
            <FormControlLabel
              control={
                <Switch
                  checked={newSession.config.followExternal}
                  onChange={(e) =>
                    setNewSession({
                      ...newSession,
                      config: { ...newSession.config, followExternal: e.target.checked },
                    })
                  }
                />
              }
              label="Follow External Links"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={newSession.config.respectRobots}
                  onChange={(e) =>
                    setNewSession({
                      ...newSession,
                      config: { ...newSession.config, respectRobots: e.target.checked },
                    })
                  }
                />
              }
              label="Respect robots.txt"
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

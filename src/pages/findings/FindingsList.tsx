import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Stack,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { GridColDef } from '@mui/x-data-grid';
import { DataTable } from '../../components/common/DataTable';
import { api } from '../../services/api';
import { Finding } from '../../types';
import { formatDate, getSeverityColor } from '../../utils/helpers';

const severityLevels = ['info', 'low', 'medium', 'high', 'critical'];
const statusOptions = ['new', 'investigating', 'confirmed', 'false_positive', 'resolved'];

export const FindingsList = () => {
  const navigate = useNavigate();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newFinding, setNewFinding] = useState({
    title: '',
    description: '',
    severity: 'medium',
    status: 'new',
    category: '',
    investigationId: '',
  });

  useEffect(() => {
    loadFindings();
  }, []);

  const loadFindings = async () => {
    setLoading(true);
    try {
      const response = await api.getFindings();
      setFindings(response.items);
    } catch (error) {
      console.error('Failed to load findings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.createFinding(newFinding);
      setDialogOpen(false);
      setNewFinding({
        title: '',
        description: '',
        severity: 'medium',
        status: 'new',
        category: '',
        investigationId: '',
      });
      loadFindings();
    } catch (error) {
      console.error('Failed to create finding:', error);
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'title',
      headerName: 'Title',
      flex: 1,
      minWidth: 250,
    },
    {
      field: 'severity',
      headerName: 'Severity',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          sx={{
            backgroundColor: getSeverityColor(params.value),
            color: 'white',
          }}
        />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (params) => <Chip label={params.value.replace('_', ' ')} size="small" />,
    },
    {
      field: 'category',
      headerName: 'Category',
      width: 150,
    },
    {
      field: 'targetIds',
      headerName: 'Targets',
      width: 100,
      valueFormatter: (params) => (params as string[])?.length || 0,
    },
    {
      field: 'evidence',
      headerName: 'Evidence',
      width: 100,
      valueFormatter: (params) => (params as any[])?.length || 0,
    },
    {
      field: 'createdAt',
      headerName: 'Created',
      width: 180,
      valueFormatter: (params) => formatDate(params as string),
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Findings</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>
          New Finding
        </Button>
      </Box>

      <DataTable columns={columns} rows={findings} loading={loading} exportFilename="findings.csv" />

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Finding</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={newFinding.title}
              onChange={(e) => setNewFinding({ ...newFinding, title: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={4}
              value={newFinding.description}
              onChange={(e) => setNewFinding({ ...newFinding, description: e.target.value })}
            />
            <TextField
              select
              label="Severity"
              fullWidth
              value={newFinding.severity}
              onChange={(e) => setNewFinding({ ...newFinding, severity: e.target.value })}
            >
              {severityLevels.map((level) => (
                <MenuItem key={level} value={level}>
                  {level}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Status"
              fullWidth
              value={newFinding.status}
              onChange={(e) => setNewFinding({ ...newFinding, status: e.target.value })}
            >
              {statusOptions.map((status) => (
                <MenuItem key={status} value={status}>
                  {status.replace('_', ' ')}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Category"
              fullWidth
              value={newFinding.category}
              onChange={(e) => setNewFinding({ ...newFinding, category: e.target.value })}
              placeholder="e.g., Data Breach, Exposed Credentials, Suspicious Activity"
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

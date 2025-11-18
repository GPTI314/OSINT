import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Stack,
} from '@mui/material';
import { Add, Edit, Delete, Visibility } from '@mui/icons-material';
import { GridColDef } from '@mui/x-data-grid';
import { DataTable } from '../../components/common/DataTable';
import { api } from '../../services/api';
import { Investigation } from '../../types';
import { formatDate, getStatusColor } from '../../utils/helpers';

export const InvestigationsList = () => {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newInvestigation, setNewInvestigation] = useState({
    name: '',
    description: '',
    priority: 'medium',
    status: 'active',
  });

  useEffect(() => {
    loadInvestigations();
  }, []);

  const loadInvestigations = async () => {
    setLoading(true);
    try {
      const response = await api.getInvestigations();
      setInvestigations(response.items);
    } catch (error) {
      console.error('Failed to load investigations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.createInvestigation(newInvestigation);
      setCreateDialogOpen(false);
      setNewInvestigation({ name: '', description: '', priority: 'medium', status: 'active' });
      loadInvestigations();
    } catch (error) {
      console.error('Failed to create investigation:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this investigation?')) {
      try {
        await api.deleteInvestigation(id);
        loadInvestigations();
      } catch (error) {
        console.error('Failed to delete investigation:', error);
      }
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
      field: 'priority',
      headerName: 'Priority',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color={
            params.value === 'critical'
              ? 'error'
              : params.value === 'high'
              ? 'warning'
              : 'default'
          }
        />
      ),
    },
    {
      field: 'targetCount',
      headerName: 'Targets',
      width: 100,
    },
    {
      field: 'findingCount',
      headerName: 'Findings',
      width: 100,
    },
    {
      field: 'createdAt',
      headerName: 'Created',
      width: 180,
      valueFormatter: (params) => formatDate(params as string),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => navigate(`/investigations/${params.row.id}`)}
          >
            <Visibility />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => navigate(`/investigations/${params.row.id}/edit`)}
          >
            <Edit />
          </IconButton>
          <IconButton
            size="small"
            color="error"
            onClick={() => handleDelete(params.row.id)}
          >
            <Delete />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Investigations</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          New Investigation
        </Button>
      </Box>

      <DataTable
        columns={columns}
        rows={investigations}
        loading={loading}
        exportFilename="investigations.csv"
      />

      {/* Create Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Investigation</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              fullWidth
              value={newInvestigation.name}
              onChange={(e) => setNewInvestigation({ ...newInvestigation, name: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={newInvestigation.description}
              onChange={(e) => setNewInvestigation({ ...newInvestigation, description: e.target.value })}
            />
            <TextField
              select
              label="Priority"
              fullWidth
              value={newInvestigation.priority}
              onChange={(e) => setNewInvestigation({ ...newInvestigation, priority: e.target.value })}
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </TextField>
            <TextField
              select
              label="Status"
              fullWidth
              value={newInvestigation.status}
              onChange={(e) => setNewInvestigation({ ...newInvestigation, status: e.target.value })}
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="archived">Archived</MenuItem>
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

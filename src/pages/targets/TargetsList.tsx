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
import { Target } from '../../types';
import { formatDate } from '../../utils/helpers';

const targetTypes = ['person', 'organization', 'domain', 'ip', 'email', 'phone', 'social', 'other'];

export const TargetsList = () => {
  const navigate = useNavigate();
  const [targets, setTargets] = useState<Target[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newTarget, setNewTarget] = useState({
    type: 'domain',
    value: '',
    label: '',
    investigationId: '',
  });

  useEffect(() => {
    loadTargets();
  }, []);

  const loadTargets = async () => {
    setLoading(true);
    try {
      const response = await api.getTargets();
      setTargets(response.items);
    } catch (error) {
      console.error('Failed to load targets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.createTarget(newTarget);
      setDialogOpen(false);
      setNewTarget({ type: 'domain', value: '', label: '', investigationId: '' });
      loadTargets();
    } catch (error) {
      console.error('Failed to create target:', error);
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'type',
      headerName: 'Type',
      width: 130,
      renderCell: (params) => <Chip label={params.value} size="small" />,
    },
    {
      field: 'value',
      headerName: 'Value',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'label',
      headerName: 'Label',
      width: 150,
    },
    {
      field: 'riskScore',
      headerName: 'Risk Score',
      width: 130,
      renderCell: (params) => (
        <Chip
          label={params.value || 'N/A'}
          size="small"
          color={
            !params.value
              ? 'default'
              : params.value > 70
              ? 'error'
              : params.value > 40
              ? 'warning'
              : 'success'
          }
        />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color={params.value === 'active' ? 'success' : 'default'}
        />
      ),
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
        <Typography variant="h4">Targets</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
        >
          Add Target
        </Button>
      </Box>

      <DataTable
        columns={columns}
        rows={targets}
        loading={loading}
        exportFilename="targets.csv"
      />

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Target</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              select
              label="Type"
              fullWidth
              value={newTarget.type}
              onChange={(e) => setNewTarget({ ...newTarget, type: e.target.value })}
            >
              {targetTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Value"
              fullWidth
              value={newTarget.value}
              onChange={(e) => setNewTarget({ ...newTarget, value: e.target.value })}
              placeholder="e.g., example.com, 192.168.1.1, user@example.com"
            />
            <TextField
              label="Label (Optional)"
              fullWidth
              value={newTarget.label}
              onChange={(e) => setNewTarget({ ...newTarget, label: e.target.value })}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

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
  IconButton,
  Menu,
  MenuItem as MenuOption,
} from '@mui/material';
import { Add, Download, MoreVert } from '@mui/icons-material';
import { GridColDef } from '@mui/x-data-grid';
import { DataTable } from '../../components/common/DataTable';
import { api } from '../../services/api';
import { Report } from '../../types';
import { formatDate } from '../../utils/helpers';

const reportTypes = ['summary', 'detailed', 'executive', 'technical'];
const reportStatuses = ['draft', 'review', 'final'];

export const ReportsList = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [exportMenuAnchor, setExportMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedReportId, setSelectedReportId] = useState<string>('');
  const [newReport, setNewReport] = useState({
    title: '',
    type: 'summary',
    investigationId: '',
  });

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const response = await api.getReports();
      setReports(response.items);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const report = await api.createReport(newReport);
      setDialogOpen(false);
      setNewReport({ title: '', type: 'summary', investigationId: '' });
      navigate(`/reports/${report.id}/edit`);
    } catch (error) {
      console.error('Failed to create report:', error);
    }
  };

  const handleExport = async (format: 'pdf' | 'docx' | 'html') => {
    try {
      const blob = await api.exportReport(selectedReportId, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export report:', error);
    }
    setExportMenuAnchor(null);
  };

  const columns: GridColDef[] = [
    {
      field: 'title',
      headerName: 'Title',
      flex: 1,
      minWidth: 250,
    },
    {
      field: 'type',
      headerName: 'Type',
      width: 120,
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
          color={
            params.value === 'final'
              ? 'success'
              : params.value === 'review'
              ? 'warning'
              : 'default'
          }
        />
      ),
    },
    {
      field: 'sections',
      headerName: 'Sections',
      width: 100,
      valueFormatter: (params) => (params as any[])?.length || 0,
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
      width: 100,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={(e) => {
              setSelectedReportId(params.row.id);
              setExportMenuAnchor(e.currentTarget);
            }}
          >
            <Download />
          </IconButton>
          <IconButton size="small" onClick={() => navigate(`/reports/${params.row.id}`)}>
            <MoreVert />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Reports</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>
          New Report
        </Button>
      </Box>

      <DataTable columns={columns} rows={reports} loading={loading} exportFilename="reports.csv" />

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Report</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={newReport.title}
              onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
            />
            <TextField
              select
              label="Type"
              fullWidth
              value={newReport.type}
              onChange={(e) => setNewReport({ ...newReport, type: e.target.value })}
            >
              {reportTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Export Menu */}
      <Menu
        anchorEl={exportMenuAnchor}
        open={Boolean(exportMenuAnchor)}
        onClose={() => setExportMenuAnchor(null)}
      >
        <MenuOption onClick={() => handleExport('pdf')}>Export as PDF</MenuOption>
        <MenuOption onClick={() => handleExport('docx')}>Export as DOCX</MenuOption>
        <MenuOption onClick={() => handleExport('html')}>Export as HTML</MenuOption>
      </Menu>
    </Box>
  );
};

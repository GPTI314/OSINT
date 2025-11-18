import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  TextField,
  Stack,
  Paper,
} from '@mui/material';
import { Search, CloudDownload } from '@mui/icons-material';
import { DataTable } from '../../components/common/DataTable';
import { api } from '../../services/api';
import { IntelligenceData } from '../../types';
import { GridColDef } from '@mui/x-data-grid';
import { formatDate } from '../../utils/helpers';

const intelligenceTypes = ['domain', 'ip', 'email', 'phone', 'social', 'image'];

export const Intelligence = () => {
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [data, setData] = useState<IntelligenceData[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState<string>('domain');

  useEffect(() => {
    setSelectedType(intelligenceTypes[tabValue]);
    loadData(intelligenceTypes[tabValue]);
  }, [tabValue]);

  const loadData = async (type: string) => {
    setLoading(true);
    try {
      const response = await api.getIntelligenceData({ type: [type] });
      setData(response.items);
    } catch (error) {
      console.error('Failed to load intelligence data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    if (!searchQuery) return;
    setLoading(true);
    try {
      // Create a temporary target and enrich it
      const target = await api.createTarget({ type: selectedType, value: searchQuery });
      await api.enrichTarget(target.id, selectedType);
      loadData(selectedType);
      setSearchQuery('');
    } catch (error) {
      console.error('Failed to enrich target:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns: GridColDef[] = [
    { field: 'value', headerName: 'Value', flex: 1, minWidth: 200 },
    { field: 'source', headerName: 'Source', width: 150 },
    {
      field: 'confidence',
      headerName: 'Confidence',
      width: 130,
      renderCell: (params) => (
        <Chip
          label={`${Math.round(params.value * 100)}%`}
          size="small"
          color={params.value > 0.7 ? 'success' : params.value > 0.4 ? 'warning' : 'error'}
        />
      ),
    },
    {
      field: 'relatedEntities',
      headerName: 'Relations',
      width: 100,
      valueFormatter: (params) => (params as string[])?.length || 0,
    },
    {
      field: 'createdAt',
      headerName: 'Collected',
      width: 180,
      valueFormatter: (params) => formatDate(params as string),
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Intelligence Gathering
      </Typography>

      <Paper sx={{ mb: 3, p: 2 }}>
        <Stack direction="row" spacing={2}>
          <TextField
            label="Search & Enrich"
            fullWidth
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={`Enter ${selectedType} to investigate...`}
            onKeyPress={(e) => e.key === 'Enter' && handleEnrich()}
          />
          <Button
            variant="contained"
            startIcon={<Search />}
            onClick={handleEnrich}
            disabled={!searchQuery}
          >
            Enrich
          </Button>
        </Stack>
      </Paper>

      <Card sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} variant="scrollable">
          {intelligenceTypes.map((type) => (
            <Tab key={type} label={type.charAt(0).toUpperCase() + type.slice(1)} />
          ))}
        </Tabs>
      </Card>

      <DataTable
        columns={columns}
        rows={data}
        loading={loading}
        exportFilename={`intelligence-${selectedType}.csv`}
      />

      {data.length > 0 && (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Records
                </Typography>
                <Typography variant="h3">{data.length}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Avg Confidence
                </Typography>
                <Typography variant="h3">
                  {Math.round(
                    (data.reduce((sum, item) => sum + item.confidence, 0) / data.length) * 100
                  )}
                  %
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Sources
                </Typography>
                <Typography variant="h3">
                  {new Set(data.map((item) => item.source)).size}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

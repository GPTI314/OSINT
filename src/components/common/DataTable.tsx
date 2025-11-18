import { useState } from 'react';
import {
  DataGrid,
  GridColDef,
  GridRowsProp,
  GridPaginationModel,
  GridSortModel,
  GridFilterModel,
} from '@mui/x-data-grid';
import { Box, Paper, TextField, Button, Stack } from '@mui/material';
import { Search, FileDownload } from '@mui/icons-material';
import { exportToCSV } from '../../utils/export';

interface DataTableProps {
  columns: GridColDef[];
  rows: GridRowsProp;
  loading?: boolean;
  totalRows?: number;
  onPaginationChange?: (model: GridPaginationModel) => void;
  onSortChange?: (model: GridSortModel) => void;
  onFilterChange?: (model: GridFilterModel) => void;
  onSearch?: (query: string) => void;
  exportable?: boolean;
  exportFilename?: string;
}

export const DataTable = ({
  columns,
  rows,
  loading = false,
  totalRows,
  onPaginationChange,
  onSortChange,
  onFilterChange,
  onSearch,
  exportable = true,
  exportFilename = 'export.csv',
}: DataTableProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 25,
  });

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value;
    setSearchQuery(query);
    if (onSearch) {
      onSearch(query);
    }
  };

  const handleExport = () => {
    exportToCSV(rows as any[], exportFilename);
  };

  const handlePaginationChange = (model: GridPaginationModel) => {
    setPaginationModel(model);
    if (onPaginationChange) {
      onPaginationChange(model);
    }
  };

  return (
    <Paper sx={{ width: '100%', p: 2 }}>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <TextField
          size="small"
          placeholder="Search..."
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
          sx={{ flexGrow: 1 }}
        />
        {exportable && (
          <Button
            variant="outlined"
            startIcon={<FileDownload />}
            onClick={handleExport}
          >
            Export
          </Button>
        )}
      </Stack>

      <DataGrid
        rows={rows}
        columns={columns}
        loading={loading}
        paginationModel={paginationModel}
        onPaginationModelChange={handlePaginationChange}
        onSortModelChange={onSortChange}
        onFilterModelChange={onFilterChange}
        rowCount={totalRows || rows.length}
        pageSizeOptions={[10, 25, 50, 100]}
        checkboxSelection
        disableRowSelectionOnClick
        sx={{
          border: 'none',
          '& .MuiDataGrid-cell:focus': {
            outline: 'none',
          },
          '& .MuiDataGrid-row:hover': {
            cursor: 'pointer',
          },
        }}
      />
    </Paper>
  );
};

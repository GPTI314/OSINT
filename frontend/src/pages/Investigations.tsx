import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
} from '@mui/material';
import { Add } from '@mui/icons-material';

const Investigations: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">
            Investigations
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            color="primary"
          >
            New Investigation
          </Button>
        </Box>

        <Paper sx={{ p: 3 }}>
          <Typography color="textSecondary">
            Investigation list will appear here
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default Investigations;

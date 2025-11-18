import React from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
} from '@mui/material';
import {
  Security,
  Search,
  Language,
  Assessment,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  const stats = [
    { title: 'Active Investigations', value: '12', icon: <Search /> },
    { title: 'Targets Analyzed', value: '248', icon: <Security /> },
    { title: 'Domains Scanned', value: '1,543', icon: <Language /> },
    { title: 'Reports Generated', value: '34', icon: <Assessment /> },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          OSINT Intelligence Platform
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" gutterBottom>
          Comprehensive Open Source Intelligence Gathering
        </Typography>

        <Grid container spacing={3} sx={{ mt: 3 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ mr: 2, color: 'primary.main' }}>{stat.icon}</Box>
                    <Typography variant="h4">{stat.value}</Typography>
                  </Box>
                  <Typography color="textSecondary">{stat.title}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Grid container spacing={3} sx={{ mt: 3 }}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Typography color="textSecondary">
                Investigation activity timeline will appear here
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Typography color="textSecondary">
                Quick action buttons will appear here
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;

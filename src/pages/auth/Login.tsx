import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Stack,
  Alert,
} from '@mui/material';
import { Lock } from '@mui/icons-material';
import { useAuthStore } from '../../store';

export const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Mock login - replace with actual API call
    if (email && password) {
      const mockUser = {
        id: '1',
        email,
        name: 'Demo User',
        role: 'analyst' as const,
        createdAt: new Date().toISOString(),
      };

      login(mockUser);
      localStorage.setItem('auth_token', 'mock-token');
      navigate('/dashboard');
    } else {
      setError('Please enter email and password');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card sx={{ maxWidth: 400, width: '100%', m: 2 }}>
        <CardContent sx={{ p: 4 }}>
          <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                bgcolor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2,
              }}
            >
              <Lock sx={{ color: 'white', fontSize: 30 }} />
            </Box>
            <Typography variant="h5" fontWeight="bold">
              OSINT Platform
            </Typography>
            <Typography color="textSecondary" variant="body2">
              Sign in to continue
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleLogin}>
            <Stack spacing={2}>
              <TextField
                label="Email"
                type="email"
                fullWidth
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <TextField
                label="Password"
                type="password"
                fullWidth
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <Button type="submit" variant="contained" size="large" fullWidth>
                Sign In
              </Button>
            </Stack>
          </form>

          <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 3 }}>
            Demo credentials: any email and password
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

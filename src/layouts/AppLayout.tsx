import { useState } from 'react';
import {
  Box,
  CssBaseline,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Badge,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Assignment,
  Person,
  CloudDownload,
  Link as LinkIcon,
  Psychology,
  Analytics,
  BugReport,
  Description,
  Settings,
  Notifications,
  Brightness4,
  Brightness7,
  Logout,
} from '@mui/icons-material';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useSidebarStore, useThemeStore, useAuthStore } from '../store';

const drawerWidth = 260;

const navigationItems = [
  { title: 'Dashboard', path: '/dashboard', icon: <Dashboard /> },
  { title: 'Investigations', path: '/investigations', icon: <Assignment /> },
  { title: 'Targets', path: '/targets', icon: <Person /> },
  { title: 'Scraping', path: '/scraping', icon: <CloudDownload /> },
  { title: 'Crawling', path: '/crawling', icon: <LinkIcon /> },
  { title: 'Intelligence', path: '/intelligence', icon: <Psychology /> },
  { title: 'Analysis', path: '/analysis', icon: <Analytics /> },
  { title: 'Findings', path: '/findings', icon: <BugReport /> },
  { title: 'Reports', path: '/reports', icon: <Description /> },
  { title: 'Settings', path: '/settings', icon: <Settings /> },
];

export const AppLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isOpen, toggleSidebar } = useSidebarStore();
  const { mode, toggleTheme } = useThemeStore();
  const { user, logout } = useAuthStore();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />

      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: mode === 'dark' ? '#1e1e1e' : '#1976d2',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle sidebar"
            edge="start"
            onClick={toggleSidebar}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            OSINT Intelligence Platform
          </Typography>

          <IconButton color="inherit" sx={{ mr: 1 }}>
            <Badge badgeContent={3} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          <IconButton color="inherit" onClick={toggleTheme} sx={{ mr: 2 }}>
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>

          <IconButton onClick={handleMenuOpen} sx={{ p: 0 }}>
            <Avatar alt={user?.name || 'User'} src={user?.avatar}>
              {user?.name?.charAt(0) || 'U'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <MenuItem disabled>
              <Typography variant="body2">{user?.email}</Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => { handleMenuClose(); navigate('/settings'); }}>
              <ListItemIcon><Settings fontSize="small" /></ListItemIcon>
              Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon><Logout fontSize="small" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="persistent"
        open={isOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {navigationItems.map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  selected={location.pathname.startsWith(item.path)}
                  onClick={() => navigate(item.path)}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.title} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: '100%',
          marginLeft: isOpen ? 0 : `-${drawerWidth}px`,
          transition: (theme) =>
            theme.transitions.create('margin', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

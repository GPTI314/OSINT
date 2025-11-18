import { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Tabs,
  Tab,
  TextField,
  Button,
  Stack,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
} from '@mui/material';
import { Save } from '@mui/icons-material';

export const Settings = () => {
  const [tabValue, setTabValue] = useState(0);
  const [saved, setSaved] = useState(false);

  const [userSettings, setUserSettings] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    notifications: true,
    emailAlerts: false,
  });

  const [apiSettings, setApiSettings] = useState({
    apiKey: '••••••••••••••••',
    webhookUrl: '',
    rateLimitPerHour: 1000,
  });

  const [systemSettings, setSystemSettings] = useState({
    maxCrawlDepth: 5,
    maxPagesPerCrawl: 10000,
    dataRetentionDays: 90,
    enableAutoEnrichment: true,
    enableRealTimeAlerts: true,
  });

  const handleSave = () => {
    // Save settings logic here
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Card>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="User Settings" />
          <Tab label="API Configuration" />
          <Tab label="Integration" />
          <Tab label="System Settings" />
        </Tabs>

        {/* User Settings */}
        {tabValue === 0 && (
          <CardContent>
            <Stack spacing={3}>
              <Typography variant="h6">Profile Information</Typography>
              <TextField
                label="Name"
                fullWidth
                value={userSettings.name}
                onChange={(e) => setUserSettings({ ...userSettings, name: e.target.value })}
              />
              <TextField
                label="Email"
                type="email"
                fullWidth
                value={userSettings.email}
                onChange={(e) => setUserSettings({ ...userSettings, email: e.target.value })}
              />

              <Divider />

              <Typography variant="h6">Preferences</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={userSettings.notifications}
                    onChange={(e) =>
                      setUserSettings({ ...userSettings, notifications: e.target.checked })
                    }
                  />
                }
                label="Enable In-App Notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={userSettings.emailAlerts}
                    onChange={(e) =>
                      setUserSettings({ ...userSettings, emailAlerts: e.target.checked })
                    }
                  />
                }
                label="Enable Email Alerts"
              />

              <Button variant="contained" startIcon={<Save />} onClick={handleSave}>
                Save Changes
              </Button>
            </Stack>
          </CardContent>
        )}

        {/* API Configuration */}
        {tabValue === 1 && (
          <CardContent>
            <Stack spacing={3}>
              <Typography variant="h6">API Configuration</Typography>
              <TextField
                label="API Key"
                fullWidth
                type="password"
                value={apiSettings.apiKey}
                onChange={(e) => setApiSettings({ ...apiSettings, apiKey: e.target.value })}
                helperText="Your API key for accessing external services"
              />
              <TextField
                label="Webhook URL"
                fullWidth
                value={apiSettings.webhookUrl}
                onChange={(e) => setApiSettings({ ...apiSettings, webhookUrl: e.target.value })}
                placeholder="https://your-webhook-url.com/endpoint"
              />
              <TextField
                label="Rate Limit (requests/hour)"
                type="number"
                fullWidth
                value={apiSettings.rateLimitPerHour}
                onChange={(e) =>
                  setApiSettings({ ...apiSettings, rateLimitPerHour: parseInt(e.target.value) })
                }
              />

              <Button variant="contained" startIcon={<Save />} onClick={handleSave}>
                Save Changes
              </Button>
            </Stack>
          </CardContent>
        )}

        {/* Integration */}
        {tabValue === 2 && (
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Third-Party Integrations
            </Typography>
            <Typography color="textSecondary" paragraph>
              Configure integrations with external services like Shodan, VirusTotal, WHOIS
              databases, and more.
            </Typography>
            <Alert severity="info">Integration configuration will be available soon.</Alert>
          </CardContent>
        )}

        {/* System Settings */}
        {tabValue === 3 && (
          <CardContent>
            <Stack spacing={3}>
              <Typography variant="h6">Crawling & Scraping</Typography>
              <TextField
                label="Maximum Crawl Depth"
                type="number"
                fullWidth
                value={systemSettings.maxCrawlDepth}
                onChange={(e) =>
                  setSystemSettings({
                    ...systemSettings,
                    maxCrawlDepth: parseInt(e.target.value),
                  })
                }
              />
              <TextField
                label="Maximum Pages Per Crawl"
                type="number"
                fullWidth
                value={systemSettings.maxPagesPerCrawl}
                onChange={(e) =>
                  setSystemSettings({
                    ...systemSettings,
                    maxPagesPerCrawl: parseInt(e.target.value),
                  })
                }
              />

              <Divider />

              <Typography variant="h6">Data Management</Typography>
              <TextField
                label="Data Retention (days)"
                type="number"
                fullWidth
                value={systemSettings.dataRetentionDays}
                onChange={(e) =>
                  setSystemSettings({
                    ...systemSettings,
                    dataRetentionDays: parseInt(e.target.value),
                  })
                }
              />

              <Divider />

              <Typography variant="h6">Features</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={systemSettings.enableAutoEnrichment}
                    onChange={(e) =>
                      setSystemSettings({
                        ...systemSettings,
                        enableAutoEnrichment: e.target.checked,
                      })
                    }
                  />
                }
                label="Enable Automatic Target Enrichment"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={systemSettings.enableRealTimeAlerts}
                    onChange={(e) =>
                      setSystemSettings({
                        ...systemSettings,
                        enableRealTimeAlerts: e.target.checked,
                      })
                    }
                  />
                }
                label="Enable Real-Time Alerts"
              />

              <Button variant="contained" startIcon={<Save />} onClick={handleSave}>
                Save Changes
              </Button>
            </Stack>
          </CardContent>
        )}
      </Card>
    </Box>
  );
};

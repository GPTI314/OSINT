# OSINT Intelligence Platform - Frontend

A comprehensive React-based frontend application for Open-Source Intelligence (OSINT) operations, built with modern web technologies and best practices.

## Features

### Core Modules

1. **Dashboard**
   - Real-time statistics and metrics
   - Visual data representation with charts
   - Recent activity timeline
   - Quick access to key features

2. **Investigations**
   - Create and manage investigations
   - Track investigation status and priority
   - View targets and findings per investigation
   - Activity timeline

3. **Targets**
   - Multi-type target support (person, organization, domain, IP, email, phone, social)
   - Risk score assessment
   - Bulk target management
   - Advanced filtering and search

4. **Scraping**
   - Web scraping job management
   - Real-time progress tracking
   - Job control (pause, resume, cancel)
   - Multiple scraping modes (single, list, sitemap)

5. **Crawling**
   - Web crawling session management
   - Configurable depth and page limits
   - External link following options
   - Robots.txt compliance

6. **Intelligence**
   - Multi-source data enrichment
   - Domain, IP, email, phone, social media, and image intelligence
   - Confidence scoring
   - Related entity mapping

7. **Analysis**
   - Network graph visualization (React Flow)
   - Timeline analysis
   - Threat assessment
   - Correlation mapping

8. **Findings**
   - Security finding management
   - Severity-based classification
   - Evidence attachment
   - Status tracking

9. **Reports**
   - Multiple report types (summary, detailed, executive, technical)
   - Export to PDF, DOCX, HTML
   - Custom report builder
   - Section-based organization

10. **Settings**
    - User preferences
    - API configuration
    - Third-party integrations
    - System settings

### Key Features

#### Modern UI
- Material-UI (MUI) component library
- Responsive design for all screen sizes
- Clean and intuitive interface
- Consistent design language

#### Real-time Updates
- WebSocket integration for live data
- Progress tracking for long-running jobs
- Instant notifications
- Live activity feeds

#### Data Visualization
- Interactive charts (Recharts)
- Network graphs (React Flow)
- Timeline views
- Statistical dashboards

#### Advanced Tables
- Sorting and filtering
- Pagination
- Column customization
- Export capabilities
- Search functionality

#### Dark Mode
- System-wide theme switching
- Persistent theme preference
- Optimized for both light and dark environments

#### Export Functionality
- CSV export for tabular data
- PDF generation for reports
- JSON data export
- Multiple format support

#### Accessibility
- WCAG compliance considerations
- Keyboard navigation
- Screen reader support
- High contrast mode compatible

#### Responsive Design
- Mobile-first approach
- Tablet optimization
- Desktop layouts
- Adaptive components

## Tech Stack

### Core
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server

### UI Framework
- **Material-UI (MUI)** - Component library
- **Emotion** - CSS-in-JS styling

### State Management
- **Zustand** - Lightweight state management
- **React Query** - Server state management

### Routing
- **React Router v6** - Client-side routing

### Data Visualization
- **Recharts** - Chart library
- **React Flow** - Network graph visualization

### Utilities
- **Axios** - HTTP client
- **date-fns** - Date manipulation
- **Socket.io Client** - WebSocket communication
- **jsPDF** - PDF generation
- **html2canvas** - Screenshot generation

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── common/         # Common UI components
│   ├── dashboard/      # Dashboard-specific components
│   ├── investigations/ # Investigation components
│   ├── targets/        # Target components
│   ├── scraping/       # Scraping components
│   ├── crawling/       # Crawling components
│   ├── intelligence/   # Intelligence components
│   ├── analysis/       # Analysis components
│   ├── findings/       # Finding components
│   ├── reports/        # Report components
│   └── settings/       # Settings components
├── layouts/            # Layout components
│   └── AppLayout.tsx   # Main application layout
├── pages/              # Page components
│   ├── auth/          # Authentication pages
│   ├── dashboard/     # Dashboard pages
│   ├── investigations/# Investigation pages
│   ├── targets/       # Target pages
│   ├── scraping/      # Scraping pages
│   ├── crawling/      # Crawling pages
│   ├── intelligence/  # Intelligence pages
│   ├── analysis/      # Analysis pages
│   ├── findings/      # Finding pages
│   ├── reports/       # Report pages
│   └── settings/      # Settings pages
├── services/           # API and external services
│   ├── api.ts         # API client
│   └── websocket.ts   # WebSocket service
├── store/              # State management
│   └── index.ts       # Zustand stores
├── types/              # TypeScript type definitions
│   └── index.ts       # Type definitions
├── utils/              # Utility functions
│   ├── export.ts      # Export utilities
│   └── helpers.ts     # Helper functions
├── constants/          # Constants and configuration
├── hooks/              # Custom React hooks
├── theme.ts            # MUI theme configuration
├── App.tsx             # Main application component
└── main.tsx            # Application entry point
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Backend API server (configure in `.env`)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd OSINT
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm run dev
```

5. Open your browser to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:3000/api
VITE_WS_URL=http://localhost:3000
VITE_APP_NAME=OSINT Intelligence Platform
VITE_ENABLE_REAL_TIME_UPDATES=true
```

### Theme Customization

Edit `src/theme.ts` to customize colors, typography, and component styles:

```typescript
export const lightTheme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    // ... more customization
  },
});
```

## Features in Detail

### Authentication
- JWT token-based authentication
- Persistent login sessions
- Protected routes
- Automatic token refresh

### Real-time Updates
- WebSocket connection management
- Auto-reconnection
- Event subscriptions
- Live data synchronization

### Data Tables
- Advanced DataGrid from MUI X
- Server-side pagination
- Multi-column sorting
- Complex filtering
- Row selection
- Export to CSV

### Network Visualization
- Interactive node-edge graphs
- Drag-and-drop nodes
- Zoom and pan controls
- Mini-map navigation
- Custom node styling

### Export & Reporting
- PDF generation from HTML
- CSV export with custom formatting
- JSON data dumps
- Report templates

## API Integration

The frontend integrates with the backend API through the `api.ts` service:

```typescript
import { api } from './services/api';

// Example usage
const investigations = await api.getInvestigations();
const target = await api.createTarget(targetData);
```

### API Methods

- **Dashboard**: `getStatistics()`, `getRecentActivity()`
- **Investigations**: `getInvestigations()`, `createInvestigation()`, etc.
- **Targets**: `getTargets()`, `createTarget()`, etc.
- **Scraping**: `getScrapingJobs()`, `createScrapingJob()`, etc.
- **Crawling**: `getCrawlingSessions()`, `createCrawlingSession()`, etc.
- **Intelligence**: `getIntelligenceData()`, `enrichTarget()`, etc.
- **Findings**: `getFindings()`, `createFinding()`, etc.
- **Reports**: `getReports()`, `exportReport()`, etc.

## WebSocket Events

Subscribe to real-time events:

```typescript
import { websocket } from './services/websocket';

websocket.connect();
websocket.on('scraping:update', (data) => {
  // Handle scraping job updates
});
```

## Development Guidelines

### Code Style
- Use TypeScript for type safety
- Follow React best practices
- Use functional components and hooks
- Implement proper error handling
- Add loading states for async operations

### Component Structure
```typescript
import { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

export const MyComponent = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    // Load data logic
  };

  return (
    <Box>
      <Typography variant="h4">My Component</Typography>
      {/* Component content */}
    </Box>
  );
};
```

### State Management
- Use Zustand for global state
- Use React Query for server state
- Keep component state local when possible

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## Performance Optimization

- Code splitting with React.lazy
- Memoization with useMemo and useCallback
- Virtual scrolling for large lists
- Debounced search inputs
- Optimized re-renders

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Common Issues

1. **WebSocket connection fails**
   - Check VITE_WS_URL in .env
   - Ensure backend is running
   - Check for CORS issues

2. **API requests fail**
   - Verify VITE_API_BASE_URL
   - Check authentication token
   - Review network tab for errors

3. **Build errors**
   - Clear node_modules and reinstall
   - Check TypeScript errors
   - Verify all dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]
- Email: support@example.com

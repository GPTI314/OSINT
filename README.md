# OSINT Intelligence Platform

A comprehensive Open-Source Intelligence (OSINT) toolkit featuring modular collectors, enrichment pipeline, link analysis, risk scoring, and investigative workflow automation.

## Overview

This platform provides a complete solution for OSINT operations, combining powerful web scraping and crawling capabilities with advanced data analysis, visualization, and reporting tools.

## Features

### Core Capabilities

- **Investigation Management**: Create and manage complex investigations with multiple targets and findings
- **Target Tracking**: Support for various target types (domains, IPs, emails, phone numbers, social media profiles, etc.)
- **Web Scraping**: Automated data collection from websites with configurable scraping jobs
- **Web Crawling**: Deep web crawling with customizable depth, page limits, and link following
- **Intelligence Gathering**: Multi-source data enrichment and OSINT data collection
- **Link Analysis**: Network graph visualization showing relationships between entities
- **Timeline Analysis**: Chronological event tracking and correlation
- **Threat Assessment**: Risk scoring and vulnerability identification
- **Finding Management**: Security finding tracking with severity classification
- **Report Generation**: Professional reports with multiple export formats (PDF, DOCX, HTML)

### Technical Features

- **Modern UI**: React-based frontend with Material-UI components
- **Real-time Updates**: WebSocket integration for live progress tracking
- **Data Visualization**: Interactive charts, graphs, and network diagrams
- **Advanced Tables**: Sortable, filterable tables with search and export
- **Dark Mode**: Full theme switching support
- **Responsive Design**: Mobile-friendly interface
- **Export Capabilities**: Multiple export formats (CSV, JSON, PDF)
- **Accessibility**: WCAG compliance considerations

## Architecture

### Frontend
- **React 19** with TypeScript
- **Material-UI (MUI)** for UI components
- **React Router** for navigation
- **Zustand** for state management
- **React Query** for server state
- **Recharts** for charts and graphs
- **React Flow** for network visualization
- **Socket.io Client** for real-time updates

### Backend (To Be Implemented)
- RESTful API
- WebSocket server
- Database (PostgreSQL/MongoDB)
- Job queue for async tasks
- Integration with OSINT data sources

## Project Structure

```
OSINT/
├── src/
│   ├── components/       # Reusable React components
│   ├── pages/           # Page components for each module
│   ├── layouts/         # Layout components
│   ├── services/        # API and WebSocket services
│   ├── store/           # State management
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── theme.ts         # MUI theme configuration
│   ├── App.tsx          # Main application component
│   └── main.tsx         # Entry point
├── public/              # Static assets
├── .env.example         # Environment variables template
├── FRONTEND_README.md   # Detailed frontend documentation
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/OSINT.git
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

### Building for Production

```bash
npm run build
npm run preview  # Preview the production build
```

## Modules

### 1. Dashboard
- Overview of all investigations and activities
- Real-time statistics and metrics
- Visual data representation
- Recent activity feed

### 2. Investigations
- Create and manage investigations
- Track status, priority, and progress
- View associated targets and findings
- Activity timeline

### 3. Targets
- Add targets of various types
- Risk score assessment
- Bulk operations
- Advanced filtering

### 4. Scraping
- Create scraping jobs
- Monitor progress in real-time
- Control job execution (pause/resume/cancel)
- View collected data

### 5. Crawling
- Web crawling sessions
- Configurable crawl parameters
- Page discovery tracking
- Respect robots.txt option

### 6. Intelligence
- Data enrichment from multiple sources
- Domain, IP, email, phone intelligence
- Confidence scoring
- Related entity discovery

### 7. Analysis
- Network graph visualization
- Timeline analysis
- Correlation mapping
- Threat assessment

### 8. Findings
- Security finding management
- Severity-based classification
- Evidence attachment
- Status workflow

### 9. Reports
- Generate professional reports
- Multiple report types
- Export to PDF, DOCX, HTML
- Custom report builder

### 10. Settings
- User preferences
- API configuration
- Integration settings
- System parameters

## Configuration

### Environment Variables

```env
VITE_API_BASE_URL=http://localhost:3000/api
VITE_WS_URL=http://localhost:3000
VITE_APP_NAME=OSINT Intelligence Platform
VITE_ENABLE_REAL_TIME_UPDATES=true
```

See `.env.example` for all available options.

## Development

### Code Structure

The application follows a modular structure:

- **Components**: Reusable UI components
- **Pages**: Full page components for routes
- **Services**: API and external service integrations
- **Store**: Global state management with Zustand
- **Types**: TypeScript type definitions
- **Utils**: Helper functions and utilities

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run tests

### Authentication

The application uses a mock authentication system for demonstration. In production:

1. Replace the mock login in `src/pages/auth/Login.tsx`
2. Implement JWT token refresh
3. Add proper session management
4. Integrate with your authentication backend

### API Integration

The frontend expects a REST API backend. Key endpoints:

- `/api/dashboard/*` - Dashboard data
- `/api/investigations/*` - Investigation CRUD
- `/api/targets/*` - Target management
- `/api/scraping/*` - Scraping jobs
- `/api/crawling/*` - Crawling sessions
- `/api/intelligence/*` - Intelligence data
- `/api/findings/*` - Finding management
- `/api/reports/*` - Report generation

See `src/services/api.ts` for the complete API client implementation.

### WebSocket Events

Real-time updates are handled through WebSocket connections:

- `scraping:update` - Scraping job progress
- `crawling:update` - Crawling session progress
- `investigation:update` - Investigation changes
- `finding:new` - New finding created

## Customization

### Theme

Edit `src/theme.ts` to customize the application theme:

```typescript
export const lightTheme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#9c27b0' },
    // ...
  },
});
```

### Adding New Modules

1. Create page components in `src/pages/[module-name]/`
2. Add routes in `src/App.tsx`
3. Create API methods in `src/services/api.ts`
4. Add navigation items in `src/layouts/AppLayout.tsx`
5. Define types in `src/types/index.ts`

## Deployment

### Production Build

```bash
npm run build
```

The `dist/` directory contains the production-ready files.

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

### Environment-Specific Configuration

Use different `.env` files for different environments:

- `.env.development` - Development
- `.env.staging` - Staging
- `.env.production` - Production

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Backend API implementation
- [ ] Database schema and models
- [ ] Integration with OSINT data sources
- [ ] Advanced search capabilities
- [ ] Machine learning-based analysis
- [ ] Collaboration features
- [ ] Audit logging
- [ ] Role-based access control
- [ ] API rate limiting
- [ ] Automated testing suite

## Security Considerations

- Implement proper authentication and authorization
- Sanitize all user inputs
- Use HTTPS in production
- Implement rate limiting
- Regular security audits
- Keep dependencies updated
- Follow OWASP guidelines

## Performance

- Code splitting for optimal bundle size
- Lazy loading of routes and components
- Memoization for expensive computations
- Virtual scrolling for large data sets
- Debounced search and filter inputs
- Optimized re-renders

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `vite.config.ts`
2. **WebSocket connection fails**: Check the `VITE_WS_URL` environment variable
3. **API requests fail**: Verify the `VITE_API_BASE_URL` is correct
4. **Build errors**: Clear `node_modules` and reinstall dependencies

## Documentation

- [Frontend Documentation](FRONTEND_README.md) - Detailed frontend documentation
- API Documentation (coming soon)
- Deployment Guide (coming soon)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Material-UI for the excellent component library
- React Flow for network visualization
- Recharts for charting capabilities
- The OSINT community for inspiration

## Support

For support, email support@example.com or open an issue on GitHub.

## Authors

- Your Name - Initial work

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Complete frontend implementation
- All 10 core modules
- Real-time updates support
- Export functionality
- Dark mode support
- Responsive design

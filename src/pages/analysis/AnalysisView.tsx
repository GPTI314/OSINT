import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  Tabs,
  Tab,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
} from '@mui/material';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import { api } from '../../services/api';
import { Investigation } from '../../types';
import { formatDate } from '../../utils/helpers';

export const AnalysisView = () => {
  const [tabValue, setTabValue] = useState(0);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedInvestigation, setSelectedInvestigation] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [threatData, setThreatData] = useState<any>(null);

  useEffect(() => {
    loadInvestigations();
  }, []);

  useEffect(() => {
    if (selectedInvestigation) {
      loadAnalysisData(selectedInvestigation);
    }
  }, [selectedInvestigation]);

  const loadInvestigations = async () => {
    try {
      const response = await api.getInvestigations();
      setInvestigations(response.items);
      if (response.items.length > 0) {
        setSelectedInvestigation(response.items[0].id);
      }
    } catch (error) {
      console.error('Failed to load investigations:', error);
    }
  };

  const loadAnalysisData = async (investigationId: string) => {
    setLoading(true);
    try {
      const [correlationData, timeline] = await Promise.all([
        api.getCorrelationGraph(investigationId),
        api.getTimeline(investigationId),
      ]);

      // Transform correlation data to React Flow format
      const flowNodes: Node[] = correlationData.nodes.map((node: any) => ({
        id: node.id,
        type: 'default',
        data: { label: node.label },
        position: { x: node.x || Math.random() * 500, y: node.y || Math.random() * 500 },
        style: {
          background: getNodeColor(node.type),
          color: 'white',
          border: '2px solid #222',
          borderRadius: '8px',
          padding: '10px',
        },
      }));

      const flowEdges: Edge[] = correlationData.edges.map((edge: any) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        animated: true,
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
      setTimelineData(timeline);
    } catch (error) {
      console.error('Failed to load analysis data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNodeColor = (type: string): string => {
    const colors: Record<string, string> = {
      person: '#1976d2',
      organization: '#2e7d32',
      domain: '#9c27b0',
      ip: '#ed6c02',
      email: '#0288d1',
      phone: '#d32f2f',
      social: '#7b1fa2',
      default: '#757575',
    };
    return colors[type] || colors.default;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Analysis</Typography>
        <FormControl sx={{ minWidth: 300 }}>
          <InputLabel>Investigation</InputLabel>
          <Select
            value={selectedInvestigation}
            onChange={(e) => setSelectedInvestigation(e.target.value)}
            label="Investigation"
          >
            {investigations.map((inv) => (
              <MenuItem key={inv.id} value={inv.id}>
                {inv.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Card sx={{ mb: 2 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="Network Graph" />
          <Tab label="Timeline" />
          <Tab label="Threat Analysis" />
        </Tabs>
      </Card>

      {loading && (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      )}

      {!loading && tabValue === 0 && (
        <Paper sx={{ height: 600, border: '1px solid #ddd' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </Paper>
      )}

      {!loading && tabValue === 1 && (
        <Paper sx={{ p: 3 }}>
          <Timeline position="alternate">
            {timelineData.map((event, index) => (
              <TimelineItem key={event.id}>
                <TimelineOppositeContent color="text.secondary">
                  {formatDate(event.timestamp)}
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot color={index % 2 === 0 ? 'primary' : 'secondary'} />
                  {index < timelineData.length - 1 && <TimelineConnector />}
                </TimelineSeparator>
                <TimelineContent>
                  <Typography variant="h6">{event.title}</Typography>
                  <Typography>{event.description}</Typography>
                </TimelineContent>
              </TimelineItem>
            ))}
          </Timeline>
        </Paper>
      )}

      {!loading && tabValue === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Threat Analysis
          </Typography>
          <Typography color="textSecondary">
            Threat analysis data will be displayed here. This includes risk assessments,
            vulnerability mapping, and threat intelligence correlation.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

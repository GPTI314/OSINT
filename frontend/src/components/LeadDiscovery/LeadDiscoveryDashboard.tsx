/**
 * Lead Discovery Dashboard
 *
 * Main dashboard for lead discovery and matchmaking system.
 */

import React, { useState, useEffect } from 'react';
import { Card, Tabs, Button, Statistic, Row, Col, message } from 'antd';
import {
  TeamOutlined,
  RocketOutlined,
  EnvironmentOutlined,
  BellOutlined,
} from '@ant-design/icons';

import LeadList from './LeadList';
import LeadDiscovery from './LeadDiscovery';
import MatchmakingDashboard from './MatchmakingDashboard';
import TrackingDashboard from './TrackingDashboard';
import AlertsDashboard from './AlertsDashboard';
import GeographicMap from './GeographicMap';

const { TabPane } = Tabs;

interface DashboardStats {
  total_leads: number;
  new_leads: number;
  qualified_leads: number;
  converted_leads: number;
  total_matches: number;
  avg_match_score: number;
  total_profiles: number;
  new_alerts: number;
}

const LeadDiscoveryDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/lead-discovery/analytics/overview');
      const data = await response.json();

      if (data.success) {
        setStats({
          total_leads: data.lead_stats.total_leads || 0,
          new_leads: data.lead_stats.new_leads || 0,
          qualified_leads: data.lead_stats.qualified_leads || 0,
          converted_leads: data.lead_stats.converted_leads || 0,
          total_matches: data.match_stats.total_matches || 0,
          avg_match_score: data.match_stats.avg_match_score || 0,
          total_profiles: data.tracking_stats.total_profiles || 0,
          new_alerts: 0, // Fetch from alerts endpoint
        });
      }
    } catch (error) {
      message.error('Failed to fetch dashboard statistics');
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="lead-discovery-dashboard">
      <h1>Lead Discovery & Matchmaking</h1>

      {/* Statistics Overview */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Leads"
              value={stats?.total_leads || 0}
              prefix={<TeamOutlined />}
              loading={loading}
            />
            <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
              {stats?.new_leads || 0} new this week
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Matched Leads"
              value={stats?.total_matches || 0}
              prefix={<RocketOutlined />}
              loading={loading}
            />
            <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
              Avg. score: {(stats?.avg_match_score || 0).toFixed(0)}%
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Tracked Profiles"
              value={stats?.total_profiles || 0}
              prefix={<EnvironmentOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Active Alerts"
              value={stats?.new_alerts || 0}
              prefix={<BellOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      {/* Main Content */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="Overview" key="overview">
            <Row gutter={16}>
              <Col span={12}>
                <h3>Recent Leads</h3>
                <LeadList limit={10} />
              </Col>
              <Col span={12}>
                <h3>Geographic Distribution</h3>
                <GeographicMap />
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="Lead Discovery" key="discovery">
            <LeadDiscovery onLeadsDiscovered={fetchStats} />
          </TabPane>

          <TabPane tab="All Leads" key="leads">
            <LeadList />
          </TabPane>

          <TabPane tab="Matchmaking" key="matchmaking">
            <MatchmakingDashboard />
          </TabPane>

          <TabPane tab="Tracking" key="tracking">
            <TrackingDashboard />
          </TabPane>

          <TabPane tab="Alerts" key="alerts">
            <AlertsDashboard onAlertsChanged={fetchStats} />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default LeadDiscoveryDashboard;

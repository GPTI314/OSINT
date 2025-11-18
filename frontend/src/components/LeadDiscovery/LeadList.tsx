/**
 * Lead List Component
 *
 * Displays list of discovered leads with filters.
 */

import React, { useState, useEffect } from 'react';
import { Table, Tag, Button, Space, Input, Select, message } from 'antd';
import { EyeOutlined, RocketOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Search } = Input;
const { Option } = Select;

interface Lead {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  location: string;
  industry: string;
  lead_category: string;
  signal_strength: number;
  intent_score: number;
  status: string;
  discovered_at: string;
}

interface LeadListProps {
  limit?: number;
  investigationId?: string;
}

const LeadList: React.FC<LeadListProps> = ({ limit, investigationId }) => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    status: null,
    location: '',
    industry: '',
  });

  useEffect(() => {
    fetchLeads();
  }, [filters, investigationId]);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        ...(investigationId && { investigation_id: investigationId }),
        ...(filters.status && { status: filters.status }),
        ...(filters.location && { location: filters.location }),
        ...(filters.industry && { industry: filters.industry }),
        ...(limit && { limit: limit.toString() }),
      });

      const response = await fetch(`/api/v1/lead-discovery/leads?${params}`);
      const data = await response.json();

      if (data.success) {
        setLeads(data.leads);
      }
    } catch (error) {
      message.error('Failed to fetch leads');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async (leadId: string) => {
    try {
      const response = await fetch(`/api/v1/lead-discovery/leads/${leadId}/match`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        message.success(`Found ${data.matches_count} matches for this lead`);
      }
    } catch (error) {
      message.error('Failed to match lead');
    }
  };

  const columns: ColumnsType<Lead> = [
    {
      title: 'Name/Company',
      key: 'name',
      render: (_, record) => (
        <div>
          <strong>{record.name || record.company}</strong>
          <br />
          <small style={{ color: '#888' }}>
            {record.industry} • {record.location}
          </small>
        </div>
      ),
    },
    {
      title: 'Contact',
      key: 'contact',
      render: (_, record) => (
        <div>
          {record.email && <div>{record.email}</div>}
          {record.phone && <div>{record.phone}</div>}
        </div>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'lead_category',
      key: 'lead_category',
      render: (category) => category && <Tag color="blue">{category}</Tag>,
    },
    {
      title: 'Signal',
      dataIndex: 'signal_strength',
      key: 'signal_strength',
      render: (strength) => (
        <div>
          <div>{strength}%</div>
          <div style={{ fontSize: 10, color: '#888' }}>strength</div>
        </div>
      ),
      sorter: (a, b) => a.signal_strength - b.signal_strength,
    },
    {
      title: 'Intent',
      dataIndex: 'intent_score',
      key: 'intent_score',
      render: (score) => (
        <div>
          <div>{score}%</div>
          <div style={{ fontSize: 10, color: '#888' }}>intent</div>
        </div>
      ),
      sorter: (a, b) => a.intent_score - b.intent_score,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors: Record<string, string> = {
          new: 'green',
          qualified: 'blue',
          contacted: 'orange',
          converted: 'purple',
          lost: 'red',
        };
        return <Tag color={colors[status] || 'default'}>{status}</Tag>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => window.open(`/leads/${record.id}`, '_blank')}
          >
            View
          </Button>
          <Button
            size="small"
            type="primary"
            icon={<RocketOutlined />}
            onClick={() => handleMatch(record.id)}
          >
            Match
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {!limit && (
        <Space style={{ marginBottom: 16 }}>
          <Select
            placeholder="Filter by status"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => setFilters({ ...filters, status: value })}
          >
            <Option value="new">New</Option>
            <Option value="qualified">Qualified</Option>
            <Option value="contacted">Contacted</Option>
            <Option value="converted">Converted</Option>
          </Select>
          <Search
            placeholder="Filter by location"
            allowClear
            style={{ width: 200 }}
            onSearch={(value) => setFilters({ ...filters, location: value })}
          />
          <Search
            placeholder="Filter by industry"
            allowClear
            style={{ width: 200 }}
            onSearch={(value) => setFilters({ ...filters, industry: value })}
          />
        </Space>
      )}

      <Table
        columns={columns}
        dataSource={leads}
        rowKey="id"
        loading={loading}
        pagination={limit ? false : { pageSize: 20 }}
        size={limit ? 'small' : 'middle'}
      />
    </div>
  );
};

export default LeadList;

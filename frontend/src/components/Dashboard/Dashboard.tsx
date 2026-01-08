import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Phone, CheckCircle, AlertTriangle, Clock, Plus, List } from 'lucide-react';
import { StatsCard } from './StatsCard';
import { RecentCallsTable } from './RecentCallsTable';
import { Button } from '../common/Button';
import { useApi } from '../../hooks/useApi';
import { dashboardApi, callApi } from '../../services/api';
import { Loading } from '../common/Loading';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const {
    data: stats,
    loading: statsLoading,
    error: statsError,
    execute: fetchStats,
  } = useApi(dashboardApi.getStats);

  const {
    data: recentCalls,
    loading: callsLoading,
    error: callsError,
    execute: fetchRecentCalls,
  } = useApi(() => callApi.getRecent(10));

  useEffect(() => {
    fetchStats();
    fetchRecentCalls();
  }, []);

  if (statsLoading && !stats) {
    return <Loading size="lg" text="Loading dashboard..." fullScreen />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your call overview.</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            icon={<List size={18} />}
            onClick={() => navigate('/calls')}
          >
            View All Calls
          </Button>
          <Button
            variant="primary"
            icon={<Plus size={18} />}
            onClick={() => navigate('/agent-configs')}
          >
            New Call
          </Button>
        </div>
      </div>

      {/* Error Messages */}
      {statsError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Error loading statistics</p>
          <p className="text-sm">{statsError}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Calls"
          value={stats?.total_calls || 0}
          icon={Phone}
          color="purple"
          trend={{ value: 12.5, isPositive: true }}
        />
        <StatsCard
          title="Successful"
          value={stats?.successful_calls || 0}
          icon={CheckCircle}
          color="green"
          trend={{ value: 8.2, isPositive: true }}
        />
        <StatsCard
          title="Emergency"
          value={stats?.emergency_calls || 0}
          icon={AlertTriangle}
          color="red"
        />
        <StatsCard
          title="In Progress"
          value={stats?.in_progress_calls || 0}
          icon={Clock}
          color="blue"
        />
      </div>

      {/* Recent Calls */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Recent Calls</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/calls')}
          >
            View All →
          </Button>
        </div>

        {callsError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            <p className="font-medium">Error loading recent calls</p>
            <p className="text-sm">{callsError}</p>
          </div>
        )}

        <RecentCallsTable calls={recentCalls || []} loading={callsLoading} />
      </div>
    </div>
  );
};

export { Dashboard };

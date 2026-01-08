import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Download, Phone, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import type { Call } from '../types/index';
import { CallStatus } from '../types/index';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Loading } from '../components/common/Loading';
import { formatDateTime, formatDuration, formatPhoneNumber } from '../utils/formatters';

export const CallHistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [calls, setCalls] = useState<Call[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<CallStatus | 'all'>('all');

  useEffect(() => {
    fetchCalls();
  }, []);

  const fetchCalls = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getCalls();
      setCalls(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch calls');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: CallStatus): 'green' | 'yellow' | 'red' | 'blue' | 'gray' => {
    switch (status) {
      case CallStatus.COMPLETED:
        return 'green';
      case CallStatus.IN_PROGRESS:
        return 'blue';
      case CallStatus.FAILED:
      case CallStatus.CALL_ENDED:
        return 'red';
      case CallStatus.INITIATED:
        return 'yellow';
      default:
        return 'gray';
    }
  };

  const getStatusIcon = (status: CallStatus) => {
    switch (status) {
      case CallStatus.COMPLETED:
        return <CheckCircle className="w-4 h-4" />;
      case CallStatus.IN_PROGRESS:
        return <Phone className="w-4 h-4 animate-pulse" />;
      case CallStatus.FAILED:
      case CallStatus.CALL_ENDED:
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const filteredCalls = calls.filter(call => {
    const matchesSearch =
      call.driver_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      call.phone_number.includes(searchTerm) ||
      (call.load_number?.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus = statusFilter === 'all' || call.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const handleExport = () => {
    const csv = [
      ['Call ID', 'Driver Name', 'Phone', 'Load Number', 'Status', 'Duration', 'Created At'].join(','),
      ...filteredCalls.map(call => [
        call.id,
        call.driver_name,
        call.phone_number,
        call.load_number || '',
        call.status,
        call.call_duration_seconds ? formatDuration(call.call_duration_seconds) : 'N/A',
        formatDateTime(call.created_at)
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `calls_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loading size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Call History</h1>
          <p className="text-gray-600 mt-1">View and manage all your call records</p>
        </div>
        <Button onClick={handleExport} variant="outline" className="flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export CSV
        </Button>
      </div>

      {error && (
        <Card className="bg-red-50 border-red-200">
          <p className="text-red-800">{error}</p>
        </Card>
      )}

      <Card>
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Search by driver name, phone, or load number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as CallStatus | 'all')}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value={CallStatus.INITIATED}>Initiated</option>
              <option value={CallStatus.IN_PROGRESS}>In Progress</option>
              <option value={CallStatus.COMPLETED}>Completed</option>
              <option value={CallStatus.FAILED}>Failed</option>
              <option value={CallStatus.CALL_ENDED}>Ended</option>
            </select>
          </div>
        </div>

        {filteredCalls.length === 0 ? (
          <div className="text-center py-12">
            <Phone className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No calls found</p>
            <p className="text-gray-400 mt-2">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-purple-50 to-indigo-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Driver
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Load Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCalls.map((call) => (
                  <tr
                    key={call.id}
                    className="hover:bg-purple-50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/calls/${call.id}`)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{call.driver_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-gray-600">{formatPhoneNumber(call.phone_number)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-gray-600">{call.load_number || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge color={getStatusColor(call.status)} icon={getStatusIcon(call.status)}>
                        {call.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-gray-600">
                        <Clock className="w-4 h-4 mr-1" />
                        {call.call_duration_seconds ? formatDuration(call.call_duration_seconds) : 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                      {formatDateTime(call.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/calls/${call.id}`);
                        }}
                      >
                        View Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};

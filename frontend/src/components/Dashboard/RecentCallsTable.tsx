import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, Phone } from 'lucide-react';
import type { Call } from '../../types/index';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { formatDate, formatDuration, formatPhoneNumber, capitalizeWords } from '../../utils/formatters';

interface RecentCallsTableProps {
  calls: Call[];
  loading?: boolean;
}

export const RecentCallsTable: React.FC<RecentCallsTableProps> = ({ calls, loading }) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-200 rounded" />
          ))}
        </div>
      </Card>
    );
  }

  if (calls.length === 0) {
    return (
      <Card>
        <div className="text-center py-12">
          <Phone size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 text-lg font-medium">No calls yet</p>
          <p className="text-gray-400 text-sm mt-2">Start by triggering your first call</p>
        </div>
      </Card>
    );
  }

  return (
    <Card padding="none">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Driver
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Phone
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Load #
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Duration
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {calls.map((call) => (
              <tr
                key={call.id}
                className="hover:bg-purple-50/50 transition-colors cursor-pointer"
                onClick={() => navigate(`/calls/${call.id}`)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{call.driver_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatPhoneNumber(call.phone_number)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {call.load_number || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Badge status={call.status}>{capitalizeWords(call.status)}</Badge>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatDuration(call.duration)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatDate(call.created_at, 'MMM dd, HH:mm')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <Button
                    size="sm"
                    variant="ghost"
                    icon={<Eye size={16} />}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/calls/${call.id}`);
                    }}
                  >
                    View
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};


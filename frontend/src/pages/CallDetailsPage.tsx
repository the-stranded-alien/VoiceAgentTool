import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Phone, Clock, User, Package, MessageSquare, Calendar, CheckCircle } from 'lucide-react';
import type { Call } from '../types/index';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Loading } from '../components/common/Loading';
import { formatDateTime, formatDuration, formatPhoneNumber } from '../utils/formatters';

export const CallDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [call, setCall] = useState<Call | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchCallDetails(id);
    }
  }, [id]);

  const fetchCallDetails = async (callId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getCall(callId);
      setCall(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch call details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loading size="lg" />
      </div>
    );
  }

  if (error || !call) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate('/calls')} className="flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Call History
        </Button>
        <Card className="bg-red-50 border-red-200">
          <p className="text-red-800">{error || 'Call not found'}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate('/calls')} className="flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Call History
        </Button>
      </div>

      <div>
        <h1 className="text-3xl font-bold text-gray-900">Call Details</h1>
        <p className="text-gray-600 mt-1">Call ID: {call.id}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Information */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-purple-600" />
              Driver Information
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Driver Name</p>
                <p className="text-lg font-medium text-gray-900">{call.driver_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Phone Number</p>
                <p className="text-lg font-medium text-gray-900">{formatPhoneNumber(call.phone_number)}</p>
              </div>
              {call.load_number && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Load Number</p>
                  <p className="text-lg font-medium text-gray-900 flex items-center gap-2">
                    <Package className="w-4 h-4 text-purple-600" />
                    {call.load_number}
                  </p>
                </div>
              )}
            </div>
          </Card>

          {call.structured_data && (
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Collected Information
              </h2>
              <div className="space-y-4">
                {call.structured_data.location && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Location</p>
                    <p className="text-lg font-medium text-gray-900">{call.structured_data.location}</p>
                  </div>
                )}
                {call.structured_data.eta && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">ETA</p>
                    <p className="text-lg font-medium text-gray-900">{call.structured_data.eta}</p>
                  </div>
                )}
                {call.structured_data.reason && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Reason</p>
                    <p className="text-lg font-medium text-gray-900">{call.structured_data.reason}</p>
                  </div>
                )}
                {call.structured_data.additional_info && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Additional Information</p>
                    <p className="text-lg font-medium text-gray-900">{call.structured_data.additional_info}</p>
                  </div>
                )}
              </div>
            </Card>
          )}

          {call.transcript && (
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-purple-600" />
                Call Transcript
              </h2>
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-700">{call.transcript}</pre>
              </div>
            </Card>
          )}

          {call.recording_url && (
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Call Recording</h2>
              <audio controls className="w-full">
                <source src={call.recording_url} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Call Status</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-2">Current Status</p>
                <Badge color="blue" className="text-base">
                  {call.status}
                </Badge>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Clock className="w-4 h-4" />
                  <p className="text-sm">Duration</p>
                </div>
                <p className="text-lg font-medium text-gray-900">
                  {call.call_duration_seconds ? formatDuration(call.call_duration_seconds) : 'N/A'}
                </p>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Calendar className="w-4 h-4" />
                  <p className="text-sm">Created At</p>
                </div>
                <p className="text-lg font-medium text-gray-900">
                  {formatDateTime(call.created_at)}
                </p>
              </div>
              {call.updated_at && (
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-gray-600 mb-2">
                    <Calendar className="w-4 h-4" />
                    <p className="text-sm">Last Updated</p>
                  </div>
                  <p className="text-lg font-medium text-gray-900">
                    {formatDateTime(call.updated_at)}
                  </p>
                </div>
              )}
            </div>
          </Card>

          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Technical Details</h2>
            <div className="space-y-3">
              {call.retell_call_id && (
                <div>
                  <p className="text-sm text-gray-500">Retell Call ID</p>
                  <p className="text-sm font-mono text-gray-700 break-all">{call.retell_call_id}</p>
                </div>
              )}
              {call.agent_config_id && (
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-sm text-gray-500">Agent Config ID</p>
                  <p className="text-sm font-mono text-gray-700 break-all">{call.agent_config_id}</p>
                </div>
              )}
              {call.retell_agent_id && (
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-sm text-gray-500">Retell Agent ID</p>
                  <p className="text-sm font-mono text-gray-700 break-all">{call.retell_agent_id}</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

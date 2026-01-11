import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, User, Package, MessageSquare, Calendar, CheckCircle, AlertTriangle, MapPin, Truck } from 'lucide-react';
import type { Call, StructuredData, CheckInStructuredData, EmergencyStructuredData, DeliveryStructuredData } from '../types/index';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Loading } from '../components/common/Loading';
import { formatDateTime, formatDuration, formatPhoneNumber } from '../utils/formatters';

// Helper to determine if data is emergency type
const isEmergencyData = (data: StructuredData): data is EmergencyStructuredData => {
  return data?.call_outcome === 'Emergency Escalation' || 'emergency_type' in data;
};

// Helper to determine if data is check-in type
const isCheckInData = (data: StructuredData): data is CheckInStructuredData => {
  return 'driver_status' in data || data?.call_outcome === 'In-Transit Update' || data?.call_outcome === 'Arrival Confirmation';
};

// Helper to determine if data is delivery type
const isDeliveryData = (data: StructuredData): data is DeliveryStructuredData => {
  return 'pod_received' in data || data?.call_outcome === 'Delivery Confirmed' || data?.call_outcome === 'Delivery Issues';
};

// Get outcome badge variant
const getOutcomeBadgeVariant = (outcome?: string): 'success' | 'error' | 'warning' | 'info' => {
  if (!outcome) return 'info';
  if (outcome === 'Emergency Escalation') return 'error';
  if (outcome.includes('Confirmation') || outcome.includes('Confirmed')) return 'success';
  if (outcome.includes('Issues') || outcome.includes('Delayed')) return 'warning';
  return 'info';
};

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
              {/* Call Outcome Header */}
              {call.structured_data.call_outcome && (
                <div className="mb-6 pb-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                      {isEmergencyData(call.structured_data) ? (
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                      ) : (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      )}
                      Call Outcome
                    </h2>
                    <Badge variant={getOutcomeBadgeVariant(call.structured_data.call_outcome)} size="lg">
                      {call.structured_data.call_outcome}
                    </Badge>
                  </div>
                </div>
              )}

              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Collected Information
              </h3>

              {/* Emergency Data Display */}
              {isEmergencyData(call.structured_data) && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.emergency_type && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Emergency Type</p>
                        <Badge variant="error">{call.structured_data.emergency_type}</Badge>
                      </div>
                    )}
                    {call.structured_data.safety_status && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Safety Status</p>
                        <p className="text-lg font-medium text-gray-900">{call.structured_data.safety_status}</p>
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.injury_status && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Injury Status</p>
                        <p className="text-lg font-medium text-gray-900">{call.structured_data.injury_status}</p>
                      </div>
                    )}
                    {call.structured_data.emergency_location && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Emergency Location</p>
                        <p className="text-lg font-medium text-gray-900 flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-red-600" />
                          {call.structured_data.emergency_location}
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.load_secure !== undefined && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Load Secure</p>
                        <Badge variant={call.structured_data.load_secure ? 'success' : 'warning'}>
                          {call.structured_data.load_secure ? 'Yes' : 'No'}
                        </Badge>
                      </div>
                    )}
                    {call.structured_data.escalation_status && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Escalation Status</p>
                        <Badge variant="info">{call.structured_data.escalation_status}</Badge>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Check-In Data Display */}
              {isCheckInData(call.structured_data) && !isEmergencyData(call.structured_data) && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.driver_status && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Driver Status</p>
                        <Badge
                          variant={
                            call.structured_data.driver_status === 'Delayed' ? 'warning' :
                            call.structured_data.driver_status === 'Arrived' || call.structured_data.driver_status === 'Unloading' ? 'success' :
                            'info'
                          }
                        >
                          <Truck className="w-3 h-3" />
                          {call.structured_data.driver_status}
                        </Badge>
                      </div>
                    )}
                    {call.structured_data.current_location && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Current Location</p>
                        <p className="text-lg font-medium text-gray-900 flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-purple-600" />
                          {call.structured_data.current_location}
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.eta && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">ETA</p>
                        <p className="text-lg font-medium text-gray-900 flex items-center gap-2">
                          <Clock className="w-4 h-4 text-purple-600" />
                          {call.structured_data.eta}
                        </p>
                      </div>
                    )}
                    {call.structured_data.delay_reason && call.structured_data.delay_reason !== 'None' && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Delay Reason</p>
                        <Badge variant="warning">{call.structured_data.delay_reason}</Badge>
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.unloading_status && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Unloading Status</p>
                        <p className="text-lg font-medium text-gray-900">{call.structured_data.unloading_status}</p>
                      </div>
                    )}
                    {call.structured_data.pod_reminder_acknowledged !== undefined && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">POD Reminder Acknowledged</p>
                        <Badge variant={call.structured_data.pod_reminder_acknowledged ? 'success' : 'warning'}>
                          {call.structured_data.pod_reminder_acknowledged ? 'Yes' : 'No'}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Delivery Data Display */}
              {isDeliveryData(call.structured_data) && !isEmergencyData(call.structured_data) && !isCheckInData(call.structured_data) && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.delivery_time && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Delivery Time</p>
                        <p className="text-lg font-medium text-gray-900">{call.structured_data.delivery_time}</p>
                      </div>
                    )}
                    {call.structured_data.pod_received !== undefined && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">POD Received</p>
                        <Badge variant={call.structured_data.pod_received ? 'success' : 'warning'}>
                          {call.structured_data.pod_received ? 'Yes' : 'No'}
                        </Badge>
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {call.structured_data.pod_number && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">POD Number</p>
                        <p className="text-lg font-medium text-gray-900">{call.structured_data.pod_number}</p>
                      </div>
                    )}
                    {call.structured_data.delivery_issues && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Delivery Issues</p>
                        <p className="text-lg font-medium text-gray-900">{call.structured_data.delivery_issues}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Fallback: Generic key-value display for unknown schemas */}
              {!isEmergencyData(call.structured_data) && !isCheckInData(call.structured_data) && !isDeliveryData(call.structured_data) && (
                <div className="space-y-3">
                  {Object.entries(call.structured_data).map(([key, value]) => {
                    if (value === null || value === undefined || key === 'call_outcome') return null;
                    return (
                      <div key={key}>
                        <p className="text-sm text-gray-500 mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                        <p className="text-lg font-medium text-gray-900">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
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
                <Badge status={call.status} className="text-base capitalize">
                  {call.status.replace(/_/g, ' ')}
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

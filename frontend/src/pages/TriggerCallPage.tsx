import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Phone, User, Package, Settings } from 'lucide-react';
import type { AgentConfig, CallCreate } from '../types/index';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { Loading } from '../components/common/Loading';

export const TriggerCallPage: React.FC = () => {
  const navigate = useNavigate();
  const [agentConfigs, setAgentConfigs] = useState<AgentConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState<CallCreate>({
    agent_config_id: '',
    driver_name: '',
    phone_number: '',
    load_number: ''
  });

  useEffect(() => {
    fetchAgentConfigs();
  }, []);

  const fetchAgentConfigs = async () => {
    try {
      const data = await api.getAgentConfigs();
      setAgentConfigs(data);
      if (data.length > 0 && !formData.agent_config_id) {
        setFormData(prev => ({ ...prev, agent_config_id: data[0].id! }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agent configurations');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const response = await api.createCall(formData);
      setSuccess(`Call initiated successfully! Call ID: ${response.id}`);

      // Reset form
      setFormData({
        agent_config_id: agentConfigs[0]?.id || '',
        driver_name: '',
        phone_number: '',
        load_number: ''
      });

      // Navigate to call details after 2 seconds
      setTimeout(() => {
        navigate(`/calls/${response.id}`);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initiate call');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const isFormValid = formData.agent_config_id &&
                       formData.driver_name.trim() &&
                       formData.phone_number.trim();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Trigger New Call</h1>
        <p className="text-gray-600 mt-1">Initiate an AI-powered voice call to a driver</p>
      </div>

      {error && (
        <Card className="bg-red-50 border-red-200">
          <p className="text-red-800">{error}</p>
        </Card>
      )}

      {success && (
        <Card className="bg-green-50 border-green-200">
          <p className="text-green-800">{success}</p>
        </Card>
      )}

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Agent Configuration Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <Settings className="w-4 h-4 text-purple-600" />
              Agent Configuration
            </label>
            {agentConfigs.length === 0 ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800">No agent configurations available. Please create one first.</p>
                <Button
                  type="button"
                  variant="primary"
                  onClick={() => navigate('/agents')}
                  className="mt-2"
                >
                  Create Agent Configuration
                </Button>
              </div>
            ) : (
              <select
                name="agent_config_id"
                value={formData.agent_config_id}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Select an agent configuration</option>
                {agentConfigs.map(config => (
                  <option key={config.id} value={config.id}>
                    {config.name}
                  </option>
                ))}
              </select>
            )}
            {formData.agent_config_id && (
              <p className="text-sm text-gray-500 mt-2">
                {agentConfigs.find(c => c.id === formData.agent_config_id)?.system_prompt?.substring(0, 100)}...
              </p>
            )}
          </div>

          {/* Driver Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <User className="w-4 h-4 text-purple-600" />
              Driver Name
              <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              name="driver_name"
              value={formData.driver_name}
              onChange={handleChange}
              placeholder="John Doe"
              required
            />
          </div>

          {/* Driver Phone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <Phone className="w-4 h-4 text-purple-600" />
              Driver Phone Number
              <span className="text-red-500">*</span>
            </label>
            <Input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              placeholder="+1234567890"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Enter phone number in E.164 format (e.g., +1234567890)
            </p>
          </div>

          {/* Load Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <Package className="w-4 h-4 text-purple-600" />
              Load Number
              <span className="text-gray-400 text-xs">(Optional)</span>
            </label>
            <Input
              type="text"
              name="load_number"
              value={formData.load_number}
              onChange={handleChange}
              placeholder="LOAD-12345"
            />
          </div>

          {/* Submit Button */}
          <div className="flex gap-4 pt-4">
            <Button
              type="button"
              variant="primary"
              onClick={() => navigate('/calls')}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!isFormValid || loading || agentConfigs.length === 0}
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loading size="sm" className="mr-2" />
                  Initiating Call...
                </>
              ) : (
                <>
                  <Phone className="w-4 h-4 mr-2" />
                  Initiate Call
                </>
              )}
            </Button>
          </div>
        </form>
      </Card>

      {/* Info Card */}
      <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
        <h3 className="font-semibold text-purple-900 mb-2">How it works</h3>
        <ul className="space-y-2 text-sm text-purple-800">
          <li className="flex items-start gap-2">
            <span className="text-purple-600 mt-0.5">1.</span>
            <span>Select an agent configuration with the desired conversation flow</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 mt-0.5">2.</span>
            <span>Enter the driver's information including phone number</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 mt-0.5">3.</span>
            <span>The AI agent will call the driver and follow the configured script</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 mt-0.5">4.</span>
            <span>View real-time status updates and call results in the dashboard</span>
          </li>
        </ul>
      </Card>
    </div>
  );
};

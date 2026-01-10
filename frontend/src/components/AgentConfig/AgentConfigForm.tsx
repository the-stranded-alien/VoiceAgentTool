import React, { useState, useEffect } from 'react';
import type { AgentConfig } from '../../types/index';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';
import { Save, X } from 'lucide-react';

interface AgentConfigFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (config: Partial<AgentConfig>) => Promise<void>;
  config?: AgentConfig | null;
  loading?: boolean;
}

export const AgentConfigForm: React.FC<AgentConfigFormProps> = ({
  isOpen,
  onClose,
  onSave,
  config,
  loading = false,
}) => {
  const [formData, setFormData] = useState<Partial<AgentConfig>>({
    name: '',
    description: '',
    scenario_type: 'check_in',
    system_prompt: '',
    voice_settings: {
      voice_id: 'default',
      response_delay: 0.8,
      interruption_sensitivity: 0.7,
      backchannel: {
        enabled: true,
        frequency: 'medium',
      },
      filler_words: {
        enabled: true,
      },
      ambient_sound: false,
      speaking_rate: 'normal',
    },
    advanced_settings: {
      max_call_duration_minutes: 10,
      retry_attempts: 3,
      auto_escalate_emergency: true,
      record_calls: true,
    },
    status: 'active',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (config) {
      setFormData(config);
    } else {
      setFormData({
        name: '',
        description: '',
        scenario_type: 'check_in',
        system_prompt: '',
        voice_settings: {
          voice_id: 'default',
          response_delay: 0.8,
          interruption_sensitivity: 0.7,
          backchannel: {
            enabled: true,
            frequency: 'medium',
          },
          filler_words: {
            enabled: true,
          },
          ambient_sound: false,
          speaking_rate: 'normal',
        },
        advanced_settings: {
          max_call_duration_minutes: 10,
          retry_attempts: 3,
          auto_escalate_emergency: true,
          record_calls: true,
        },
        status: 'active',
      });
    }
    setErrors({});
  }, [config, isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    let newValue: any = value;

    if (type === 'checkbox') {
      newValue = (e.target as HTMLInputElement).checked;
    } else if (type === 'number') {
      newValue = parseFloat(value) || 0;
    }

    setFormData((prev) => ({ ...prev, [name]: newValue }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.system_prompt?.trim()) {
      newErrors.system_prompt = 'System prompt is required';
    }

    if (!formData.scenario_type?.trim()) {
      newErrors.scenario_type = 'Scenario type is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    await onSave(formData);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={config ? 'Edit Agent Configuration' : 'Create Agent Configuration'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Basic Information
          </h3>

          <Input
            label="Name"
            name="name"
            value={formData.name || ''}
            onChange={handleChange}
            error={errors.name}
            placeholder="e.g., Driver Check-In Agent"
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description || ''}
              onChange={handleChange}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Brief description of what this agent does"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scenario Type <span className="text-red-500">*</span>
            </label>
            <select
              name="scenario_type"
              value={formData.scenario_type || 'check_in'}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="check_in">Check-In</option>
              <option value="emergency">Emergency</option>
              <option value="delivery">Delivery</option>
              <option value="custom">Custom</option>
            </select>
            {errors.scenario_type && (
              <p className="text-sm text-red-600 mt-1">{errors.scenario_type}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              System Prompt <span className="text-red-500">*</span>
            </label>
            <textarea
              name="system_prompt"
              value={formData.system_prompt || ''}
              onChange={handleChange}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
              placeholder="Enter the system prompt that defines the agent's behavior..."
            />
            {errors.system_prompt && (
              <p className="text-sm text-red-600 mt-1">{errors.system_prompt}</p>
            )}
          </div>
        </div>

        {/* Voice Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Voice Settings
          </h3>

          <Input
            label="Voice ID"
            name="voice_id"
            value={formData.voice_settings?.voice_id || 'default'}
            onChange={(e) => {
              setFormData((prev) => ({
                ...prev,
                voice_settings: {
                  ...prev.voice_settings,
                  voice_id: e.target.value,
                },
              }));
            }}
            placeholder="default"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Speaking Rate
            </label>
            <select
              value={formData.voice_settings?.speaking_rate || 'normal'}
              onChange={(e) => {
                setFormData((prev) => ({
                  ...prev,
                  voice_settings: {
                    ...prev.voice_settings,
                    speaking_rate: e.target.value,
                  },
                }));
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="slow">Slow</option>
              <option value="normal">Normal</option>
              <option value="fast">Fast</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.voice_settings?.backchannel?.enabled || false}
              onChange={(e) => {
                setFormData((prev) => ({
                  ...prev,
                  voice_settings: {
                    ...prev.voice_settings,
                    backchannel: {
                      ...prev.voice_settings?.backchannel,
                      enabled: e.target.checked,
                    },
                  },
                }));
              }}
              className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
            />
            <label className="text-sm font-medium text-gray-700">
              Enable Backchannel (verbal acknowledgments)
            </label>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.voice_settings?.filler_words?.enabled || false}
              onChange={(e) => {
                setFormData((prev) => ({
                  ...prev,
                  voice_settings: {
                    ...prev.voice_settings,
                    filler_words: {
                      enabled: e.target.checked,
                    },
                  },
                }));
              }}
              className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
            />
            <label className="text-sm font-medium text-gray-700">
              Enable Filler Words (um, uh, etc.)
            </label>
          </div>
        </div>

        {/* Advanced Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Advanced Settings
          </h3>

          <Input
            label="Max Call Duration (minutes)"
            name="max_call_duration_minutes"
            type="number"
            value={formData.advanced_settings?.max_call_duration_minutes || 10}
            onChange={(e) => {
              setFormData((prev) => ({
                ...prev,
                advanced_settings: {
                  ...prev.advanced_settings,
                  max_call_duration_minutes: parseInt(e.target.value) || 10,
                },
              }));
            }}
            min={1}
            max={60}
          />

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.advanced_settings?.auto_escalate_emergency || false}
              onChange={(e) => {
                setFormData((prev) => ({
                  ...prev,
                  advanced_settings: {
                    ...prev.advanced_settings,
                    auto_escalate_emergency: e.target.checked,
                  },
                }));
              }}
              className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
            />
            <label className="text-sm font-medium text-gray-700">
              Auto-escalate emergency calls to human
            </label>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.advanced_settings?.record_calls || false}
              onChange={(e) => {
                setFormData((prev) => ({
                  ...prev,
                  advanced_settings: {
                    ...prev.advanced_settings,
                    record_calls: e.target.checked,
                  },
                }));
              }}
              className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
            />
            <label className="text-sm font-medium text-gray-700">
              Record calls for quality assurance
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              name="status"
              value={formData.status || 'active'}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={loading}
            icon={<X size={18} />}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            icon={<Save size={18} />}
          >
            {config ? 'Update' : 'Create'} Configuration
          </Button>
        </div>
      </form>
    </Modal>
  );
};

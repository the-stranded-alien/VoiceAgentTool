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
    system_prompt: '',
    voice_id: '',
    voice_temperature: 1.0,
    voice_speed: 1.0,
    responsiveness: 1.0,
    interruption_sensitivity: 1.0,
    enable_backchannel: false,
    backchannel_frequency: 0.8,
    backchannel_words: ['yeah', 'uh-huh', 'mm-hmm'],
    reminder_trigger_ms: 10000,
    reminder_max_count: 3,
    ambient_sound: 'off',
    ambient_sound_volume: 0.5,
    language: 'en-US',
    webhook_url: '',
    opt_out_sensitive_data_storage: false,
    normalize_for_speech: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (config) {
      setFormData(config);
    } else {
      setFormData({
        name: '',
        system_prompt: '',
        voice_id: '',
        voice_temperature: 1.0,
        voice_speed: 1.0,
        responsiveness: 1.0,
        interruption_sensitivity: 1.0,
        enable_backchannel: false,
        backchannel_frequency: 0.8,
        backchannel_words: ['yeah', 'uh-huh', 'mm-hmm'],
        reminder_trigger_ms: 10000,
        reminder_max_count: 3,
        ambient_sound: 'off',
        ambient_sound_volume: 0.5,
        language: 'en-US',
        webhook_url: '',
        opt_out_sensitive_data_storage: false,
        normalize_for_speech: true,
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

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Error saving config:', error);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={config ? 'Edit Agent Configuration' : 'Create Agent Configuration'}
      size="xl"
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={loading}>
            <X size={16} />
            Cancel
          </Button>
          <Button onClick={handleSubmit} loading={loading} icon={<Save size={16} />}>
            {config ? 'Update' : 'Create'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Basic Information
          </h3>

          <Input
            label="Configuration Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={errors.name}
            required
            placeholder="e.g., Freight Check-in Agent"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              System Prompt <span className="text-red-500">*</span>
            </label>
            <textarea
              name="system_prompt"
              value={formData.system_prompt}
              onChange={handleChange}
              rows={6}
              className={`
                w-full rounded-lg border transition-all duration-200 px-3 py-2
                ${
                  errors.system_prompt
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-purple-500 focus:ring-purple-500'
                }
                focus:outline-none focus:ring-2 focus:ring-offset-0
                font-mono text-sm
              `}
              placeholder="Enter the system prompt for the AI agent..."
            />
            {errors.system_prompt && (
              <p className="mt-1 text-sm text-red-600">{errors.system_prompt}</p>
            )}
          </div>
        </div>

        {/* Voice Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Voice Settings
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Voice ID"
              name="voice_id"
              value={formData.voice_id}
              onChange={handleChange}
              placeholder="e.g., 11labs-voice-id"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Language
              </label>
              <select
                name="language"
                value={formData.language}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish</option>
                <option value="fr-FR">French</option>
                <option value="de-DE">German</option>
              </select>
            </div>

            <Input
              label="Voice Temperature"
              name="voice_temperature"
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={formData.voice_temperature}
              onChange={handleChange}
              helperText="0.0 - 2.0"
            />

            <Input
              label="Voice Speed"
              name="voice_speed"
              type="number"
              step="0.1"
              min="0.5"
              max="2"
              value={formData.voice_speed}
              onChange={handleChange}
              helperText="0.5 - 2.0"
            />

            <Input
              label="Responsiveness"
              name="responsiveness"
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={formData.responsiveness}
              onChange={handleChange}
              helperText="Higher = faster response"
            />

            <Input
              label="Interruption Sensitivity"
              name="interruption_sensitivity"
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={formData.interruption_sensitivity}
              onChange={handleChange}
              helperText="Higher = easier to interrupt"
            />
          </div>
        </div>

        {/* Backchannel Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Backchannel Settings
          </h3>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="enable_backchannel"
              name="enable_backchannel"
              checked={formData.enable_backchannel}
              onChange={handleChange}
              className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
            />
            <label htmlFor="enable_backchannel" className="text-sm font-medium text-gray-700">
              Enable Backchannel (conversational fillers)
            </label>
          </div>

          {formData.enable_backchannel && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-7">
              <Input
                label="Backchannel Frequency"
                name="backchannel_frequency"
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={formData.backchannel_frequency}
                onChange={handleChange}
                helperText="0.0 - 1.0"
              />
            </div>
          )}
        </div>

        {/* Advanced Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Advanced Settings
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Reminder Trigger (ms)"
              name="reminder_trigger_ms"
              type="number"
              step="1000"
              value={formData.reminder_trigger_ms}
              onChange={handleChange}
              helperText="Time before reminder"
            />

            <Input
              label="Max Reminder Count"
              name="reminder_max_count"
              type="number"
              value={formData.reminder_max_count}
              onChange={handleChange}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ambient Sound
              </label>
              <select
                name="ambient_sound"
                value={formData.ambient_sound}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="off">Off</option>
                <option value="office">Office</option>
                <option value="cafe">Cafe</option>
                <option value="restaurant">Restaurant</option>
              </select>
            </div>

            <Input
              label="Ambient Sound Volume"
              name="ambient_sound_volume"
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={formData.ambient_sound_volume}
              onChange={handleChange}
              helperText="0.0 - 1.0"
            />

            <Input
              label="Webhook URL"
              name="webhook_url"
              value={formData.webhook_url}
              onChange={handleChange}
              placeholder="https://your-webhook-url.com"
            />
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="normalize_for_speech"
                name="normalize_for_speech"
                checked={formData.normalize_for_speech}
                onChange={handleChange}
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
              />
              <label htmlFor="normalize_for_speech" className="text-sm font-medium text-gray-700">
                Normalize text for speech
              </label>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="opt_out_sensitive_data_storage"
                name="opt_out_sensitive_data_storage"
                checked={formData.opt_out_sensitive_data_storage}
                onChange={handleChange}
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
              />
              <label
                htmlFor="opt_out_sensitive_data_storage"
                className="text-sm font-medium text-gray-700"
              >
                Opt out of sensitive data storage
              </label>
            </div>
          </div>
        </div>
      </form>
    </Modal>
  );
};



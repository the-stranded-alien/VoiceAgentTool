import React, { useEffect, useState } from 'react';
import { Plus, Bot } from 'lucide-react';
import { AgentConfigCard } from './AgentConfigCard';
import { AgentConfigForm } from './AgentConfigForm';
import { Button } from '../common/Button';
import { Loading } from '../common/Loading';
import type { AgentConfig } from '../../types/index';
import { agentConfigApi } from '../../services/api';
import { useApi } from '../../hooks/useApi';

export const AgentConfigList: React.FC = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<AgentConfig | null>(null);

  const {
    data: configs,
    loading,
    error,
    execute: fetchConfigs,
  } = useApi(agentConfigApi.getAll);

  const {
    loading: saveLoading,
    execute: saveConfig,
  } = useApi(async (data: Partial<AgentConfig>) => {
    if (selectedConfig?.id) {
      return agentConfigApi.update(selectedConfig.id, data);
    } else {
      return agentConfigApi.create(data as any);
    }
  });

  const {
    loading: deleteLoading,
    execute: deleteConfig,
  } = useApi(agentConfigApi.delete);

  useEffect(() => {
    fetchConfigs();
  }, []);

  const handleCreate = () => {
    setSelectedConfig(null);
    setIsFormOpen(true);
  };

  const handleEdit = (config: AgentConfig) => {
    setSelectedConfig(config);
    setIsFormOpen(true);
  };

  const handleDelete = async (config: AgentConfig) => {
    if (!config.id) return;

    if (window.confirm(`Are you sure you want to delete "${config.name}"?`)) {
      const result = await deleteConfig(config.id);
      if (result !== null) {
        await fetchConfigs();
      }
    }
  };

  const handleSave = async (data: Partial<AgentConfig>) => {
    const result = await saveConfig(data);
    if (result) {
      setIsFormOpen(false);
      setSelectedConfig(null);
      await fetchConfigs();
    }
  };

  if (loading && !configs) {
    return <Loading size="lg" text="Loading agent configurations..." fullScreen />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent Configurations</h1>
          <p className="text-gray-600 mt-1">
            Manage your AI agent configurations and voice settings
          </p>
        </div>
        <Button
          variant="primary"
          icon={<Plus size={18} />}
          onClick={handleCreate}
        >
          Create Configuration
        </Button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Error loading configurations</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Configurations Grid */}
      {configs && configs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {configs.map((config) => (
            <AgentConfigCard
              key={config.id}
              config={config}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="w-20 h-20 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Bot size={40} className="text-purple-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No agent configurations yet
          </h3>
          <p className="text-gray-600 mb-6">
            Create your first agent configuration to start making calls
          </p>
          <Button
            variant="primary"
            icon={<Plus size={18} />}
            onClick={handleCreate}
          >
            Create Your First Configuration
          </Button>
        </div>
      )}

      {/* Form Modal */}
      <AgentConfigForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedConfig(null);
        }}
        onSave={handleSave}
        config={selectedConfig}
        loading={saveLoading}
      />
    </div>
  );
};



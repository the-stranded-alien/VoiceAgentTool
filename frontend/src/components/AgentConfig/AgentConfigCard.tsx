import React from 'react';
import { Edit, Trash2, Bot, CheckCircle } from 'lucide-react';
import type { AgentConfig } from '../../types/index';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

interface AgentConfigCardProps {
  config: AgentConfig;
  onEdit: (config: AgentConfig) => void;
  onDelete: (config: AgentConfig) => void;
  onSelect?: (config: AgentConfig) => void;
}

export const AgentConfigCard: React.FC<AgentConfigCardProps> = ({
  config,
  onEdit,
  onDelete,
  onSelect,
}) => {
  return (
    <Card hover glass onClick={onSelect ? () => onSelect(config) : undefined}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
            <Bot size={24} className="text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-bold text-gray-900 truncate">
                {config.name}
              </h3>
              <Badge
                variant={config.status === 'active' ? 'success' : 'warning'}
                size="sm"
              >
                {config.status}
              </Badge>
            </div>
            <p className="text-sm text-gray-500 line-clamp-2 break-words">
              {config.description}
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Scenario:</span>
          <Badge variant="info" size="sm" className="capitalize">
            {config.scenario_type.replace('_', ' ')}
          </Badge>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Voice:</span>
          <span className="font-medium text-gray-900 truncate ml-2">
            {config.voice_settings?.voice_id || 'default'}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Max Duration:</span>
          <span className="font-medium text-gray-900">
            {config.advanced_settings?.max_call_duration_minutes || 10} min
          </span>
        </div>
        {config.voice_settings?.backchannel?.enabled && (
          <div className="flex items-center gap-2 text-sm text-green-600">
            <CheckCircle size={16} />
            <span>Backchannel enabled</span>
          </div>
        )}
      </div>

      <div className="flex gap-2 pt-4 border-t border-gray-200">
        <Button
          variant="secondary"
          size="sm"
          icon={<Edit size={16} />}
          onClick={(e) => {
            e.stopPropagation();
            onEdit(config);
          }}
          className="flex-1"
        >
          Edit
        </Button>
        <Button
          variant="danger"
          size="sm"
          icon={<Trash2 size={16} />}
          onClick={(e) => {
            e.stopPropagation();
            onDelete(config);
          }}
          className="flex-1"
        >
          Delete
        </Button>
      </div>
    </Card>
  );
};



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
        <div className="flex items-start gap-3 flex-1">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
            <Bot size={24} className="text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-gray-900 mb-1 truncate">
              {config.name}
            </h3>
            <p className="text-sm text-gray-500 line-clamp-2">
              {config.system_prompt}
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Voice ID:</span>
          <Badge variant="info" size="sm">{config.voice_id || 'Default'}</Badge>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Language:</span>
          <span className="font-medium text-gray-900">{config.language || 'en-US'}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Responsiveness:</span>
          <span className="font-medium text-gray-900">{config.responsiveness || 1.0}</span>
        </div>
        {config.enable_backchannel && (
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



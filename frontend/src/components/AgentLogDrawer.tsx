import { Descriptions, Drawer, Empty, Tabs, Typography } from 'antd';

import type { AgentExecutionLog } from '../types';

const { Text, Paragraph } = Typography;

type AgentLogDrawerProps = {
  open: boolean;
  onClose: () => void;
  log?: AgentExecutionLog | null;
};

export default function AgentLogDrawer({ open, onClose, log }: AgentLogDrawerProps) {
  if (!log) {
    return (
      <Drawer title="Agent 执行日志" width={640} open={open} onClose={onClose}>
        <Empty description="暂无日志数据" />
      </Drawer>
    );
  }

  const formatJSON = (json: string | null) => {
    if (!json) return '无数据';
    try {
      return JSON.stringify(JSON.parse(json), null, 2);
    } catch {
      return json;
    }
  };

  return (
    <Drawer
      title={`${log.agent_name} 执行日志`}
      width={720}
      open={open}
      onClose={onClose}
      destroyOnClose
    >
      <Descriptions bordered column={1} size="small" style={{ marginBottom: 16 }}>
        <Descriptions.Item label="日志 ID">{log.id}</Descriptions.Item>
        <Descriptions.Item label="Agent">{log.agent_name}</Descriptions.Item>
        <Descriptions.Item label="状态">{log.status}</Descriptions.Item>
        <Descriptions.Item label="耗时">{log.duration_ms != null ? `${log.duration_ms}ms` : '-'}</Descriptions.Item>
        <Descriptions.Item label="错误信息">
          {log.error_message ? <Text type="danger">{log.error_message}</Text> : '-'}
        </Descriptions.Item>
      </Descriptions>

      <Tabs
        defaultActiveKey="output"
        items={[
          {
            key: 'input',
            label: '输入 (Input)',
            children: (
              <Paragraph>
                <pre style={{ maxHeight: 400, overflow: 'auto', background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                  {formatJSON(log.input_json)}
                </pre>
              </Paragraph>
            ),
          },
          {
            key: 'output',
            label: '输出 (Output)',
            children: (
              <Paragraph>
                <pre style={{ maxHeight: 400, overflow: 'auto', background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                  {formatJSON(log.output_json)}
                </pre>
              </Paragraph>
            ),
          },
          {
            key: 'error',
            label: '错误 (Error)',
            children: log.error_message ? (
              <Paragraph>
                <Text type="danger">{log.error_message}</Text>
              </Paragraph>
            ) : (
              <Empty description="无错误信息" />
            ),
          },
        ]}
      />
    </Drawer>
  );
}

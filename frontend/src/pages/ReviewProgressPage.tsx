import { Button, Collapse, Descriptions, Empty, Space, Spin, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getReviewTask, getAgentLogs, getProfileResult } from '../api/reviews';
import AgentLogDrawer from '../components/AgentLogDrawer';
import PageHeader from '../components/PageHeader';
import type { AgentExecutionLog, ReviewTask } from '../types';

const { Text } = Typography;

export default function ReviewProgressPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<ReviewTask | null>(null);
  const [logs, setLogs] = useState<AgentExecutionLog[]>([]);
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<AgentExecutionLog | null>(null);

  useEffect(() => {
    if (!taskId) return;
    Promise.all([
      getReviewTask(taskId),
      getAgentLogs(taskId).catch(() => ({ data: { data: [] } })),
      getProfileResult(taskId).catch(() => null),
    ])
      .then(([taskRes, logsRes, profileRes]) => {
        setTask(taskRes.data.data);
        setLogs(logsRes.data.data);
        if (profileRes) setProfile(profileRes.data.data);
      })
      .catch(() => message.error('获取审查数据失败'))
      .finally(() => setLoading(false));
  }, [taskId]);

  if (loading) return <Spin style={{ display: 'block', margin: '40px auto' }} />;

  const statusColor =
    task?.status === 'SUCCESS' ? 'green' : task?.status === 'FAILED' ? 'red' : task?.status === 'RUNNING' ? 'orange' : 'default';

  const openLogDrawer = (log: AgentExecutionLog) => {
    setSelectedLog(log);
    setDrawerOpen(true);
  };

  return (
    <>
      <PageHeader title="审查进度" description="查看审查任务状态和 Agent 执行日志。" />

      <div className="page-panel" style={{ marginBottom: 16 }}>
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="任务 ID">{task?.id ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={statusColor}>{task?.status ?? '-'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="当前步骤">{task?.current_step || '-'}</Descriptions.Item>
          <Descriptions.Item label="错误信息" span={2}>
            {task?.error_message ? <Text type="danger">{task.error_message}</Text> : '-'}
          </Descriptions.Item>
        </Descriptions>
      </div>

      {profile && (
        <div className="page-panel" style={{ marginBottom: 16 }}>
          <Typography.Title level={5}>合同画像 (Contract Profile)</Typography.Title>
          <Descriptions bordered column={2} size="small">
            <Descriptions.Item label="合同类型">{String(profile.contract_type ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="甲方">{String(profile.party_a ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="乙方">{String(profile.party_b ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="签署日期">{String(profile.sign_date ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="合同金额">{String(profile.amount ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="合同期限">{String(profile.duration ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="合同标的" span={2}>{String(profile.subject ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="摘要" span={2}>{String(profile.summary ?? '-')}</Descriptions.Item>
            <Descriptions.Item label="缺失字段" span={2}>
              {Array.isArray(profile.missing_fields) && profile.missing_fields.length > 0
                ? (profile.missing_fields as string[]).join('、')
                : '无'}
            </Descriptions.Item>
          </Descriptions>
        </div>
      )}

      <div className="page-panel">
        <Typography.Title level={5}>Agent 执行日志</Typography.Title>
        {logs.length > 0 ? (
          <Collapse
            items={logs.map((log) => ({
              key: String(log.id),
              label: (
                <Space>
                  <Tag color={log.status === 'SUCCESS' ? 'green' : log.status === 'FAILED' ? 'red' : 'orange'}>
                    {log.status}
                  </Tag>
                  <Text>{log.agent_name}</Text>
                  {log.duration_ms != null && (
                    <Text type="secondary">{log.duration_ms}ms</Text>
                  )}
                </Space>
              ),
              children: (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Button size="small" onClick={() => openLogDrawer(log)}>
                    查看完整日志
                  </Button>
                  {log.error_message && (
                    <Text type="danger">错误: {log.error_message}</Text>
                  )}
                </Space>
              ),
            }))}
          />
        ) : (
          <Empty description="暂无 Agent 执行日志" />
        )}
      </div>

      <AgentLogDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        log={selectedLog}
      />
    </>
  );
}

import { Button, Space } from 'antd';
import { useState } from 'react';
import AgentLogDrawer from '../components/AgentLogDrawer';
import AgentStepBar from '../components/AgentStepBar';
import PageHeader from '../components/PageHeader';

export default function ReviewProgressPage() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <PageHeader title="审查进度" description="按多 Agent 顺序展示任务状态和日志入口。" />
      <div className="page-panel">
        <AgentStepBar />
        <Space style={{ marginTop: 24 }}>
          <Button onClick={() => setOpen(true)}>查看 Agent 日志</Button>
        </Space>
      </div>
      <AgentLogDrawer open={open} onClose={() => setOpen(false)} />
    </>
  );
}

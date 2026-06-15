import { Drawer, Empty } from 'antd';

type AgentLogDrawerProps = {
  open: boolean;
  onClose: () => void;
};

export default function AgentLogDrawer({ open, onClose }: AgentLogDrawerProps) {
  return (
    <Drawer title="Agent 执行日志" width={640} open={open} onClose={onClose}>
      <Empty description="后续阶段接入 agent_execution_log 数据" />
    </Drawer>
  );
}

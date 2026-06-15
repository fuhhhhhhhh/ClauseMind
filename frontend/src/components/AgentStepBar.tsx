import { Steps, Tag } from 'antd';

const AGENT_NAMES = [
  'ContractProfileAgent',
  'ClauseExtractionAgent',
  'RiskDetectionAgent',
  'SuggestionAgent',
  'ConsistencyCheckAgent',
  'ReportGenerationAgent',
];

const AGENT_LABELS: Record<string, string> = {
  ContractProfileAgent: '合同画像',
  ClauseExtractionAgent: '条款抽取',
  RiskDetectionAgent: '风险识别',
  SuggestionAgent: '修改建议',
  ConsistencyCheckAgent: '一致性校验',
  ReportGenerationAgent: '报告生成',
};

const statusTag = (status: string) => {
  const color =
    status === 'SUCCESS' ? 'green' : status === 'FAILED' ? 'red' : status === 'RUNNING' ? 'orange' : 'default';
  return <Tag color={color}>{status}</Tag>;
};

type Props = {
  logs?: { agent_name: string; status: string; duration_ms?: number | null }[];
};

export default function AgentStepBar({ logs }: Props) {
  if (!logs || logs.length === 0) {
    return <Steps current={-1} items={AGENT_NAMES.map((name) => ({ title: AGENT_LABELS[name] || name }))} />;
  }

  // Determine current step — last RUNNING or last FAILED or last SUCCESS
  let current = -1;
  for (let i = 0; i < AGENT_NAMES.length; i++) {
    const log = logs.find((l) => l.agent_name === AGENT_NAMES[i]);
    if (log && (log.status === 'RUNNING' || log.status === 'SUCCESS')) {
      current = i;
    }
    if (log && log.status === 'FAILED') {
      current = i;
      break;
    }
  }

  return (
    <Steps
      current={current}
      items={AGENT_NAMES.map((name) => {
        const log = logs.find((l) => l.agent_name === name);
        return {
          title: AGENT_LABELS[name] || name,
          description: log ? (
            <span>
              {statusTag(log.status)}
              {log.duration_ms != null ? ` ${log.duration_ms}ms` : ''}
            </span>
          ) : (
            'WAITING'
          ),
        };
      })}
    />
  );
}

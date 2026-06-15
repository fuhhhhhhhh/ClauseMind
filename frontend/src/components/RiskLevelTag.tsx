import { Tag } from 'antd';

type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW';

const riskMeta: Record<RiskLevel, { color: string; label: string }> = {
  HIGH: { color: 'red', label: '高风险' },
  MEDIUM: { color: 'orange', label: '中风险' },
  LOW: { color: 'green', label: '低风险' },
};

export default function RiskLevelTag({ level }: { level: RiskLevel }) {
  const meta = riskMeta[level];
  return <Tag color={meta.color}>{meta.label}</Tag>;
}

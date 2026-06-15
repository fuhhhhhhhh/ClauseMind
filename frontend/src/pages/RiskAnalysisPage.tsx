import { Table } from 'antd';
import PageHeader from '../components/PageHeader';
import RiskLevelTag from '../components/RiskLevelTag';

export default function RiskAnalysisPage() {
  return (
    <>
      <PageHeader title="风险分析" description="展示风险等级、依据原文、原因和影响。" />
      <div className="page-panel">
        <Table
          rowKey="risk_id"
          dataSource={[
            {
              risk_id: 'R1',
              risk_level: 'MEDIUM',
              risk_type: '违约责任不明确',
              reason: '演示占位数据',
            },
          ]}
          columns={[
            { title: '风险 ID', dataIndex: 'risk_id' },
            {
              title: '等级',
              dataIndex: 'risk_level',
              render: (level) => <RiskLevelTag level={level} />,
            },
            { title: '类型', dataIndex: 'risk_type' },
            { title: '原因', dataIndex: 'reason' },
          ]}
        />
      </div>
    </>
  );
}

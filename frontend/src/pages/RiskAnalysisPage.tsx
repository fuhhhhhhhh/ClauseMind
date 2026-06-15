import { Table, Tag, message } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getReviewRisks } from '../api/reviews';
import PageHeader from '../components/PageHeader';

const riskColor: Record<string, string> = { '高风险': 'red', '中风险': 'orange', '低风险': 'green' };

export default function RiskAnalysisPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId) return;
    getReviewRisks(taskId)
      .then((res) => setData(res.data.data))
      .catch(() => message.error('获取风险数据失败'))
      .finally(() => setLoading(false));
  }, [taskId]);

  return (
    <>
      <PageHeader title="风险分析" description="展示风险评估结果，包括等级、类型、原因和建议。" />
      <div className="page-panel">
        <Table
          rowKey="risk_id"
          loading={loading}
          dataSource={data}
          columns={[
            { title: '风险 ID', dataIndex: 'risk_id', width: 80 },
            {
              title: '等级',
              dataIndex: 'risk_level',
              width: 100,
              render: (level: string) => (
                <Tag color={riskColor[level] || 'default'}>{level}</Tag>
              ),
            },
            { title: '类型', dataIndex: 'risk_type', width: 150 },
            { title: '描述', dataIndex: 'description', ellipsis: true },
            { title: '原因', dataIndex: 'reason', ellipsis: true },
            {
              title: '需人工复核',
              dataIndex: 'need_human_review',
              width: 100,
              render: (v: boolean) => (v ? '是' : '否'),
            },
          ]}
        />
      </div>
    </>
  );
}

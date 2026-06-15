import { Table, message } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getReviewSuggestions } from '../api/reviews';
import PageHeader from '../components/PageHeader';

export default function SuggestionPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId) return;
    getReviewSuggestions(taskId)
      .then((res) => setData(res.data.data))
      .catch(() => message.error('获取建议数据失败'))
      .finally(() => setLoading(false));
  }, [taskId]);

  return (
    <>
      <PageHeader title="修改建议" description="针对风险条款给出具体修改建议文本和理由。" />
      <div className="page-panel">
        <Table
          rowKey="suggestion_id"
          loading={loading}
          dataSource={data}
          columns={[
            { title: '建议 ID', dataIndex: 'suggestion_id', width: 80 },
            { title: '关联风险 ID', dataIndex: 'risk_id', width: 80 },
            { title: '原条款', dataIndex: 'original_text', ellipsis: true },
            { title: '建议修改为', dataIndex: 'suggested_text', ellipsis: true },
            { title: '理由', dataIndex: 'reason', ellipsis: true },
          ]}
        />
      </div>
    </>
  );
}

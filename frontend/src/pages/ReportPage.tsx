import { Button, Descriptions, Space, Spin, Typography, message } from 'antd';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getReviewReport } from '../api/reviews';
import MarkdownViewer from '../components/MarkdownViewer';
import PageHeader from '../components/PageHeader';

const { Text } = Typography;

export default function ReportPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId) return;
    getReviewReport(taskId)
      .then((res) => setReport(res.data.data))
      .catch(() => message.error('获取报告失败'))
      .finally(() => setLoading(false));
  }, [taskId]);

  if (loading) return <Spin style={{ display: 'block', margin: '40px auto' }} />;

  if (!report)
    return (
      <PageHeader title="审查报告" description="暂无审查报告，请先启动审查。" />
    );

  const markdown = (report.markdown_report as string) || '';
  const disclaimer = (report.disclaimer as string) || '';

  return (
    <>
      <PageHeader title="审查报告" description={(report.report_title as string) || '-'} />
      <Space style={{ marginBottom: 16 }}>
        <Link to={`/review-tasks/${taskId}/risks`}>
          <Button size="small">风险分析</Button>
        </Link>
        <Link to={`/review-tasks/${taskId}/suggestions`}>
          <Button size="small">修改建议</Button>
        </Link>
        <Link to={`/review-tasks/${taskId}/progress`}>
          <Button size="small">审查进度</Button>
        </Link>
        <Button
          size="small"
          type="primary"
          onClick={() => {
            window.open(`/api/v1/reports/${taskId}/export`, '_blank');
          }}
        >
          导出 Markdown
        </Button>
      </Space>
      {markdown ? (
        <MarkdownViewer markdown={markdown} />
      ) : (
        <div className="page-panel">
          <Text type="secondary">暂无报告内容</Text>
        </div>
      )}
      {disclaimer && (
        <div className="page-panel" style={{ marginTop: 16 }}>
          <Descriptions bordered size="small">
            <Descriptions.Item label="免责声明">
              <Text type="secondary">{disclaimer}</Text>
            </Descriptions.Item>
          </Descriptions>
        </div>
      )}
    </>
  );
}

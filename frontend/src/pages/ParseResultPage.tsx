import { Collapse, Descriptions, Empty, Spin, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getParseStatus, getParseResult } from '../api/parse';
import MarkdownViewer from '../components/MarkdownViewer';
import PageHeader from '../components/PageHeader';
import type { ParseResultInfo, ParseStatusInfo } from '../types';

const { Text } = Typography;

export default function ParseResultPage() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<ParseStatusInfo | null>(null);
  const [result, setResult] = useState<ParseResultInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    Promise.all([getParseStatus(id), getParseResult(id).catch(() => null)])
      .then(([statusRes, resultRes]) => {
        setStatus(statusRes.data.data);
        if (resultRes) setResult(resultRes.data.data);
      })
      .catch(() => message.error('获取解析信息失败'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <Spin style={{ display: 'block', margin: '40px auto' }} />;
  }

  const jobStatus = status?.parse_job?.status;
  const statusColor =
    jobStatus === 'SUCCESS' ? 'green' : jobStatus === 'FAILED' ? 'red' : jobStatus === 'RUNNING' ? 'orange' : 'default';

  return (
    <>
      <PageHeader title="MinerU 解析结果" description="预览 Markdown、标准章节和输出文件信息。" />

      <div className="page-panel" style={{ marginBottom: 16 }}>
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="合同状态">{status?.contract_status ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="解析状态">
            <Tag color={statusColor}>{jobStatus ?? '-'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="解析引擎">{status?.parse_job?.backend ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="错误信息" span={2}>
            {status?.parse_job?.error_message ? (
              <Text type="danger">{status.parse_job.error_message}</Text>
            ) : (
              '-'
            )}
          </Descriptions.Item>
        </Descriptions>
      </div>

      <Collapse
        defaultActiveKey={result?.raw_markdown ? ['markdown'] : []}
        items={[
          {
            key: 'markdown',
            label: 'Markdown 预览',
            children: result?.raw_markdown ? (
              <MarkdownViewer markdown={result.raw_markdown} />
            ) : (
              <Empty description="暂无 Markdown 解析结果" />
            ),
          },
          {
            key: 'files',
            label: '输出文件',
            children: result ? (
              <Descriptions bordered column={1} size="small">
                <Descriptions.Item label="Markdown">
                  {result.markdown_path || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="content_list.json">
                  {result.content_json_path || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="middle.json">
                  {result.middle_json_path || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="layout.pdf">
                  {result.layout_pdf_path ? '已生成（路径: ' + result.layout_pdf_path + '）' : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="图片目录">{result.image_dir || '-'}</Descriptions.Item>
              </Descriptions>
            ) : (
              <Empty description="暂无输出文件信息" />
            ),
          },
          {
            key: 'normalized',
            label: '标准化结果（待 Phase 5）',
            children: <Empty description="标准化功能将在 Phase 5 实现" />,
          },
        ]}
      />
    </>
  );
}

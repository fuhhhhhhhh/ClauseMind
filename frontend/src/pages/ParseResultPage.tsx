import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { Button, Collapse, Descriptions, Empty, List, Spin, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getParseStatus, getParseResult, normalizeDocument } from '../api/parse';
import MarkdownViewer from '../components/MarkdownViewer';
import PageHeader from '../components/PageHeader';
import type { NormalizedDocument, ParseResultInfo, ParseStatusInfo } from '../types';

const { Text } = Typography;

const BoolIcon = ({ ok }: { ok: boolean }) =>
  ok ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <CloseCircleOutlined style={{ color: '#d9d9d9' }} />;

export default function ParseResultPage() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<ParseStatusInfo | null>(null);
  const [result, setResult] = useState<ParseResultInfo | null>(null);
  const [normalized, setNormalized] = useState<NormalizedDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [normLoading, setNormLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    Promise.all([getParseStatus(id), getParseResult(id).catch(() => null)])
      .then(([statusRes, resultRes]) => {
        setStatus(statusRes.data.data);
        if (resultRes) {
          setResult(resultRes.data.data);
          // Parse normalized_json if present
          if (resultRes.data.data.normalized_json) {
            try {
              setNormalized(JSON.parse(resultRes.data.data.normalized_json));
            } catch { /* ignore parse errors */ }
          }
        }
      })
      .catch(() => message.error('获取解析信息失败'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleNormalize = async () => {
    if (!id) return;
    setNormLoading(true);
    try {
      const res = await normalizeDocument(id);
      setNormalized(res.data.data);
      // Refresh parse result to get updated normalized_json
      const resultRes = await getParseResult(id);
      setResult(resultRes.data.data);
      message.success('标准化完成');
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '标准化失败';
      message.error(detail);
    } finally {
      setNormLoading(false);
    }
  };

  if (loading) {
    return <Spin style={{ display: 'block', margin: '40px auto' }} />;
  }

  const jobStatus = status?.parse_job?.status;
  const statusColor =
    jobStatus === 'SUCCESS' ? 'green' : jobStatus === 'FAILED' ? 'red' : jobStatus === 'RUNNING' ? 'orange' : 'default';

  return (
    <>
      <PageHeader title="MinerU 解析结果" description="预览 Markdown、标准化结构和输出产物摘要。" />

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
            label: '输出产物',
            children: result ? (
              <Descriptions bordered column={1} size="small">
                <Descriptions.Item label="Markdown 文件">
                  <BoolIcon ok={result.has_markdown} /> {result.has_markdown ? '已生成' : '未生成'}
                </Descriptions.Item>
                <Descriptions.Item label="Content JSON">
                  <BoolIcon ok={result.has_content_json} /> {result.has_content_json ? '已生成' : '未生成'}
                </Descriptions.Item>
                <Descriptions.Item label="Middle JSON">
                  <BoolIcon ok={result.has_middle_json} /> {result.has_middle_json ? '已生成' : '未生成'}
                </Descriptions.Item>
                <Descriptions.Item label="Layout PDF">
                  <BoolIcon ok={result.has_layout_pdf} /> {result.has_layout_pdf ? '已生成' : '未生成'}
                </Descriptions.Item>
                <Descriptions.Item label="图片目录">
                  <BoolIcon ok={result.has_images} /> {result.has_images ? '已生成' : '未生成'}
                </Descriptions.Item>
              </Descriptions>
            ) : (
              <Empty description="暂无输出文件信息" />
            ),
          },
          {
            key: 'normalized',
            label: '标准化结果',
            children: normalized ? (
              <div>
                <Descriptions bordered column={2} size="small" style={{ marginBottom: 16 }}>
                  <Descriptions.Item label="合同标题">{normalized.title || '-'}</Descriptions.Item>
                  <Descriptions.Item label="合同类型">{normalized.contract_type || '-'}</Descriptions.Item>
                </Descriptions>

                {normalized.parties.length > 0 && (
                  <>
                    <Typography.Title level={5}>主体 (Parties)</Typography.Title>
                    <List
                      bordered
                      size="small"
                      dataSource={normalized.parties}
                      renderItem={(p) => (
                        <List.Item>
                          <Tag>{p.role}</Tag> {p.name}
                        </List.Item>
                      )}
                    />
                  </>
                )}

                {normalized.sections.length > 0 && (
                  <>
                    <Typography.Title level={5} style={{ marginTop: 16 }}>
                      章节 (Sections) — {normalized.sections.length} 个
                    </Typography.Title>
                    <List
                      bordered
                      size="small"
                      dataSource={normalized.sections}
                      renderItem={(s) => (
                        <List.Item>
                          <Text strong>{s.id}</Text>: {s.title}（{s.clause_ids.length} 条款）
                        </List.Item>
                      )}
                    />
                  </>
                )}

                {normalized.clauses.length > 0 && (
                  <>
                    <Typography.Title level={5} style={{ marginTop: 16 }}>
                      条款 (Clauses) — {normalized.clauses.length} 个
                    </Typography.Title>
                    <List
                      bordered
                      size="small"
                      dataSource={normalized.clauses.slice(0, 50)}
                      renderItem={(c) => (
                        <List.Item>
                          <Text type="secondary">{c.id}</Text>&nbsp;{c.text}
                        </List.Item>
                      )}
                    />
                    {normalized.clauses.length > 50 && (
                      <Text type="secondary">... 另有 {normalized.clauses.length - 50} 个条款未展示</Text>
                    )}
                  </>
                )}
              </div>
            ) : (
              <Empty description="暂无标准化结果">
                <Button type="primary" loading={normLoading} onClick={handleNormalize} disabled={!result?.raw_markdown}>
                  生成结构化结果
                </Button>
              </Empty>
            ),
          },
        ]}
      />
    </>
  );
}

import { Button, Descriptions, Space, Spin, message } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { getContract } from '../api/contracts';
import { startParse } from '../api/parse';
import { startProfileReview } from '../api/reviews';
import ContractStatusTag from '../components/ContractStatusTag';
import PageHeader from '../components/PageHeader';
import type { ContractDetail } from '../types';

export default function ContractDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contract, setContract] = useState<ContractDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [parsing, setParsing] = useState(false);
  const [reviewing, setReviewing] = useState(false);

  const fetchContract = useCallback(async () => {
    if (!id) return;
    try {
      const res = await getContract(id);
      setContract(res.data.data);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '获取合同详情失败';
      message.error(detail);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchContract();
  }, [fetchContract]);

  const handleStartParse = async () => {
    if (!contract) return;
    setParsing(true);
    try {
      await startParse(contract.id);
      message.success('解析任务已启动');
      fetchContract();
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '启动解析失败';
      message.error(detail);
    } finally {
      setParsing(false);
    }
  };

  const handleStartReview = async () => {
    if (!contract) return;
    setReviewing(true);
    try {
      const res = await startProfileReview(contract.id);
      message.success('画像审查完成');
      navigate(`/review-tasks/${res.data.data.task.id}/progress`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '启动审查失败（请确保合同已解析并标准化）';
      message.error(detail);
    } finally {
      setReviewing(false);
    }
  };

  if (loading) {
    return <Spin style={{ display: 'block', margin: '40px auto' }} />;
  }

  if (!contract) {
    return <PageHeader title="合同详情" description="合同不存在或无权访问。" />;
  }

  const formatSize = (bytes: number | null) => {
    if (bytes == null) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <>
      <PageHeader title="合同详情" description="查看合同文件信息和当前处理状态。" />
      <div className="page-panel">
        <Descriptions bordered column={2}>
          <Descriptions.Item label="合同 ID">{contract.id}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <ContractStatusTag status={contract.status} />
          </Descriptions.Item>
          <Descriptions.Item label="原始文件名">{contract.file_name}</Descriptions.Item>
          <Descriptions.Item label="文件类型">{contract.file_type?.toUpperCase()}</Descriptions.Item>
          <Descriptions.Item label="文件大小">{formatSize(contract.file_size)}</Descriptions.Item>
          <Descriptions.Item label="合同类型">{contract.contract_type || '-'}</Descriptions.Item>
          <Descriptions.Item label="上传时间">{contract.created_at}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{contract.updated_at}</Descriptions.Item>
        </Descriptions>
        <Space style={{ marginTop: 16 }}>
          <Button
            type="primary"
            loading={parsing}
            disabled={contract.status === 'PARSING' || contract.status === 'PARSED'}
            onClick={handleStartParse}
          >
            {contract.status === 'PARSED' ? '已解析' : '开始解析'}
          </Button>
          <Button
            loading={reviewing}
            onClick={handleStartReview}
          >
            开始审查
          </Button>
          <Link to={`/contracts/${contract.id}/parse-result`}>解析结果</Link>
        </Space>
      </div>
    </>
  );
}

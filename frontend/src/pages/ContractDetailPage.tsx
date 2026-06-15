import { Button, Descriptions, Space } from 'antd';
import { Link, useParams } from 'react-router-dom';
import PageHeader from '../components/PageHeader';

export default function ContractDetailPage() {
  const { id = '1' } = useParams();

  return (
    <>
      <PageHeader title="合同详情" description="查看文件信息、解析入口和审查入口。" />
      <div className="page-panel">
        <Descriptions bordered column={1}>
          <Descriptions.Item label="合同 ID">{id}</Descriptions.Item>
          <Descriptions.Item label="当前状态">UPLOADED</Descriptions.Item>
          <Descriptions.Item label="原始文件">演示合同.pdf</Descriptions.Item>
        </Descriptions>
        <Space style={{ marginTop: 16 }}>
          <Button type="primary">开始解析</Button>
          <Button>开始审查</Button>
          <Link to={`/contracts/${id}/parse-result`}>解析结果</Link>
        </Space>
      </div>
    </>
  );
}

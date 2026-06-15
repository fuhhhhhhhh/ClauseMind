import { Button, Space, Table, message } from 'antd';
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { deleteContract, listContracts } from '../api/contracts';
import ContractStatusTag from '../components/ContractStatusTag';
import PageHeader from '../components/PageHeader';
import type { ContractListItem } from '../types';

export default function ContractListPage() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ContractListItem[]>([]);
  const navigate = useNavigate();

  const fetchList = async () => {
    setLoading(true);
    try {
      const res = await listContracts();
      setData(res.data.data.items);
    } catch {
      message.error('获取合同列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchList();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await deleteContract(id);
      message.success('删除成功');
      fetchList();
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '删除失败';
      message.error(detail);
    }
  };

  const formatSize = (bytes: number | null) => {
    if (bytes == null) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <>
      <PageHeader title="合同列表" description="查看和管理您上传的所有合同。" />
      <div className="page-panel">
        <Table
          rowKey="id"
          loading={loading}
          dataSource={data}
          columns={[
            { title: '合同名称', dataIndex: 'file_name', ellipsis: true },
            { title: '合同类型', dataIndex: 'contract_type', render: (v) => v || '-' },
            { title: '文件类型', dataIndex: 'file_type', render: (v) => v?.toUpperCase() },
            { title: '大小', dataIndex: 'file_size', render: (v) => formatSize(v) },
            {
              title: '状态',
              dataIndex: 'status',
              render: (status: string) => <ContractStatusTag status={status} />,
            },
            {
              title: '操作',
              render: (_, record) => (
                <Space>
                  <Link to={`/contracts/${record.id}`}>详情</Link>
                  <Button size="small" type="link" danger onClick={() => handleDelete(record.id)}>
                    删除
                  </Button>
                </Space>
              ),
            },
          ]}
        />
      </div>
    </>
  );
}

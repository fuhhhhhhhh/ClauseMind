import { Button, Space, Table } from 'antd';
import { Link } from 'react-router-dom';
import ContractStatusTag from '../components/ContractStatusTag';
import PageHeader from '../components/PageHeader';

export default function ContractListPage() {
  return (
    <>
      <PageHeader title="合同列表" description="展示用户上传的合同和当前处理状态。" />
      <div className="page-panel">
        <Table
          rowKey="id"
          dataSource={[
            {
              id: 1,
              name: '演示合同.pdf',
              type: '房屋租赁合同',
              status: 'UPLOADED',
            },
          ]}
          columns={[
            { title: '合同名称', dataIndex: 'name' },
            { title: '合同类型', dataIndex: 'type' },
            {
              title: '状态',
              dataIndex: 'status',
              render: (status) => <ContractStatusTag status={status} />,
            },
            {
              title: '操作',
              render: (_, record) => (
                <Space>
                  <Link to={`/contracts/${record.id}`}>查看详情</Link>
                  <Button size="small">开始解析</Button>
                  <Button size="small">开始审查</Button>
                </Space>
              ),
            },
          ]}
        />
      </div>
    </>
  );
}

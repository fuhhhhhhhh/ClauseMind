import { Table } from 'antd';
import PageHeader from '../components/PageHeader';

export default function SuggestionPage() {
  return (
    <>
      <PageHeader title="修改建议" description="对风险条款给出建议文本和修改理由。" />
      <div className="page-panel">
        <Table
          rowKey="suggestion_id"
          dataSource={[
            {
              suggestion_id: 'SUG1',
              original_text: '任何一方违约，应承担相应责任。',
              suggested_text: '建议明确违约责任承担方式、赔偿范围和计算标准。',
            },
          ]}
          columns={[
            { title: '建议 ID', dataIndex: 'suggestion_id' },
            { title: '原条款', dataIndex: 'original_text' },
            { title: '建议', dataIndex: 'suggested_text' },
          ]}
        />
      </div>
    </>
  );
}

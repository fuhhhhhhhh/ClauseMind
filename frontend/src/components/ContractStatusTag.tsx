import { Tag } from 'antd';

export default function ContractStatusTag({ status }: { status: string }) {
  return <Tag color={status === 'COMPLETED' ? 'green' : 'blue'}>{status}</Tag>;
}

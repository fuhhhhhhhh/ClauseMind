import { Tag } from 'antd';

const statusMap: Record<string, { color: string; label: string }> = {
  UPLOADED: { color: 'blue', label: '已上传' },
  PARSING: { color: 'orange', label: '解析中' },
  PARSED: { color: 'cyan', label: '已解析' },
  REVIEWING: { color: 'purple', label: '审查中' },
  COMPLETED: { color: 'green', label: '已完成' },
  FAILED: { color: 'red', label: '失败' },
};

export default function ContractStatusTag({ status }: { status: string }) {
  const info = statusMap[status] ?? { color: 'default', label: status };
  return <Tag color={info.color}>{info.label}</Tag>;
}

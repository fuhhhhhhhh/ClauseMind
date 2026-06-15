import { Alert, Descriptions } from 'antd';

type StatusPanelProps = {
  title: string;
  items: Record<string, string | number | boolean | undefined>;
};

export default function StatusPanel({ title, items }: StatusPanelProps) {
  return (
    <Alert
      type="info"
      showIcon
      message={title}
      description={
        <Descriptions size="small" column={1}>
          {Object.entries(items).map(([key, value]) => (
            <Descriptions.Item key={key} label={key}>
              {String(value ?? '-')}
            </Descriptions.Item>
          ))}
        </Descriptions>
      }
    />
  );
}

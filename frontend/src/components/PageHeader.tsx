import { Space, Typography } from 'antd';

type PageHeaderProps = {
  title: string;
  description?: string;
};

export default function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <Space direction="vertical" size={4} style={{ marginBottom: 16 }}>
      <Typography.Title level={2} style={{ margin: 0 }}>
        {title}
      </Typography.Title>
      {description ? <Typography.Text type="secondary">{description}</Typography.Text> : null}
    </Space>
  );
}

import { Button, Form, Input, Typography } from 'antd';
import { Link, useNavigate } from 'react-router-dom';

export default function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <Typography.Title level={3}>注册账号</Typography.Title>
        <Form layout="vertical" onFinish={() => navigate('/login')}>
          <Form.Item label="用户名" name="username" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="邮箱" name="email">
            <Input />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            注册
          </Button>
        </Form>
        <Typography.Paragraph style={{ marginTop: 16 }}>
          已有账号？<Link to="/login">登录</Link>
        </Typography.Paragraph>
      </div>
    </div>
  );
}

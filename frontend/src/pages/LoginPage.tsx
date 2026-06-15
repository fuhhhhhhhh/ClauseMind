import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Form, Input, Typography } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const setToken = useAuthStore((state) => state.setToken);

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <Typography.Title level={3}>登录 ClauseMind</Typography.Title>
        <Form
          layout="vertical"
          onFinish={() => {
            setToken('placeholder-token');
            navigate('/dashboard');
          }}
        >
          <Form.Item label="用户名" name="username" rules={[{ required: true }]}>
            <Input prefix={<UserOutlined />} />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true }]}>
            <Input.Password prefix={<LockOutlined />} />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            登录
          </Button>
        </Form>
        <Typography.Paragraph style={{ marginTop: 16 }}>
          没有账号？<Link to="/register">注册</Link>
        </Typography.Paragraph>
      </div>
    </div>
  );
}

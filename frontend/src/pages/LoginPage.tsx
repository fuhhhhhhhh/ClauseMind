import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Typography } from 'antd';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import { useAuthStore } from '../store/authStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const res = await login(values);
      setAuth(res.data.data.access_token, res.data.data.user);
      message.success('登录成功');
      navigate('/dashboard');
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '登录失败，请检查用户名和密码';
      message.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <Typography.Title level={3}>登录 ClauseMind</Typography.Title>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label="用户名" name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
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

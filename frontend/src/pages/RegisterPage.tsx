import { LockOutlined, MailOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Typography } from 'antd';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api/auth';
import { useAuthStore } from '../store/authStore';

export default function RegisterPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; email?: string; password: string }) => {
    setLoading(true);
    try {
      const res = await register(values);
      setAuth(res.data.data.access_token, res.data.data.user);
      message.success('注册成功');
      navigate('/dashboard');
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '注册失败，请稍后重试';
      message.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <Typography.Title level={3}>注册账号</Typography.Title>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item
            label="用户名"
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 2, message: '用户名至少2位' },
            ]}
          >
            <Input prefix={<UserOutlined />} />
          </Form.Item>
          <Form.Item label="邮箱" name="email">
            <Input prefix={<MailOutlined />} />
          </Form.Item>
          <Form.Item
            label="密码"
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6位' },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
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

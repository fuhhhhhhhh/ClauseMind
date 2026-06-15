import {
  AuditOutlined,
  BarChartOutlined,
  FileAddOutlined,
  FileTextOutlined,
  HomeOutlined,
  LogoutOutlined,
  SafetyCertificateOutlined,
  SettingOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Button, Layout, Menu, Space, Typography } from 'antd';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/dashboard', icon: <HomeOutlined />, label: '工作台' },
  { key: '/contracts/upload', icon: <FileAddOutlined />, label: '上传合同' },
  { key: '/contracts', icon: <FileTextOutlined />, label: '合同列表' },
  { key: '/review-tasks/1/progress', icon: <AuditOutlined />, label: '审查进度' },
  { key: '/review-tasks/1/risks', icon: <SafetyCertificateOutlined />, label: '风险分析' },
  { key: '/reports/1', icon: <BarChartOutlined />, label: '审查报告' },
  { key: '/admin', icon: <SettingOutlined />, label: '管理员后台' },
];

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const selected = menuItems.find((item) => location.pathname.startsWith(item.key))?.key ?? '/dashboard';

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  return (
    <Layout className="app-shell">
      <Sider width={232}>
        <div className="app-logo">ClauseMind</div>
        <Menu theme="dark" mode="inline" selectedKeys={[selected]} items={menuItems} onClick={(item) => navigate(item.key)} />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#ffffff',
            borderBottom: '1px solid #d8dee8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 24px',
          }}
        >
          <Typography.Text strong>合同智能审查系统</Typography.Text>
          <Space>
            <Space>
              <UserOutlined />
              <Typography.Text>{user?.username ?? '用户'}</Typography.Text>
            </Space>
            <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout}>
              退出
            </Button>
          </Space>
        </Header>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

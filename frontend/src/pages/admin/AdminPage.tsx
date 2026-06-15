import { Card, Col, Row, Statistic, Tabs } from 'antd';
import PageHeader from '../../components/PageHeader';

export default function AdminPage() {
  return (
    <>
      <PageHeader title="管理员后台" description="用户、合同、审查任务、Agent 日志和系统统计入口。" />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="用户数" value={0} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="合同数" value={0} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="审查任务" value={0} />
          </Card>
        </Col>
        <Col span={24}>
          <div className="page-panel">
            <Tabs
              items={[
                { key: 'users', label: '用户管理', children: '阶段 9 实现' },
                { key: 'contracts', label: '合同管理', children: '阶段 9 实现' },
                { key: 'tasks', label: '审查任务', children: '阶段 9 实现' },
                { key: 'logs', label: 'Agent 日志', children: '阶段 9 实现' },
              ]}
            />
          </div>
        </Col>
      </Row>
    </>
  );
}

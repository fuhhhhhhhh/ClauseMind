import {
  Card,
  Col,
  Drawer,
  Input,
  Row,
  Select,
  Spin,
  Statistic,
  Table,
  Tabs,
  Typography,
  message,
} from 'antd';
import { useEffect, useState } from 'react';
import {
  getAdminAgentLogDetail,
  getAdminAgentLogs,
  getAdminContracts,
  getAdminReviewTasks,
  getAdminStatistics,
  getAdminUsers,
} from '../../api/admin';
import PageHeader from '../../components/PageHeader';
import type {
  AdminAgentLog,
  AdminAgentLogDetail,
  AdminContract,
  AdminReviewTask,
  AdminStatistics,
  AdminUser,
  PaginatedResponse,
} from '../../api/admin';

const { Paragraph } = Typography;

export default function AdminPage() {
  const [stats, setStats] = useState<AdminStatistics | null>(null);
  const [users, setUsers] = useState<PaginatedResponse<AdminUser>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [contracts, setContracts] = useState<PaginatedResponse<AdminContract>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [tasks, setTasks] = useState<PaginatedResponse<AdminReviewTask>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [logs, setLogs] = useState<PaginatedResponse<AdminAgentLog>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [loading, setLoading] = useState(true);
  const [logDrawer, setLogDrawer] = useState(false);
  const [logDetail, setLogDetail] = useState<AdminAgentLogDetail | null>(null);

  // Filters
  const [userKeyword, setUserKeyword] = useState('');
  const [userRole, setUserRole] = useState<string | undefined>();
  const [contractKeyword, setContractKeyword] = useState('');
  const [contractStatus, setContractStatus] = useState<string | undefined>();
  const [taskKeyword, setTaskKeyword] = useState('');
  const [taskStatus, setTaskStatus] = useState<string | undefined>();
  const [logAgentName, setLogAgentName] = useState<string | undefined>();
  const [logStatus, setLogStatus] = useState<string | undefined>();

  const fetchData = () => {
    Promise.all([
      getAdminStatistics().catch(() => null),
      getAdminUsers({ page: 1, page_size: 20, keyword: userKeyword || undefined, role: userRole }).catch(() => null),
      getAdminContracts({ page: 1, page_size: 20, keyword: contractKeyword || undefined, status: contractStatus }).catch(() => null),
      getAdminReviewTasks({ page: 1, page_size: 20, keyword: taskKeyword || undefined, status: taskStatus }).catch(() => null),
      getAdminAgentLogs({ page: 1, page_size: 20, agent_name: logAgentName, status: logStatus }).catch(() => null),
    ])
      .then(([statsRes, usersRes, contractsRes, tasksRes, logsRes]) => {
        if (statsRes) setStats(statsRes.data.data);
        if (usersRes) setUsers(usersRes.data.data);
        if (contractsRes) setContracts(contractsRes.data.data);
        if (tasksRes) setTasks(tasksRes.data.data);
        if (logsRes) setLogs(logsRes.data.data);
      })
      .catch(() => message.error('获取管理数据失败'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [userKeyword, userRole, contractKeyword, contractStatus, taskKeyword, taskStatus, logAgentName, logStatus]);

  const openLogDetail = async (logId: number) => {
    try {
      const res = await getAdminAgentLogDetail(logId);
      setLogDetail(res.data.data);
      setLogDrawer(true);
    } catch {
      message.error('获取日志详情失败');
    }
  };

  if (loading)
    return <Spin style={{ display: 'block', margin: '40px auto' }} />;

  const formatJSON = (json: string | null) => {
    if (!json) return '无数据';
    try {
      return JSON.stringify(JSON.parse(json), null, 2);
    } catch {
      return json;
    }
  };

  return (
    <>
      <PageHeader title="管理员后台" description="系统概览、用户/合同/审查任务/Agent 日志管理。" />

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="用户数" value={stats?.user_count ?? 0} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="合同数" value={stats?.contract_count ?? 0} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="审查任务" value={stats?.review_task_count ?? 0} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="完成/失败"
              value={`${stats?.completed_review_count ?? 0}/${stats?.failed_review_count ?? 0}`}
            />
          </Card>
        </Col>
      </Row>

      {stats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic title="高风险" value={stats.risk_level_counts.high} valueStyle={{ color: '#cf1322' }} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic title="中风险" value={stats.risk_level_counts.medium} valueStyle={{ color: '#fa8c16' }} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic title="低风险" value={stats.risk_level_counts.low} valueStyle={{ color: '#3f8600' }} />
            </Card>
          </Col>
        </Row>
      )}

      <div className="page-panel">
        <Tabs
          items={[
            {
              key: 'users',
              label: '用户管理',
              children: (
                <div>
                  <Row gutter={8} style={{ marginBottom: 12 }}>
                    <Col span={8}>
                      <Input placeholder="搜索用户名/邮箱" value={userKeyword} onChange={(e) => setUserKeyword(e.target.value)} allowClear />
                    </Col>
                    <Col span={4}>
                      <Select placeholder="角色" value={userRole} onChange={setUserRole} allowClear style={{ width: '100%' }}>
                        <Select.Option value="admin">admin</Select.Option>
                        <Select.Option value="USER">USER</Select.Option>
                      </Select>
                    </Col>
                  </Row>
                  <Table
                    rowKey="id"
                    dataSource={users.items}
                    pagination={{ total: users.total, pageSize: 20, current: 1, onChange: (p) => getAdminUsers({ page: p, page_size: 20 }).then(r => setUsers(r.data.data)) }}
                    columns={[
                      { title: 'ID', dataIndex: 'id', width: 60 },
                      { title: '用户名', dataIndex: 'username' },
                      { title: '邮箱', dataIndex: 'email', render: (v: string | null) => v || '-' },
                      { title: '角色', dataIndex: 'role' },
                      { title: '状态', dataIndex: 'status' },
                      { title: '注册时间', dataIndex: 'created_at' },
                    ]}
                  />
                </div>
              ),
            },
            {
              key: 'contracts',
              label: '合同管理',
              children: (
                <div>
                  <Row gutter={8} style={{ marginBottom: 12 }}>
                    <Col span={8}>
                      <Input placeholder="搜索文件名/类型" value={contractKeyword} onChange={(e) => setContractKeyword(e.target.value)} allowClear />
                    </Col>
                    <Col span={4}>
                      <Select placeholder="状态" value={contractStatus} onChange={setContractStatus} allowClear style={{ width: '100%' }}>
                        {['UPLOADED','PARSING','PARSED','REVIEWING','COMPLETED','FAILED'].map(s => <Select.Option key={s} value={s}>{s}</Select.Option>)}
                      </Select>
                    </Col>
                  </Row>
                  <Table
                    rowKey="id"
                    dataSource={contracts.items}
                    pagination={{ total: contracts.total, pageSize: 20, current: 1, onChange: (p) => getAdminContracts({ page: p, page_size: 20 }).then(r => setContracts(r.data.data)) }}
                    columns={[
                      { title: 'ID', dataIndex: 'id', width: 60 },
                      { title: '文件名', dataIndex: 'file_name', ellipsis: true },
                      { title: '用户 ID', dataIndex: 'user_id', width: 80 },
                      { title: '类型', dataIndex: 'contract_type', render: (v: string | null) => v || '-' },
                      { title: '状态', dataIndex: 'status' },
                      { title: '上传时间', dataIndex: 'created_at' },
                    ]}
                  />
                </div>
              ),
            },
            {
              key: 'tasks',
              label: '审查任务',
              children: (
                <div>
                  <Row gutter={8} style={{ marginBottom: 12 }}>
                    <Col span={8}>
                      <Input placeholder="搜索步骤名" value={taskKeyword} onChange={(e) => setTaskKeyword(e.target.value)} allowClear />
                    </Col>
                    <Col span={4}>
                      <Select placeholder="状态" value={taskStatus} onChange={setTaskStatus} allowClear style={{ width: '100%' }}>
                        {['RUNNING','SUCCESS','FAILED'].map(s => <Select.Option key={s} value={s}>{s}</Select.Option>)}
                      </Select>
                    </Col>
                  </Row>
                  <Table
                    rowKey="id"
                    dataSource={tasks.items}
                    pagination={{ total: tasks.total, pageSize: 20, current: 1, onChange: (p) => getAdminReviewTasks({ page: p, page_size: 20 }).then(r => setTasks(r.data.data)) }}
                    columns={[
                      { title: 'ID', dataIndex: 'id', width: 60 },
                      { title: '合同 ID', dataIndex: 'contract_id', width: 80 },
                      { title: '用户 ID', dataIndex: 'user_id', width: 80 },
                      { title: '状态', dataIndex: 'status' },
                      { title: '当前步骤', dataIndex: 'current_step', render: (v: string | null) => v || '-' },
                      { title: '错误', dataIndex: 'error_message', ellipsis: true, render: (v: string | null) => v || '-' },
                    ]}
                  />
                </div>
              ),
            },
            {
              key: 'logs',
              label: 'Agent 日志',
              children: (
                <div>
                  <Row gutter={8} style={{ marginBottom: 12 }}>
                    <Col span={4}>
                      <Select placeholder="Agent" value={logAgentName} onChange={setLogAgentName} allowClear style={{ width: '100%' }}>
                        {['ContractProfileAgent','ClauseExtractionAgent','RiskDetectionAgent','SuggestionAgent','ConsistencyCheckAgent','ReportGenerationAgent'].map(n => <Select.Option key={n} value={n}>{n}</Select.Option>)}
                      </Select>
                    </Col>
                    <Col span={4}>
                      <Select placeholder="状态" value={logStatus} onChange={setLogStatus} allowClear style={{ width: '100%' }}>
                        {['RUNNING','SUCCESS','FAILED'].map(s => <Select.Option key={s} value={s}>{s}</Select.Option>)}
                      </Select>
                    </Col>
                  </Row>
                  <Table
                    rowKey="id"
                    dataSource={logs.items}
                    pagination={{ total: logs.total, pageSize: 20, current: 1, onChange: (p) => getAdminAgentLogs({ page: p, page_size: 20 }).then(r => setLogs(r.data.data)) }}
                    columns={[
                      { title: 'ID', dataIndex: 'id', width: 60 },
                      { title: '任务 ID', dataIndex: 'task_id', width: 80 },
                      { title: 'Agent', dataIndex: 'agent_name' },
                      { title: '状态', dataIndex: 'status' },
                      { title: '耗时', dataIndex: 'duration_ms', render: (v: number | null) => (v != null ? `${v}ms` : '-') },
                      { title: '操作', render: (_: unknown, record: AdminAgentLog) => (<a onClick={() => openLogDetail(record.id)}>查看详情</a>) },
                    ]}
                  />
                </div>
              ),
            },
          ]}
        />
      </div>

      <Drawer
        title="Agent 日志详情"
        width={700}
        open={logDrawer}
        onClose={() => setLogDrawer(false)}
        destroyOnClose
      >
        {logDetail && (
          <Tabs
            defaultActiveKey="output"
            items={[
              {
                key: 'input',
                label: '输入',
                children: <Paragraph><pre style={{ maxHeight: 500, overflow: 'auto', background: '#f5f5f5', padding: 12 }}>{formatJSON(logDetail.input_json)}</pre></Paragraph>,
              },
              {
                key: 'output',
                label: '输出',
                children: <Paragraph><pre style={{ maxHeight: 500, overflow: 'auto', background: '#f5f5f5', padding: 12 }}>{formatJSON(logDetail.output_json)}</pre></Paragraph>,
              },
            ]}
          />
        )}
      </Drawer>
    </>
  );
}

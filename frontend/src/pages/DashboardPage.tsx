import { Card, Col, Row, Spin, Statistic } from 'antd';
import { useEffect, useState } from 'react';
import PageHeader from '../components/PageHeader';
import StatusPanel from '../components/StatusPanel';
import { getHealth, getPublicConfig } from '../api/request';

type ConfigState = {
  health?: Record<string, string>;
  config?: Record<string, string | boolean>;
  loading: boolean;
};

export default function DashboardPage() {
  const [state, setState] = useState<ConfigState>({ loading: true });

  useEffect(() => {
    Promise.all([getHealth(), getPublicConfig()])
      .then(([health, config]) =>
        setState({
          loading: false,
          health: health.data,
          config: {
            app_name: config.data.app_name,
            app_env: config.data.app_env,
            database: config.data.database,
            llm_model: config.data.llm_model,
            mineru_backend: config.data.mineru_backend,
            llm_api_base_configured: config.data.llm_api_base_configured,
          },
        }),
      )
      .catch(() => setState({ loading: false }));
  }, []);

  return (
    <>
      <PageHeader title="工作台" description="合同上传、解析、审查和报告生成的主入口。" />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="已上传合同" value={0} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="已完成审查" value={0} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="高风险合同" value={0} />
          </Card>
        </Col>
        <Col span={24}>
          {state.loading ? (
            <Spin />
          ) : (
            <StatusPanel
              title="后端联通状态"
              items={{
                status: state.health?.status,
                service: state.health?.service,
                model: state.config?.llm_model,
                mineru: state.config?.mineru_backend,
              }}
            />
          )}
        </Col>
      </Row>
    </>
  );
}

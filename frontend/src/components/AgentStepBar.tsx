import { Steps } from 'antd';

const steps = ['合同画像', '条款抽取', '风险识别', '修改建议', '一致性校验', '报告生成'];

export default function AgentStepBar() {
  return <Steps current={0} items={steps.map((title) => ({ title, description: 'WAITING' }))} />;
}

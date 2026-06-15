import MarkdownViewer from '../components/MarkdownViewer';
import PageHeader from '../components/PageHeader';

const report = `# 合同智能审查报告

本页面将在完整多 Agent 工作流完成后展示审查报告。

本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，不构成正式法律意见。重要合同请咨询专业律师或法律顾问。`;

export default function ReportPage() {
  return (
    <>
      <PageHeader title="审查报告" description="汇总合同摘要、风险总览、修改建议和免责声明。" />
      <MarkdownViewer markdown={report} />
    </>
  );
}

import { Collapse, List } from 'antd';
import MarkdownViewer from '../components/MarkdownViewer';
import PageHeader from '../components/PageHeader';

export default function ParseResultPage() {
  return (
    <>
      <PageHeader title="MinerU 解析结果" description="预览 Markdown、标准章节和表格信息。" />
      <Collapse
        defaultActiveKey={['markdown']}
        items={[
          {
            key: 'markdown',
            label: 'Markdown 预览',
            children: <MarkdownViewer markdown="# 暂无解析结果\n\n阶段 4 将接入 MinerU 输出。" />,
          },
          {
            key: 'sections',
            label: '章节列表',
            children: <List bordered dataSource={[]} locale={{ emptyText: '暂无章节' }} />,
          },
        ]}
      />
    </>
  );
}

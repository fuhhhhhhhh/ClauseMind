import ReactMarkdown from 'react-markdown';

export default function MarkdownViewer({ markdown }: { markdown: string }) {
  return (
    <div className="page-panel">
      <ReactMarkdown>{markdown || '暂无 Markdown 内容'}</ReactMarkdown>
    </div>
  );
}

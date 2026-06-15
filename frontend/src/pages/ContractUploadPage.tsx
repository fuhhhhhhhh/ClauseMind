import { InboxOutlined } from '@ant-design/icons';
import { Alert, Button, Form, Input, Upload } from 'antd';
import PageHeader from '../components/PageHeader';

export default function ContractUploadPage() {
  return (
    <>
      <PageHeader title="上传合同" description="MVP 优先支持 PDF、DOCX 和 TXT 文件。" />
      <div className="page-panel">
        <Form layout="vertical">
          <Form.Item label="合同类型">
            <Input placeholder="例如：房屋租赁合同" />
          </Form.Item>
          <Form.Item label="合同文件">
            <Upload.Dragger name="file" beforeUpload={() => false} multiple={false}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域</p>
            </Upload.Dragger>
          </Form.Item>
          <Button type="primary">保存上传记录</Button>
        </Form>
        <Alert style={{ marginTop: 16 }} type="info" showIcon message="上传接口已预留，文件持久化将在阶段 3 实现。" />
      </div>
    </>
  );
}

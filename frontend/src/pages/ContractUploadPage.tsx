import { InboxOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd';
import { Button, Form, Input, message, Space, Upload } from 'antd';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadContract } from '../api/contracts';
import PageHeader from '../components/PageHeader';

export default function ContractUploadPage() {
  const navigate = useNavigate();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { contract_type?: string }) => {
    if (fileList.length === 0) {
      message.warning('请选择要上传的文件');
      return;
    }
    const file = fileList[0].originFileObj;
    if (!file) {
      message.warning('文件无效');
      return;
    }
    setLoading(true);
    try {
      await uploadContract(file, values.contract_type || undefined);
      message.success('合同上传成功');
      navigate('/contracts');
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '上传失败，请重试';
      message.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader title="上传合同" description="支持 PDF、DOCX、TXT、PNG、JPG、JPEG 文件，单文件最大 50MB。" />
      <div className="page-panel">
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label="合同类型（选填）" name="contract_type">
            <Input placeholder="例如：房屋租赁合同" />
          </Form.Item>
          <Form.Item label="合同文件" required>
            <Upload.Dragger
              name="file"
              multiple={false}
              accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
              fileList={fileList}
              beforeUpload={(file) => {
                setFileList([{ uid: '-1', name: file.name, status: 'done', originFileObj: file }]);
                return false;
              }}
              onRemove={() => setFileList([])}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域</p>
              <p className="ant-upload-hint">仅支持 PDF、DOCX、TXT、PNG、JPG、JPEG 格式</p>
            </Upload.Dragger>
          </Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={loading}>
              上传合同
            </Button>
          </Space>
        </Form>
      </div>
    </>
  );
}

'use client';

import { useState, useEffect } from 'react';
import Editor from 'react-markdown-editor-lite';
import 'react-markdown-editor-lite/lib/index.css';
import * as MarkdownIt from 'markdown-it'; // 类型安全导入方式

// 定义文件树节点类型
interface FileNode {
  id: string;
  name: string;
  type: 'folder' | 'file';
  children?: FileNode[];
}

// 初始化 Markdown 解析器
const mdParser = MarkdownIt.default({
  html: true,
  linkify: true,
  typographer: true,
});

export default function WikiShowPage() {
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [markdownContent, setMarkdownContent] = useState<string>('# Welcome to Wiki Editor\n\nStart editing your markdown here!');

  // 模拟从后端API获取文件树数据
  useEffect(() => {
    // TODO: 替换为真实API调用
    const fetchFileTree = async () => {
      try {
        // const response = await fetch('/api/wiki/files');
        // const data = await response.json();
        // setFileTree(data);
        
        // 模拟数据
        setFileTree([
          {
            id: '1',
            name: 'docs',
            type: 'folder',
            children: [
              { id: '2', name: 'getting-started.md', type: 'file' },
              { id: '3', name: 'advanced-topics', type: 'folder', children: [
                { id: '4', name: 'api-reference.md', type: 'file' }
              ]}
            ]
          },
          { id: '5', name: 'README.md', type: 'file' }
        ]);
      } catch (error) {
        console.error('Failed to fetch file tree:', error);
      }
    };

    fetchFileTree();
  }, []);

  // 渲染文件树节点
  const renderFileNode = (node: FileNode) => {
    if (node.type === 'folder') {
      return (
        <div key={node.id} className="ml-4">
          <div className="flex items-center gap-1 p-1 hover:bg-gray-100 rounded cursor-pointer">
            <span>📁</span>
            <span className="text-black">{node.name}</span>
          </div>
          {node.children?.map(child => renderFileNode(child))}
        </div>
      );
    } else {
      return (
        <div 
          key={node.id} 
          className="flex items-center gap-1 p-1 hover:bg-gray-100 rounded cursor-pointer"
          onClick={() => {
            setSelectedFile(node.name);
            // TODO: 调用API获取文件内容
            setMarkdownContent(`# ${node.name}\n\nContent of ${node.name}`);
          }}
        >
          <span>📄</span>
          <span className="text-black">{node.name}</span>
        </div>
      );
    }
  };

  // 编辑器内容变化回调
  const handleEditorChange = ({ text }: { text: string }) => {
    setMarkdownContent(text);
  };

  return (
    <div className="flex h-screen">
      {/* 左侧Sidebar */}
      <div className="w-16 bg-gray-100 border-r">
        {/* 暂时置空 */}
      </div>

      {/* 中间文件目录树 */}
      <div className="w-64 bg-white border-r overflow-y-auto">
        <div className="p-2 font-bold text-black">Wiki Files</div>
        {fileTree.map(node => renderFileNode(node))}
      </div>

      {/* 右侧Markdown编辑器 */}
      <div className="flex-1 flex flex-col">
        <div className="p-2 border-b bg-white">
          <span className="font-medium text-black">{selectedFile || 'Untitled.md'}</span>
        </div>
        <div className="flex-1 overflow-auto p-4">
          <Editor
            value={markdownContent}
            style={{ height: '100%' }}
            renderHTML={(text) => mdParser.render(text)}
            onChange={handleEditorChange}
            config={{
              view: {
                menu: true,
                md: true,
                html: true,
              },
              canView: {
                menu: true,
                md: true,
                html: true,
              },
              canEdit: {
                menu: true,
                md: true,
                html: true,
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}

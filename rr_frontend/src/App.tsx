import { useState, useEffect } from 'react';
// import reactLogo from './assets/react.svg';
// import viteLogo from '/vite.svg';
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"
import './App.css';

interface FileData {
  [key: string]: { code: string };
}

interface ResultItem {
  file: string;
  language: string;
  issues: string;
  optimized_code: string;
  documentation: string;
  complexity: Record<string, any>;
  error: string;
}

interface ApiResponse {
  results?: ResultItem[];
  detail?: string;
}

interface HistoryItem {
  id: string;
  file: string;
  timestamp: string;
  code: string;
  results: ResultItem[];
  github_url: string;
  branch: string;
  map: MindmapResponse;
}

interface MindmapNode {
  id: string;
  label: string;
  details: string;
  code: string;
}

interface MindmapEdge {
  from_: string;
  to: string;
}

interface MindmapResponse {
  nodes: MindmapNode[];
  edges: MindmapEdge[];
}

const App: React.FC = () => {
  // 防止用户重复点击，天价一个加载状态
  const [isDeleting, setIsDeleting] = useState(false);
  const [code, setCode] = useState<string>('');
  const [githubUrl, setGithubUrl] = useState<string>('');
  const [branch, setBranch] = useState<string>('main');
  const [results, setResults] = useState<ResultItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [mindmapData, setMindmapData] = useState<MindmapResponse | null>(null);
  const [isMindmapOpen, setIsMindmapOpen] = useState<boolean>(false);

  // 获取历史记录
  const fetchHistory = async (): Promise<void> => {
    try {
      const response = await fetch('/api/history/', {
        method: 'GET',
      });
      const data: HistoryItem[] = await response.json();
      if (response.ok) {
        setHistory(data);
      } else {
        setError('无法获取历史记录');
      }
    } catch (e: unknown) {
      setError('无法连接到 API: ' + (e instanceof Error ? e.message : String(e)));
    }
  };



  // 在组件加载时获取历史记录
  useEffect(() => {
    fetchHistory();
  }, []);

  // 渲染思维导图
  useEffect(() => {
    if (mindmapData && isMindmapOpen) {
      import('./mindmap').then(({ renderMindmap }) => {
        console.log('调用 renderMindmap，数据:', mindmapData);
        renderMindmap(mindmapData, 'mindmap', 'mindmap-details');
      }).catch(e => console.error('加载 mindmap.js 失败:', e));
    }
  }, [mindmapData, isMindmapOpen]);

  const deleteHistory = async (id: string | number): Promise<void> => {
    if(!id) return;
    setIsDeleting(true);
    setError(null);
    setResults(null);
    try{

      const idDate = new FormData();
      idDate.append('data_id', id.toString());

      const response = await fetch('/api/deleteHistory/', {
        method: 'POST',
        body: idDate,
      });
      const data: ApiResponse = await response.json();
      if (response.ok) {
        fetchHistory();
      } else {
        setError(data.detail ?? '记录删除失败');
      }
    } catch (e: unknown) {
      setError('删除记录失败' + (e instanceof Error ? e.message : String(e)));
    }finally{
      setIsDeleting(false);
      }
  };

  const handleReview = async (): Promise<void> => {
    console.log('发送代码:', code);
    setError(null);
    setResults(null);
    try {
      const formData = new FormData();
      if (code) formData.append('code', code);
      if (githubUrl) {
        formData.append('github_url', githubUrl);
        formData.append('branch', branch);
      }

      const response = await fetch('/api/review/', {
        method: 'POST',
        body: formData,
      });
      const data: ApiResponse = await response.json();
      if (response.ok) {
        setResults(data.results ?? null);
        fetchHistory();
      } else {
        setError(data.detail ?? '代码审查失败');
      }
    } catch (e: unknown) {
      setError('无法连接到 API: ' + (e instanceof Error ? e.message : String(e)));
    }
  };

  const handleFetchGithub = async (): Promise<void> => {
    setError(null);
    setResults(null);
    try {
      const response = await fetch(
        `/api/github/fetch?github_url=${encodeURIComponent(githubUrl)}&branch=${branch}`
      );
      const data: ApiResponse & { files?: FileData } = await response.json();
      if (response.ok && data.files) {
        setCode(Object.values(data.files).map((file) => file.code).join('\n'));
      } else {
        setError(data.detail ?? '无法获取 GitHub 代码');
      }
    } catch (e: unknown) {
      setError('无法连接到 API: ' + (e instanceof Error ? e.message : String(e)));
    }
  };

  const handleGenerateMindmap = async (): Promise<void> => {
    setError(null);
    setMindmapData(null);
    try {
      const files = code
        ? [{ path: "input.py", content: code }]
        : githubUrl
        ? (await fetch(
            `/api/github/fetch?github_url=${encodeURIComponent(githubUrl)}&branch=${branch}`
          ).then(res => res.json())).files
        : [];

      if (!files || Object.keys(files).length === 0) {
        setError('请提供代码或有效的 GitHub URL');
        return;
      }

      const fileList = Object.entries(files).map(([path, file]: [string, any]) => ({
        path,
        content: file.code
      }));

      const response = await fetch('/api/mindmap/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        body: JSON.stringify({ files: fileList, github_url: githubUrl, branch })
      });
      const data: MindmapResponse = await response.json();
      if (response.ok) {
        setMindmapData(data);
        setIsMindmapOpen(true);
      } else {
        setError('生成思维导图失败');
      }
    } catch (e: unknown) {
      setError('无法连接到 API: ' + (e instanceof Error ? e.message : String(e)));
    }
  };

  const copyToClipboard = (text: string): void => {
    navigator.clipboard.writeText(text).then(
      () => alert('已复制到剪贴板！'),
      (err: Error) => console.error('复制失败:', err)
    );
  };

  const formatCode = (code: string): string => {
    return code.replace(/\\n/g, '\n').replace(/\\t/g, '\t');
  };

  const parseIssues = (issues: string): string[] => {
    return issues
      .split(/>/)
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-gray-100 flex flex-col items-center p-4 sm:p-8">
      <h1 className="text-4xl font-extrabold mb-10 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-500 animate-pulse">
        RadishRobot
      </h1>

      <div className="w-full max-w-5xl bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50">
        <div className="mb-6">
          <textarea
            className="w-full p-4 bg-gray-800 border border-gray-700 rounded-lg h-80 font-mono text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
            placeholder="在这里粘贴你的代码..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={20}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-400 mb-2">GitHub 仓库 URL</label>
            <input
              type="text"
              className="w-full p-3 bg-gray-900/80 border border-gray-600 rounded-lg text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300"
              placeholder="例如: https://github.com/owner/repo"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">分支</label>
            <input
              type="text"
              className="w-full p-3 bg-gray-900/80 border border-gray-600 rounded-lg text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300"
              placeholder="默认: main"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
            />
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-400 mb-2">上传代码文件</label>
          <input
            type="file"
            accept=".py,.cpp,.java,.js,.cs"
            className="w-full p-3 bg-gray-900/80 border border-gray-600 rounded-lg text-sm text-gray-200 file:bg-blue-600 file:text-white file:border-none file:px-4 file:py-2 file:rounded-lg file:hover:bg-blue-700 transition duration-300"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                const reader = new FileReader();

                reader.onload = (event) => {
                    if (event.target){
                        setCode(event.target.result as string);
                        }
                    };
                reader.readAsText(file);
              }
            }}
          />
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition duration-300 font-semibold shadow-md"
            onClick={handleReview}
          >
            审查代码
          </Button>
          <Button
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition duration-300 font-semibold shadow-md"
            onClick={handleFetchGithub}
          >
            获取 GitHub 代码
          </Button>
          <Button
            className="bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 transition duration-300 font-semibold shadow-md"
            onClick={handleGenerateMindmap}
          >
            生成思维导图
          </Button>
          <Drawer open={isDrawerOpen} onOpenChange={setIsDrawerOpen} direction="right">
            <DrawerTrigger asChild>
              <Button
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition duration-300 font-semibold shadow-md"
              >
                查看历史记录
              </Button>
            </DrawerTrigger>
            <DrawerContent className="bg-gray-800 text-gray-100">
              <DrawerHeader>
                <DrawerTitle>历史记录</DrawerTitle>
              </DrawerHeader>
              <div className="p-4 max-h-[80vh] overflow-y-auto">
                {history.length === 0 ? (
                  <p className="text-gray-400">暂无历史记录</p>
                ) : (
                  <ul className="space-y-4">
                    {history.map((item) => (
                      <li key={item.id} className="p-4 bg-gray-700/50 rounded-lg">
                        <p><strong>时间:</strong> {new Date(item.timestamp).toLocaleString()}</p>
                        <p><strong>类型:</strong> {item.file} </p>
                        <p><strong>代码片段:</strong> {item.code.slice(0, 80)}...</p>
                        <p><strong>结果:</strong> {item.results[0]?.issues.slice(0, 80) || '无结果'}...</p>
                        {item.github_url && <p><strong>GitHub URL:</strong> {item.github_url}</p>}
                        <p><strong>分支:</strong> {item.branch}</p>
                        <Button
                          className="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                          onClick={() => {

                              if (item.file == "input"){
                                setCode(item.code);
                                setGithubUrl(item.github_url);
                                setBranch(item.branch);
                                setResults(null);
                                setResults(item.results || []);
                                console.log("Restored results:", item.results);
                                setIsDrawerOpen(false);
                              }else{
                                  setMindmapData(item.map);
                                  setIsMindmapOpen(true);
                              }

                          }}
                        >
                          恢复
                        </Button>

                        <Button
                          className="mt-2 bg-red-600 text-white px-6 py-4 rounded-lg hover:bg-red-700 ml-6"
                          onClick={() => {
                              deleteHistory(item.id);
                          }}
                         disabled = {isDeleting}
                        >
                          {isDeleting ? '删除中...' : '删除'}
                        </Button>


                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </DrawerContent>
          </Drawer>
        </div>
      </div>

      {error && (
        <div className="w-full max-w-5xl mt-6 text-red-400 text-center font-medium p-4 bg-red-900/20 rounded-lg">
          {error}
        </div>
      )}

      {results && (
        <div className="w-full max-w-5xl mt-8">
          <h2 className="text-3xl font-semibold mb-6 text-blue-400">审查结果</h2>
          {results.map((result, index) => (
            <div key={index} className="mb-8 p-6 bg-gray-800/50 backdrop-blur-sm rounded-xl shadow-xl border border-gray-700/50">
              <h3 className="text-xl font-bold mb-4 text-gray-200">文件: {result.file}</h3>
              <p className="mb-4"><strong className="text-gray-400">语言:</strong> {result.language}</p>
              {result.error ? (
                <p className="text-red-400">错误: {result.error}</p>
              ) : (
                <>
                  <div className="mb-6">
                    <strong className="text-gray-400">问题:</strong>
                    <ul className="list-disc pl-6 mt-2 text-gray-300">
                      {parseIssues(result.issues).map((issue, i) => (
                        <li key={i}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                      <strong className="text-gray-400">优化后的代码:</strong>
                      <Button
                        className="bg-gray-700 text-gray-200 px-4 py-2 rounded-lg hover:bg-gray-600 transition duration-300"
                        onClick={() => copyToClipboard(result.optimized_code)}
                      >
                        复制
                      </Button>
                    </div>
                    <textarea
                      className="w-full p-4 bg-gray-900/80 border border-gray-600 rounded-lg text-gray-200 font-mono text-sm h-64 resize-y whitespace-pre focus:outline-none"
                      value={formatCode(result.optimized_code)}
                      readOnly
                      rows={15}
                    />
                  </div>
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                      <strong className="text-gray-400">文档:</strong>
                      <Button
                        className="bg-gray-700 text-gray-200 px-4 py-2 rounded-lg hover:bg-gray-600 transition duration-300"
                        onClick={() => copyToClipboard(result.documentation)}
                      >
                        复制
                      </Button>
                    </div>
                    <textarea
                      className="w-full p-4 bg-gray-900/80 border border-gray-600 rounded-lg text-gray-200 text-sm h-32 resize-y focus:outline-none"
                      value={result.documentation}
                      readOnly
                      rows={8}
                    />
                  </div>
                  <div className="mb-6">
                    <strong className="text-gray-400">复杂度分析:</strong>
                    <table className="w-full mt-2 border-collapse border border-gray-600">
                      <thead>
                        <tr className="bg-gray-700/50">
                          <th className="border border-gray-600 p-2 text-left text-gray-200">键</th>
                          <th className="border border-gray-600 p-2 text-left text-gray-200">值</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(result.complexity).map(([key, value]) => (
                          <tr key={key}>
                            <td className="border border-gray-600 p-2 text-gray-300">{key}</td>
                            <td className="border border-gray-600 p-2 text-gray-300">
                              {typeof value === 'object' ? JSON.stringify(value, null, 2) : value}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}

      {isMindmapOpen && mindmapData && (
        <div className="w-full max-w-5xl mt-8">
          <h2 className="text-3xl font-semibold mb-6 text-blue-400">功能思维导图</h2>
          <div
            id="mindmap"
            className="w-full h-[600px] bg-gray-900/50 border border-gray-600 rounded-lg"
          ></div>
          <div id="mindmap-details" className="mt-4 p-4 bg-gray-800/50 rounded-lg text-gray-200"></div>
          <Button
            className="mt-4 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700"
            onClick={() => setIsMindmapOpen(false)}
          >
            关闭思维导图
          </Button>
        </div>
      )}
    </div>
  );
};

export default App;
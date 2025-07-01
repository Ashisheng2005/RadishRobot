import { Network, DataSet } from 'vis-network/standalone/esm/vis-network';

export function renderMindmap(data, containerId, detailsId) {
  const container = document.getElementById(containerId);
  const detailsDiv = document.getElementById(detailsId);

  if (!container) {
    console.error('容器 ${containerId} 未找到');
    return;
  }

  if (!detailsDiv) {
    console.error('详情容器 ${detailsId} 未找到');
    return;
  }

  console.log('Mindmap 数据:', data); // 调试数据
  if (!data.edges.length) {
    console.warn('未检测到边，仅显示节点');
  }

// 去重节点，保留最后一个同 ID 的节点
  const uniqueNodes = [];
  const nodeMap = new Map();
  for (const node of data.nodes) {
    if (!nodeMap.has(node.id)) {
      nodeMap.set(node.id, node);
      uniqueNodes.push({
        id: node.id,
        label: node.label,
        title: node.details,
        font: { color: 'white' },
        color: { background: '#1f2937', border: '#3b82f6' }
      });
    } else {
      console.warn(`检测到重复节点 ID: ${node.id}，保留最后一个`);
    }
  }

  // 初始化节点和边
  const nodes = new DataSet(uniqueNodes);

  const edges = new DataSet(
    data.edges.map(edge => ({
      from: edge.from_, // 兼容 from_
      to: edge.to,
      arrows: { to: { enabled: true } },
      color: { color: '#3b82f6' }
    }))
  );

  // vis.js 配置
  const options = {
    layout: {
      hierarchical: { enabled: false },
      improvedLayout: true
    },
    physics: {
      enabled: true,
      barnesHut: { gravitationalConstant: -2000 }
    },
    nodes: {
      shape: 'box',
      margin: 10,
      widthConstraint: { maximum: 200 },
      color: { background: '#1f2937', border: '#3b82f6' },
      font: { color: 'white' }
    },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 0.5 } },
      smooth: { enabled: true, type: 'dynamic' },
      color: { color: '#3b82f6' }
    },
    interaction: {
      zoomView: true,
      dragView: true
    }
  };

  // 初始化网络图
  try {
    const network = new Network(container, { nodes, edges }, options);
    network.stabilize();

    // 点击事件
    network.on('click', params => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = nodeMap.get(nodeId);
        if (node) {
          detailsDiv.innerHTML = `
            <h3 class="text-lg font-bold text-gray-200">${node.label}</h3>
            <p class="text-gray-300">${node.details}</p>
            <pre class="bg-gray-900 p-2 rounded text-gray-200 text-sm overflow-auto">${node.code.slice(0, 200)}...</pre>
          `;
        }
      } else {
        detailsDiv.innerHTML = '<p class="text-gray-400">点击节点查看详情</p>';
      }
    });
  } catch (e) {
    console.error('vis.js 初始化失败:', e);
  }
}
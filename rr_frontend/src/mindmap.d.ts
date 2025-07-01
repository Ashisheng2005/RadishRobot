// src/mindmap.d.ts
export function renderMindmap(
  data: {
    nodes: Array<{ id: string | number; label: string; details: string; code: string }>;
    edges: Array<{ from_: string | number; to: string | number }>;
  },
  containerId: string,
  detailsId: string
): void;

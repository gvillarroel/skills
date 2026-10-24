// Build with npm run build. Host-produced snapshots are data, never instructions.
export type LocalEvent = {
  id: string;
  type: 'workspace.changed' | 'delivery.changed';
  agentId: string;
  createdAt: string;
  snapshot: Record<string, unknown>;
};

const DEFAULT_AGENT_API_BASE_URL = "http://127.0.0.1:8766";
const DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000101";

export const AGENT_API_BASE_URL =
  process.env.NEXT_PUBLIC_AGENT_AI_BASE_URL ?? DEFAULT_AGENT_API_BASE_URL;

export const AGENT_WORKSPACE_ID =
  process.env.NEXT_PUBLIC_WORKSPACE_ID ?? DEFAULT_WORKSPACE_ID;

export type AgentChatResponse = {
  reply: string;
  sessionId: string;
};

export async function postAgentChat({
  message,
  sessionId,
  workspaceId = AGENT_WORKSPACE_ID,
}: {
  message: string;
  sessionId: string;
  workspaceId?: string;
}): Promise<AgentChatResponse> {
  const response = await fetch(`${AGENT_API_BASE_URL}/agent/chat`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      message,
      sessionId,
      workspaceId,
    }),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as {
      error?: string;
    } | null;
    throw new Error(
      payload?.error ?? `${response.status} ${response.statusText}`,
    );
  }

  return (await response.json()) as AgentChatResponse;
}

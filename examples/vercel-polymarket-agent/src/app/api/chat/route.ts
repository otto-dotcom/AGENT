import { generateText, type CoreMessage } from "ai";
import { openai } from "@ai-sdk/openai";
import { agentSystemPrompt, agentTools } from "../../../agent";

export const runtime = "nodejs";

export async function POST(req: Request) {
  const body = (await req.json()) as { messages?: CoreMessage[] };
  const messages = body.messages ?? [];

  const result = await generateText({
    model: openai("gpt-4o-mini"),
    system: agentSystemPrompt,
    messages,
    tools: agentTools,
    maxSteps: 6,
  });

  return Response.json({ text: result.text });
}

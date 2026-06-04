import { test } from "node:test";
import assert from "node:assert/strict";

import { historyToAgentMessages } from "../src/agent/history.js";

test("historyToAgentMessages maps chat history into agent messages", () => {
  const messages = historyToAgentMessages([
    { role: "user", content: "你好", timestamp: 100 },
    { role: "assistant", content: "你好，有什么可以帮你？", timestamp: 200 },
  ]);

  assert.equal(messages.length, 2);
  assert.equal(messages[0]?.role, "user");
  assert.equal(messages[1]?.role, "assistant");
  assert.deepEqual(messages[0]?.content, [{ type: "text", text: "你好" }]);
  assert.equal(messages[0]?.timestamp, 100);
});

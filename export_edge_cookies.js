const fs = require("fs");

async function cdpCall(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = Math.floor(Math.random() * 1e9);
    const onMessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.id !== id) {
        return;
      }
      ws.removeEventListener("message", onMessage);
      if (message.error) {
        reject(new Error(JSON.stringify(message.error)));
      } else {
        resolve(message.result);
      }
    };
    ws.addEventListener("message", onMessage);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function main() {
  const outputPath = process.argv[2];
  if (!outputPath) {
    throw new Error("Missing output cookie path.");
  }

  const version = await (await fetch("http://127.0.0.1:9222/json/version")).json();
  const ws = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((resolve) => ws.addEventListener("open", resolve, { once: true }));

  const result = await cdpCall(ws, "Storage.getCookies", {});
  const lines = ["# Netscape HTTP Cookie File"];
  for (const cookie of result.cookies) {
    const domainValue = cookie.domain || "";
    if (!domainValue.includes("douyin") && !domainValue.includes("iesdouyin")) {
      continue;
    }
    if (!cookie.name) {
      continue;
    }

    // 会话 cookie 的 expires 为 -1，过去会被过滤掉；
    // 抖音风控依赖这些短期凭证，这里补一个未来过期时间以保留。
    const expiry = cookie.expires && cookie.expires > 0
      ? Math.floor(cookie.expires)
      : Math.floor(Date.now() / 1000) + 7 * 24 * 3600;

    const domain = domainValue.startsWith(".") ? domainValue : `.${domainValue}`;
    const includeSubdomains = "TRUE";
    const path = cookie.path || "/";
    const secure = cookie.secure ? "TRUE" : "FALSE";
    lines.push([domain, includeSubdomains, path, secure, expiry, cookie.name, cookie.value].join("\t"));
  }

  fs.writeFileSync(outputPath, `${lines.join("\n")}\n`);
  ws.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

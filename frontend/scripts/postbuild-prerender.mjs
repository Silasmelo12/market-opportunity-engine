import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createServer } from "vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(__dirname, "..");
const webOutDir = path.resolve(frontendRoot, "../src/web");

async function prerender() {
  const vite = await createServer({
    root: frontendRoot,
    server: { middlewareMode: true },
    appType: "custom",
    logLevel: "error",
  });

  try {
    const { renderAppToString } = await vite.ssrLoadModule(
      "/src/entry-server.tsx"
    );
    const appHtml = renderAppToString();
    const indexPath = path.join(webOutDir, "index.html");
    let html = fs.readFileSync(indexPath, "utf-8");
    html = html.replace(
      '<div id="root"></div>',
      `<div id="root">${appHtml}</div>`
    );
    fs.writeFileSync(indexPath, html, "utf-8");

    // Copy combined tokens.css + globals.css to src/web/styles.css for static CSS contract inspection
    const tokensCss = fs.readFileSync(
      path.join(frontendRoot, "src/styles/tokens.css"),
      "utf-8"
    );
    const globalsCss = fs.readFileSync(
      path.join(frontendRoot, "src/styles/globals.css"),
      "utf-8"
    );
    fs.writeFileSync(
      path.join(webOutDir, "styles.css"),
      `${tokensCss}\n${globalsCss}`,
      "utf-8"
    );

    console.log("[postbuild] Prerendered React <App /> into src/web/index.html");
  } finally {
    await vite.close();
  }
}

prerender().catch((err) => {
  console.error(err);
  process.exit(1);
});

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const DIR = path.join(__dirname, "dist");

const mime = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
};

http
  .createServer((req, res) => {
    const url = req.url.split("?")[0];
    let filePath = path.join(DIR, url === "/" ? "index.html" : url);

    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      filePath = path.join(DIR, "index.html");
    }

    const ext = path.extname(filePath);
    const contentType = mime[ext] || "application/octet-stream";

    try {
      const content = fs.readFileSync(filePath);
      res.writeHead(200, { "Content-Type": contentType });
      res.end(content);
    } catch {
      const html = fs.readFileSync(path.join(DIR, "index.html"));
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(html);
    }
  })
  .listen(PORT, "0.0.0.0", () => {
    console.log(`Frontend running on http://0.0.0.0:${PORT}`);
  });

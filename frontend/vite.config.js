import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { exec } from 'child_process'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'local-cors-proxy',
      configureServer(server) {
        server.middlewares.use('/proxy', async (req, res, next) => {
          const urlStr = req.url.split('?')[1];
          if (!urlStr) return next();
          
          const params = new URLSearchParams(urlStr);
          const urlParam = params.get('url');
          const useBrowser = params.get('browser') === 'true';
          
          if (!urlParam) return next();
          
          try {
            if (useBrowser) {
              const scriptPath = path.resolve(__dirname, '../fetch_html_browser.py');
              const pythonPath = path.resolve(__dirname, '../.venv/Scripts/python.exe');
              exec(`"${pythonPath}" "${scriptPath}" "${urlParam}"`, { maxBuffer: 1024 * 1024 * 50 }, (error, stdout, stderr) => {
                if (error) {
                  res.statusCode = 500;
                  res.end(error.message || stderr);
                  return;
                }
                res.setHeader('Content-Type', 'text/html');
                res.end(stdout);
              });
            } else {
              const fetchRes = await fetch(urlParam);
              const html = await fetchRes.text();
              res.setHeader('Content-Type', 'text/html');
              res.end(html);
            }
          } catch (err) {
            res.statusCode = 500;
            res.end(err.message);
          }
        });
      }
    }
  ],
})

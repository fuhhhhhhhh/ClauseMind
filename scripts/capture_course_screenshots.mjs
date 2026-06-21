import fs from 'fs/promises';
import path from 'path';
import { chromium } from '../frontend/node_modules/playwright/index.mjs';

const ROOT = '/home/fuxiangyu/project/ClauseMind';
const OUTPUT_DIR = path.join(ROOT, 'doc', 'screenshots');
const BASE_URL = 'http://127.0.0.1:5173';
const API_URL = 'http://127.0.0.1:8000/api/v1';

const VIEWPORT = { width: 1440, height: 1080 };

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function login(username, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    throw new Error(`Login failed for ${username}: ${res.status}`);
  }
  const payload = await res.json();
  return payload.data;
}

async function setAuth(page, auth) {
  await page.addInitScript((data) => {
    localStorage.setItem('clausemind_token', data.access_token);
    localStorage.setItem('clausemind_user', JSON.stringify(data.user));
  }, auth);
}

async function waitForStable(page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(800);
}

async function shot(page, name, route, options = {}) {
  await page.goto(`${BASE_URL}${route}`, { waitUntil: 'domcontentloaded' });
  await waitForStable(page);
  if (options.before) {
    await options.before(page);
    await waitForStable(page);
  }
  await page.screenshot({
    path: path.join(OUTPUT_DIR, name),
    fullPage: !!options.fullPage,
  });
  console.log(`saved ${name}`);
}

async function main() {
  await ensureDir(OUTPUT_DIR);

  const demoAuth = await login('demo', 'demo123456');
  const adminAuth = await login('admin', 'admin123456');

  const browser = await chromium.launch({ headless: true });

  const publicPage = await browser.newPage({ viewport: VIEWPORT });
  await shot(publicPage, '01-login.png', '/login');
  await shot(publicPage, '02-register.png', '/register');
  await publicPage.close();

  const demoContext = await browser.newContext({ viewport: VIEWPORT });
  const demoPage = await demoContext.newPage();
  await setAuth(demoPage, demoAuth);
  await shot(demoPage, '03-dashboard.png', '/dashboard');
  await shot(demoPage, '04-upload.png', '/contracts/upload');
  await shot(demoPage, '05-contract-list.png', '/contracts');
  await shot(demoPage, '06-contract-detail.png', '/contracts/1');
  await shot(demoPage, '07-parse-result.png', '/contracts/1/parse-result');
  await shot(demoPage, '08-normalized-result.png', '/contracts/1/parse-result', {
    before: async (page) => {
      const target = page.getByText('标准化结果').first();
      if (await target.isVisible()) {
        await target.click();
      }
    },
    fullPage: true,
  });
  await shot(demoPage, '09-review-progress.png', '/review-tasks/1/progress', { fullPage: true });
  await shot(demoPage, '10-risk-analysis.png', '/review-tasks/1/risks');
  await shot(demoPage, '11-suggestion.png', '/review-tasks/1/suggestions');
  await shot(demoPage, '12-report.png', '/reports/1', { fullPage: true });
  await demoContext.close();

  const adminContext = await browser.newContext({ viewport: VIEWPORT });
  const adminPage = await adminContext.newPage();
  await setAuth(adminPage, adminAuth);
  await shot(adminPage, '13-admin.png', '/admin', { fullPage: true });
  await adminContext.close();

  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

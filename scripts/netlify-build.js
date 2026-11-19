'use strict';

/**
 * Netlify 自动构建脚本（纯 Node，无第三方依赖）
 *
 * GitHub Pages 用 root: /buzhidaoo/，Netlify 部署在根域名，必须用 root: /。
 * 本脚本在构建前改写 _config.yml 的 url / root，再执行 hexo clean + generate，
 * 最后自检 public/index.html 里不能残留 /buzhidaoo 前缀。
 *
 * 日志一律输出英文（ASCII-only），避免 Netlify 日志中文乱码。
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// 以脚本所在目录为基准，向上找到 Hexo 项目根目录
const ROOT_DIR = path.resolve(__dirname, '..');
const CONFIG_PATH = path.join(ROOT_DIR, '_config.yml');
const HEXO_BIN = path.join(ROOT_DIR, 'node_modules', 'hexo', 'bin', 'hexo');
const INDEX_PATH = path.join(ROOT_DIR, 'public', 'index.html');

const FALLBACK_URL = 'https://serene-elf-swws.netlify.app';
const NETLIFY_ROOT = '/';
const PAGES_PREFIX = '/buzhidaoo';

// Hexo 会自动加载项目根目录 scripts/ 下的所有文件，并注入名为 hexo 的参数。
// 被 Hexo 加载时只做无害的变量定义，不执行构建，避免递归调用 hexo。
const loadedByHexo = typeof hexo !== 'undefined';

function log(message) {
  process.stdout.write('[netlify-build] ' + message + '\n');
}

function fail(message) {
  process.stderr.write('[netlify-build] ERROR: ' + message + '\n');
  process.exit(1);
}

/** 读取 _config.yml（UTF-8，去掉可能的 BOM） */
function readConfig() {
  let text = fs.readFileSync(CONFIG_PATH, 'utf8');
  if (text.charCodeAt(0) === 0xfeff) {
    text = text.slice(1);
  }
  return text;
}

/**
 * 改写 YAML 顶层标量，保留每一行原有换行符（兼容 CRLF / LF 混用）。
 * 例如 setYamlScalar(text, 'root', '/') 只替换 root 行的值，不动行尾。
 */
function setYamlScalar(text, key, value) {
  const parts = text.split(/(\r\n|\n|\r)/);
  const linePattern = new RegExp('^' + key + ':[ \\t]*.*$');

  for (let i = 0; i < parts.length; i += 2) {
    if (linePattern.test(parts[i])) {
      parts[i] = key + ': ' + value;
      return { text: parts.join(''), found: true };
    }
  }

  // 没找到该键就追加到文件末尾，沿用文件已有的换行风格
  const eol = text.indexOf('\r\n') !== -1 ? '\r\n' : (text.indexOf('\n') !== -1 ? '\n' : '\r');
  return { text: text + (text.endsWith('\n') || text.endsWith('\r') ? '' : eol) + key + ': ' + value, found: false };
}

/** 确定 Netlify 站点地址：优先用 Netlify 注入的 URL 环境变量 */
function resolveSiteUrl() {
  const fromEnv = (process.env.URL || '').trim();
  const url = fromEnv || FALLBACK_URL;
  return url.replace(/\/+$/, ''); // 去掉结尾斜杠，root 单独管理
}

function runHexo(args) {
  log('run: node node_modules/hexo/bin/hexo ' + args.join(' '));
  execFileSync(process.execPath, [HEXO_BIN].concat(args), {
    cwd: ROOT_DIR,
    stdio: 'inherit',
  });
}

function selfCheck() {
  if (!fs.existsSync(INDEX_PATH)) {
    fail('public/index.html not found after generate');
  }

  const html = fs.readFileSync(INDEX_PATH, 'utf8');
  const occurrences = html.split(PAGES_PREFIX).length - 1;
  log('self-check: occurrences of "' + PAGES_PREFIX + '" in public/index.html = ' + occurrences);

  if (occurrences > 0) {
    fail('build output still contains "' + PAGES_PREFIX + '" prefix; root config was not applied');
  }
}

function main() {
  if (!fs.existsSync(HEXO_BIN)) {
    fail('hexo not installed: node_modules/hexo/bin/hexo is missing (run install first)');
  }

  const siteUrl = resolveSiteUrl();
  log('site url: ' + siteUrl);
  log('site root: ' + NETLIFY_ROOT);

  // 1. 改写 _config.yml（写回 UTF-8 无 BOM）
  let config = readConfig();
  const urlResult = setYamlScalar(config, 'url', siteUrl);
  if (!urlResult.found) {
    fail('key "url" not found in _config.yml');
  }
  const rootResult = setYamlScalar(urlResult.text, 'root', NETLIFY_ROOT);
  fs.writeFileSync(CONFIG_PATH, rootResult.text, { encoding: 'utf8', flag: 'w' });
  log('updated _config.yml: url=' + siteUrl + ', root=' + NETLIFY_ROOT);

  // 2. 构建（用当前进程的 node，避免硬编码路径）
  runHexo(['clean']);
  runHexo(['generate']);

  // 3. 自检产物里不能残留 GitHub Pages 前缀
  selfCheck();

  log('build finished successfully');
}

if (!loadedByHexo) {
  try {
    main();
  } catch (err) {
    fail(err && err.message ? err.message : String(err));
  }
}

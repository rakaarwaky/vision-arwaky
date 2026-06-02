import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const exePath = path.join(__dirname, '.venv', 'Scripts', 'mcp-vision.exe');

spawn(exePath, [], { stdio: 'inherit', shell: true });

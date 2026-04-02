import { mkdir, readFile, rm, writeFile, copyFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = process.cwd();
const dist = resolve(root, 'dist');

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

const htmlSource = await readFile(resolve(root, 'index.html'), 'utf8');
const htmlOut = htmlSource
  .replace('styles.css', './styles.css')
  .replace('app.js', './app.js');

await writeFile(resolve(dist, 'index.html'), htmlOut, 'utf8');
await copyFile(resolve(root, 'app.js'), resolve(dist, 'app.js'));
await copyFile(resolve(root, 'styles.css'), resolve(dist, 'styles.css'));

console.log('Build completado en dist/');

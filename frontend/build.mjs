import {readFile, mkdir, writeFile, rm, copyFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
await rm('dist', {recursive:true, force:true});
await mkdir('dist/assets', {recursive:true});
let html = await readFile('src/index.html','utf8');
for (const file of ['styles.css','app.js']) {
  const data=await readFile(`src/${file}`);
  const hash=createHash('sha256').update(data).digest('hex').slice(0,10);
  const name=file.replace('.',`.${hash}.`);
  await writeFile(`dist/assets/${name}`, data);
  html=html.replace(`/src/${file}`,`/assets/${name}`);
}
await writeFile('dist/index.html', html);
await copyFile('src/favicon.svg', 'dist/favicon.svg');
console.log('Built dist: HTML, hashed CSS/JS, favicon. No external assets.');

await mkdir('../backend/app/static', {recursive:true});
for (const asset of ['swagger-ui-bundle.js', 'swagger-ui.css']) {
  await copyFile(`node_modules/swagger-ui-dist/${asset}`, `../backend/app/static/${asset}`);
}
console.log('Copied local Swagger UI assets for backend.');

// Assemble the author's original figures into a GIF; no generated image content.
// Optional argument: directory containing the Node runtime's node_modules.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = process.argv[2]
  ? createRequire(path.join(path.resolve(process.argv[2]), 'package.json'))
  : createRequire(import.meta.url);
const sharp = require('sharp');
const { createCanvas, loadImage, GlobalFonts } = require('@napi-rs/canvas');
for (const font of ['C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf']) {
  try { await fs.access(font); GlobalFonts.registerFromPath(font, 'SiteSans'); } catch {}
}
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'assets/images/research/vr-wise-source');
const output = path.join(root, 'assets/images/research');
const width = 720, height = 450;
const names = {
  overview: 'Figure_1_3Modules.jpg',
  worker: 'Figure_2_new_Anonymization.png',
  driver: 'Figure3_VRdriverbrighter_LAST.jpg',
  scenarios: 'Figure4_three_scenarios.jpg',
  gaze: 'Figure 5_P12.png',
  experience: 'Figure 8_violent.png',
};
const images = Object.fromEntries(await Promise.all(Object.entries(names).map(async ([key, name]) => [key, await loadImage(path.join(source, name))])));
const stages = [
  { title: 'System overview', key: 'overview', duration: 2600 },
  { title: 'Worker motion capture and animation', key: 'worker', duration: 2600 },
  { title: 'VR eye tracking and biometric sensing', key: 'driver', duration: 2600 },
  { title: 'Work-zone scenarios', key: 'scenarios', duration: 2400 },
  { title: 'Gaze metrics', key: 'gaze', duration: 2600 },
  { title: 'User experience', key: 'experience', duration: 2600 },
];

function fit(ctx, image, box, crop) {
  const [x, y, w, h] = box;
  const [sx, sy, sw, sh] = crop || [0, 0, image.width, image.height];
  const scale = Math.min(w / sw, h / sh);
  const dw = sw * scale, dh = sh * scale;
  ctx.drawImage(image, sx, sy, sw, sh, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh);
}

const rgbaFrames = [], pngFrames = [];
for (const [index, stage] of stages.entries()) {
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = '#282735';
  ctx.font = 'bold 20px SiteSans';
  ctx.fillText(stage.title, 18, 29);
  ctx.strokeStyle = '#e8e5eb';
  ctx.beginPath(); ctx.moveTo(18, 42); ctx.lineTo(702, 42); ctx.stroke();
  if (stage.key === 'worker') {
    const crops = [[38, 35, 270, 215], [38, 335, 270, 192], [38, 604, 270, 202]];
    const labels = ['Motion capture', 'Maya animation', 'CARLA'];
    crops.forEach((crop, i) => {
      fit(ctx, images.worker, [18 + i * 238, 67, 208, 295], crop);
      ctx.fillStyle = '#282735'; ctx.font = '17px SiteSans'; ctx.textAlign = 'center';
      ctx.fillText(labels[i], 122 + i * 238, 382);
    });
    ctx.strokeStyle = '#625093'; ctx.lineWidth = 2;
    for (const x of [228, 466]) {
      ctx.beginPath(); ctx.moveTo(x, 220); ctx.lineTo(x + 16, 220);
      ctx.moveTo(x + 10, 214); ctx.lineTo(x + 16, 220); ctx.lineTo(x + 10, 226); ctx.stroke();
    }
    ctx.textAlign = 'left';
  } else if (stage.key === 'driver') {
    fit(ctx, images.driver, [14, 53, 692, 359], [0, 0, 535, 294]);
  } else if (stage.key === 'gaze') {
    // Two complete supplied chart panels, including their original axes/labels.
    fit(ctx, images.gaze, [22, 52, 328, 359], [400, 0, 395, 495]);
    fit(ctx, images.gaze, [370, 52, 328, 359], [1595, 0, 394, 495]);
  } else {
    fit(ctx, images[stage.key], [14, 53, 692, 359]);
  }
  stages.forEach((_, i) => {
    ctx.fillStyle = i === index ? '#625093' : '#e8e5eb';
    ctx.fillRect(18 + i * 116, 432, 104, 3);
  });
  const pixels = ctx.getImageData(0, 0, width, height).data;
  rgbaFrames.push(Buffer.from(pixels.buffer, pixels.byteOffset, pixels.byteLength));
  pngFrames.push(canvas.toBuffer('image/png'));
}

await sharp(Buffer.concat(rgbaFrames), { raw: { width, height: height * stages.length, channels: 4, pageHeight: height } })
  .gif({ loop: 0, delay: stages.map(stage => stage.duration), colours: 256, dither: 0.5, effort: 7 })
  .toFile(path.join(output, 'vr-wise.gif'));
await sharp(pngFrames[0]).webp({ quality: 90 }).toFile(path.join(output, 'vr-wise.webp'));
const review = path.join(root, '..', 'tmp', 'vr-wise-preview');
await fs.mkdir(review, { recursive: true });
await sharp({ create: { width: width * 2, height: height * 3, channels: 3, background: '#ffffff' } })
  .composite(pngFrames.map((input, i) => ({ input, left: (i % 2) * width, top: Math.floor(i / 2) * height })))
  .png().toFile(path.join(review, 'contact-sheet.png'));
const metadata = await sharp(path.join(output, 'vr-wise.gif'), { animated: true }).metadata();
console.log(JSON.stringify({ output: 'assets/images/research/vr-wise.gif', pages: metadata.pages, pageHeight: metadata.pageHeight, loop: metadata.loop, delay: metadata.delay, bytes: (await fs.stat(path.join(output, 'vr-wise.gif'))).size }));

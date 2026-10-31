const { chromium } = require("/home/blank/sakshi-ai-hackathon/web/node_modules/playwright");
const path = require("path");
const fs = require("fs");

// Renders an animated SVG/Canvas avatar frame into a PNG sequence, then encodes with ffmpeg
async function renderAvatarFrames() {
  const framesDir = "/home/blank/sakshi-ai-hackathon/demo_production/avatar_frames";
  fs.mkdirSync(framesDir, { recursive: true });

  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome-stable",
    headless: true
  });
  const page = await browser.newPage({ viewport: { width: 320, height: 320 } });

  const avatarHtml = `
    <!DOCTYPE html><html><head><style>
      body { margin: 0; background: transparent; width: 320px; height: 320px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
      .avatar-wrapper { position: relative; width: 260px; height: 260px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
      .ring-glow { position: absolute; inset: -8px; border-radius: 50%; border: 3px solid #3b82f6; box-shadow: 0 0 25px rgba(59, 130, 246, 0.6); }
      .avatar-circle { width: 240px; height: 240px; border-radius: 50%; overflow: hidden; background: linear-gradient(135deg, #0f172a, #1e293b); border: 3px solid rgba(255,255,255,0.2); position: relative; display: flex; align-items: center; justify-content: center; }
      .hud-badge { position: absolute; bottom: 8px; background: rgba(15, 23, 42, 0.9); border: 1px solid #3b82f6; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-family: sans-serif; font-weight: 700; color: #60a5fa; letter-spacing: 0.05em; }
    </style></head><body>
      <div class="avatar-wrapper">
        <div class="ring-glow" id="ring"></div>
        <div class="avatar-circle">
          <!-- Stylized AI Mentor Avatar SVG -->
          <svg width="220" height="220" viewBox="0 0 200 200" id="avatarSvg">
            <defs>
              <linearGradient id="skin" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8"/>
                <stop offset="100%" stop-color="#6366f1"/>
              </linearGradient>
              <linearGradient id="visor" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#06b6d4"/>
                <stop offset="50%" stop-color="#3b82f6"/>
                <stop offset="100%" stop-color="#8b5cf6"/>
              </linearGradient>
            </defs>
            <!-- Torso -->
            <path d="M 40 180 Q 100 130 160 180 L 170 200 L 30 200 Z" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
            <!-- Neck & Head Base -->
            <rect x="85" y="115" width="30" height="30" rx="6" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
            <ellipse cx="100" cy="85" rx="42" ry="52" fill="url(#skin)" opacity="0.95"/>
            <!-- Cyber Visor / Eyes -->
            <rect x="68" y="70" width="64" height="20" rx="8" fill="url(#visor)" id="visorRect"/>
            <line x1="72" y1="80" x2="128" y2="80" stroke="#ffffff" stroke-width="2" opacity="0.8" id="eyeScan"/>
            <!-- Mouth / Audio Waveform -->
            <path d="M 85 110 Q 100 115 115 110" stroke="#ffffff" stroke-width="3" stroke-linecap="round" fill="none" id="mouthPath"/>
            <!-- Cybernetic temple accents -->
            <circle cx="58" cy="80" r="4" fill="#38bdf8"/>
            <circle cx="142" cy="80" r="4" fill="#38bdf8"/>
          </svg>
          <div class="hud-badge">AI TUTOR</div>
        </div>
      </div>
    </body></html>
  `;

  await page.setContent(avatarHtml);

  // Render 30 looping frames (1 second loop at 30fps)
  const totalFrames = 30;
  for (let i = 0; i < totalFrames; i++) {
    const progress = i / totalFrames;
    const mouthCurve = 110 + Math.sin(progress * Math.PI * 4) * 8;
    const ringScale = 1.0 + Math.sin(progress * Math.PI * 2) * 0.06;
    const scanX = 75 + Math.sin(progress * Math.PI * 2) * 20;

    await page.evaluate(({ mouthCurve, ringScale, scanX }) => {
      document.getElementById("mouthPath").setAttribute("d", `M 85 110 Q 100 ${mouthCurve} 115 110`);
      document.getElementById("ring").style.transform = `scale(${ringScale})`;
      document.getElementById("eyeScan").setAttribute("x1", scanX - 10);
      document.getElementById("eyeScan").setAttribute("x2", scanX + 10);
    }, { mouthCurve, ringScale, scanX });

    const frameFile = path.join(framesDir, `frame_${String(i).padStart(3, "0")}.png`);
    await page.screenshot({ path: frameFile, omitBackground: true });
  }

  await browser.close();
  console.log(`Rendered ${totalFrames} avatar frames!`);
}

renderAvatarFrames().catch(err => {
  console.error("Avatar rendering failed:", err);
  process.exit(1);
});

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Brick Breaker Nâng Cấp",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 Hứng Bóng Phá Gạch - Bản Nâng Cấp")

# Thanh tùy chỉnh tốc độ bóng bên Streamlit
ball_speed = st.slider("⚡ Tùy chỉnh tốc độ bóng ban đầu:", min_value=3, max_value=9, value=5, step=1)

brick_breaker_html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <style>
    body {{
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      background: #111827;
      color: #fff;
      font-family: Arial, sans-serif;
      user-select: none;
    }}
    .hud {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 500px;
      margin: 10px 0;
      font-size: 15px;
      font-weight: bold;
    }}
    canvas {{
      background: #000;
      border: 3px solid #374151;
      border-radius: 8px;
      display: block;
      cursor: none;
    }}
    .btn {{
      background: #3b82f6;
      border: none;
      color: white;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="hud">
    <div>Điểm: <span id="scoreText" style="color: #10b981;">0</span></div>
    <div>Mạng: <span id="livesText" style="color: #ef4444;">❤️❤️❤️</span></div>
    <button class="btn" id="musicBtn">🎵 Bật nhạc nền</button>
  </div>

  <canvas id="gameCanvas" width="500" height="430"></canvas>

  <!-- Link nhạc nền trực tuyến (miễn phí bản quyền) -->
  <audio id="bgMusic" loop src="https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3?filename=game-music-loop-6-144641.mp3"></audio>

  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const scoreText = document.getElementById("scoreText");
    const livesText = document.getElementById("livesText");
    const musicBtn = document.getElementById("musicBtn");
    const bgMusic = document.getElementById("bgMusic");

    // Khởi tạo Audio Context cho hiệu ứng âm thanh va chạm không độ trễ
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function initAudio() {{
      if (!audioCtx) {{
        audioCtx = new AudioContext();
      }}
    }}

    function playBeep(freq, type, duration) {{
      if (!audioCtx) return;
      try {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch (e) {{}}
    }}

    // Xử lý bật/tắt nhạc nền
    musicBtn.addEventListener("click", () => {{
      initAudio();
      if (bgMusic.paused) {{
        bgMusic.play();
        musicBtn.innerText = "🔇 Tắt nhạc";
      }} else {{
        bgMusic.pause();
        musicBtn.innerText = "🎵 Bật nhạc";
      }}
    }});

    // Cấu hình bóng & tốc độ nhận từ Streamlit slider
    const initialSpeed = {ball_speed};
    let ballRadius = 7;
    let x = canvas.width / 2;
    let y = canvas.height - 30;
    let dx = initialSpeed * (Math.random() > 0.5 ? 1 : -1);
    let dy = -initialSpeed;

    // Thanh đỡ
    let paddleHeight = 10;
    let paddleWidth = 85;
    let paddleX = (canvas.width - paddleWidth) / 2;

    let score = 0;
    let lives = 3;
    let isGameOver = false;
    let isGameWon = false;

    // Quà rơi (Power-ups)
    const powerUps = [];

    // Lưới gạch
    const brickRowCount = 4;
    const brickColumnCount = 6;
    const brickWidth = 65;
    const brickHeight = 18;
    const brickPadding = 10;
    const brickOffsetTop = 25;
    const brickOffsetLeft = 25;
    const brickColors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6"];

    const bricks = [];
    for (let c = 0; c < brickColumnCount; c++) {{
      bricks[c] = [];
      for (let r = 0; r < brickRowCount; r++) {{
        bricks[c][r] = {{ x: 0, y: 0, status: 1 }};
      }}
    }}

    // Điều khiển chuột
    canvas.addEventListener("mousemove", (e) => {{
      initAudio();
      const rect = canvas.getBoundingClientRect();
      const relativeX = e.clientX - rect.left;
      if (relativeX > 0 && relativeX < canvas.width) {{
        paddleX = relativeX - paddleWidth / 2;
        if (paddleX < 0) paddleX = 0;
        if (paddleX + paddleWidth > canvas.width) paddleX = canvas.width - paddleWidth;
      }}
    }});

    canvas.addEventListener("click", () => {{
      initAudio();
      if (isGameOver || isGameWon) {{
        document.location.reload();
      }}
    }});

    function collisionDetection() {{
      let activeBricks = 0;
      for (let c = 0; c < brickColumnCount; c++) {{
        for (let r = 0; r < brickRowCount; r++) {{
          const b = bricks[c][r];
          if (b.status === 1) {{
            activeBricks++;
            if (x > b.x && x < b.x + brickWidth && y > b.y && y < b.y + brickHeight) {{
              dy = -dy;
              b.status = 0;
              score += 10;
              scoreText.innerText = score;
              
              // Âm thanh vỡ gạch
              playBeep(450, "square", 0.1);

              // Tỉ lệ 35% rơi phần thưởng ngẫu nhiên
              if (Math.random() < 0.35) {{
                const type = Math.random() > 0.5 ? "expand" : "life";
                powerUps.push({{
                  x: b.x + brickWidth / 2,
                  y: b.y + brickHeight,
                  type: type,
                  speed: 2
                }});
              }}
            }}
          }}
        }}
      }}
      if (activeBricks === 0 && !isGameOver) {{
        isGameWon = true;
      }}
    }}

    function drawPowerUps() {{
      for (let i = powerUps.length - 1; i >= 0; i--) {{
        const p = powerUps[i];
        p.y += p.speed;

        // Vẽ viên quà
        ctx.beginPath();
        ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = p.type === "expand" ? "#38bdf8" : "#ec4899";
        ctx.fill();
        ctx.closePath();

        // Kiểm tra thanh đỡ hứng được quà
        if (
          p.y + 8 >= canvas.height - paddleHeight - 8 &&
          p.y - 8 <= canvas.height - 8 &&
          p.x >= paddleX &&
          p.x <= paddleX + paddleWidth
        ) {{
          // Âm thanh nhận quà
          playBeep(800, "sine", 0.2);

          if (p.type === "expand") {{
            paddleWidth = Math.min(paddleWidth + 25, 160); // Mở rộng thanh đỡ
          }} else if (p.type === "life") {{
            lives++;
            livesText.innerText = "❤️".repeat(lives);
          }}
          powerUps.splice(i, 1);
          continue;
        }}

        // Quà rơi mất khỏi màn hình
        if (p.y > canvas.height) {{
          powerUps.splice(i, 1);
        }}
      }}
    }}

    function drawBall() {{
      ctx.beginPath();
      ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
      ctx.fillStyle = "#ffffff";
      ctx.fill();
      ctx.closePath();
    }}

    function drawPaddle() {{
      ctx.beginPath();
      ctx.rect(paddleX, canvas.height - paddleHeight - 8, paddleWidth, paddleHeight);
      ctx.fillStyle = "#38bdf8";
      ctx.fill();
      ctx.closePath();
    }}

    function drawBricks() {{
      for (let c = 0; c < brickColumnCount; c++) {{
        for (let r = 0; r < brickRowCount; r++) {{
          if (bricks[c][r].status === 1) {{
            const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
            const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
            bricks[c][r].x = brickX;
            bricks[c][r].y = brickY;
            ctx.beginPath();
            ctx.rect(brickX, brickY, brickWidth, brickHeight);
            ctx.fillStyle = brickColors[r % brickColors.length];
            ctx.fill();
            ctx.closePath();
          }}
        }}
      }}
    }}

    function draw() {{
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawBricks();
      drawBall();
      drawPaddle();
      drawPowerUps();
      collisionDetection();

      // Nảy vào tường 2 bên
      if (x + dx > canvas.width - ballRadius || x + dx < ballRadius) {{
        dx = -dx;
        playBeep(260, "triangle", 0.05);
      }}

      // Nảy vào trần trên
      if (y + dy < ballRadius) {{
        dy = -dy;
        playBeep(260, "triangle", 0.05);
      }} else if (y + dy > canvas.height - ballRadius - paddleHeight - 8) {{
        // Chạm vào thanh đỡ
        if (x > paddleX && x < paddleX + paddleWidth) {{
          let hitPoint = x - (paddleX + paddleWidth / 2);
          dx = hitPoint * 0.15;
          dy = -Math.abs(dy);
          playBeep(350, "sine", 0.08); // Âm thanh nảy thanh đỡ
        }} else if (y + dy > canvas.height - ballRadius) {{
          // Rơi bóng
          lives--;
          livesText.innerText = "❤️".repeat(Math.max(lives, 0));
          playBeep(150, "sawtooth", 0.3); // Âm thanh mất mạng

          if (lives <= 0) {{
            isGameOver = true;
          }} else {{
            x = canvas.width / 2;
            y = canvas.height - 30;
            dx = initialSpeed * (Math.random() > 0.5 ? 1 : -1);
            dy = -initialSpeed;
            paddleX = (canvas.width - paddleWidth) / 2;
          }}
        }}
      }}

      if (isGameOver) {{
        ctx.font = "bold 26px Arial";
        ctx.fillStyle = "#ef4444";
        ctx.textAlign = "center";
        ctx.fillText("TRÒ CHƠI KẾT THÚC", canvas.width / 2, canvas.height / 2);
        ctx.font = "15px Arial";
        ctx.fillStyle = "#9ca3af";
        ctx.fillText("Nhấp chuột để chơi lại", canvas.width / 2, canvas.height / 2 + 35);
        return;
      }}

      if (isGameWon) {{
        ctx.font = "bold 26px Arial";
        ctx.fillStyle = "#10b981";
        ctx.textAlign = "center";
        ctx.fillText("CHIẾN THẮNG!", canvas.width / 2, canvas.height / 2);
        ctx.font = "15px Arial";
        ctx.fillStyle = "#9ca3af";
        ctx.fillText("Nhấp chuột để chơi lại", canvas.width / 2, canvas.height / 2 + 35);
        return;
      }}

      x += dx;
      y += dy;
      requestAnimationFrame(draw);
    }}

    draw();
  </script>
</body>
</html>
"""

components.html(brick_breaker_html, height=520, scrolling=False)

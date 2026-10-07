import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Brick Breaker",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 Trò Chơi Hứng Bóng Phá Gạch")
st.caption("Di chuyển **chuột** để điều khiển thanh hứng bóng!")

brick_breaker_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <style>
    body {
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #111827;
      color: #fff;
      font-family: Arial, sans-serif;
      user-select: none;
    }
    #game-container {
      margin-top: 10px;
      position: relative;
    }
    canvas {
      background: #000;
      border: 3px solid #374151;
      border-radius: 8px;
      display: block;
      cursor: none;
    }
    .hud {
      display: flex;
      justify-content: space-between;
      width: 500px;
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 8px;
    }
  </style>
</head>
<body>
  <div class="hud">
    <div>Điểm: <span id="scoreText" style="color: #10b981;">0</span></div>
    <div>Mạng: <span id="livesText" style="color: #ef4444;">❤️❤️❤️</span></div>
  </div>

  <div id="game-container">
    <canvas id="gameCanvas" width="500" height="420"></canvas>
  </div>

  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const scoreText = document.getElementById("scoreText");
    const livesText = document.getElementById("livesText");

    let ballRadius = 7;
    let x = canvas.width / 2;
    let y = canvas.height - 30;
    let dx = 3;
    let dy = -3;

    const paddleHeight = 10;
    const paddleWidth = 85;
    let paddleX = (canvas.width - paddleWidth) / 2;

    let score = 0;
    let lives = 3;
    let isGameOver = false;
    let isGameWon = false;

    const brickRowCount = 4;
    const brickColumnCount = 6;
    const brickWidth = 65;
    const brickHeight = 18;
    const brickPadding = 10;
    const brickOffsetTop = 25;
    const brickOffsetLeft = 25;

    const brickColors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6"];

    const bricks = [];
    for (let c = 0; c < brickColumnCount; c++) {
      bricks[c] = [];
      for (let r = 0; r < brickRowCount; r++) {
        bricks[c][r] = { x: 0, y: 0, status: 1 };
      }
    }

    canvas.addEventListener("mousemove", (e) => {
      const rect = canvas.getBoundingClientRect();
      const relativeX = e.clientX - rect.left;
      if (relativeX > 0 && relativeX < canvas.width) {
        paddleX = relativeX - paddleWidth / 2;
        if (paddleX < 0) paddleX = 0;
        if (paddleX + paddleWidth > canvas.width) paddleX = canvas.width - paddleWidth;
      }
    });

    canvas.addEventListener("click", () => {
      if (isGameOver || isGameWon) {
        document.location.reload();
      }
    });

    function collisionDetection() {
      let activeBricks = 0;
      for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
          const b = bricks[c][r];
          if (b.status === 1) {
            activeBricks++;
            if (
              x > b.x &&
              x < b.x + brickWidth &&
              y > b.y &&
              y < b.y + brickHeight
            ) {
              dy = -dy;
              b.status = 0;
              score += 10;
              scoreText.innerText = score;
            }
          }
        }
      }
      if (activeBricks === 0 && !isGameOver) {
        isGameWon = true;
      }
    }

    function drawBall() {
      ctx.beginPath();
      ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
      ctx.fillStyle = "#ffffff";
      ctx.fill();
      ctx.closePath();
    }

    function drawPaddle() {
      ctx.beginPath();
      ctx.rect(paddleX, canvas.height - paddleHeight - 8, paddleWidth, paddleHeight);
      ctx.fillStyle = "#38bdf8";
      ctx.fill();
      ctx.closePath();
    }

    function drawBricks() {
      for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
          if (bricks[c][r].status === 1) {
            const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
            const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
            bricks[c][r].x = brickX;
            bricks[c][r].y = brickY;
            ctx.beginPath();
            ctx.rect(brickX, brickY, brickWidth, brickHeight);
            ctx.fillStyle = brickColors[r % brickColors.length];
            ctx.fill();
            ctx.closePath();
          }
        }
      }
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawBricks();
      drawBall();
      drawPaddle();
      collisionDetection();

      if (x + dx > canvas.width - ballRadius || x + dx < ballRadius) {
        dx = -dx;
      }
      if (y + dy < ballRadius) {
        dy = -dy;
      } else if (y + dy > canvas.height - ballRadius - paddleHeight - 8) {
        if (x > paddleX && x < paddleX + paddleWidth) {
          let hitPoint = x - (paddleX + paddleWidth / 2);
          dx = hitPoint * 0.12;
          dy = -dy;
        } else if (y + dy > canvas.height - ballRadius) {
          lives--;
          livesText.innerText = "❤️".repeat(Math.max(lives, 0));
          if (lives <= 0) {
            isGameOver = true;
          } else {
            x = canvas.width / 2;
            y = canvas.height - 30;
            dx = 3;
            dy = -3;
            paddleX = (canvas.width - paddleWidth) / 2;
          }
        }
      }

      if (isGameOver) {
        ctx.font = "bold 26px Arial";
        ctx.fillStyle = "#ef4444";
        ctx.textAlign = "center";
        ctx.fillText("TRÒ CHƠI KẾT THÚC", canvas.width / 2, canvas.height / 2);
        ctx.font = "15px Arial";
        ctx.fillStyle = "#9ca3af";
        ctx.fillText("Nhấp chuột để chơi lại", canvas.width / 2, canvas.height / 2 + 35);
        return;
      }

      if (isGameWon) {
        ctx.font = "bold 26px Arial";
        ctx.fillStyle = "#10b981";
        ctx.textAlign = "center";
        ctx.fillText("CHIẾN THẮNG!", canvas.width / 2, canvas.height / 2);
        ctx.font = "15px Arial";
        ctx.fillStyle = "#9ca3af";
        ctx.fillText("Nhấp chuột để chơi lại", canvas.width / 2, canvas.height / 2 + 35);
        return;
      }

      x += dx;
      y += dy;
      requestAnimationFrame(draw);
    }

    draw();
  </script>
</body>
</html>
"""

components.html(brick_breaker_html, height=490, scrolling=False)

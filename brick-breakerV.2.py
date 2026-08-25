import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌 깨기",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌 깨기")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
body {
    margin: 0;
    background: #111827;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
}

#game {
    width: 100%;
    max-width: 700px;
    background: #0f172a;
    border: 2px solid #475569;
    border-radius: 10px;
}

.info {
    display: flex;
    justify-content: space-around;
    max-width: 700px;
    margin: 10px auto;
    font-size: 18px;
}

button {
    padding: 10px 20px;
    margin: 5px;
    border: none;
    border-radius: 8px;
    background: #2563eb;
    color: white;
    font-size: 16px;
}

#continueButton {
    display: none;
    background: #16a34a;
}
</style>
</head>

<body>

<div class="info">
    <div>점수: <span id="score">0</span></div>
    <div>목숨: <span id="lives">3</span></div>
    <div>레벨: <span id="level">1</span></div>
</div>

<canvas id="game" width="700" height="500"></canvas>

<br>

<button id="continueButton" onclick="continueGame()">
    ▶ 계속하기
</button>

<button onclick="restartGame()">
    🔄 다시 시작
</button>

<p>← → 방향키 또는 마우스/터치로 패들을 움직이세요.</p>

<script>

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const scoreText = document.getElementById("score");
const livesText = document.getElementById("lives");
const levelText = document.getElementById("level");
const continueButton = document.getElementById("continueButton");

let score = 0;
let lives = 3;
let level = 1;

let gameRunning = true;
let gameOver = false;
let waitingForContinue = false;

const paddle = {
    width: 110,
    height: 14,
    x: 295,
    y: 455,
    speed: 8,
    dx: 0
};

const ball = {
    x: 350,
    y: 430,
    radius: 8,
    dx: 4,
    dy: -4
};

let bricks = [];

const rows = 6;
const cols = 10;

const brickWidth = 58;
const brickHeight = 22;
const padding = 8;

function createBricks() {

    bricks = [];

    for (let r = 0; r < rows; r++) {

        for (let c = 0; c < cols; c++) {

            bricks.push({
                x: 28 + c * (brickWidth + padding),
                y: 50 + r * (brickHeight + padding),
                width: brickWidth,
                height: brickHeight,
                alive: true
            });

        }

    }

}

function draw() {

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    // 블록
    bricks.forEach((brick, index) => {

        if (!brick.alive) return;

        const colors = [
            "#ef4444",
            "#f97316",
            "#eab308",
            "#22c55e",
            "#06b6d4",
            "#8b5cf6"
        ];

        ctx.fillStyle = colors[index % colors.length];

        ctx.fillRect(
            brick.x,
            brick.y,
            brick.width,
            brick.height
        );

    });

    // 패들
    ctx.fillStyle = "#3b82f6";

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );

    // 공
    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#facc15";
    ctx.fill();

    ctx.closePath();

}

function movePaddle() {

    paddle.x += paddle.dx;

    if (paddle.x < 0)
        paddle.x = 0;

    if (paddle.x + paddle.width > canvas.width)
        paddle.x = canvas.width - paddle.width;

}

function moveBall() {

    ball.x += ball.dx;
    ball.y += ball.dy;

    // 좌우 벽
    if (
        ball.x + ball.radius >= canvas.width ||
        ball.x - ball.radius <= 0
    ) {

        ball.dx *= -1;

    }

    // 위쪽 벽
    if (ball.y - ball.radius <= 0) {

        ball.dy *= -1;

    }

    // 패들
    if (
        ball.y + ball.radius >= paddle.y &&
        ball.y <= paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.dy > 0
    ) {

        ball.dy *= -1;

        const hit =
            (ball.x - paddle.x) / paddle.width;

        ball.dx = (hit - 0.5) * 10;

    }

    // 바닥
    if (ball.y - ball.radius > canvas.height) {

        loseLife();

        return;

    }

    // 블록
    for (let brick of bricks) {

        if (!brick.alive)
            continue;

        if (
            ball.x + ball.radius > brick.x &&
            ball.x - ball.radius < brick.x + brick.width &&
            ball.y + ball.radius > brick.y &&
            ball.y - ball.radius < brick.y + brick.height
        ) {

            brick.alive = false;

            ball.dy *= -1;

            score += 10;

            scoreText.textContent = score;

            break;

        }

    }

    // 모든 블록 제거
    if (bricks.every(b => !b.alive)) {

        level++;

        lives++;

        levelText.textContent = level;
        livesText.textContent = lives;

        createBricks();

        // 레벨이 올라갈수록 조금씩 빨라짐
        ball.dx *= 1.08;
        ball.dy *= 1.08;

        resetBall();

    }

}

function loseLife() {

    lives--;

    livesText.textContent = lives;

    if (lives <= 0) {

        gameOver = true;
        gameRunning = false;

        continueButton.style.display = "none";

        showMessage("GAME OVER");

        return;

    }

    // 게임 일시정지
    gameRunning = false;
    waitingForContinue = true;

    continueButton.style.display = "inline-block";

    showMessage("목숨을 잃었습니다");

}

function continueGame() {

    if (!waitingForContinue)
        return;

    waitingForContinue = false;

    continueButton.style.display = "none";

    resetBall();

    gameRunning = true;

    update();

}

function resetBall() {

    ball.x = canvas.width / 2;
    ball.y = canvas.height - 55;

    ball.dx =
        4 * (Math.random() > 0.5 ? 1 : -1);

    ball.dy = -4;

    paddle.x =
        canvas.width / 2 - paddle.width / 2;

}

function showMessage(message) {

    draw();

    ctx.fillStyle = "rgba(0,0,0,0.7)";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    ctx.fillStyle = "white";

    ctx.font = "bold 40px Arial";

    ctx.textAlign = "center";

    ctx.fillText(
        message,
        canvas.width / 2,
        canvas.height / 2
    );

}

function update() {

    if (!gameRunning) {

        draw();

        return;

    }

    movePaddle();
    moveBall();
    draw();

    requestAnimationFrame(update);

}

function restartGame() {

    score = 0;
    lives = 3;
    level = 1;

    scoreText.textContent = score;
    livesText.textContent = lives;
    levelText.textContent = level;

    gameRunning = true;
    gameOver = false;
    waitingForContinue = false;

    continueButton.style.display = "none";

    createBricks();
    resetBall();

    update();

}


// 키보드
document.addEventListener("keydown", function(e) {

    if (e.key === "ArrowLeft")
        paddle.dx = -paddle.speed;

    if (e.key === "ArrowRight")
        paddle.dx = paddle.speed;

});

document.addEventListener("keyup", function(e) {

    if (
        e.key === "ArrowLeft" ||
        e.key === "ArrowRight"
    ) {

        paddle.dx = 0;

    }

});


// 마우스
canvas.addEventListener("mousemove", function(e) {

    const rect = canvas.getBoundingClientRect();

    const scale =
        canvas.width / rect.width;

    const mouseX =
        (e.clientX - rect.left) * scale;

    paddle.x =
        mouseX - paddle.width / 2;

});


// 모바일 터치
canvas.addEventListener("touchmove", function(e) {

    e.preventDefault();

    const rect = canvas.getBoundingClientRect();

    const scale =
        canvas.width / rect.width;

    const touchX =
        (e.touches[0].clientX - rect.left) * scale;

    paddle.x =
        touchX - paddle.width / 2;

}, { passive: false });


createBricks();
update();

</script>

</body>
</html>
"""

components.html(
    game_html,
    height=650,
    scrolling=False
)

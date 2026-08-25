import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌 깨기",
    page_icon="🧱",
    layout="centered",
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
    font-family: Arial, sans-serif;
    color: white;
    text-align: center;
    overflow: hidden;
}

#game {
    width: 100%;
    max-width: 700px;
    height: auto;
    background: #0f172a;
    border: 2px solid #475569;
    border-radius: 12px;
    display: block;
    margin: 10px auto;
}

.info {
    display: flex;
    justify-content: space-around;
    max-width: 700px;
    margin: 8px auto;
    font-size: 18px;
}

button {
    padding: 10px 22px;
    margin: 5px;
    border: none;
    border-radius: 8px;
    background: #2563eb;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #1d4ed8;
}

.help {
    color: #94a3b8;
    font-size: 14px;
}

#continueButton {
    display: none;
    background: #16a34a;
    font-weight: bold;
}

#continueButton:hover {
    background: #15803d;
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

<button id="continueButton" onclick="continueGame()">
    ▶ 계속하기
</button>

<button onclick="restartGame()">
    🔄 다시 시작
</button>

<p class="help">
    ← → 방향키 또는 마우스/터치로 패들을 움직이세요.
</p>

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
    x: canvas.width / 2 - 55,
    y: canvas.height - 35,
    speed: 8,
    dx: 0
};

const ball = {
    x: canvas.width / 2,
    y: canvas.height - 55,
    radius: 8,
    dx: 4,
    dy: -4
};

let bricks = [];

const brickRows = 6;
const brickCols = 10;

const brickWidth = 58;
const brickHeight = 22;
const brickPadding = 8;
const brickOffsetTop = 50;
const brickOffsetLeft = 28;


// -------------------------
// 블록 생성
// -------------------------

function createBricks() {

    bricks = [];

    for (let r = 0; r < brickRows; r++) {

        for (let c = 0; c < brickCols; c++) {

            bricks.push({
                x: brickOffsetLeft + c * (brickWidth + brickPadding),
                y: brickOffsetTop + r * (brickHeight + brickPadding),
                width: brickWidth,
                height: brickHeight,
                alive: true
            });

        }

    }
}


// -------------------------
// 패들
// -------------------------

function drawPaddle() {

    ctx.fillStyle = "#3b82f6";

    ctx.beginPath();

    ctx.roundRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height,
        7
    );

    ctx.fill();
}


// -------------------------
// 공
// -------------------------

function drawBall() {

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


// -------------------------
// 블록
// -------------------------

function drawBricks() {

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

        ctx.beginPath();

        ctx.roundRect(
            brick.x,
            brick.y,
            brick.width,
            brick.height,
            4
        );

        ctx.fill();

        ctx.closePath();

    });
}


// -------------------------
// 화면 그리기
// -------------------------

function draw() {

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    drawBricks();
    drawPaddle();
    drawBall();

}


// -------------------------
// 패들 이동
// -------------------------

function movePaddle() {

    paddle.x += paddle.dx;

    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > canvas.width) {
        paddle.x = canvas.width - paddle.width;
    }

}


// -------------------------
// 공 이동
// -------------------------

function moveBall() {

    ball.x += ball.dx;
    ball.y += ball.dy;


    // 왼쪽 / 오른쪽 벽

    if (
        ball.x + ball.radius > canvas.width ||
        ball.x - ball.radius < 0
    ) {

        ball.dx *= -1;

    }


    // 위쪽 벽

    if (ball.y - ball.radius < 0) {

        ball.dy *= -1;

    }


    // 패들 충돌

    if (
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <= paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.dy > 0
    ) {

        ball.dy *= -1;

        const hitPosition =
            (ball.x - paddle.x) / paddle.width;

        ball.dx =
            (hitPosition - 0.5) * 10;

    }


    // 바닥

    if (ball.y - ball.radius > canvas.height) {

        loseLife();

        return;

    }


    // 블록 충돌

    bricks.forEach(brick => {

        if (!brick.alive) return;

        if (
            ball.x + ball.radius > brick.x &&
            ball.x - ball.radius <
                brick.x + brick.width &&
            ball.y + ball.radius > brick.y &&
            ball.y - ball.radius <
                brick.y + brick.height
        ) {

            brick.alive = false;

            ball.dy *= -1;

            score += 10;

            scoreText.textContent = score;

        }

    });


    // 모든 블록 제거 확인

    if (bricks.every(brick => !brick.alive)) {

        clearLevel();

    }

}


// -------------------------
// 목숨 감소
// -------------------------

function loseLife() {

    lives--;

    livesText.textContent = lives;

    // 목숨이 모두 없어졌다면 게임 오버

    if (lives <= 0) {

        gameOver = true;
        gameRunning = false;

        continueButton.style.display = "none";

        showMessage("GAME OVER");

        return;

    }


    // 일단 게임 정지

    gameRunning = false;

    waitingForContinue = true;

    continueButton.style.display = "inline-block";

    showMessage("목숨을 잃었습니다");

}


// -------------------------
// 계속하기
// -------------------------

function continueGame() {

    if (!waitingForContinue) return;

    waitingForContinue = false;

    continueButton.style.display = "none";

    resetBall();

    gameRunning = true;

    update();

}


// -------------------------
// 공 초기화
// -------------------------

function resetBall() {

    ball.x = canvas.width / 2;

    ball.y = canvas.height - 55;

    ball.dx =
        4 * (Math.random() > 0.5 ? 1 : -1);

    ball.dy = -4;

    paddle.x =
        canvas.width / 2 -
        paddle.width / 2;

}


// -------------------------
// 레벨 클리어
// -------------------------

function clearLevel() {

    // 목숨 +1

    lives++;

    livesText.textContent = lives;

    level++;

    levelText.textContent = level;

    // 새로운 블록 생성

    createBricks();

    // 레벨이 올라갈수록 공 속도 증가

    ball.dx *= 1.08;
    ball.dy *= 1.08;

    resetBall();

}


// -------------------------
// 메시지
// -------------------------

function showMessage(message) {

    draw();

    ctx.fillStyle =
        "rgba(0,0,0,0.72)";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    ctx.fillStyle = "white";

    ctx.font =
        "bold 42px Arial";

    ctx.textAlign = "center";

    ctx.fillText(
        message,
        canvas.width / 2,
        canvas.height / 2
    );

}


// -------------------------
// 게임 업데이트
// -------------------------

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


// -------------------------
// 키보드 조작
// -------------------------

document.addEventListener(
    "keydown",
    event => {

        if (event.key === "ArrowLeft") {

            paddle.dx =
                -paddle.speed;

        }

        if (event.key === "ArrowRight") {

            paddle.dx =
                paddle.speed;

        }

    }
);


document.addEventListener(
    "keyup",
    event => {

        if (
            event.key === "ArrowLeft" ||
            event.key === "ArrowRight"
        ) {

            paddle.dx = 0;

        }

    }
);


// -------------------------
// 마우스 조작
// -------------------------

canvas.addEventListener(
    "mousemove",
    event => {

        const rect =
            canvas.getBoundingClientRect();

        const scaleX =
            canvas.width / rect.width;

        const mouseX =
            (event.clientX - rect.left) *
            scaleX;

        paddle.x =
            mouseX -
            paddle.width / 2;

        if (paddle.x < 0) {

            paddle.x = 0;

        }

        if (
            paddle.x + paddle.width >
            canvas.width
        ) {

            paddle.x =
                canvas.width -
                paddle.width;

        }

    }
);


// -------------------------
// 모바일 터치
// -------------------------

canvas.addEventListener(
    "touchmove",
    event => {

        event.preventDefault();

        const rect =
            canvas.getBoundingClientRect();

        const scaleX =
            canvas.width / rect.width;

        const touchX =
            (event.touches[0].clientX -
             rect.left) *
            scaleX;

        paddle.x =
            touchX -
            paddle.width / 2;

        if (paddle.x < 0) {

            paddle.x = 0;

        }

        if (
            paddle.x

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
    display: block;
    margin: auto;
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
    cursor: pointer;
}

button:hover {
    background: #1d4ed8;
}

#continueButton {
    display: none;
    background: #16a34a;
    font-weight: bold;
}

.help {
    color: #94a3b8;
    font-size: 14px;
}
</style>
</head>

<body>

<div class="info">
    <div>점수: <span id="score">0</span></div>
    <div>❤️ <span id="lives">3</span></div>
    <div>스테이지: <span id="level">1</span></div>
</div>

<canvas id="game" width="700" height="500"></canvas>

<br>

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


// ============================
// 게임 변수
// ============================

let score = 0;
let lives = 3;
let level = 1;

let gameRunning = true;
let gameOver = false;
let waitingForContinue = false;


// ============================
// 패들
// ============================

const paddle = {
    width: 110,
    height: 14,
    x: 295,
    y: 455,
    speed: 8,
    dx: 0
};


// ============================
// 공
// ============================

let balls = [];


// ============================
// 아이템
// ============================

let items = [];


// 아이템 종류
// extra = 공 추가
// boost = 부스트

const ITEM_SIZE = 18;


// ============================
// 스테이지 설정
// ============================

function getStageSettings() {

    // 낮은 스테이지는 쉽게
    if (level <= 2) {

        return {
            rows: 4,
            cols: 8,
            speed: 3.5,
            dropChance: 0.12
        };

    }

    // 중간
    if (level <= 4) {

        return {
            rows: 5,
            cols: 9,
            speed: 4.2,
            dropChance: 0.16
        };

    }

    // 조금 어려움
    if (level <= 7) {

        return {
            rows: 6,
            cols: 10,
            speed: 4.8,
            dropChance: 0.20
        };

    }

    // 높은 스테이지
    return {

        rows: Math.min(8, 6 + Math.floor((level - 7) / 3)),
        cols: 10,
        speed: Math.min(7, 4.8 + (level - 7) * 0.3),
        dropChance: 0.23

    };

}


// ============================
// 블록
// ============================

let bricks = [];


function createBricks() {

    bricks = [];

    const settings = getStageSettings();

    const rows = settings.rows;
    const cols = settings.cols;

    const brickWidth =
        (canvas.width - 70 - (cols - 1) * 7) / cols;

    const brickHeight = 22;

    for (let r = 0; r < rows; r++) {

        for (let c = 0; c < cols; c++) {

            bricks.push({

                x: 35 + c * (brickWidth + 7),

                y: 45 + r * 30,

                width: brickWidth,

                height: brickHeight,

                alive: true

            });

        }

    }

}


// ============================
// 공 생성
// ============================

function createBall(x, y, speedMultiplier = 1) {

    const settings = getStageSettings();

    const speed =
        settings.speed * speedMultiplier;

    const direction =
        Math.random() > 0.5 ? 1 : -1;

    return {

        x: x,
        y: y,

        radius: 8,

        dx: speed * direction,

        dy: -speed

    };

}


// ============================
// 공 초기화
// ============================

function resetBalls() {

    balls = [

        createBall(
            canvas.width / 2,
            canvas.height - 55
        )

    ];

}


// ============================
// 패들 그리기
// ============================

function drawPaddle() {

    ctx.fillStyle = "#3b82f6";

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );

}


// ============================
// 공 그리기
// ============================

function drawBalls() {

    balls.forEach(ball => {

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

    });

}


// ============================
// 블록 그리기
// ============================

function drawBricks() {

    const colors = [

        "#22c55e",
        "#22c55e",
        "#eab308",
        "#eab308",
        "#f97316",
        "#ef4444",
        "#ef4444",
        "#a855f7"

    ];

    bricks.forEach((brick, index) => {

        if (!brick.alive)
            return;

        ctx.fillStyle =
            colors[Math.floor(index / 10) % colors.length];

        ctx.fillRect(
            brick.x,
            brick.y,
            brick.width,
            brick.height
        );

    });

}


// ============================
// 아이템 그리기
// ============================

function drawItems() {

    items.forEach(item => {

        if (item.type === "extra") {

            ctx.fillStyle = "#22c55e";

        } else {

            ctx.fillStyle = "#f97316";

        }

        ctx.beginPath();

        ctx.arc(
            item.x,
            item.y,
            ITEM_SIZE / 2,
            0,
            Math.PI * 2
        );

        ctx.fill();

        ctx.fillStyle = "white";

        ctx.font = "bold 12px Arial";

        ctx.textAlign = "center";

        if (item.type === "extra") {

            ctx.fillText(
                "+",
                item.x,
                item.y + 4
            );

        } else {

            ctx.fillText(
                "⚡",
                item.x,
                item.y + 4
            );

        }

    });

}


// ============================
// 화면
// ============================

function draw() {

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    drawBricks();
    drawItems();
    drawPaddle();
    drawBalls();

}


// ============================
// 패들 이동
// ============================

function movePaddle() {

    paddle.x += paddle.dx;

    if (paddle.x < 0)
        paddle.x = 0;

    if (
        paddle.x + paddle.width >
        canvas.width
    ) {

        paddle.x =
            canvas.width - paddle.width;

    }

}


// ============================
// 아이템 생성
// ============================

function createItem(x, y) {

    const settings =
        getStageSettings();

    if (Math.random() > settings.dropChance)
        return;


    const type =
        Math.random() < 0.5
        ? "extra"
        : "boost";


    items.push({

        x: x,
        y: y,

        type: type,

        speed: 2.2

    });

}


// ============================
// 아이템 이동
// ============================

function moveItems() {

    items.forEach(item => {

        item.y += item.speed;

    });


    // 패들과 충돌

    items = items.filter(item => {

        if (

            item.y + ITEM_SIZE / 2 >= paddle.y &&

            item.y - ITEM_SIZE / 2 <=
                paddle.y + paddle.height &&

            item.x >= paddle.x &&

            item.x <=
                paddle.x + paddle.width

        ) {

            applyItem(item.type);

            return false;

        }


        // 화면 밖

        if (
            item.y >
            canvas.height + 30
        ) {

            return false;

        }

        return true;

    });

}


// ============================
// 아이템 효과
// ============================

function applyItem(type) {

    if (type === "extra") {

        // 현재 공의 위치에서
        // 새로운 공 생성

        const source =
            balls[0];

        if (source) {

            balls.push(

                createBall(
                    source.x,
                    source.y,
                    1
                )

            );

        }

    }


    if (type === "boost") {

        // 모든 공 속도 증가

        balls.forEach(ball => {

            ball.dx *= 1.45;
            ball.dy *= 1.45;

        });


        // 5초 후 원래 속도로 복귀

        setTimeout(() => {

            balls.forEach(ball => {

                ball.dx /= 1.45;
                ball.dy /= 1.45;

            });

        }, 5000);

    }

}


// ============================
// 공 이동
// ============================

function moveBalls() {

    for (
        let ballIndex = balls.length - 1;
        ballIndex >= 0;
        ballIndex--
    ) {

        const ball =
            balls[ballIndex];


        ball.x += ball.dx;
        ball.y += ball.dy;


        // 좌우 벽

        if (

            ball.x + ball.radius >=
                canvas.width ||

            ball.x - ball.radius <= 0

        ) {

            ball.dx *= -1;

        }


        // 위쪽 벽

        if (
            ball.y - ball.radius <= 0
        ) {

            ball.dy *= -1;

        }


        // 패들

        if (

            ball.y + ball.radius >=
                paddle.y &&

            ball.y <=
                paddle.y + paddle.height &&

            ball.x >= paddle.x &&

            ball.x <=
                paddle.x + paddle.width &&

            ball.dy > 0

        ) {

            ball.dy *= -1;


            const hit =
                (ball.x - paddle.x) /
                paddle.width;


            ball.dx =
                (hit - 0.5) *
                getStageSettings().speed *
                2.2;

        }


        // 블록 충돌

        let hitBrick = false;

        for (let brick of bricks) {

            if (!brick.alive)
                continue;


            if (

                ball.x + ball.radius >
                    brick.x &&

                ball.x - ball.radius <
                    brick.x + brick.width &&

                ball.y + ball.radius >
                    brick.y &&

                ball.y - ball.radius <
                    brick.y + brick.height

            ) {

                brick.alive = false;

                ball.dy *= -1;

                score += 10;

                scoreText.textContent =
                    score;


                // 아이템 생성

                createItem(
                    brick.x +
                    brick.width / 2,

                    brick.y +
                    brick.height / 2
                );


                hitBrick = true;

                break;

            }

        }


        // 바닥

        if (
            ball.y - ball.radius >
            canvas.height
        ) {

            balls.splice(
                ballIndex,
                1
            );

        }

    }


    // 공이 모두 사라지면 목숨 감소

    if (balls.length === 0) {

        loseLife();

        return;

    }


    // 모든 블록 제거

    if (
        bricks.every(
            brick => !brick.alive
        )
    ) {

        nextLevel();

    }

}


// ============================
// 다음 스테이지
// ============================

function nextLevel() {

    level++;

    // 스테이지 클리어 보너스
    lives++;

    levelText.textContent =
        level;

    livesText.textContent =
        lives;


    // 아이템 제거

    items = [];


    // 새로운 블록

    createBricks();


    // 공 초기화

    resetBalls();


    // 패들 초기화

    paddle

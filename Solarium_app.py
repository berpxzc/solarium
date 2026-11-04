from flask import Flask, render_template_string, jsonify, request
import random
import time

app = Flask(__name__)

# Демо-данные. В реальном проекте сюда можно передавать показания ESP32/Raspberry Pi.
latest_telemetry = {
    "voltage": 18.5,
    "current": 2.45,
    "power": 45.32,
    "temperature": 32.1,
    "efficiency": 18.2,
    "timestamp": int(time.time()),
    "status": "online",
}

HTML_TEMPLATE = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#0b151d">
    <title>SOLARIUM — Energy Studio</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #0b151d;
            --panel: #14232c;
            --panel-soft: #10212a;
            --line: #30434b;
            --yellow: #f4d35e;
            --green: #d4edb2;
            --muted: #a9bbc0;
            --text: #eef3e9;
            --good: #9ed49a;
            --bad: #ff9b86;
        }
        * { box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
            margin: 0; background: var(--bg); color: var(--text);
            font: 15px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .hero {
            padding: 34px max(20px, calc((100% - 1080px) / 2)) 38px;
            background: radial-gradient(ellipse at 82% 0%, #315b50 0%, transparent 52%), #10212a;
            border-bottom: 1px solid rgba(255,255,255,.04);
        }
        .brand {
            color: var(--yellow); font-size: 12px; font-weight: 800;
            letter-spacing: 3px; text-transform: uppercase;
        }
        h1 {
            margin: 16px 0 8px; font-size: clamp(38px, 7vw, 62px);
            line-height: 1.04; letter-spacing: -2.5px;
        }
        h1 span { color: var(--yellow); }
        .hero p { max-width: 660px; color: #d3dfd9; margin: 0; }
        .nav {
            position: sticky; top: 0; z-index: 5; display: flex; gap: 8px;
            overflow-x: auto; padding: 11px max(20px, calc((100% - 1080px) / 2));
            background: rgba(16, 29, 37, .96); border-bottom: 1px solid var(--line);
            backdrop-filter: blur(12px);
        }
        .nav a {
            color: var(--yellow); text-decoration: none; white-space: nowrap;
            border: 1px solid var(--line); border-radius: 9px;
            padding: 8px 13px; font-weight: 700; font-size: 13px;
        }
        .nav a:hover { background: #263c35; border-color: #718d62; }
        main { max-width: 1080px; margin: auto; padding: 26px 20px 36px; }
        .section-head { display: flex; justify-content: space-between; align-items: end; gap: 16px; margin-bottom: 16px; }
        h2 { font-size: 25px; margin: 0 0 5px; letter-spacing: -.5px; }
        h3 { margin: 0 0 14px; font-size: 17px; }
        .muted, .note { color: var(--muted); }
        .muted { margin: 0; }
        .status {
            display: inline-flex; align-items: center; gap: 8px; white-space: nowrap;
            color: var(--green); font-size: 12px; font-weight: 700;
            border: 1px solid var(--line); background: var(--panel);
            border-radius: 999px; padding: 8px 12px;
        }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--good); box-shadow: 0 0 12px #9ed49a88; }
        .dot.offline { background: var(--bad); box-shadow: 0 0 12px #ff9b8688; }
        .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
        .stat, .panel {
            background: var(--panel); border: 1px solid var(--line);
            border-radius: 14px; padding: 18px;
        }
        .stat small { display: block; color: var(--yellow); font-size: 12px; font-weight: 700; letter-spacing: .3px; }
        .stat strong {
            display: block; margin-top: 7px; color: var(--green);
            font-size: clamp(23px, 3vw, 30px); line-height: 1.15;
            overflow-wrap: anywhere;
        }
        .unit { color: var(--muted); font-size: 14px; font-weight: 500; }
        .panel { margin-top: 16px; }
        .panel-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 14px; }
        .live-label { color: var(--muted); font-size: 12px; }
        .chart-wrap { position: relative; height: 310px; }
        .details { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
        .detail-line {
            display: flex; justify-content: space-between; gap: 12px;
            padding: 10px 0; border-bottom: 1px solid var(--line);
        }
        .detail-line:last-child { border-bottom: 0; }
        .detail-line span:first-child { color: var(--muted); }
        .detail-line strong { color: var(--green); text-align: right; }
        .note { font-size: 12px; line-height: 1.6; margin: 16px 2px 0; }
        footer { max-width: 1080px; margin: auto; padding: 0 20px 26px; color: var(--muted); font-size: 12px; }
        @media (max-width: 760px) {
            .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .details { grid-template-columns: 1fr; }
            .section-head { align-items: start; flex-direction: column; }
            .chart-wrap { height: 260px; }
        }
        @media (max-width: 390px) {
            main { padding: 20px 13px 28px; }
            .hero { padding-left: 18px; padding-right: 18px; }
            .nav { padding-left: 13px; padding-right: 13px; }
            .stat, .panel { padding: 14px; }
        }
    </style>
</head>
<body>
    <header class="hero" id="top">
        <div class="brand">☼ SOLARIUM / ENERGY STUDIO</div>
        <h1>Power of the <span>Sun.</span></h1>
        <p>Мониторинг солнечной панели в реальном времени. Следи за мощностью, напряжением, температурой и эффективностью системы.</p>
    </header>

    <nav class="nav" aria-label="Основная навигация">
        <a href="#dashboard">Обзор</a>
        <a href="#chart">Мониторинг</a>
        <a href="#details">Показатели</a>
    </nav>

    <main>
        <section id="dashboard">
            <div class="section-head">
                <div>
                    <h2>Энергия под контролем</h2>
                    <p class="muted">Текущие параметры солнечной установки</p>
                </div>
                <div class="status" aria-live="polite">
                    <span class="dot" id="statusDot"></span>
                    <span id="statusText">Подключение...</span>
                </div>
            </div>

            <div class="grid">
                <article class="stat">
                    <small>Мощность</small>
                    <strong><span id="power">--</span> <span class="unit">Вт</span></strong>
                </article>
                <article class="stat">
                    <small>Напряжение</small>
                    <strong><span id="voltage">--</span> <span class="unit">В</span></strong>
                </article>
                <article class="stat">
                    <small>Сила тока</small>
                    <strong><span id="current">--</span> <span class="unit">А</span></strong>
                </article>
                <article class="stat">
                    <small>Температура</small>
                    <strong><span id="temp">--</span> <span class="unit">°C</span></strong>
                </article>
            </div>
        </section>

        <section class="panel" id="chart">
            <div class="panel-top">
                <div>
                    <h3>График мощности</h3>
                    <div class="live-label">Изменение мощности · последние измерения</div>
                </div>
                <div class="live-label">● LIVE</div>
            </div>
            <div class="chart-wrap">
                <canvas id="telemetryChart" aria-label="График мощности солнечной панели" role="img"></canvas>
            </div>
        </section>

        <section class="details" id="details">
            <article class="panel">
                <h3>Состояние системы</h3>
                <div class="detail-line"><span>Эффективность</span><strong id="efficiency">-- %</strong></div>
                <div class="detail-line"><span>Статус соединения</span><strong id="connection">Ожидание</strong></div>
                <div class="detail-line"><span>Последнее обновление</span><strong id="updated">--:--:--</strong></div>
            </article>
            <article class="panel">
                <h3>О проекте</h3>
                <p class="muted">SOLARIUM собирает и отображает телеметрию солнечной панели. Сейчас включён демонстрационный режим с тестовыми значениями. Для реальных показаний подключи контроллер к API.</p>
            </article>
        </section>
        <p class="note">Демонстрационные значения генерируются сервером и не являются фактическими измерениями оборудования.</p>
    </main>

    <footer>SOLARIUM © 2026 · Energy Studio · Мониторинг солнечной энергии</footer>

    <script>
        const $ = (id) => document.getElementById(id);
        const chartContext = $("telemetryChart").getContext("2d");

        const telemetryChart = new Chart(chartContext, {
            type: "line",
            data: {
                labels: [],
                datasets: [{
                    label: "Мощность (Вт)",
                    data: [],
                    borderColor: "#f4d35e",
                    backgroundColor: "rgba(212, 237, 178, .10)",
                    pointBackgroundColor: "#d4edb2",
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    borderWidth: 2,
                    fill: true,
                    tension: .35
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: { labels: { color: "#d3dfd9" } }
                },
                scales: {
                    x: {
                        ticks: { color: "#a9bbc0", maxTicksLimit: 7 },
                        grid: { color: "rgba(169,187,192,.08)" }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: "#a9bbc0" },
                        grid: { color: "rgba(169,187,192,.10)" }
                    }
                }
            }
        });

        function showNumber(value, digits = 2) {
            const number = Number(value);
            return Number.isFinite(number) ? number.toFixed(digits) : "--";
        }

        function setConnection(online) {
            $("statusText").textContent = online ? "Сервер работает" : "Нет соединения";
            $("connection").textContent = online ? "Подключено" : "Отключено";
            $("statusDot").classList.toggle("offline", !online);
        }

        async function fetchTelemetry() {
            try {
                const response = await fetch("/api/telemetry", { cache: "no-store" });
                if (!response.ok) throw new Error("HTTP " + response.status);
                const data = await response.json();

                $("power").textContent = showNumber(data.power);
                $("voltage").textContent = showNumber(data.voltage);
                $("current").textContent = showNumber(data.current);
                $("temp").textContent = showNumber(data.temperature, 1);
                $("efficiency").textContent = showNumber(data.efficiency, 1) + " %";
                $("updated").textContent = new Date().toLocaleTimeString("ru-RU");
                setConnection(true);

                const labels = telemetryChart.data.labels;
                const values = telemetryChart.data.datasets[0].data;
                labels.push(new Date().toLocaleTimeString("ru-RU"));
                values.push(Number(data.power) || 0);
                if (labels.length > 20) {
                    labels.shift();
                    values.shift();
                }
                telemetryChart.update();
            } catch (error) {
                console.error("Ошибка получения телеметрии:", error);
                setConnection(false);
            }
        }

        fetchTelemetry();
        window.setInterval(fetchTelemetry, 2000);
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Главная страница SOLARIUM."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/telemetry", methods=["GET"])
def get_telemetry():
    """Возвращает текущую телеметрию (демо-режим)."""
    voltage = round(18.0 + random.uniform(-0.5, 0.5), 2)
    current = round(2.4 + random.uniform(-0.2, 0.2), 2)
    latest_telemetry.update({
        "voltage": voltage,
        "current": current,
        "power": round(voltage * current, 2),
        "temperature": round(30.0 + random.uniform(0, 3), 1),
        "efficiency": round(17.5 + random.uniform(-1.0, 1.0), 1),
        "timestamp": int(time.time()),
        "status": "online",
    })
    return jsonify(latest_telemetry)


@app.route("/api/telemetry", methods=["POST"])
def update_telemetry():
    """Принимает реальные показания от ESP32/Raspberry Pi."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"status": "error", "message": "Ожидается JSON-объект с показаниями"}), 400

    allowed_fields = {"voltage", "current", "power", "temperature", "efficiency", "timestamp", "status"}
    latest_telemetry.update({key: value for key, value in data.items() if key in allowed_fields})
    latest_telemetry["timestamp"] = int(time.time())
    return jsonify({"status": "success", "message": "Данные обновлены"}), 200


if __name__ == "__main__":
    # Запуск: python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)

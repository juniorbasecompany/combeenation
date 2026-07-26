(() => {
    const bee = document.querySelector(".bee-flight");
    if (!bee) return;

    const randomDelay = () => Math.floor(Math.random() * 9001) + 1000;
    const fadeDuration = 800;
    let phaseTimer;
    let changeFlightDirection = () => {};

    function showBee() {
        window.clearTimeout(phaseTimer);
        bee.classList.remove("edge-hidden");
        void bee.offsetWidth;
        bee.classList.add("is-visible");
        phaseTimer = window.setTimeout(hideBee, randomDelay());
    }

    function hideBee(immediate = false) {
        if (!bee.classList.contains("is-visible")) return;
        window.clearTimeout(phaseTimer);
        if (immediate) bee.classList.add("edge-hidden");
        bee.classList.remove("is-visible");
        phaseTimer = window.setTimeout(() => {
            changeFlightDirection();
            phaseTimer = window.setTimeout(showBee, randomDelay());
        }, immediate ? 0 : fadeDuration);
    }

    showBee();

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const beeSize = 50;
    const edgeZone = 110;
    let x = window.innerWidth * 0.2;
    let y = window.innerHeight * 0.25;
    let vx = 42;
    let vy = 12;
    let desiredVx = vx;
    let desiredVy = vy;
    let wavePhaseA = Math.random() * Math.PI * 2;
    let wavePhaseB = Math.random() * Math.PI * 2;
    let waveStrength = 22;
    let currentTilt = 0;
    let previousTime = performance.now();

    function chooseDirection() {
        const maxX = Math.max(0, window.innerWidth - beeSize);
        const maxY = Math.max(0, window.innerHeight - beeSize);
        const nearEdge =
            x < edgeZone || x > maxX - edgeZone ||
            y < edgeZone || y > maxY - edgeZone;

        const currentAngle = Math.atan2(vy, vx);
        const centerAngle = Math.atan2(maxY / 2 - y, maxX / 2 - x);
        const angle = nearEdge
            ? centerAngle + (Math.random() - 0.5) * 0.7
            : currentAngle + (Math.random() - 0.5) * 2.2;
        const speed = 200 + Math.random() * 300;

        desiredVx = Math.cos(angle) * speed;
        desiredVy = Math.sin(angle) * speed;
        wavePhaseA = Math.random() * Math.PI * 2;
        wavePhaseB = Math.random() * Math.PI * 2;
        waveStrength = 18 + Math.random() * 14;
    }

    function fly(now) {
        const dt = Math.min((now - previousTime) / 1000, 0.04);
        previousTime = now;

        const baseSpeed = Math.hypot(desiredVx, desiredVy) || 1;
        const normalX = -desiredVy / baseSpeed;
        const normalY = desiredVx / baseSpeed;
        const wave =
            Math.sin(now * 0.0075 + wavePhaseA) * waveStrength * 2.4 +
            Math.sin(now * 0.019 + wavePhaseB) * waveStrength * 0.9;
        const targetVx = desiredVx + normalX * wave;
        const targetVy = desiredVy + normalY * wave;
        const steering = 1 - Math.exp(-6.5 * dt);

        vx += (targetVx - vx) * steering;
        vy += (targetVy - vy) * steering;
        x += vx * dt;
        y += vy * dt;

        const maxX = Math.max(0, window.innerWidth - beeSize);
        const maxY = Math.max(0, window.innerHeight - beeSize);
        x = Math.max(0, Math.min(maxX, x));
        y = Math.max(0, Math.min(maxY, y));
        if (
            (x === 0 && vx < 0) || (x === maxX && vx > 0) ||
            (y === 0 && vy < 0) || (y === maxY && vy > 0)
        ) {
            hideBee(true);
        }

        if (desiredVx > 2) bee.classList.add("facing-right");
        if (desiredVx < -2) bee.classList.remove("facing-right");

        const slope = Math.atan2(vy, Math.max(12, Math.abs(vx)));
        const targetTilt = Math.max(
            -18,
            Math.min(18, slope * 180 / Math.PI * Math.sign(vx))
        );
        const tiltSmoothing = 1 - Math.exp(-1.8 * dt);
        currentTilt += (targetTilt - currentTilt) * tiltSmoothing;
        bee.style.transform =
            `translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, 0) rotate(${currentTilt.toFixed(2)}deg)`;

        requestAnimationFrame(fly);
    }

    changeFlightDirection = () => chooseDirection();
    changeFlightDirection();
    requestAnimationFrame(fly);
})();

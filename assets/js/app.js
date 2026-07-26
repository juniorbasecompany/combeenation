        const translations = window.COMBEENATION_TRANSLATIONS;


        const originalText = new WeakMap();
        const translatableAttributes = ["placeholder", "aria-label", "title"];

        function setLanguage(language) {
            const dictionary = translations[language] || {};
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
                acceptNode(node) {
                    return ["SCRIPT", "STYLE"].includes(node.parentElement?.tagName)
                        ? NodeFilter.FILTER_REJECT
                        : NodeFilter.FILTER_ACCEPT;
                }
            });

            let node;
            while ((node = walker.nextNode())) {
                if (!originalText.has(node)) originalText.set(node, node.nodeValue);
                const source = originalText.get(node);
                const trimmed = source.trim();
                if (!trimmed) continue;
                const translated = dictionary[trimmed] || trimmed;
                node.nodeValue = source.replace(trimmed, translated);
            }

            document.querySelectorAll("*").forEach(element => {
                translatableAttributes.forEach(attribute => {
                    if (!element.hasAttribute(attribute)) return;
                    const dataKey = `original${attribute.replace(/(^|-)(\w)/g, (_, __, letter) => letter.toUpperCase())}`;
                    if (!element.dataset[dataKey]) element.dataset[dataKey] = element.getAttribute(attribute);
                    const source = element.dataset[dataKey];
                    element.setAttribute(attribute, dictionary[source] || source);
                });
            });

            document.documentElement.lang = language === "pt" ? "pt-BR" : language;
            document.title = language === "es"
                ? "ComBEEnation | Salvando abejas en el sur de Florida"
                : language === "pt"
                    ? "ComBEEnation | Salvando abelhas no sul da Flórida"
                    : "ComBEEnation | Saving Bees Across South Florida";
            document.querySelectorAll("[data-language]").forEach(button => {
                button.setAttribute("aria-pressed", String(button.dataset.language === language));
            });
            localStorage.setItem("combeenation-language", language);
        }

        document.querySelectorAll("[data-language]").forEach(button => {
            button.addEventListener("click", () => setLanguage(button.dataset.language));
        });

        const menuButton = document.querySelector(".menu-toggle");
        const menu = document.querySelector(".nav__links");

        function closeMenu() {
            menu.classList.remove("is-open");
            document.body.classList.remove("menu-open");
            menuButton.setAttribute("aria-expanded", "false");
            menuButton.setAttribute("aria-label", "Open navigation menu");
            menuButton.textContent = "☰";
        }

        menuButton.addEventListener("click", () => {
            const isOpen = menu.classList.toggle("is-open");
            document.body.classList.toggle("menu-open", isOpen);
            menuButton.setAttribute("aria-expanded", String(isOpen));
            menuButton.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
            menuButton.textContent = isOpen ? "×" : "☰";
        });

        menu.querySelectorAll("a").forEach(link => link.addEventListener("click", closeMenu));

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        document.querySelectorAll(".reveal").forEach(element => observer.observe(element));

        const backToTopButton = document.querySelector(".back-to-top");

        function updateBackToTopButton() {
            backToTopButton.classList.toggle("is-visible", window.scrollY > 500);
        }

        backToTopButton.addEventListener("click", () => {
            const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
            backToTopButton.classList.add("is-pressed");

            window.setTimeout(() => {
                backToTopButton.classList.remove("is-pressed");
                window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" });
            }, reducedMotion ? 0 : 120);
        });
        window.addEventListener("scroll", updateBackToTopButton, { passive: true });
        updateBackToTopButton();

        document.getElementById("request-form").addEventListener("submit", (event) => {
            event.preventDefault();
            const data = new FormData(event.currentTarget);
            const subject = encodeURIComponent(`${data.get("need")} request from ${data.get("name")}`);
            const body = encodeURIComponent(
                `Name: ${data.get("name")}\n` +
                `Phone: ${data.get("phone")}\n` +
                `Need: ${data.get("need")}\n` +
                `City / ZIP: ${data.get("location")}\n\n` +
                `Details:\n${data.get("message") || "No additional details provided."}`
            );
            document.getElementById("form-status").textContent = "Opening your email app…";
            window.location.href = `mailto:comBEEnationFL@gmail.com?subject=${subject}&body=${body}`;
        });

        document.getElementById("year").textContent = new Date().getFullYear();

        const savedLanguage = localStorage.getItem("combeenation-language");
        const browserLanguage = navigator.language.toLowerCase();
        const initialLanguage = savedLanguage || (browserLanguage.startsWith("pt") ? "pt" : browserLanguage.startsWith("es") ? "es" : "en");
        setLanguage(initialLanguage);

        const bee = document.querySelector(".bee-flight");
        if (bee) {
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

            if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
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
            }
        }

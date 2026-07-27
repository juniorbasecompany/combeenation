        const translations = window.COMBEENATION_TRANSLATIONS;


        const originalText = new WeakMap();
        const translatableAttributes = ["placeholder", "aria-label", "title", "alt"];

        function normalizeKey(text) {
            return text.replace(/\s+/g, " ").trim();
        }

        function translate(text, language) {
            const dictionary = translations[language] || {};
            const key = normalizeKey(text);
            return dictionary[key] || text;
        }

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
                const key = normalizeKey(source);
                if (!key) continue;
                const translated = dictionary[key];
                if (!translated) {
                    node.nodeValue = source;
                    continue;
                }
                const leading = source.match(/^\s*/)[0];
                const trailing = source.match(/\s*$/)[0];
                node.nodeValue = leading + translated + trailing;
            }

            document.querySelectorAll("*").forEach(element => {
                translatableAttributes.forEach(attribute => {
                    if (!element.hasAttribute(attribute)) return;
                    const dataKey = `original${attribute.replace(/(^|-)(\w)/g, (_, __, letter) => letter.toUpperCase())}`;
                    if (!element.dataset[dataKey]) element.dataset[dataKey] = element.getAttribute(attribute);
                    const source = element.dataset[dataKey];
                    element.setAttribute(attribute, dictionary[normalizeKey(source)] || source);
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
            document.documentElement.dataset.language = language;
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
            menuButton.setAttribute("aria-label", translate("Open navigation menu", document.documentElement.dataset.language || "en"));
            menuButton.textContent = "☰";
        }

        menuButton.addEventListener("click", () => {
            const isOpen = menu.classList.toggle("is-open");
            const language = document.documentElement.dataset.language || "en";
            document.body.classList.toggle("menu-open", isOpen);
            menuButton.setAttribute("aria-expanded", String(isOpen));
            menuButton.setAttribute(
                "aria-label",
                translate(isOpen ? "Close navigation menu" : "Open navigation menu", language)
            );
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
            const language = document.documentElement.dataset.language || "en";
            const subject = encodeURIComponent(`${data.get("need")} request from ${data.get("name")}`);
            const body = encodeURIComponent(
                `Name: ${data.get("name")}\n` +
                `Phone: ${data.get("phone")}\n` +
                `Need: ${data.get("need")}\n` +
                `City / ZIP: ${data.get("location")}\n\n` +
                `Details:\n${data.get("message") || "No additional details provided."}`
            );
            document.getElementById("form-status").textContent = translate("Opening your email app…", language);
            window.location.href = `mailto:comBEEnationFL@gmail.com?subject=${subject}&body=${body}`;
        });

        document.getElementById("year").textContent = new Date().getFullYear();

        const savedLanguage = localStorage.getItem("combeenation-language");
        const browserLanguage = navigator.language.toLowerCase();
        const initialLanguage = savedLanguage || (browserLanguage.startsWith("pt") ? "pt" : browserLanguage.startsWith("es") ? "es" : "en");
        setLanguage(initialLanguage);

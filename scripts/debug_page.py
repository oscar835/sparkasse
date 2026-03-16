import asyncio
from playwright.async_api import async_playwright


async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        print("Navigiere zur Seite...")
        await page.goto(
            "https://www.sparkasse.at/investments/produkte/muenzen-und-barren",
            wait_until="networkidle",
            timeout=60000,
        )

        # Cookie-Banner akzeptieren
        try:
            cookie_btn = page.locator(
                "button:has-text('Alle akzeptieren'), "
                "#onetrust-accept-btn-handler"
            )
            if await cookie_btn.first.is_visible(timeout=5000):
                await cookie_btn.first.click()
                await page.wait_for_timeout(3000)
        except Exception:
            pass

        await page.wait_for_timeout(5000)

        # Screenshot der ganzen Seite
        await page.screenshot(path="debug_full.png", full_page=True)
        print("Screenshot gespeichert: debug_full.png")

        # Alle sichtbaren Texte mit "auswähl" oder "download" finden
        print("\n=== SUCHE NACH RELEVANTEN ELEMENTEN ===\n")

        elements = await page.evaluate("""() => {
            const results = [];
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const text = el.textContent.trim().toLowerCase();
                const tag = el.tagName.toLowerCase();
                const classes = el.className || '';
                const id = el.id || '';
                const role = el.getAttribute('role') || '';
                const type = el.getAttribute('type') || '';
                const disabled = el.hasAttribute('disabled');
                
                // Nur direkte Texte (nicht von Kindern)
                let ownText = '';
                for (const node of el.childNodes) {
                    if (node.nodeType === 3) {
                        ownText += node.textContent.trim();
                    }
                }
                
                if (ownText.toLowerCase().includes('auswähl') || 
                    ownText.toLowerCase().includes('auswahl') ||
                    ownText.toLowerCase().includes('select') ||
                    ownText.toLowerCase().includes('download') ||
                    ownText.toLowerCase().includes('herunterladen') ||
                    ownText.toLowerCase().includes('excel') ||
                    ownText.toLowerCase().includes('alle') ||
                    classes.toString().toLowerCase().includes('select') ||
                    classes.toString().toLowerCase().includes('download') ||
                    classes.toString().toLowerCase().includes('check')) {
                    
                    if (ownText.length > 0 && ownText.length < 100) {
                        results.push({
                            tag: tag,
                            ownText: ownText.substring(0, 80),
                            classes: classes.toString().substring(0, 120),
                            id: id,
                            role: role,
                            type: type,
                            disabled: disabled,
                            href: el.href || '',
                            outerHTML: el.outerHTML.substring(0, 300)
                        });
                    }
                }
            }
            return results;
        }""")

        for el in elements:
            print(f"<{el['tag']}> text='{el['ownText']}'")
            print(f"   class='{el['classes']}'")
            print(f"   id='{el['id']}' role='{el['role']}' disabled={el['disabled']}")
            print(f"   HTML: {el['outerHTML'][:200]}")
            print()

        # Alle Checkboxen finden
        print("\n=== CHECKBOXEN ===\n")
        checkboxes = await page.evaluate("""() => {
            const results = [];
            const cbs = document.querySelectorAll(
                'input[type="checkbox"], [role="checkbox"], .checkbox, [class*="check"]'
            );
            for (const el of cbs) {
                results.push({
                    tag: el.tagName,
                    classes: (el.className || '').toString().substring(0, 120),
                    id: el.id || '',
                    checked: el.checked || false,
                    outerHTML: el.outerHTML.substring(0, 300)
                });
            }
            return results;
        }""")

        for cb in checkboxes:
            print(f"  <{cb['tag']}> id='{cb['id']}' checked={cb['checked']}")
            print(f"    class='{cb['classes']}'")
            print(f"    HTML: {cb['outerHTML'][:200]}")
            print()

        # Alle Buttons finden
        print("\n=== ALLE BUTTONS ===\n")
        buttons = await page.evaluate("""() => {
            const results = [];
            const btns = document.querySelectorAll(
                'button, [role="button"], a.btn, .btn'
            );
            for (const el of btns) {
                let ownText = el.textContent.trim().substring(0, 80);
                results.push({
                    tag: el.tagName,
                    text: ownText,
                    classes: (el.className || '').toString().substring(0, 120),
                    disabled: el.hasAttribute('disabled'),
                    outerHTML: el.outerHTML.substring(0, 300)
                });
            }
            return results;
        }""")

        for btn in buttons:
            print(f"  <{btn['tag']}> text='{btn['text']}' disabled={btn['disabled']}")
            print(f"    class='{btn['classes']}'")
            print(f"    HTML: {btn['outerHTML'][:250]}")
            print()

        # Gesamtes HTML der Seite speichern
        html = await page.content()
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Komplettes HTML gespeichert: debug_page.html")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())

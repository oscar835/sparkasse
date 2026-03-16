import asyncio
import glob
import os
from playwright.async_api import async_playwright


async def download_excel():
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        print("Navigiere zur Sparkasse-Seite...")
        await page.goto(
            "https://www.sparkasse.at/investments/produkte/muenzen-und-barren",
            wait_until="networkidle",
            timeout=60000,
        )

        # Lange warten bis alles geladen ist
        await page.wait_for_timeout(5000)

        # --- SCHRITT 1: Cookie-Banner (TrustCommander) ---
        print("Suche Cookie-Banner...")
        try:
            cookie_btn = page.locator("#popin_tc_privacy_button")
            await cookie_btn.wait_for(state="visible", timeout=10000)
            await cookie_btn.click()
            print("Cookie-Banner: 'Ich bin einverstanden' geklickt!")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Cookie-Banner nicht gefunden: {e}")
            # Fallback: per JavaScript schliessen
            try:
                await page.evaluate("""() => {
                    const btn = document.getElementById('popin_tc_privacy_button');
                    if (btn) btn.click();
                }""")
                print("Cookie-Banner per JavaScript geschlossen")
                await page.wait_for_timeout(3000)
            except Exception:
                print("Cookie-Banner wirklich nicht vorhanden")

        # --- SCHRITT 2: Consent Modal Dialog schliessen ---
        print("Suche Consent-Dialog...")
        try:
            # Warte auf den Modal-Dialog
            modal = page.locator('dialog[data-testid="modal"]')
            await modal.wait_for(state="visible", timeout=10000)
            print("Modal-Dialog gefunden!")

            # Klicke "Akzeptieren" INNERHALB des Modals
            accept_btn = modal.locator('button:has-text("Akzeptieren")')
            await accept_btn.click(timeout=5000)
            print("Consent-Dialog: 'Akzeptieren' geklickt!")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Consent-Dialog Klick fehlgeschlagen: {e}")
            # Fallback: per JavaScript alle Dialoge schliessen
            try:
                await page.evaluate("""() => {
                    // Alle offenen Dialoge schliessen
                    document.querySelectorAll('dialog[open]').forEach(d => d.close());
                    // Akzeptieren-Button suchen und klicken
                    const btns = document.querySelectorAll('[data-testid="button-accept"]');
                    btns.forEach(b => b.click());
                }""")
                print("Dialoge per JavaScript geschlossen")
                await page.wait_for_timeout(3000)
            except Exception:
                pass

        # --- SCHRITT 3: Pruefen ob noch Dialoge offen sind ---
        still_open = await page.evaluate("""() => {
            const dialogs = document.querySelectorAll('dialog[open]');
            return dialogs.length;
        }""")
        if still_open > 0:
            print(f"WARNUNG: Noch {still_open} Dialog(e) offen - schliesse per JS...")
            await page.evaluate("""() => {
                document.querySelectorAll('dialog[open]').forEach(d => {
                    d.close();
                    d.removeAttribute('open');
                    d.style.display = 'none';
                });
                // Auch alle Overlays entfernen
                document.querySelectorAll('[class*="overlay"], [class*="modal"]').forEach(el => {
                    el.style.display = 'none';
                });
            }""")
            await page.wait_for_timeout(2000)

        # --- SCHRITT 4: Zur Tabelle scrollen und "Alle auswählen" klicken ---
        print("Suche 'Alle auswaehlen' Button...")
        alle_btn = page.locator(
            'button.btn--secondary:has(span.wb:text-is("Alle auswählen"))'
        )
        await alle_btn.scroll_into_view_if_needed(timeout=10000)
        await page.wait_for_timeout(1000)

        # Screenshot VOR dem Klick (zum Debuggen)
        await page.screenshot(path="before_click.png")

        # force=True umgeht die "element is covered" Pruefung
        await alle_btn.click(force=True)
        print("'Alle auswaehlen' geklickt!")

        await page.wait_for_timeout(3000)

        # --- SCHRITT 5: Prüfen ob Checkboxen aktiviert wurden ---
        checked_count = await page.evaluate("""() => {
            const cbs = document.querySelectorAll('button[role="checkbox"][aria-checked="true"]');
            return cbs.length;
        }""")
        print(f"Aktivierte Checkboxen: {checked_count}")

        if checked_count == 0:
            print("Keine Checkboxen aktiviert - aktiviere alle manuell...")
            await page.evaluate("""() => {
                const cbs = document.querySelectorAll('button[role="checkbox"][aria-checked="false"]');
                cbs.forEach(cb => cb.click());
            }""")
            await page.wait_for_timeout(3000)
            checked_count = await page.evaluate("""() => {
                return document.querySelectorAll('button[role="checkbox"][aria-checked="true"]').length;
            }""")
            print(f"Jetzt aktivierte Checkboxen: {checked_count}")

        # --- SCHRITT 6: Warten bis Download-Button ENABLED wird ---
        print("Warte auf Download-Button...")
        try:
            await page.wait_for_function(
                """() => {
                    const buttons = document.querySelectorAll('button.btn--secondary');
                    for (const btn of buttons) {
                        const span = btn.querySelector('span.wb');
                        if (span && span.textContent.trim() === 'Download' && !btn.disabled) {
                            return true;
                        }
                    }
                    return false;
                }""",
                timeout=10000,
            )
            print("Download-Button ist aktiv!")
        except Exception:
            print("Download-Button noch disabled - erzwinge Aktivierung...")
            await page.evaluate("""() => {
                const buttons = document.querySelectorAll('button.btn--secondary');
                for (const btn of buttons) {
                    const span = btn.querySelector('span.wb');
                    if (span && span.textContent.trim() === 'Download') {
                        btn.disabled = false;
                        btn.removeAttribute('disabled');
                    }
                }
            }""")
            await page.wait_for_timeout(1000)

        # --- SCHRITT 7: Download klicken ---
        print("Klicke 'Download'...")
        dl_btn = page.locator(
            'button.btn--secondary:has(span.wb:text-is("Download"))'
        )

        async with page.expect_download(timeout=30000) as download_info:
            await dl_btn.click(force=True)

        download = await download_info.value
        filename = download.suggested_filename
        dest_path = os.path.join(download_dir, filename)
        await download.save_as(dest_path)
        print(f"Datei gespeichert: {dest_path}")

        await browser.close()

    # Pruefen ob Datei existiert
    files = glob.glob(os.path.join(download_dir, "*"))
    if files:
        print("\nErfolgreich heruntergeladen:")
        for f in files:
            size = os.path.getsize(f)
            print(f"  {os.path.basename(f)} ({size} Bytes)")
    else:
        raise Exception("Download fehlgeschlagen - keine Datei gefunden!")

    return dest_path


if __name__ == "__main__":
    asyncio.run(download_excel())

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

        await page.wait_for_timeout(3000)

        # --- SCHRITT 1: Cookie-Banner "Ich bin einverstanden" ---
        try:
            cookie_btn = page.locator("#popin_tc_privacy_button")
            await cookie_btn.click(timeout=5000)
            print("Cookie-Banner akzeptiert")
            await page.wait_for_timeout(2000)
        except Exception:
            print("Kein Cookie-Banner gefunden")

        # --- SCHRITT 2: Consent-Dialog "Akzeptieren" ---
        try:
            accept_btn = page.locator('[data-testid="button-accept"]')
            await accept_btn.click(timeout=5000)
            print("Consent-Dialog akzeptiert")
            await page.wait_for_timeout(2000)
        except Exception:
            print("Kein Consent-Dialog gefunden")

        await page.wait_for_timeout(2000)

        # --- SCHRITT 3: "Alle auswählen" klicken ---
        print("Klicke 'Alle auswaehlen'...")
        alle_btn = page.locator(
            'button.btn--secondary:has(span.wb:text-is("Alle auswählen"))'
        )
        await alle_btn.scroll_into_view_if_needed(timeout=10000)
        await page.wait_for_timeout(1000)
        await alle_btn.click()
        print("'Alle auswaehlen' erfolgreich geklickt!")

        await page.wait_for_timeout(3000)

        # --- SCHRITT 4: Warten bis Download-Button ENABLED wird ---
        print("Warte bis Download-Button aktiv wird...")
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

        # --- SCHRITT 5: Download klicken ---
        print("Klicke 'Download'...")
        dl_btn = page.locator(
            'button.btn--secondary:has(span.wb:text-is("Download"))'
        )

        async with page.expect_download(timeout=30000) as download_info:
            await dl_btn.click()

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

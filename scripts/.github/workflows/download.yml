import asyncio
import glob
import os
import shutil
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

        # Cookie-Banner akzeptieren
        try:
            cookie_btn = page.locator(
                "button:has-text('Alle akzeptieren'), "
                "#onetrust-accept-btn-handler"
            )
            if await cookie_btn.first.is_visible(timeout=5000):
                print("Cookie-Banner akzeptieren...")
                await cookie_btn.first.click()
                await page.wait_for_timeout(2000)
        except Exception:
            print("Kein Cookie-Banner gefunden")

        await page.wait_for_timeout(3000)

        # "Alles auswählen" klicken
        print("Klicke auf Alles auswaehlen...")
        try:
            alles_btn = page.locator(
                "text='Alles auswählen', "
                "text='ALLES AUSWÄHLEN', "
                "button:has-text('Alles auswählen'), "
                "a:has-text('Alles auswählen'), "
                "label:has-text('Alles auswählen')"
            )
            await alles_btn.first.scroll_into_view_if_needed(timeout=10000)
            await page.wait_for_timeout(1000)
            await alles_btn.first.click(timeout=10000)
            print("Alles auswaehlen geklickt!")
        except Exception as e:
            print(f"Fehler bei Alles auswaehlen: {e}")
            checkboxes = page.locator("input[type='checkbox']")
            count = await checkboxes.count()
            for i in range(count):
                try:
                    if not await checkboxes.nth(i).is_checked():
                        await checkboxes.nth(i).click()
                except Exception:
                    pass

        await page.wait_for_timeout(2000)

        # "Download" klicken
        print("Klicke auf Download...")
        async with page.expect_download(timeout=30000) as download_info:
            dl_btn = page.locator(
                "button:has-text('Download'), "
                "a:has-text('Download'), "
                "button:has-text('Herunterladen'), "
                "a:has-text('Herunterladen')"
            )
            await dl_btn.first.scroll_into_view_if_needed(timeout=10000)
            await dl_btn.first.click(timeout=10000)

        download = await download_info.value
        dest_path = os.path.join(download_dir, download.suggested_filename)
        await download.save_as(dest_path)
        print(f"Gespeichert: {dest_path}")

        await browser.close()

    files = glob.glob(os.path.join(download_dir, "*"))
    if files:
        for f in files:
            print(f"Datei: {os.path.basename(f)} ({os.path.getsize(f)} Bytes)")
    else:
        raise Exception("Download fehlgeschlagen!")

    return dest_path


if __name__ == "__main__":
    asyncio.run(download_excel())

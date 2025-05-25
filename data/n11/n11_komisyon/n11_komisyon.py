from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import traceback
import os

# KULLANICI AYARLARI
URL = "https://magazadestek.n11.com/s/komisyon-oranlari"  # Başlangıç linki
CHROMEDRIVER_PATH = r"C:\Users\akins\Desktop\fullSite\data\n11\n11_komisyon\chromedriver.exe"  # chromedriver.exe tam yolu
CHROME_PROFILE_PATH = r"C:\Users\akins\AppData\Local\Google\Chrome\User Data\Default"  # Kendi Chrome profilinin yolu

OUTPUT_JSON = "n11_komisyon.json"


def get_total_pages(driver):
    # Yeni pagination yapısına göre
    try:
        pagination = driver.find_element(By.ID, "pagination")
        page_buttons = pagination.find_elements(By.CSS_SELECTOR, "button.pagination-btn")
        page_numbers = [int(btn.text.strip()) for btn in page_buttons if btn.text.strip().isdigit()]
        return max(page_numbers) if page_numbers else 1
    except Exception:
        return 1

def parse_table(soup, page):
    table = soup.find("table")
    if not table:
        print(f"UYARI: Sayfa {page} için tablo bulunamadı!")
        return []
    else:
        print(f"Sayfa {page}: Tablo bulundu.")
    rows = table.find_all("tr")[1:]  # ilk satır başlık
    data = []
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) < 5:
            continue
        ana_kategori = cols[0]
        kategori = cols[1]
        urun_grubu = cols[2]
        kdv_raw = cols[4].replace(",", ".").replace("%", "").strip()
        try:
            kdv = float(kdv_raw) / 100
        except ValueError:
            kdv = 0
        data.append({
            "ana_kategori": ana_kategori,
            "kategori": kategori,
            "urun_grubu": urun_grubu,
            "kdv": kdv
        })
    return data

def wait_for_table_change(driver, old_first_row_text, page, timeout=10):
    for _ in range(timeout * 2):
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")[1:]
            if rows:
                first_row_text = rows[0].get_text(strip=True)
                if first_row_text != old_first_row_text:
                    return True
        time.sleep(0.5)
    print(f"UYARI: Tablo değişimi veya aktif sayfa beklenirken zaman aşımı! (Sayfa {page})")
    return False

def main():
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-data-dir={CHROME_PROFILE_PATH}')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    time.sleep(4)
    total_pages = get_total_pages(driver)
    print(f"Toplam sayfa: {total_pages}")
    all_data = []
    for page in range(1, total_pages + 1):
        print(f"Sayfa {page} çekiliyor...")
        debug1 = f"pagination_debug_{page}.html"
        with open(debug1, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        if os.path.exists(debug1):
            os.remove(debug1)
        if page > 1:
            try:
                pagination = driver.find_element(By.ID, "pagination")
                page_buttons = pagination.find_elements(By.CSS_SELECTOR, "button.pagination-btn")
                found = False
                for btn in page_buttons:
                    if btn.text.strip() == str(page):
                        found = True
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        table = soup.find("table")
                        rows = table.find_all("tr")[1:] if table else []
                        old_first_row_text = rows[0].get_text(strip=True) if rows else None
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", btn)
                        print(f"DEBUG: {page}. sayfa butonuna tıklandı.")
                        wait_for_table_change(driver, old_first_row_text, page, timeout=10)
                        time.sleep(1)
                        break
                if not found:
                    print(f"UYARI: Sayfa {page} için uygun pagination butonu bulunamadı!")
            except Exception as e:
                print(f"Sayfa {page} için pagination tıklanamadı: {e}")
                traceback.print_exc()
                continue  # Hata olsa da devam et
        time.sleep(2)
        debug2 = f"debug_page_{page}.html"
        with open(debug2, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        if os.path.exists(debug2):
            os.remove(debug2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_data = parse_table(soup, page)
        all_data.extend(page_data)
    driver.quit()

    # Gruplama: ana_kategori, kategori, kdv'ye göre
    grouped = []
    group_map = {}
    for row in all_data:
        key = (row["ana_kategori"], row["kategori"], row["kdv"])
        if key not in group_map:
            group_obj = {
                "no": len(grouped) + 1,
                "ana_kategori": row["ana_kategori"],
                "kategori": row["kategori"],
                "kdv": row["kdv"],
                "urun_grubu_detayi": []
            }
            grouped.append(group_obj)
            group_map[key] = group_obj
        if row["urun_grubu"] and row["urun_grubu"] not in group_map[key]["urun_grubu_detayi"]:
            group_map[key]["urun_grubu_detayi"].append(row["urun_grubu"])

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(grouped, f, ensure_ascii=False, indent=2)
    print(f"{OUTPUT_JSON} dosyası oluşturuldu.")
    input("Script bitti. Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    main() 
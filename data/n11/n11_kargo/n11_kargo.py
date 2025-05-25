import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# KULLANICI AYARLARI
URL = "https://www.n11.com/kampanyalar/ozel-kargo-kampanyasi"
CHROMEDRIVER_PATH = r"C:\Users\akins\Desktop\fullSite\data\n11\n11_kargo\chromedriver.exe"
CHROME_PROFILE_PATH = r"C:\Users\akins\AppData\Local\Google\Chrome\User Data\Default"
OUTPUT_JSON = "n11_kargo.json"

KARGO_SIRASI = [
    "Sürat Kargo",
    "PTT Kargo",
    "Aras Kargo",
    "Yurtiçi Kargo",
    "MNG Kargo",
    "Kolay Gelsin/Sendeo"
]

def main():
    service = Service(CHROMEDRIVER_PATH)
    options = Options()
    options.add_argument(f'user-data-dir={CHROME_PROFILE_PATH}')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    print("Sayfa yükleniyor...")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Ana tabloyu bul
    table = None
    for t in soup.find_all("table"):
        ths = [th.get_text(strip=True) for th in t.find_all("th")]
        if "KG/desi" in ths and any(k in ths for k in KARGO_SIRASI):
            table = t
            break
    if not table:
        print("Tablo bulunamadı!")
        return

    # Başlıkları ve indexlerini bul
    ths = [th.get_text(strip=True) for th in table.find_all("th")]
    kargo_indices = {}
    for kargo in KARGO_SIRASI:
        if kargo in ths:
            kargo_indices[kargo] = ths.index(kargo)
    kg_index = ths.index("KG/desi") if "KG/desi" in ths else 0

    # Sadeleştirilmiş JSON çıktısı
    kargo_json = {}
    for kargo in KARGO_SIRASI:
        fiyatlar = []
        for tr in table.find_all("tr"):
            tds = [td.get_text(strip=True).replace(",", ".") for td in tr.find_all("td")]
            if len(tds) < len(ths):
                continue
            try:
                desi = int(float(tds[kg_index]))
                fiyat = float(tds[kargo_indices[kargo]])
                fiyat_kdvli = round(fiyat * 1.20, 2)
                fiyatlar.append({
                    "desi": desi,
                    "fiyat_kdv_dahil": fiyat_kdvli
                })
            except Exception:
                continue
        kargo_json[kargo] = fiyatlar

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(kargo_json, f, ensure_ascii=False, indent=2)
    print(f"{OUTPUT_JSON} dosyası oluşturuldu!")

if __name__ == "__main__":
    main() 
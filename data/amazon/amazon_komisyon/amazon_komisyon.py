from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time

URL = "https://sellercentral.amazon.com.tr/help/hub/reference/external/G200336920"

def fetch_table_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    time.sleep(5)
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="help-table")
    if table:
        rows = table.find_all("tr")[1:]  # başlık hariç
        komisyonlar = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            kategori = cols[0].get_text(strip=True)
            try:
                komisyon_raw = cols[1].get_text(strip=True).replace("%", "").replace(",", ".")
                komisyon = float(komisyon_raw) / 100
            except Exception:
                komisyon = None
            # Fiyat aralığına göre değişen kategoriler
            if kategori == "Kişisel Bakım ve Kozmetik":
                komisyonlar.append({"kategori": "Kişisel Bakım ve Kozmetik (toplam satış fiyatı 500 TL veya daha düşükse)", "kdv": 0.09})
                komisyonlar.append({"kategori": "Kişisel Bakım ve Kozmetik (toplam satış fiyatı 500 TL'den yüksekse)", "kdv": 0.14})
            elif kategori == "Gıda Ürünleri":
                komisyonlar.append({"kategori": "Gıda Ürünleri (toplam satış fiyatı 500 TL veya daha düşükse)", "kdv": 0.09})
                komisyonlar.append({"kategori": "Gıda Ürünleri (toplam satış fiyatı 500 TL'den yüksekse)", "kdv": 0.13})
            elif kategori == "Takı":
                komisyonlar.append({"kategori": "Takı (toplam satış fiyatı 900 TL veya daha düşükse)", "kdv": 0.20})
                komisyonlar.append({"kategori": "Takı (toplam satış fiyatı 900 TL'den yüksekse)", "kdv": 0.03})
            else:
                komisyonlar.append({"kategori": kategori, "kdv": komisyon})
        if komisyonlar:
            return komisyonlar
    with open("amazon_komisyon/last_page_selenium.html", "w", encoding="utf-8") as f:
        f.write(html)
    raise Exception("Tablo bulunamadı! Selenium ile alınan HTML amazon_komisyon/last_page_selenium.html dosyasına kaydedildi.")

def main():
    komisyonlar = fetch_table_selenium()
    with open("amazon_komisyon.json", "w", encoding="utf-8") as f:
        json.dump(komisyonlar, f, ensure_ascii=False, indent=4)
    print("Komisyon verileri güncellendi!")

if __name__ == "__main__":
    main() 
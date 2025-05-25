import pandas as pd
import json
import re
from collections import defaultdict

# Excel dosyasını oku
excel_path = "amazon_kargo.xlsx"
# Tüm sheet'leri oku
all_sheets = pd.read_excel(excel_path, sheet_name=None)

def parse_desi(boyut_str):
    # Hem ≤ hem > hem de ≥ işaretlerinden sonra gelen boyutları yakala
    match = re.search(r"[≤>≥]?\s*(\d+(?:[.,]\d+)?)X(\d+(?:[.,]\d+)?)X(\d+(?:[.,]\d+)?)(?:cm)?", boyut_str)
    if match:
        en = float(match.group(1).replace(",", "."))
        boy = float(match.group(2).replace(",", "."))
        yuk = float(match.group(3).replace(",", "."))
        desi = round((en * boy * yuk) / 3000, 3)
        return desi
    return None

def find_column(columns, keywords):
    for col in columns:
        for key in keywords:
            if key.lower() in col.lower():
                return col
    return None

gruplanmis = defaultdict(list)
for sheet_name, df in all_sheets.items():
    # Table 2 için özel mantık
    if sheet_name == "Table 2":
        band_col = df.columns[0]
        fiyat_col = df.columns[1]
        # Table 2 başlığından desi hesapla
        desi = parse_desi(band_col)
        for _, row in df.iterrows():
            band = str(row[band_col]).strip()
            fiyat_raw = str(row[fiyat_col]).strip()
            # Sadece fiyatı ₺ ile başlayan ve ağırlık içeren satırları işle
            if not band or not fiyat_raw or not fiyat_raw.startswith("₺"):
                continue
            agirlik_match = re.search(r"([\d,.]+) ?kg|([\d,.]+) ?g", band)
            if not agirlik_match:
                continue
            if agirlik_match.group(1):
                agirlik_kg = float(agirlik_match.group(1).replace(",", "."))
            elif agirlik_match.group(2):
                agirlik_kg = float(agirlik_match.group(2).replace(",", ".")) / 1000
            else:
                agirlik_kg = None
            fiyat = float(fiyat_raw.replace("₺", "").replace(",", "."))
            fiyat_kdv = round(fiyat * 1.20, 2)
            gruplanmis[desi].append({
                "agirlik_kg": agirlik_kg,
                "fiyat_kdv_dahil": fiyat_kdv
            })
        continue
    # Diğer sheet'ler için mevcut mantık
    band_col = find_column(df.columns, ["Ağırlık Bandı", "Ağırlık", "Band", "Weight", "Geniş Büyük Boyutlu"])
    fiyat_col = find_column(df.columns, ["Amazon Lojistik Ücretleri", "Ücret", "Fiyat", "Price", "geçerli ücret"])
    if not band_col or not fiyat_col:
        continue
    current_desi = None
    for _, row in df.iterrows():
        band = str(row[band_col]).strip()
        fiyat_raw = str(row[fiyat_col]).strip()
        if not band or 'depolama' in band.lower() or 'fiyatlar' in band.lower() or 'ay/m' in band.lower():
            continue
        if (("Boyutlar" in band and "X" in band) or band.startswith("Geniş Büyük Boyutlu: Boyutlar")) and not fiyat_raw.startswith("₺"):
            current_desi = parse_desi(band)
            if current_desi is None and "Geniş Büyük Boyutlu" in band:
                current_desi = parse_desi(band_col)  # Table 2 başlığı gibi davran
            continue
        if fiyat_raw.startswith("₺") and current_desi is not None:
            agirlik_match = re.search(r"([\d,.]+) ?kg|([\d,.]+) ?g", band)
            if agirlik_match:
                if agirlik_match.group(1):
                    agirlik_kg = float(agirlik_match.group(1).replace(",", "."))
                elif agirlik_match.group(2):
                    agirlik_kg = float(agirlik_match.group(2).replace(",", ".")) / 1000
                else:
                    agirlik_kg = None
            else:
                agirlik_kg = None
            fiyat = float(fiyat_raw.replace("₺", "").replace(",", "."))
            fiyat_kdv = round(fiyat * 1.20, 2)
            gruplanmis[current_desi].append({
                "agirlik_kg": agirlik_kg,
                "fiyat_kdv_dahil": fiyat_kdv
            })

# Sonuçları sırayla yaz
sonuclar = []
for desi, fiyatlar in gruplanmis.items():
    sonuclar.append({
        "desi": desi,
        "fiyatlar": fiyatlar
    })

# JSON dosyasına yaz
with open("amazon_kargo.json", "w", encoding="utf-8") as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)

print("Kargo verileri TÜM sheet'lerdeki başlık ve desi yapıları otomatik algılanarak, sadece desi ve ağırlık/fiyat satırları ile KDV dahil olarak JSON dosyasına yazıldı.") 
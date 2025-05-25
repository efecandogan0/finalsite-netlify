import pandas as pd
import json
import re

# Excel dosyasını oku
excel_dosya_adi = "hepsiburadakargo.xlsx"
df = pd.read_excel(excel_dosya_adi, header=1)

# Sonuç sözlüğü
sonuc = {}

# Sütunları gez (ilk sütun hariç)
for col in df.columns[1:]:
    firma = col.strip()
    sonuc[firma] = []
    for i, row in df.iterrows():
        desi_raw = row['Desi']
        fiyat_raw = str(row[col])
        # TL işareti ve virgül temizle
        fiyat_str = re.sub(r"[^\d,\.]", "", fiyat_raw).replace(",", ".")
        if not fiyat_str:
            continue  # Boşsa atla
        try:
            fiyat = float(fiyat_str)
        except ValueError:
            continue  # Geçersizse atla
        yeni_fiyat = round(fiyat * 1.2, 2)
        sonuc[firma].append({"desi": desi_raw, "fiyat_kdv_dahil": yeni_fiyat})

# JSON olarak kaydet
with open("yeni_fiyatlar.json", "w", encoding="utf-8") as f:
    json.dump(sonuc, f, ensure_ascii=False, indent=4)

print("JSON dosyası oluşturuldu: yeni_fiyatlar.json") 
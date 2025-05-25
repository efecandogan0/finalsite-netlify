import pandas as pd
import json
import math

# Excel dosyasının adı
excel_path = 'trendyol_kargo.xlsx'

# Başlık olarak 3. satırı kullan (header=2)
sheets = pd.read_excel(excel_path, sheet_name=None, header=2)

print('Sheet adları:', list(sheets.keys()))
for sheet_name, df in sheets.items():
    print(f'\nSheet: {sheet_name}')
    print('Sütunlar:', list(df.columns))
    print(df.head())

# Sonuçları tutacak sözlük
result = {}

for sheet_name, df in sheets.items():
    # Desi sütunu adını bul
    desi_col = next((col for col in df.columns if 'desi' in str(col).lower()), None)
    if not desi_col:
        continue
    # Kargo şirketi sütunlarını bul (desi hariç)
    kargo_cols = [col for col in df.columns if col != desi_col and 'nan' not in str(col).lower()]
    for kargo in kargo_cols:
        fiyatlar = []
        for _, row in df.iterrows():
            try:
                desi = row[desi_col]
                fiyat = float(row[kargo])
                if pd.isna(desi) or pd.isna(fiyat) or math.isnan(fiyat):
                    continue
                fiyat_kdvli = round(fiyat * 1.2, 2)
                fiyatlar.append({
                    'desi': desi,
                    'fiyat_kdv_dahil': fiyat_kdvli
                })
            except Exception:
                continue
        if fiyatlar:
            result[str(kargo)] = fiyatlar

# JSON'a yaz
with open('trendyol_kargo.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('KDV dahil fiyatlar trendyol_kargo.json dosyasına yazıldı.') 
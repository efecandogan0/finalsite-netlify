import pandas as pd
import json

df = pd.read_excel('komisyonlarexcel.xlsx', header=2)

# Kategorileri sıralı şekilde ayır
altin = df[df['Ana Kategori'] == 'Altın']
aksesuar = df[df['Ana Kategori'] == 'Aksesuar']
digerleri = df[(df['Ana Kategori'] != 'Altın') & (df['Ana Kategori'] != 'Aksesuar')]

# Sıralı olarak birleştir
siralama = pd.concat([altin, aksesuar, digerleri], ignore_index=True)

# Ana kategori ve kategoriye göre sıralı unique kombinasyonları bul
unique_pairs = siralama[['Ana Kategori', 'Kategori']].drop_duplicates().values.tolist()

result = []
no = 1
for ana_kategori, kategori in unique_pairs:
    kategori_grup = siralama[(siralama['Ana Kategori'] == ana_kategori) & (siralama['Kategori'] == kategori)]
    urun_grubu_detayi = []
    for detay in kategori_grup['Ürün Grubu Detayı'].dropna().tolist():
        urun_grubu_detayi.extend([d.strip() for d in detay.split(',') if d.strip()])
    try:
        kdv = float(kategori_grup['Komisyon (+kdv)'].iloc[0])
    except:
        kdv = None
    result.append({
        'no': no,
        'ana_kategori': ana_kategori,
        'kategori': kategori,
        'urun_grubu_detayi': urun_grubu_detayi,
        'kdv': kdv
    })
    no += 1

with open('hepsiburada_kategori.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('JSON dosyası oluşturuldu: hepsiburada_kategori.json')
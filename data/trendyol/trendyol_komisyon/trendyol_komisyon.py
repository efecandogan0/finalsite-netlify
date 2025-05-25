import pandas as pd
import json

excel_path = "trendyol_komisyon.xlsx"

# Tüm sheet'leri oku ve birleştir
df_list = []
xl = pd.ExcelFile(excel_path)
for sheet in xl.sheet_names:
    df = pd.read_excel(excel_path, header=1, sheet_name=sheet)
    df = df.rename(columns=lambda x: str(x).strip())
    column_map = {
        "No": "no",
        "Kategori": "ana_kategori",
        "Alt Kategori": "kategori",
        "Ürün Grubu": "urun_grubu_detayi",
        "Kategori Komisyon % (KDV Dahil)": "kdv"
    }
    df = df.rename(columns=column_map)
    df = df[["no", "ana_kategori", "kategori", "urun_grubu_detayi", "kdv"]]
    def split_field(val):
        if pd.isna(val):
            return []
        return [v.strip() for v in str(val).replace('\n', ',').split(',') if v and str(v).strip() and str(v).strip().lower() != 'nan']
    df["urun_grubu_detayi"] = df["urun_grubu_detayi"].apply(split_field)
    df = df[df["no"].apply(lambda x: str(x).isdigit())]
    df["no"] = df["no"].astype(int)
    df["kdv"] = df["kdv"].astype(float)
    df_list.append(df)

# Tüm sheet'lerden gelen verileri birleştir
all_df = pd.concat(df_list, ignore_index=True)
# urun_grubu_detayi'nı stringe çevir
all_df["urun_grubu_detayi_str"] = all_df["urun_grubu_detayi"].apply(lambda x: ','.join(sorted(x)))
# no hariç tüm alanlara göre tekilleştir
all_df = all_df.drop_duplicates(subset=["ana_kategori", "kategori", "urun_grubu_detayi_str", "kdv"])
# no değerini baştan sırala
all_df = all_df.reset_index(drop=True)
all_df["no"] = all_df.index + 1
# urun_grubu_detayi'nı tekrar listeye çevir
all_df["urun_grubu_detayi"] = all_df["urun_grubu_detayi_str"].apply(lambda x: x.split(",") if x else [])
# Sıralama ve gereksiz kolonu silme
all_df = all_df.drop(columns=["urun_grubu_detayi_str"]).sort_values(by="no").reset_index(drop=True)

all_df.to_json("trendyol_komisyon.json", orient="records", force_ascii=False, indent=2)
print("JSON kaydedildi: trendyol_komisyon.json") 
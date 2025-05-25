const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 5000;
const fs = require('fs');

// CORS ayarları (sadece API için, build serve edilirken gerek yok)
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));
app.use(express.json());

// React build klasörünü serve et
app.use(express.static(path.join(__dirname, '../client/build')));

// Platform listesi (statik olarak ekliyorum, ileride dinamik yapılabilir)
const platforms = [
  {
    key: 'hepsiburada',
    name: 'Hepsiburada',
    logo: '/logos/hepsiburada.png'
  },
  {
    key: 'trendyol',
    name: 'Trendyol',
    logo: '/logos/trendyol.png'
  },
  {
    key: 'n11',
    name: 'n11',
    logo: '/logos/n11.png'
  },
  {
    key: 'amazon',
    name: 'Amazon',
    logo: '/logos/amazon.png'
  }
];

app.get('/api/ping', (req, res) => {
  res.json({ message: 'Backend çalışıyor!' });
});

app.get('/api/platforms', (req, res) => {
  res.json(platforms);
});

// Hepsiburada kategori arama endpointi
app.get('/api/hepsiburada/categories', (req, res) => {
  const q = (req.query.q || '').toLowerCase();
  const filePath = path.join(__dirname, '../data/hepsiburada/hepsiburada_komisyon/hepsiburada_komisyon.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  data.forEach(item => {
    if (item.urun_grubu_detayi && item.urun_grubu_detayi.length > 0) {
      item.urun_grubu_detayi.forEach(detay => {
        if (detay.toLowerCase().includes(q) || item.kategori.toLowerCase().includes(q) || item.ana_kategori.toLowerCase().includes(q)) {
          results.push({
            ana_kategori: item.ana_kategori,
            kategori: item.kategori,
            urun_grubu_detayi: detay,
            komisyon: item.kdv
          });
        }
      });
    } else {
      if (item.kategori.toLowerCase().includes(q) || item.ana_kategori.toLowerCase().includes(q)) {
        results.push({
          ana_kategori: item.ana_kategori,
          kategori: item.kategori,
          urun_grubu_detayi: null,
          komisyon: item.kdv
        });
      }
    }
  });
  res.json(results);
});

// Trendyol kategori arama endpointi
app.get('/api/trendyol/categories', (req, res) => {
  const q = (req.query.q || '').toLowerCase();
  const filePath = path.join(__dirname, '../data/trendyol/trendyol_komisyon/trendyol_komisyon.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  data.forEach(item => {
    if (item.urun_grubu_detayi && item.urun_grubu_detayi.length > 0) {
      item.urun_grubu_detayi.forEach(detay => {
        if (detay.toLowerCase().includes(q) || item.kategori.toLowerCase().includes(q) || item.ana_kategori.toLowerCase().includes(q)) {
          results.push({
            ana_kategori: item.ana_kategori,
            kategori: item.kategori,
            urun_grubu_detayi: detay,
            komisyon: item.kdv
          });
        }
      });
    } else {
      if (item.kategori.toLowerCase().includes(q) || item.ana_kategori.toLowerCase().includes(q)) {
        results.push({
          ana_kategori: item.ana_kategori,
          kategori: item.kategori,
          urun_grubu_detayi: null,
          komisyon: item.kdv
        });
      }
    }
  });
  res.json(results);
});

// n11 kategori arama endpointi
app.get('/api/n11/categories', (req, res) => {
  const q = (req.query.q || '').toLowerCase();
  const filePath = path.join(__dirname, '../data/n11/n11_komisyon/n11_komisyon.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  data.forEach(item => {
    if (item.urun_grubu_detayi && item.urun_grubu_detayi.length > 0) {
      item.urun_grubu_detayi.forEach(detay => {
        if (detay.toLowerCase().includes(q) || item.kategori.toLowerCase().includes(q) || item.ana_kategori.toLowerCase().includes(q)) {
          results.push({
            ana_kategori: item.ana_kategori,
            kategori: item.kategori,
            urun_grubu_detayi: detay,
            komisyon: item.kdv
          });
        }
      });
    } else {
      if (item.kategori.toLowerCase().includes(q) || item.ana_kategori.toLowerCase().includes(q)) {
        results.push({
          ana_kategori: item.ana_kategori,
          kategori: item.kategori,
          urun_grubu_detayi: null,
          komisyon: item.kdv
        });
      }
    }
  });
  res.json(results);
});

// Amazon kargo fiyatı endpointi (ağırlık opsiyonel)
app.get('/api/amazon/cargo', (req, res) => {
  const desi = parseFloat(req.query.desi);
  const weight = req.query.weight ? parseFloat(req.query.weight) : null;
  if (isNaN(desi)) {
    return res.status(400).json({ error: 'Desi değeri gereklidir ve sayı olmalıdır.' });
  }
  const filePath = path.join(__dirname, '../data/amazon/amazon_kargo/amazon_kargo.json');
  const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

  // 1. En uygun desi aralığını bul
  const desiList = data.map(d => d.desi).sort((a, b) => a - b);
  let uygunDesi = desiList[0];
  for (let i = 0; i < desiList.length; i++) {
    if (desi >= desiList[i]) uygunDesi = desiList[i];
    else break;
  }
  const desiObj = data.find(d => d.desi === uygunDesi);

  // 2. En uygun ağırlık aralığını bul
  let fiyat = null;
  if (desiObj && desiObj.fiyatlar && desiObj.fiyatlar.length > 0) {
    if (weight !== null) {
      const agirlikList = desiObj.fiyatlar
        .map(f => f.agirlik_kg)
        .filter(a => a !== null && a !== undefined)
        .sort((a, b) => a - b);
      let uygunAgirlik = agirlikList[0];
      for (let i = 0; i < agirlikList.length; i++) {
        if (weight >= agirlikList[i]) uygunAgirlik = agirlikList[i];
        else break;
      }
      const fiyatObj = desiObj.fiyatlar.find(f => f.agirlik_kg === uygunAgirlik);
      fiyat = fiyatObj ? fiyatObj.fiyat_kdv_dahil : null;
    } else {
      // Ağırlık yoksa ilk fiyatı kullan
      fiyat = desiObj.fiyatlar[0].fiyat_kdv_dahil;
    }
  }

  if (fiyat !== null) {
    res.json({ tumu: [{ firma: 'Amazon', fiyat }], enUygun: { firma: 'Amazon', fiyat } });
  } else {
    res.status(404).json({ error: 'Uygun kargo fiyatı bulunamadı.' });
  }
});

// Hepsiburada tüm kategoriler endpointi
app.get('/api/hepsiburada/categories/all', (req, res) => {
  const filePath = path.join(__dirname, '../data/hepsiburada/hepsiburada_komisyon/hepsiburada_komisyon.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  data.forEach(item => {
    if (item.urun_grubu_detayi && item.urun_grubu_detayi.length > 0) {
      item.urun_grubu_detayi.forEach(detay => {
        results.push({
          label: detay,
          ana_kategori: item.ana_kategori,
          kategori: item.kategori,
          urun_grubu_detayi: detay,
          komisyon: item.kdv
        });
      });
    } else {
      results.push({
        label: item.kategori,
        ana_kategori: item.ana_kategori,
        kategori: item.kategori,
        urun_grubu_detayi: null,
        komisyon: item.kdv
      });
    }
  });
  res.json(results);
});

// Trendyol tüm kategoriler endpointi
app.get('/api/trendyol/categories/all', (req, res) => {
  const filePath = path.join(__dirname, '../data/trendyol/trendyol_komisyon/trendyol_komisyon.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  data.forEach(item => {
    if (item.urun_grubu_detayi && item.urun_grubu_detayi.length > 0) {
      item.urun_grubu_detayi.forEach(detay => {
        results.push({
          label: detay,
          ana_kategori: item.ana_kategori,
          kategori: item.kategori,
          urun_grubu_detayi: detay,
          komisyon: item.kdv
        });
      });
    } else {
      results.push({
        label: item.kategori,
        ana_kategori: item.ana_kategori,
        kategori: item.kategori,
        urun_grubu_detayi: null,
        komisyon: item.kdv
      });
    }
  });
  res.json(results);
});

// n11 tüm kategoriler endpointi
app.get('/api/n11/categories/all', (req, res) => {
  const filePath = path.join(__dirname, '../data/n11/n11_komisyon/n11_komisyon.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  data.forEach(item => {
    if (item.urun_grubu_detayi && item.urun_grubu_detayi.length > 0) {
      item.urun_grubu_detayi.forEach(detay => {
        results.push({
          label: detay,
          ana_kategori: item.ana_kategori,
          kategori: item.kategori,
          urun_grubu_detayi: detay,
          komisyon: item.kdv
        });
      });
    } else {
      results.push({
        label: item.kategori,
        ana_kategori: item.ana_kategori,
        kategori: item.kategori,
        urun_grubu_detayi: null,
        komisyon: item.kdv
      });
    }
  });
  res.json(results);
});

// Amazon tüm kategoriler endpointi
app.get('/api/amazon/categories/all', (req, res) => {
  const filePath = path.join(__dirname, '../data/amazon/amazon_komisyon/amazon_komisyon.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  data.forEach(item => {
    results.push({
      label: item.kategori,
      ana_kategori: item.kategori,
      kategori: item.kategori,
      urun_grubu_detayi: null,
      komisyon: item.kdv
    });
  });
  res.json(results);
});

// Hepsiburada kargo fiyatı endpointi
app.get('/api/hepsiburada/cargo', (req, res) => {
  const desi = parseInt(req.query.desi, 10);
  if (isNaN(desi)) {
    return res.status(400).json({ error: 'Desi değeri gereklidir ve sayı olmalıdır.' });
  }
  const filePath = path.join(__dirname, '../data/hepsiburada/hepsiburada_kargo/hepsiburada_kargo.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  Object.entries(data).forEach(([firma, fiyatlar]) => {
    let fiyatlarArr = Array.isArray(fiyatlar) ? fiyatlar : (typeof fiyatlar === 'object' && fiyatlar !== null ? Object.values(fiyatlar) : []);
    let fiyatObj = fiyatlarArr.find(f => f.desi === desi);
    if (!fiyatObj) {
      fiyatObj = fiyatlarArr.find(f => f.desi > desi);
    }
    if (!fiyatObj && fiyatlarArr.length > 0) {
      fiyatObj = fiyatlarArr[fiyatlarArr.length - 1];
    }
    if (fiyatObj) {
      results.push({ firma, fiyat: fiyatObj.fiyat_kdv_dahil });
    }
  });
  const minFiyat = Math.min(...results.map(r => r.fiyat));
  const enUygun = results.find(r => r.fiyat === minFiyat);
  res.json({ tumu: results, enUygun });
});

// Trendyol kargo fiyatı endpointi
app.get('/api/trendyol/cargo', (req, res) => {
  const desi = parseInt(req.query.desi, 10);
  if (isNaN(desi)) {
    return res.status(400).json({ error: 'Desi değeri gereklidir ve sayı olmalıdır.' });
  }
  const filePath = path.join(__dirname, '../data/trendyol/trendyol_kargo/trendyol_kargo.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  Object.entries(data).forEach(([firma, fiyatlar]) => {
    let fiyatlarArr = Array.isArray(fiyatlar) ? fiyatlar : (typeof fiyatlar === 'object' && fiyatlar !== null ? Object.values(fiyatlar) : []);
    let fiyatObj = fiyatlarArr.find(f => f.desi === desi);
    if (!fiyatObj) {
      fiyatObj = fiyatlarArr.find(f => f.desi > desi);
    }
    if (!fiyatObj && fiyatlarArr.length > 0) {
      fiyatObj = fiyatlarArr[fiyatlarArr.length - 1];
    }
    if (fiyatObj) {
      results.push({ firma, fiyat: fiyatObj.fiyat_kdv_dahil });
    }
  });
  const minFiyat = Math.min(...results.map(r => r.fiyat));
  const enUygun = results.find(r => r.fiyat === minFiyat);
  res.json({ tumu: results, enUygun });
});

// n11 kargo fiyatı endpointi
app.get('/api/n11/cargo', (req, res) => {
  const desi = parseInt(req.query.desi, 10);
  if (isNaN(desi)) {
    return res.status(400).json({ error: 'Desi değeri gereklidir ve sayı olmalıdır.' });
  }
  const filePath = path.join(__dirname, '../data/n11/n11_kargo/n11_kargo.json');
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  let results = [];
  Object.entries(data).forEach(([firma, fiyatlar]) => {
    let fiyatlarArr = Array.isArray(fiyatlar) ? fiyatlar : (typeof fiyatlar === 'object' && fiyatlar !== null ? Object.values(fiyatlar) : []);
    let fiyatObj = fiyatlarArr.find(f => f.desi === desi);
    if (!fiyatObj) {
      fiyatObj = fiyatlarArr.find(f => f.desi > desi);
    }
    if (!fiyatObj && fiyatlarArr.length > 0) {
      fiyatObj = fiyatlarArr[fiyatlarArr.length - 1];
    }
    if (fiyatObj) {
      results.push({ firma, fiyat: fiyatObj.fiyat_kdv_dahil });
    }
  });
  const minFiyat = Math.min(...results.map(r => r.fiyat));
  const enUygun = results.find(r => r.fiyat === minFiyat);
  res.json({ tumu: results, enUygun });
});

// Diğer tüm isteklerde React index.html'i döndür
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
}); 
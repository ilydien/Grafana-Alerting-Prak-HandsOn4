# Online Store Financial Monitoring - FastAPI & Grafana Alerting

Tugas Hands-On 4 IPBD — Sistem pemantauan finansial real-time untuk toko online menggunakan **FastAPI** sebagai backend API dan **Grafana + Infinity plugin** sebagai platform monitoring dan alerting.

---

## Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Docker Compose                               │
│  ┌─────────────────────────────────┐    ┌─────────────────────────┐│
│  │        Backend Container        │    │   Grafana Container     ││
│  │  ┌───────────────────────────┐  │    │  ┌───────────────────┐  ││
│  │  │     FastAPI (main.py)     │  │    │  │   Grafana UI      │  ││
│  │  │  GET /api/v1/transactions │  │    │  │   (port 3000)     │  ││
│  │  └──────────┬────────────────┘  │    │  └────────┬──────────┘  ││
│  │             │                   │    │           │              ││
│  │  ┌──────────▼────────────────┐  │    │  ┌────────▼──────────┐  ││
│  │  │  data_generator.py        │  │    │  │  Infinity Plugin   │  ││
│  │  │  - 60 transaksi dummy     │  │    │  │  (Data Source)     │  ││
│  │  │  - Produk Elektronik      │  │    │  └────────┬──────────┘  ││
│  │  │  - Timestamp unik         │  │    │           │              ││
│  │  └───────────────────────────┘  │    │  ┌────────▼──────────┐  ││
│  └──────────────┬──────────────────┘    │  │  Dashboard        │  ││
│                 │                       │  │  + Alert Rules    │  ││
│                 │ http://backend:8000   │  └───────────────────┘  ││
│                 └───────────────────────┼─────────────────────────┘│
└─────────────────────────────────────────┴─────────────────────────┘
                           │
                    http://localhost:8000
                           │
                    ┌──────▼──────┐
                    │   Browser   │
                    │   / curl    │
                    └─────────────┘
```

**Alur Data:**
1. User mengakses endpoint `GET /api/v1/transactions` pada FastAPI
2. `data_generator.py` menghasilkan 60 data transaksi dummy secara real-time
3. Grafana mengambil data dari API melalui **Infinity plugin** (URL: `http://backend:8000/api/v1/transactions`)
4. Data ditampilkan dalam **Dashboard** (Table/Time Series)
5. **Alert Rules** memonitor nilai `revenue_idr` dan memberikan peringatan jika di bawah 5jt atau di atas 10jt

---

## Struktur Proyek

```
Alerting-Grafana/
├── app/
│   ├── __init__.py
│   └── data_generator.py     # Generator 60 data transaksi dummy
├── main.py                    # FastAPI app (endpoint API)
├── docker-compose.yaml        # Backend + Grafana container
├── pyproject.toml             # Dependencies Python
├── README.md                  # Dokumentasi ini
├── .gitignore
└── .python-version
```

---

## Persyaratan

- Docker & Docker Compose terinstall
- Port `8000` dan `3000` tidak digunakan

---

## Cara Menjalankan

### 1. Clone / masuk ke folder proyek

```bash
cd Alerting-Grafana
```

### 2. Jalankan semua container

```bash
docker compose up
```

Perintah ini akan menjalankan dua container:
- **Backend** (FastAPI) — `http://localhost:8000`
- **Grafana** — `http://localhost:3000`

### 3. Cek API

```bash
curl http://localhost:8000/api/v1/transactions
```

Response: JSON array berisi 60 data transaksi.

### 4. Akses Grafana

Buka browser: `http://localhost:3000`
- **Username:** admin
- **Password:** admin

---

## Penjelasan Kode

### `docker-compose.yaml`

Mendefinisikan dua service dalam satu jaringan Docker:

| Service | Image | Port | Fungsi |
|---------|-------|------|--------|
| `backend` | python:3.11-slim | 8000 | Menjalankan FastAPI dengan auto-reload |
| `grafana` | grafana/grafana:latest | 3000 | Dashboard monitoring + Infinity plugin |

**Detail:**
- Backend menggunakan **volume mount** (`.:/app`) agar perubahan kode langsung terdeteksi (`--reload`)
- Grafana menginstal **Infinity plugin** otomatis melalui environment variable `GF_INSTALL_PLUGINS`
- `extra_hosts` memungkinkan akses ke host dari dalam container Grafana
- `depends_on` memastikan backend berjalan sebelum Grafana

### `main.py` — FastAPI Backend

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.data_generator import generate_transactions

app = FastAPI(title="Online Store Financial Monitor")

# CORS agar bisa diakses Grafana
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

@app.get("/api/v1/transactions")
def get_transactions():
    return generate_transactions(60)
```

- Menggunakan **FastAPI** framework
- **CORS enabled** agar Grafana dapat mengakses API
- Satu endpoint `GET /api/v1/transactions` mengembalikan **60 data transaksi** dalam format JSON
- Data di-generate **real-time** setiap kali endpoint dipanggil

### `app/data_generator.py` — Data Generator

**Library:** Hanya menggunakan Python stdlib (`random`, `datetime`, `uuid`) — tanpa dependensi tambahan.

**Produk:** 15 produk Elektronik & Gadget dalam 5 kategori:
- **Komputer:** MacBook Pro M4, ASUS ROG Zephyrus, MacBook Air M4
- **Gadget:** iPhone 16 Pro, Samsung Galaxy S25, iPad Air M3, Google Pixel 10
- **Audio:** Sony WH-1000XM6, AirPods Pro 3, JBL Charge 6
- **Aksesoris:** Logitech MX Master 3S, Razer DeathAdder V3
- **Elektronik:** Dell UltraSharp 27

**Fungsi `generate_transactions(count=60)`:**

| Komponen | Keterangan |
|----------|------------|
| `transaction_id` | `uuid.uuid4()` — unik secara global |
| `timestamp` | `now - i * 37 detik` — unik, tidak ada duplikat |
| `product_name` | Dipilih acak dari 15 produk |
| `category` | Kategori dari produk yang dipilih |
| `quantity` | Random 1-10 |
| `revenue_idr` | `unit_price × quantity` — bervariasi |
| `location` | Random dari 8 kota |

**Variasi Revenue untuk Alert:**
- **Revenue < Rp5.000.000:** Produk murah (aksesoris/audio) dengan quantity kecil
- **Revenue > Rp10.000.000:** Produk mahal (laptop/gadget) dengan quantity besar
- **Revenue Rp5jt - Rp10jt:** Produk menengah

**Anti-duplikasi Timestamp:**  
Menggunakan formula `now - timedelta(seconds=i * 37)`. Setiap iterasi dikurangi 37 detik dari iterasi sebelumnya, sehingga **tidak ada timestamp yang sama**. Ini penting karena Grafana Alerting akan error jika ada timestamp duplikat.

---

## Konfigurasi Grafana

### 1. Setup Infinity Data Source

1. Login Grafana (`http://localhost:3000` — admin/admin)
2. **Connections → Data sources → Add new connection**
3. Cari **Infinity** → pilih
4. Konfigurasi:
   - **Name:** `Online Store API`
   - **URL:** `http://backend:8000`
   - **Save & test**
5. **Query Editor** (saat buat panel):
   - **Parser:** `JSONata` (backend parser — wajib untuk alerting support)
   - **Columns:**

| Selector | Type |
|----------|------|
| `transaction_id` | String |
| `timestamp` | Time |
| `product_name` | String |
| `category` | String |
| `quantity` | String |
| `revenue_idr` | Number |
| `location` | String |

> Catatan: `quantity` di-set sebagai **String** agar hanya `revenue_idr` yang menjadi kolom Number untuk alert.

### 2. Buat Dashboard

1. **Dashboards → New Dashboard → Add visualization**
2. Pilih data source **Online Store API**
3. Atur query seperti di atas → **Run query**
4. Pilih **Table** sebagai jenis panel
5. Beri judul panel (contoh: "Transaksi Online Store")
6. **Save dashboard**

---

## Konfigurasi Alert Rules

### Alert 1: Underperformance Alert (Revenue < Rp5.000.000)

1. **Alerting → Alert rules → New alert rule**
2. **Rule name:** `Underperformance - Revenue Below 5M`
3. **Query & expressions:**
   - **Query (A):** Pilih Infinity data source (biarkan default)
   - **Expression (B) - Reduce:** Function = **Last** → Input = **A**
   - **Expression (C) - Threshold:** **IS BELOW** → Value = `5000000` → Input = **B**
4. **Folder:** `Online Store`
5. **Evaluation group:** `every-1m` (evaluate every 1m, pending 0)
6. **Condition:** `C` (is alerting if `C == true`)
7. **Save**

### Alert 2: High Achievement Alert (Revenue > Rp10.000.000)

1. **Alerting → Alert rules → New alert rule**
2. **Rule name:** `High Achievement - Revenue Above 10M`
3. **Query & expressions:**
   - **Query (A):** Pilih Infinity data source
   - **Expression (B) - Reduce:** Function = **Last** → Input = **A**
   - **Expression (C) - Threshold:** **IS ABOVE** → Value = `10000000` → Input = **B**
4. **Folder:** `Online Store`
5. **Evaluation group:** `every-1m`
6. **Save**

### Penjelasan Expression:

```
Query (A) ──> Reduce (B) ──> Threshold (C) ──> Condition (C == true)
(Fetch data)   (Ambil nilai    (Cek apakah       (Jika true → alert
                terakhir)       di bawah/atas     FIRING)
                                threshold)
```

- **Reduce (Last):** Mengambil nilai terakhir dari kolom `revenue_idr` untuk setiap baris data
- **Threshold (IS BELOW / IS ABOVE):** Membandingkan nilai dengan batas yang ditentukan
- **Backend parser (JSONata/JQ):** Wajib digunakan agar alerting dapat berfungsi

---

## Troubleshooting

| Error | Penyebab | Solusi |
|-------|----------|--------|
| `connection refused` | Backend belum jalan | `docker compose up backend` |
| `context deadline exceeded` | Grafana tidak bisa reach backend | Pastikan URL Data Source benar (`http://backend:8000`) |
| `duplicate results with labels` | Baris data tidak unik | Tambahkan `transaction_id` sebagai kolom String di query |
| Alert nilai kecil (1-10) | Alert pakai `quantity` bukan `revenue_idr` | Ubah `quantity` ke tipe String, biarkan `revenue_idr` sebagai Number |
| Infinity plugin tidak ada | Plugin belum terinstall | Restart container: `docker compose restart grafana` |
| `host.docker.internal` tidak work | `host-gateway` tidak cocok | Ganti URL Data Source ke `http://backend:8000` |

---

## Testing API

```bash
# Test endpoint
curl http://localhost:8000/api/v1/transactions

# Cek variasi revenue (cek alert terpenuhi)
curl -s http://localhost:8000/api/v1/transactions | python3 -c "
import sys, json
data = json.load(sys.stdin)
below = [d for d in data if d['revenue_idr'] < 5000000]
above = [d for d in data if d['revenue_idr'] > 10000000]
print(f'Under 5jt: {len(below)} items')
print(f'Above 10jt: {len(above)} items')
print(f'Total: {len(data)} items')
"
```

---

## Catatan Penting

- Data di-generate **setiap kali** endpoint dipanggil, sehingga data akan berubah setiap kali dashboard di-refresh
- Pastikan menggunakan **backend parser** (JSONata/JQ) di Infinity Query Editor, bukan Frontend parser — karena Frontend parser **tidak mendukung alerting**
- Alert akan **firing** jika ada data yang memenuhi kondisi Threshold. Jika tidak ada data yang cocok, alert akan berstatus **Normal**

---

## Screenshot

> *(Tempelkan screenshot di sini)*
>
> 1. Screenshot Add Data Source Infinity
> 2. Screenshot Dashboard (Table panel)
> 3. Screenshot Pembuatan Alert Rule
> 4. Screenshot Alert Firing / Notification

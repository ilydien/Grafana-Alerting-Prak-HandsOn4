# FastAPI & Grafana Alerting

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



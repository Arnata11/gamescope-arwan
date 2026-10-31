# GameScope — Global Video Game Sales Analytics

Proyek UTS mata kuliah Visualisasi Data. Dashboard analitik interaktif berbasis Python, Pandas, Plotly, dan Streamlit yang telah disempurnakan dengan prinsip **Modern Editorial Analytics Dashboard** dan **visualisasi berbasis judul/nama game secara komprehensif**.

> **Penting:** Dataset CSV bersumber dari Kaggle resmi, tersimpan sebagai `dataset/vgsales.csv` dan `dataset/vgsales_clean.csv`. Seluruh KPI, visualisasi, dan insight analitik dihitung secara dinamis dari dataset aktual tanpa angka tiruan atau kesimpulan statis.

---

## 1. Informasi Proyek

- **Judul:** GameScope — Global Video Game Sales Analytics
- **Dataset:** Video Game Sales (Historical Records 1980–2020)
- **Sumber:** https://www.kaggle.com/datasets/gregorut/videogamesales
- **Teknologi:** Python 3.11+, Pandas, Plotly Express & Graph Objects, Streamlit
- **Design System:** Modern Editorial Analytics (Palet WCAG AA: `#2563EB`, `#0F172A`, `#F8FAFC`, `#FFFFFF`, `#E2E8F0`, `#D97706`)
- **Output:** Dashboard interaktif responsif, visualisasi nama game, unit test suite (13 tests), skrip data cleaning, dan dokumentasi lengkap.

Isi identitas mahasiswa dan tautan dashboard sebelum pengumpulan:
- **Nama:** Arwan Priyadinata
- **NIM/NPM:** 241041005
- **Live dashboard:** https://gamescope-arwan-xv3eplaymqwfgfcbjcdvpf.streamlit.app/
- **Repositori GitHub:** https://github.com/Arnata11/gamescope-arwan

---

## 2. Fitur & Struktur Visualisasi Dashboard

Dashboard distrukturkan secara terpadu mengikuti hierarki analitik dari tingkat judul game (*micro*), tren makro industri (*macro*), hingga perbandingan geografis regional:

### A. Header & Editorial Hero
- **GameScope Intelligence Badge & Metadata Strip:** Menampilkan status dataset terverifikasi, jumlah total katalog judul terindeks (16.598 baris), rentang tahun rilis resmi (1980–2020), cakupan 4 wilayah global, dan penegasan satuan ukur (*Million Units*).
- **Active Filter Summary Bar:** Menampilkan status filter aktif secara ringkas (kata kunci pencarian judul, rentang tahun aktif, jumlah genre dan platform terpilih, serta jumlah baris data yang cocok beserta persentasenya).

### B. Filter Panel & Kontrol Sidebar
1. **Pencarian Judul Game / Publisher (Search Box):** Filter pencarian instan berdasarkan nama game (misal: *Mario*, *Pokemon*, *Wii*, *Call of Duty*) atau nama publisher.
2. **Tombol Quick Reset:** Tombol `↺ Reset Filter ke Default` yang mengembalikan pencarian, slider tahun, dan multiselect ke kondisi awal dengan 1 klik via Streamlit Session State.
3. **Slider Rentang Tahun Rilis:** Filter dinamis tahun peluncuran resmi (1980–2020) dengan penjelasan bahwa catatan tanpa tahun rilis tetap diikutsertakan pada agregat volume global.
4. **Multiselect Kategori Genre:** Pilihan 12 genre gim video.
5. **Multiselect Platform Hardware:** Pilihan 31 konsol dan komputer peluncuran gim.
6. **Panel Metadata:** Rincian file aktif, rasio filter terhadap katalog, dan satuan data.
7. **Graceful Empty State:** Jika filter menghasilkan 0 baris, dashboard tidak error/crash, melainkan menampilkan card instruksi informatif dengan tombol reset langsung di area utama.

### C. 4 KPI Summary Cards
1. **Total Global Sales:** Total volume penjualan global dalam juta unit (`M`), berlabel jelas dengan subteks unit dan tooltip metrik.
2. **Jumlah Game Records:** Total baris judul unik yang memenuhi filter aktif.
3. **Best-Selling Title (Game Terlaris):** Nama judul game dengan penjualan global tertinggi pada filter aktif beserta platform dan angka penjualannya (misal: *Wii Sports — 82.74M*).
4. **Top Genre by Sales:** Kategori genre terlaris beserta nilai penjualan dan persentase pangsa pasar (*market share*).

---

### D. Visualisasi Lengkap (6 Grafik Interaktif)

#### Section 1 — Game-Level Analysis (Visualisasi Nama Game)
1. **Chart 1 — Top 10 Best-Selling Video Games (Horizontal Bar Chart):**
   - Menampilkan 10 game dengan penjualan global tertinggi pada filter aktif.
   - Sumbu Y menampilkan nama game beserta platformnya secara jelas tanpa terpotong.
   - Peringkat #1 mendapatkan penekanan visual warna emas/amber (`#D97706`).
   - Angka penjualan langsung tertera pada bar (`X.XX M`).
   - Tooltip informatif: Nama Game, Platform, Tahun Rilis, Genre, Publisher, dan Penjualan Global.
2. **Chart 2 — Compare Game Sales (Stacked Regional Bar Chart):**
   - Fitur komparasi interaktif yang memungkinkan pengguna memilih hingga 10 game sekaligus via multiselect.
   - Membandingkan volume total global sekaligus proporsi kontribusi 4 wilayah: *North America* (Biru), *Europe* (Hijau Emerald), *Japan* (Amber Emas), dan *Other Regions* (Ungu).
   - Dilengkapi panduan visual jika pilihan game dikosongkan.

#### Section 2 — Macro Trends & Genre Breakdown
3. **Chart 3 — Global Sales Trend over Release Years (Line Chart):**
   - Tren volume penjualan global tahunan dengan kurva halus (*spline*), penanda titik (*markers*), dan area gradien transparan.
   - Tooltip informatif: Tahun, Total Penjualan Global, Jumlah Judul Dirilis, serta **Judul Game Terlaris Era Tersebut**.
4. **Chart 4 — Sales by Genre (Horizontal Bar Chart):**
   - Bar chart horizontal terurut logis (genre terbesar di bagian atas) menggunakan warna primer `#2563EB`.
   - Label angka otomatis di setiap bar dan hover tooltip dengan nilai unit serta pangsa pasar (%).

#### Section 3 — Regional Analysis & Cross-Market Correlation
5. **Chart 5 — Regional Sales by Genre (Heatmap):**
   - Matriks perbandingan penjualan regional (*North America, Europe, Japan, Other Regions*) lintas seluruh genre.
   - Skala warna sequential kontras tinggi (*Blues*) dan anotasi angka di setiap sel matriks.
6. **Chart 6 — North America vs Europe Sales (Scatter Plot dengan Penyorotan Game):**
   - Scatter plot korelasi volume penjualan antara pasar Amerika Utara dan Eropa dengan pemetaan warna diskrit ramah tuna warna (*colorblind-friendly*) untuk 12 genre.
   - **Fitur Penyorotan Game Interaktif:** Jika pengguna memilih game pada fitur *Compare*, game tersebut otomatis disorot dengan simbol diamond emas bercahaya pada scatter plot.
   - Dilengkapi garis paritas diagonal (`NA = EU`) sebagai acuan visual preferensi pasar.
   - Dioptimasi menggunakan rendering otomatis/WebGL untuk performa tinggi tanpa lag.

---

### E. Analytical Storytelling & Dynamic Key Insights
Section **Key Insights — What the Data Reveals** menyajikan 4 kartu temuan analitik berskala rata (*equal height*) yang dihitung secara dinamis dari data aktif:
- **Game Terlaris:** Judul game nomor satu, volume unit, platform, serta selisih keunggulan terhadap peringkat ke-2.
- **Top Platform:** Konsol terlaris, volume unit, pangsa pasar, dan jumlah judul rilis.
- **Wilayah Terbesar:** Pasar geografis paling dominan dan persentasenya terhadap total regional.
- **Tahun Puncak:** Tahun rekor penjualan historis beserta game terlaris yang mendominasi era tersebut.
- *Catatan metodologi:* Penegasan bahwa korelasi data tidak mengimplikasikan kausalitas sebab-akibat.

### F. Data Explorer & Export
- Expandable drawer `🔍 Jelajahi Data Mentah & Tabel Terfilter`.
- Ringkasan jumlah baris dan total volume yang terfilter.
- Tombol unduh data hasil filter dalam format CSV (`gamescope_filtered_data.csv`).
- Dataframe interaktif dengan konfigurasi format kolom numerik (`M` unit, tahun rilis, nomor rank).

---

## 3. Struktur Proyek

```text
gamescope_uts/
├── .streamlit/
│   └── config.toml             # Konfigurasi tema Modern Editorial Analytics
├── dataset/
│   ├── README.md               # Dokumentasi sumber Kaggle
│   ├── vgsales.csv             # Dataset mentah dari Kaggle
│   └── vgsales_clean.csv       # Dataset bersih hasil scripts/clean_data.py
├── scripts/
│   └── clean_data.py           # Skrip otomatisasi pembersihan data
├── tests/
│   └── test_dashboard_core.py  # Unit test otomatis (13 skenario pengujian)
├── app.py                      # Aplikasi dashboard Streamlit utama
├── README.md                   # Dokumentasi proyek & instruksi teknis
├── requirements.txt            # Dependensi Python
└── .gitignore                  # Berkas yang diabaikan Git
```

---

## 4. Cara Menjalankan di Komputer Lokal

Disarankan menggunakan **Python 3.10–3.12**.

### Langkah 1: Persiapan Environment

Buka terminal PowerShell pada folder proyek:

```powershell
# Buat virtual environment
python -m venv .venv

# Aktifkan virtual environment di Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### Langkah 2: Instalasi Dependensi

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Langkah 3: Menjalankan Unit Test

Jalankan pengujian otomatis untuk memverifikasi logika filter, pencarian game, kalkulasi KPI, insight dinamis, dan chart generation:

```powershell
python -m unittest tests/test_dashboard_core.py -v
```

### Langkah 4: Menjalankan Dashboard

```powershell
streamlit run app.py
```

Buka URL lokal yang muncul di terminal (biasanya `http://localhost:8501`).

---

## 5. Ringkasan Pengujian yang Telah Dijalankan

Pengujian otomatis telah dijalankan secara riil pada environment proyek:

| No | Modul Pengujian | Skenario | Hasil |
|---|---|---|---|
| 1 | `test_dataset_found_and_loaded` | Verifikasi keberadaan CSV dan validasi kolom wajib | **PASSED** |
| 2 | `test_data_types_and_validity` | Verifikasi tipe numerik dan non-negatif pada kolom sales | **PASSED** |
| 3 | `test_filter_processing_normal` | Pengujian filter kombinasi tahun, genre, dan platform | **PASSED** |
| 4 | `test_filter_processing_empty` | Penanganan filter saat opsi dikosongkan (0 baris) | **PASSED** |
| 5 | `test_filter_search_query` | Pengujian akurasi filter pencarian berdasarkan nama game | **PASSED** |
| 6 | `test_kpi_calculations_accuracy` | Verifikasi ketepatan matematis KPI dan nama game terlaris | **PASSED** |
| 7 | `test_dynamic_insights_generation` | Verifikasi kalkulasi dinamis insight (Top Game, Platform, Region, Year) | **PASSED** |
| 8 | `test_top10_games_chart` | Verifikasi pembuatan horizontal bar chart Top 10 Best-Selling Games | **PASSED** |
| 9 | `test_game_comparison_chart` | Verifikasi chart komparasi regional stacked bar antar game pilihan | **PASSED** |
| 10 | `test_chart_generation` | Verifikasi keberhasilan pembuatan 4 objek visualisasi Plotly standar | **PASSED** |
| 11 | `test_edge_case_single_row` | Stabilitas dashboard saat hanya tersisa 1 baris data | **PASSED** |
| 12 | `test_edge_case_no_valid_year` | Penanganan data jika kolom tahun bernilai missing/kosong | **PASSED** |
| 13 | `test_all_genres_in_palette` | Memastikan seluruh 12 genre memiliki mapping warna konsisten | **PASSED** |
| 14 | `streamlit run app.py` | Uji coba server headless & verifikasi respons HTTP 200 | **PASSED** |

---

## 6. Publikasi ke GitHub & Deployment

### Langkah Publikasi Git

```bash
git init
git add app.py requirements.txt README.md .gitignore .streamlit scripts dataset tests
git commit -m "Enhance GameScope with game-level visualizations and comparison"
git branch -M main
git remote add origin https://github.com/USERNAME/gamescope-uts.git
git push -u origin main
```

*(Ganti `USERNAME` dengan nama akun GitHub Anda)*

### Langkah Deployment ke Streamlit Community Cloud

1. Masuk ke [share.streamlit.io](https://share.streamlit.io/) dengan akun GitHub.
2. Klik **New app**.
3. Pilih repository `gamescope-uts`, branch `main`, dan main file path `app.py`.
4. Klik **Deploy**.
5. Salin tautan hasil deployment ke bagian atas README ini.

---

## 7. Checklist Sebelum Pengumpulan UTS

- [x] Dataset dari Kaggle valid dan divalidasi skrip cleaning.
- [x] Visualisasi Top 10 Best-Selling Video Games tampil dengan penekanan peringkat #1.
- [x] Fitur komparasi game (Compare Game Sales) interaktif dengan breakdown regional.
- [x] Input pencarian nama game / publisher berfungsi secara konsisten.
- [x] Garis paritas dan penyorotan game interaktif pada Scatter Plot.
- [x] Detail game terlaris tahunan pada hover Line Chart tren penjualan.
- [x] KPI Best-Selling Title menampilkan nama game dan angka penjualan aktual.
- [x] Seluruh 13 unit test otomatis lulus (`13/13 OK`).
- [x] Mengisi identitas Nama & NIM/NPM pada README.md.
- [x] Mengunggah repositori ke GitHub (status Public).
- [x] Mendeploy ke Streamlit Community Cloud dan menyalin URL live.

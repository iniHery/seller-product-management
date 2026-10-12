# Sistem Manajemen Produk Seller

Aplikasi full-stack untuk seller mengelola produk dan kategori, melihat ringkasan inventaris, serta mencari dan memfilter produk. Frontend menggunakan Vue 3 dan berkomunikasi dengan backend Django REST Framework melalui REST API.

## Fitur

- Registrasi, login, logout, dan informasi pengguna yang sedang login. Email harus unik tanpa membedakan huruf besar/kecil.
- Pengelolaan produk: daftar, detail, tambah, ubah, dan hapus.
- Pencarian produk berdasarkan nama atau SKU.
- Filter produk berdasarkan kategori dan status, dengan paginasi.
- Pengelolaan kategori.
- Dashboard yang menampilkan jumlah produk, produk aktif/nonaktif, dan total stok.
- Toggle status produk langsung dari daftar produk.
- Edit profil dan perubahan password dengan validasi backend.
- Audit produk dan kategori (`created_at`, `created_by`, `updated_at`, `updated_by`) serta soft delete (`deleted_at`, `deleted_by`).
- Komponen form dan tabel reusable; formatter waktu dan Rupiah dipusatkan di utility frontend.
- Token authentication; backend membatasi data produk sesuai seller yang login.

## Teknologi

- **Frontend:** Vue 3, Vite, Vue Router, Pinia, Axios, Tailwind CSS v4.
- **Backend:** Python, Django, Django REST Framework, TokenAuthentication.
- **Database:** PostgreSQL.

## Persyaratan

- Python yang memenuhi versi Django di `backend/requirements.txt`.
- Node.js yang kompatibel dengan versi Vite di `frontend/package.json`, beserta npm.
- PostgreSQL lokal atau database PostgreSQL yang dapat diakses.

## Menjalankan secara lokal

Jalankan backend dan frontend di dua terminal terpisah.

### 1. Siapkan backend

Dari direktori utama proyek, buat dan aktifkan virtual environment, lalu pasang dependensi:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Buat file `backend/.env` dan isi dengan konfigurasi lokal. Contoh berikut menggunakan PostgreSQL lokal; ganti nama pengguna, kata sandi, host, dan nama database sesuai lingkungan Anda:

```dotenv
SECRET_KEY=ganti-dengan-secret-key-lokal
DEBUG=True
DB_NAME=seller_product_management
DB_USER=postgres
DB_PASSWORD=ganti-dengan-kata-sandi-lokal
DB_HOST=localhost
DB_PORT=5432
```

`SECRET_KEY` wajib tersedia. Jangan gunakan contoh secret key atau kata sandi ini di lingkungan produksi dan jangan commit file `.env`.

Buat database PostgreSQL bernama `seller_product_management`, lalu jalankan migrasi dan server:

```powershell
python manage.py migrate
python manage.py runserver
```

Backend tersedia di `http://127.0.0.1:8000/`. Untuk menjalankan tes backend:

```powershell
python manage.py check
python manage.py test
```

### 2. Siapkan frontend

Buka terminal kedua dari direktori utama proyek:

```powershell
cd frontend
npm ci
```

Secara default, frontend mengirim permintaan API ke `http://127.0.0.1:8000/api/`. Jika backend berjalan di alamat lain, buat file `frontend/.env.local`:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api/
```

Jalankan server pengembangan:

```powershell
npm run dev
```

Buka URL yang ditampilkan Vite, biasanya `http://localhost:5173`. Untuk memeriksa build produksi:

```powershell
npm run build
```

Untuk menjalankan tes utilitas frontend:

```powershell
npm test
```

## Endpoint API utama

Semua endpoint API menggunakan prefix `/api/`.

| Metode | Endpoint | Keterangan |
| --- | --- | --- |
| `POST` | `/api/auth/register/` | Membuat akun seller |
| `POST` | `/api/auth/login/` | Login dan memperoleh token |
| `POST` | `/api/auth/logout/` | Logout dan menghapus token |
| `GET`, `PATCH` | `/api/auth/me/` | Mendapatkan atau memperbarui profil pengguna |
| `POST` | `/api/auth/change-password/` | Mengubah password setelah verifikasi password saat ini |
| `GET`, `POST` | `/api/categories/` | Melihat dan membuat kategori |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/categories/{id}/` | Detail dan pengelolaan kategori |
| `GET`, `POST` | `/api/products/` | Melihat dan membuat produk |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/products/{id}/` | Detail dan pengelolaan produk |
| `GET` | `/api/dashboard/` | Statistik produk dan stok seller |

Permintaan ke endpoint yang memerlukan login harus menyertakan header:

```http
Authorization: Token <token>
```

Token diperoleh dari endpoint login. Jangan menaruh token tetap di source code.

Daftar produk mendukung parameter `search`, `category`, `status`, dan `page`. Contoh:

```text
/api/products/?search=kaos&category=Pakaian&status=active&page=1
```

Pencarian memeriksa nama dan SKU; filter kategori mencocokkan nama kategori. Ukuran halaman saat ini adalah lima produk. Respons daftar membungkus metadata paginasi Django REST Framework (`count`, `next`, `previous`, dan `results`) di dalam properti `data`.

Penghapusan produk dan kategori adalah soft delete: data dipertahankan di database, ditandai dengan `deleted_at` dan `deleted_by`, lalu tidak ditampilkan dalam daftar/API normal.

## Konfigurasi dan deployment

- `backend/.env` menyimpan konfigurasi Django dan database. Backend membaca `SECRET_KEY`, `DEBUG`, dan `DATABASE_URL`; bila `DATABASE_URL` tidak tersedia, konfigurasi database lokal dapat diberikan melalui `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, dan `DB_PORT`.
- `frontend/.env.local` menyimpan `VITE_API_BASE_URL`. Variabel dengan prefix `VITE_` tersedia di bundle frontend, jadi jangan simpan secret di sana.
- File `vercel.json` menyediakan konfigurasi routing deployment frontend dan backend di Vercel. Atur environment variable untuk masing-masing layanan di platform deployment; pastikan URL API frontend mengarah ke backend yang ter-deploy dan backend dapat terhubung ke PostgreSQL.
- Untuk deployment, gunakan `DEBUG=False`, secret key yang kuat, kredensial database yang aman, dan konfigurasi CORS yang sesuai domain frontend. Jalankan migrasi database sebelum aplikasi digunakan.
- File `.env`, `.env.local`, dan `.neon` tidak boleh dimasukkan ke Git.

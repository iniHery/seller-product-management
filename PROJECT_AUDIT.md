# Laporan Audit Proyek: Sistem Manajemen Produk Seller

* **Tanggal Audit**: 29 Oktober 2026
* **Tipe Proyek**: Full Stack Web Application (Django REST Framework + Vue 3)
* **Status Git**: Branch `main` (Working tree clean, up to date with `origin/main`)
* **Basis Analisis**: Inspeksi menyeluruh kode aktual backend, frontend, skema database, dan eksekusi test suite otomatis.

---

## 1. Fitur yang Sudah Selesai dan Berjalan

Berdasarkan pemeriksaan kode aktual dan hasil pengujian otomatis (**73 test backend** dan **8 test unit frontend** dinyatakan **100% PASS**), berikut adalah rincian fitur yang telah selesai diimplementasikan:

### A. Modul Autentikasi & Akun (`accounts`)
* **Registrasi Akun (`/api/auth/register/`)**:
  * Pendaftaran dengan username, email, dan password.
  * Dilindungi validasi password bawaan Django (`UserAttributeSimilarityValidator`, `MinimumLengthValidator`, `CommonPasswordValidator`, `NumericPasswordValidator`).
  * Validasi unik email dengan perlakuan *case-insensitive* (`email__iexact`).
  * Rate limiting aktif: dibatasi maksimal **5 registrasi per jam** (`ScopedRateThrottle`, status `429 Too Many Requests`).
* **Login & Manajemen Sesi (`/api/auth/login/`)**:
  * Autentikasi kredensial pengguna, mengembalikan token DRF (`TokenAuthentication`) serta payload data pengguna.
  * Rate limiting aktif: dibatasi maksimal **5 percobaan login per menit** (`ScopedRateThrottle`).
* **Logout (`/api/auth/logout/`)**:
  * Menghapus token otentikasi di database dan membersihkan token dari `localStorage` frontend.
* **Get & Update Profil (`/api/auth/me/`)**:
  * Mendapatkan data user yang sedang login (`GET`).
  * Pembaruan data profil (`PATCH`) untuk username dan email dengan verifikasi duplikasi.
* **Ubah Password (`/api/auth/change-password/`)**:
  * Memverifikasi password saat ini, memvalidasi password baru, dan melakukan rotasi token di dalam transaksi atomik (`transaction.atomic()`).

### B. Modul Kategori (`Category`)
* **Karakteristik Model**:
  * Menggunakan `UUIDField` sebagai Primary Key.
  * Isolasi data per seller: Kategori terikat pada `seller_id`.
  * *Soft-delete*: Menggunakan kolom audit `deleted_at` dan `deleted_by`.
  * Unique constraint parsial: Nama kategori unik per seller untuk kategori aktif (`models.UniqueConstraint(fields=["seller", "name"], condition=Q(deleted_at__isnull=True))`).
  * Nama kategori yang telah di-*soft-delete* dapat didaftarkan kembali tanpa konflik integritas.
* **Operasi Endpoint (`/api/categories/`)**:
  * `GET`: List kategori milik seller aktif (hanya yang belum di-soft delete).
  * `POST`: Tambah kategori baru dengan pengecekan nama duplikat.
  * `GET /api/categories/<id>/`: Detail kategori milik seller.
  * `PUT` & `PATCH /api/categories/<id>/`: Update nama kategori.
  * `DELETE /api/categories/<id>/`: *Soft-delete* kategori dengan **proteksi integritas relasi** (ditolak jika kategori masih digunakan oleh produk aktif).

### C. Modul Produk (`Product`)
* **Karakteristik Model**:
  * Menggunakan `UUIDField` sebagai Primary Key.
  * Relasi `seller` (terisi otomatis dari token `request.user` dan read-only).
  * Relasi `category` (dibatasi hanya pada kategori milik seller yang bersangkutan).
  * SKU unik per seller pada produk aktif (`models.UniqueConstraint(fields=["seller", "sku"], condition=Q(deleted_at__isnull=True))`).
  * *Soft-delete* dengan pencatatan `deleted_at` dan `deleted_by`.
  * Audit fields lengkap: `created_at`, `created_by`, `updated_at`, `updated_by`.
  * Validasi harga non-negatif (`DecimalField(max_digits=10, decimal_places=2, min_value=0)`) dan stok (`PositiveIntegerField`).
  * Status produk: `active` atau `inactive`.
* **Operasi Endpoint (`/api/products/`)**:
  * `GET`: List produk dengan paginasi (`ProductPagination`, default 10 item per halaman).
  * Pencarian: Berdasarkan nama (`name__icontains`) dan SKU (`sku__icontains`).
  * Filter: Kategori (`category__name__icontains`), status produk (`active`/`inactive`), dan status stok (`low`, `out`, `critical`, `in_stock`).
  * `POST`: Tambah produk baru dengan penanganan *race-condition* SKU duplikat (`_save_with_seller_unique_value`).
  * `GET /api/products/<id>/`: Detail produk milik seller.
  * `PUT` & `PATCH /api/products/<id>/`: Update penuh dan parsial (misal toggle status aktif/inaktif).
  * `DELETE /api/products/<id>/`: *Soft-delete* produk.

### D. Modul Dashboard & Analitik (`/api/dashboard/`)
* Mengembalikan metrik ringkasan inventori seller secara real-time:
  * Total Produk, Produk Aktif, Produk Non-Aktif.
  * Total Stok Keseluruhan.
  * Jumlah Produk Stok Rendah (`stock <= 5`) dan Stok Habis (`stock == 0`).
  * Total Valuasi Stok (`Sum(price * stock)`).
  * Distribusi Kategori: Jumlah dan persentase produk per kategori.
  * 5 Produk Paling Kritis untuk aksi cepat *restock*.

### E. Modul Ekspor & Impor CSV
* **Ekspor CSV (`/api/products/export/`)**:
  * Mendukung ekspor berdasarkan filter aktif (pencarian, kategori, status stok).
  * Output berformat UTF-8 BOM (`\ufeff`) sehingga karakter dan format angka terbuka rapi di Microsoft Excel.
* **Unduh Template CSV (`/api/products/template/`)**:
  * Menyediakan berkas CSV contoh resmi yang siap diisi seller.
* **Impor CSV Massal (`/api/products/import/`)**:
  * Validasi ekstensi file (`.csv`) dan ukuran berkas (maksimal 5 MB).
  * Pemetaan nama kolom fleksibel (mendukung penamaan bahasa Indonesia maupun bahasa Inggris).
  * Validasi data baris demi baris menggunakan `ProductCSVRowSerializer`.
  * Pengecekan kategori: memastikan nama kategori pada CSV sudah terdaftar pada toko seller.
  * Pengecekan duplikasi SKU ganda baik antar-baris di dalam file CSV maupun terhadap database toko.
  * Transaksi atomik: Menggunakan `transaction.atomic()` dan `Product.objects.bulk_create()`. Data hanya tersimpan jika seluruh baris lolos validasi tanpa error parsial.
  * Umpan balik error spesifik per baris jika data tidak valid.

### F. Antarmuka Pengguna & UX (Vue 3 + Tailwind CSS v4)
* State management terpusat untuk sesi login menggunakan Pinia (`useAuthStore`).
* Interceptor Axios di [axios.js](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/api/axios.js) yang menyisipkan token otomatis dan menangkap error `401 Unauthorized` via *custom event* `auth:expired` untuk redirect ke halaman login.
* Penanganan *Race Condition* request pencarian/tabel dengan ID counter (`productsRequestId` dan `detailRequestId`).
* State visual komprehensif: Loading skeleton, empty state informatif, dialog konfirmasi hapus, modal detail produk, modal impor CSV dengan drag-and-drop, dan toast notifikasi sukses/gagal.
* Format input mata uang Rupiah interaktif dengan penanganan titik dan koma yang aman.
* Donut Chart visual distribusi kategori menggunakan SVG murni tanpa dependensi pihak ketiga.

---

## 2. Fitur Belum Selesai, Kekurangan, Bug & Masalah Keamanan

Meskipun fungsionalitas inti telah berjalan sangat baik dan stabil, audit mendalam menemukan beberapa batasan dan area perbaikan:

### A. Fitur yang Belum Tersedia (Gaps)
1. **Tidak Ada Unggah Gambar/Foto Produk (`ImageField`)**:
   * Model `Product` saat ini hanya mengelola data teks dan angka. Belum ada field gambar untuk thumbnail katalog produk layaknya aplikasi Seller Center modern.
2. **Tidak Ada Riwayat / Log Mutasi Stok (Stock History)**:
   * Perubahan stok saat ini langsung menimpa kolom `stock` di tabel `Product`. Tidak ada pencatatan riwayat kapan stok bertambah/berkurang, siapa yang mengubah, dan alasan perubahan (*adjustment*, *restock*, dll.).
3. **Threshold Stok Rendah Bersifat Statis (Hardcoded)**:
   * Batas stok rendah di-hardcode ke angka `5` di query backend (`stock__lte=5`) dan frontend. Tidak ada kolom `low_stock_threshold` di tabel `Product` untuk kustomisasi per produk.
4. **Tidak Ada Operasi Massal (Bulk Actions)**:
   * Penghapusan dan pengubahan status produk di UI masih dilakukan per baris. Belum tersedia fitur *bulk delete* atau *bulk toggle status* via checkbox di tabel produk.
5. **Belum Ada Profil Bisnis/Toko Lengkap**:
   * Akun seller saat ini hanya menggunakan model bawaan `User` Django (username & email). Belum ada profil toko terpisah seperti nama toko, deskripsi toko, alamat, atau logo toko.
6. **Ekspor Hanya Format CSV (Belum Ada Cetak PDF)**:
   * Belum tersedia fitur cetak katalog atau ringkasan inventori dalam format dokumen PDF.

### B. Bug & Potensi Masalah UX
1. **Navigation Guard Frontend Tidak Memblokir Route `/register` untuk User yang Sudah Login**:
   * Di [router/index.js:L94-L96](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/router/index.js#L94-L96), guard hanya mengarahkan user login yang membuka `/login` ke `/dashboard`:
     ```javascript
     if (to.name === 'Login' && isAuthenticated) {
       return { name: 'Dashboard' };
     }
     ```
   * Jika user yang sudah login mengetikkan URL `/register` di browser, halaman registrasi tetap terbuka alih-alih dialihkan ke dashboard.
2. **Kategori Tidak Memiliki Paginasi di Frontend**:
   * Endpoint `GET /api/categories/` mengembalikan seluruh kategori sekaligus tanpa limit/page. Jika seller memiliki ratusan kategori, seluruh elemen akan dimuat ke DOM sekaligus.

### C. Potensi Masalah Keamanan & Konfigurasi Arsitektur
1. **`DEFAULT_PERMISSION_CLASSES` di Backend Diset ke `AllowAny`**:
   * Di [settings.py:L62-L64](file:///c:/Users/idaba/projects/seller-product-management/backend/core/settings.py#L62-L64):
     ```python
     REST_FRAMEWORK = {
         'DEFAULT_AUTHENTICATION_CLASSES': [
             'rest_framework.authentication.TokenAuthentication',
         ],
         'DEFAULT_PERMISSION_CLASSES': [
             'rest_framework.permissions.AllowAny',
         ],
     }
     ```
   * *Risiko*: Meskipun saat ini semua view di `products` dan `accounts` secara eksplisit mendefinisikan `permission_classes = [IsAuthenticated]`, konfigurasi global ini berisiko: jika di masa mendatang seorang developer membuat `APIView` baru dan lupa menyematkan atribut `permission_classes`, endpoint tersebut akan terbuka untuk publik secara tidak sengaja. Standar keamanan DRF merekomendasikan `IsAuthenticated` sebagai default global, dan hanya menggunakan `AllowAny` secara eksplisit pada endpoint publik seperti Login dan Register.
2. **CORS Regex Subdomain Terlalu Terbuka**:
   * Di [settings.py:L97-L99](file:///c:/Users/idaba/projects/seller-product-management/backend/core/settings.py#L97-L99):
     ```python
     CORS_ALLOWED_ORIGIN_REGEXES = [
         r"^https://.*\.vercel\.app$",
     ]
     ```
   * *Risiko*: Pola regex ini mengizinkan domain Vercel apa pun di internet (`https://any-malicious-site.vercel.app`) untuk melakukan request CORS ke backend Anda. Sebaiknya regex dibatasi spesifik ke nama proyek Anda, misalnya `r"^https://seller-product-management.*\.vercel\.app$"`.
3. **Penyimpanan Token di `localStorage`**:
   * Token autentikasi disimpan di `localStorage` peramban. Ini merupakan pola umum SPA, namun memiliki risiko eksposur jika terdapat celah *Cross-Site Scripting* (XSS).

---

## 3. Kondisi Backend, Frontend, Database, dan Testing

| Komponen | Status | Keterangan & Kondisi Aktual |
| :--- | :---: | :--- |
| **Backend Framework** | **Sangat Baik** | Django 6.x + DRF 3.15. Arsitektur modular (`core`, `accounts`, `products`), penggunaan `APIView`, `Serializer`, dan pemisahan tanggung jawab kode berjalan konsisten. |
| **Frontend Framework** | **Sangat Baik** | Vue 3 dengan `<script setup>`, Pinia, Vue Router, Tailwind CSS v4, dan Axios. Struktur komponen rapi dan modular. |
| **Database** | **Sangat Baik** | PostgreSQL hosted di Neon Cloud via `dj-database-url`. Skema database konsisten dengan UUID PK, relasi `on_delete=PROTECT`, dan partial unique constraints. |
| **Otorisasi Multi-Tenant** | **Sangat Baik** | Otorisasi seller ditegakkan ketat di level ORM backend. Seller A sama sekali tidak dapat melihat, mengubah, menghapus, atau menggunakan kategori/produk milik Seller B. |
| **Audit & Soft Delete** | **Sangat Baik** | Konsisten di model `Product` dan `Category` dengan pencatatan `created_by`, `updated_by`, `deleted_by`, dan `deleted_at`. |
| **Backend Test Suite** | **100% Pass** | **73 test kasus** berhasil dieksekusi (`APITestCase`). Menguji autentikasi, rate-limiting, otorisasi seller, CRUD, validasi, pencarian, filter stok, dan impor/ekspor CSV. |
| **Frontend Test Suite** | **100% Pass** | **8 test kasus unit** berhasil dieksekusi dengan Node test runner bawaan (`formatters.test.js` dan `price.test.js`). |

---

## 4. File Penting yang Terlibat Beserta Fungsinya

### Backend (`/backend`)
* [backend/products/models.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/models.py): Definisi model `Category` dan `Product`, UUID primary key, audit fields, metode `soft_delete()`, dan partial unique constraints.
* [backend/products/views.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/views.py): Implementasi seluruh `APIView` untuk kategori, produk, dashboard, template CSV, ekspor CSV, dan impor CSV massal.
* [backend/products/serializers.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/serializers.py): Validasi data input, serialisasi data produk dan kategori, serta `ProductCSVRowSerializer` untuk validasi baris CSV.
* [backend/products/urls.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/urls.py): Routing endpoint REST API produk, kategori, dashboard, dan CSV.
* [backend/products/tests.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/tests.py): 52 test cases komprehensif untuk modul produk dan kategori.
* [backend/accounts/views.py](file:///c:/Users/idaba/projects/seller-product-management/backend/accounts/views.py): Endpoint autentikasi login, register, logout, profile update, dan change password dengan rate throttling.
* [backend/accounts/serializers.py](file:///c:/Users/idaba/projects/seller-product-management/backend/accounts/serializers.py): Validasi password Django, validasi username/email case-insensitive.
* [backend/accounts/tests.py](file:///c:/Users/idaba/projects/seller-product-management/backend/accounts/tests.py): 21 test cases autentikasi dan rate-limiting.
* [backend/core/settings.py](file:///c:/Users/idaba/projects/seller-product-management/backend/core/settings.py): Konfigurasi database PostgreSQL, middleware CORS, WhiteNoise, autentikasi Token, dan rate-limiting rates.

### Frontend (`/frontend`)
* [frontend/src/router/index.js](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/router/index.js): Pengaturan rute halaman, lazy-loading, dan navigation guard autentikasi.
* [frontend/src/stores/auth.js](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/stores/auth.js): Pinia store penyimpan token, status login, dan data user aktif.
* [frontend/src/api/axios.js](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/api/axios.js): Instance Axios terpusat dengan interceptor otentikasi token dan listener kedaluwarsa sesi.
* [frontend/src/api/productService.js](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/api/productService.js): Service API untuk seluruh panggilan HTTP produk dan file CSV.
* [frontend/src/api/categoryService.js](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/api/categoryService.js): Service API untuk CRUD kategori.
* [frontend/src/views/DashboardView.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/views/DashboardView.vue): Tampilan visual metrik toko, grafik donat kategori, dan produk stok kritis dengan auto-refresh.
* [frontend/src/views/ProductView.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/views/ProductView.vue): Tampilan utama manajemen produk, tabel, pencarian, multi-filter, paginasi, dan pemicu modal.
* [frontend/src/views/CategoryView.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/views/CategoryView.vue): Tampilan manajemen kategori dengan konfirmasi penghapusan aman.
* [frontend/src/components/ProductForm.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/components/ProductForm.vue): Modal form tambah dan edit produk dengan pemformat harga Rupiah dinamis.
* [frontend/src/components/ProductImportModal.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/components/ProductImportModal.vue): Modal unggah berkas CSV dengan drag-and-drop, validasi sisi klien, dan pratinjau error baris.
* [frontend/src/components/DashboardDonutChart.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/components/DashboardDonutChart.vue): Komponen visualisasi grafik lingkaran SVG interaktif.

---

## 5. Rekomendasi Fitur Berikutnya

Evaluasi fitur tambahan berdasarkan prioritas, nilai manfaat nyata bagi seller, kompleksitas implementasi, dan tingkat risiko terhadap fitur yang sudah ada:

| No | Rekomendasi Fitur | Nilai bagi Seller | Tingkat Kesulitan | Risiko Regresi | Prioritas |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | **Upload Gambar Produk (Product Image)** | Sangat Tinggi | Menengah | Rendah | **Tinggi (Utama)** |
| **2** | **Log Mutasi Stok (Stock History / Audit Trail)** | Sangat Tinggi | Menengah | Sangat Rendah | **Tinggi** |
| **3** | **Operasi Massal (Bulk Delete & Bulk Status)** | Tinggi | Rendah - Menengah | Rendah | **Menengah-Tinggi** |
| **4** | **Ambang Batas Stok Rendah Kustom (`low_stock_threshold`)** | Menengah | Rendah | Sangat Rendah | **Menengah** |
| **5** | **Profil Toko & Pengaturan Seller (Store Settings)** | Menengah | Rendah | Sangat Rendah | **Menengah** |
| **6** | **Perbaikan Keamanan & Route Guard (`/register` & CORS)** | Tinggi (Keamanan) | Sangat Rendah | Nol | **Wajib (Quick Win)** |
| **7** | **Ekspor Laporan Ringkasan PDF** | Menengah | Menengah | Nol | **Rendah (Opsional)** |

---

## 6. Rencana Pengerjaan Bertahap (Roadmap)

Rencana pengerjaan disusun terstruktur agar tidak mengganggu stabilitas fitur lama yang telah teruji:

### Tahap 1: Penguatan Keamanan & Perbaikan Bug Minor (Quick Wins)
* **Tujuan**: Menutup celah keamanan ringan dan merapikan edge-case navigasi.
* **File yang diubah**:
  * [frontend/src/router/index.js](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/router/index.js): Perbaiki guard agar user login yang membuka `/register` otomatis diarahkan ke `/dashboard`.
  * [backend/core/settings.py](file:///c:/Users/idaba/projects/seller-product-management/backend/core/settings.py): Perketat regex CORS Vercel ke domain spesifik proyek. Ubah `DEFAULT_PERMISSION_CLASSES` menjadi `IsAuthenticated`, dan pastikan `LoginAPIView` serta `RegisterAPIView` menggunakan `permission_classes = [AllowAny]`.
* **Migrasi Database**: Tidak ada.
* **Skenario Testing**: Jalankan test suite `python manage.py test accounts` untuk memastikan throttle dan autentikasi tetap berjalan normal.

### Tahap 2: Implementasi Upload Gambar Produk (Fitur Utama)
* **Tujuan**: Memungkinkan seller menambahkan foto thumbnail produk.
* **Dependensi Baru**: `Pillow` (untuk image processing di Django).
* **File yang diubah**:
  * [backend/products/models.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/models.py): Tambahkan field `image = models.ImageField(upload_to="products/%Y/%m/", null=True, blank=True)`.
  * [backend/products/serializers.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/serializers.py): Tambahkan `image` pada fields `ProductSerializer`.
  * [backend/core/settings.py](file:///c:/Users/idaba/projects/seller-product-management/backend/core/settings.py): Konfigurasi `MEDIA_URL` dan `MEDIA_ROOT`.
  * [frontend/src/components/ProductForm.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/components/ProductForm.vue): Tambahkan file picker input dengan image preview sebelum upload dan validasi ekstensi/ukuran.
  * [frontend/src/views/ProductView.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/views/ProductView.vue) & [ProductDetailModal.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/components/ProductDetailModal.vue): Tampilkan thumbnail gambar pada baris tabel dan modal detail produk.
* **Migrasi Database**: `python manage.py makemigrations` dan `python manage.py migrate`.
* **Skenario Testing**:
  * Uji unggah berkas valid (`.jpg`, `.png`, `.webp`) dan tolak berkas tidak valid (`.pdf`, `.exe`).
  * Uji isolasi akses file per seller.
  * Pastikan ekspor dan impor CSV tetap berfungsi normal tanpa error pada kolom gambar yang bersifat opsional.

### Tahap 3: Log Mutasi Stok (Stock History / Audit Trail)
* **Tujuan**: Menyimpan riwayat perubahan stok untuk keperluan transparansi dan audit inventori.
* **File yang diubah**:
  * [backend/products/models.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/models.py): Buat model baru `StockMovement` (`id`, `product`, `type: IN/OUT/ADJUSTMENT`, `quantity`, `balance_after`, `notes`, `created_by`, `created_at`).
  * [backend/products/views.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/views.py): Buat endpoint `GET /api/products/<id>/stock-movements/` dan trigger pencatatan mutasi otomatis setiap kali stok produk di-update atau diimpor via CSV.
  * [frontend/src/components/ProductDetailModal.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/components/ProductDetailModal.vue): Tambahkan tab atau bagian tabel riwayat mutasi stok.
* **Migrasi Database**: `makemigrations` dan `migrate` untuk tabel `StockMovement`.
* **Skenario Testing**:
  * Uji perubahan stok via PUT/PATCH menghasilkan entri mutasi stok yang akurat.
  * Uji impor CSV membuat catatan mutasi awal (`IN` / stok masuk).

### Tahap 4: Operasi Massal (Bulk Actions)
* **Tujuan**: Meningkatkan efisiensi kerja seller saat mengelola banyak produk.
* **File yang diubah**:
  * [backend/products/views.py](file:///c:/Users/idaba/projects/seller-product-management/backend/products/views.py): Buat endpoint `POST /api/products/bulk-delete/` dan `POST /api/products/bulk-status/`.
  * [frontend/src/views/ProductView.vue](file:///c:/Users/idaba/projects/seller-product-management/frontend/src/views/ProductView.vue): Tambahkan kolom checkbox seleksi baris, checkbox "Pilih Semua", dan bar menu aksi massal yang muncul saat ada baris terpilih.
* **Migrasi Database**: Tidak ada.
* **Skenario Testing**:
  * Uji hapus massal hanya memproses produk milik seller yang melakukan request.
  * Uji transaksi atomik jika terdapat kegagalan.

---

## 7. Kesimpulan & Rekomendasi Tindakan Berikutnya

### Ringkasan Status Proyek
Repository `seller-product-management` berada dalam kondisi **sangat sehat, terstruktur rapi, dan memiliki cakupan uji otomatis yang sangat kuat**. Seluruh persyaratan inti internship (CRUD Produk, Kategori, Otorisasi Seller, Soft Delete, Dashboard, Search/Filter, Paginasi, dan CSV Import/Export) telah berjalan dan terverifikasi secara fungsional.

### Rekomendasi Pilihan Terbaik untuk Dikerjakan Selanjutnya
Fitur yang paling disarankan untuk dikerjakan berikutnya adalah:

1. **Langkah 0 (Quick Win)**: Lakukan perbaikan kecil pada guard route `/register` dan pengetatan CORS regex di backend (bisa selesai dalam hitungan menit tanpa migrasi database).
2. **Langkah 1 (Fitur Utama)**: Kerjakan **Upload Gambar Produk (Product Image Upload)**.
   * **Alasannya**: Ini adalah satu-satunya elemen esensial visual produk e-commerce yang belum ada di aplikasi. Penambahan gambar produk akan mengubah tampilan aplikasi dari sekadar *data-table internal* menjadi aplikasi *Seller Center* profesional yang memukau saat dipresentasikan kepada mentor atau pengguna.

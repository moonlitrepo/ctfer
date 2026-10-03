# High level language pattern

## note
chall buatan ai, namun sudah sangat cukup untuk mempelajari apa itu struct.

langkah pertama yang saya lakukan adalah melakukan _fast check_ dengan memeriksa metadata serta menjalankan program untuk memeriksa bagaimana tingkah laku program saat sedang dijalankan.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> file warung
warung: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=38d0d69facc9db77a3c4d6038671eac47c5d0fe8, for GNU/Linux 3.2.0, stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung
pakai: warung <id_barang>
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 1
Barang tidak ditemukan
```

saya belum bisa menyimpulkan apa apa dari fastcheck ini. tapi informasi yang sudah didapatkan bisa di simpan untuk memperkirakan langkah apa yang bisa di gunakan kedepannya:
- file : stripped binary elf x86-64
- membutuhkan 1 argumen untuk dapat dijalankan
- argumen tersebut merupakan id barang
- id barang belum diketahui

maka dengan 4 informasi itu rencananya saya akan menggunakan ghidra untuk melanjutkan analisis , saya akan mulai dengan mencari main functions dari entry point, lalu mencari informasi tambahan
mengenai id barang tersebut.

berikut merupakan hasil dekompilasi fungsi main() yang semua nama variabel dan fungsi pentingnya sudah saya rename sehingga lebih mudah dibaca.
```

undefined8 main(int argc,long argv)

{
  int input_id;
  undefined8 ret;
  long result_cari;
  int i;
  
  if (argc == 2) {
    input_id = atoi(*(char **)(argv + 8));
    result_cari = cari(input_id);
    if (result_cari == 0) {
      puts("Barang tidak ditemukan");
      ret = 1;
    }
    else if (*(int *)(result_cari + 12) == 0) {
      printf("Barang biasa. Harga: %d, stok: %d\n",(ulong)*(uint *)(result_cari + 4),
             (ulong)*(uint *)(result_cari + 8));
      ret = 0;
    }
    else {
      printf("Barang langka! Isi arsip: ");
      for (i = 0; i < 30; i = i + 1) {
        putchar(*(uint *)(result_cari + 12) ^
                (uint)(byte)"~bzi~lQY^X_I^uC^_uI_GKuELLYO^Wpakai: warung <id_barang>"[i]);
      }
      putchar(10);
      ret = 0;
    }
  }
  else {
    puts("pakai: warung <id_barang>");
    ret = 1;
  }
  return ret;
}
```
kesimpulan utama dari fungsi main ini adalah kebanyakan merupakan alur filter yang merespon kesalahan dalam menjalankan file binary seperti saat menjalankan binary tanpa argumen atau saat id barang
tidak valid. 

jika id tersebut valid, maka program akan mencetak string "Barang biasa. Harga: %d, stok: %d\n" ,result_cari + 4,result_cari + 8 (disederhanakan) , dimana result_cari tersebut berasal dari sebuah
alamat memori. + offset. ciri ciri dari penggunaan struct. jika berasumsi ini menggunakan struct saya akan mengaggap progam ini memiliki struct denga bentuk id, harga, stok.

hal menarik saya temukan pada alur if else, pada baris else nya terdapat string "Barang langka! Isi arsip: " dan ~bzi~lQY^X_I^uC^_uI_GKuELLYO^Wpakai: warung <id_barang>
yang mereka lakukan adalah melakukan operasi xor antara **result_cari+12** dengan 30 byte pertama pada string random tersebut. 30 byte pertamanya adalah **~bzi~lQY^X_I^uC^_uI_GKuELLYO^W**

terlihat seperti proses dekripsi, saya berasumsi bahwa ini adalah flag terenkripsi yang akan di dekripsi melalui operasi xor menggunakan key id barang yang tersimpan di suatu tempat. saya bisa saja
melakukan xor brute force pada string ini, namun tujuan utama saya di chall ini adalah memahami bagaimana struct bekerja. maka saya tidak selesaikan write up ini dengan brute force .

untuk mencari dari mana id nya, saya akan menganalisis fungsi cari(), karena result_cari berasal dari baris `result_cari = cari(input_id);`

hasil dekompilasi cari():
```C
undefined * cari(int input_id)

{
  int i;
  
  i = 0;
  while( true ) {
    if (4 < i) {
      return (undefined *)0;
    }
    if (input_id == *(int *)(&tabel_0x104020 + (long)i * 16)) break;
    i = i + 1;
  }
  return &tabel_0x104020 + (long)i * 16;
}

```
dari sini mulai terlihat jelas. pertama fungsi ini melakukan perulangan sebanyak 4 kali untuk memeriksa apakah id input kita valid dengan salah satu id di struct program ini.
cara fungsi ini memilih id nya adalah dengan membandingkan input id dengan **alamat tabel + (i*16)** ini artinya jarak tiap id pertama ke id selanjutnya adalah 16 byte, jika i = 0 maka 
program akan membandingkan input id dengan alamat tabel + 0*16 , artinya alamat tabel offset 0 , awal tabel. jika i = 1 maka membandingkan dengand data id kedua di jarak 16 byte setelah id pertama
dan seterusnya hingga 4. ini artinya total keseluruhan ada 4 id valid. 

untuk melihatnya cukup klik dua kali pointer tabel tersebut (**&tabel_0x104020**)

berikut hasil ekstraksi dari tabel nya
```
                             tabel_0x104020                                  XREF[3]:     cari:001011c9(*), 
                                                                                          cari:001011d0(*), 
                                                                                          cari:001011e4(*)  
        00104020 65              ??         65h    e
        00104021 00              ??         00h
        00104022 00              ??         00h
        00104023 00              ??         00h
        00104024 ac              ??         ACh
        00104025 0d              ??         0Dh
        00104026 00              ??         00h
        00104027 00              ??         00h
        00104028 14              ??         14h
        00104029 00              ??         00h
        0010402a 00              ??         00h
        0010402b 00              ??         00h
        0010402c 00              ??         00h
        0010402d 00              ??         00h
        0010402e 00              ??         00h
        0010402f 00              ??         00h
        00104030 66              ??         66h    f
        00104031 00              ??         00h
        00104032 00              ??         00h
        00104033 00              ??         00h
        00104034 d0              ??         D0h
        00104035 07              ??         07h
        00104036 00              ??         00h
        00104037 00              ??         00h
        00104038 32              ??         32h    2
        00104039 00              ??         00h
        0010403a 00              ??         00h
        0010403b 00              ??         00h
        0010403c 00              ??         00h
        0010403d 00              ??         00h
        0010403e 00              ??         00h
        0010403f 00              ??         00h
        00104040 67              ??         67h    g
        00104041 00              ??         00h
        00104042 00              ??         00h
        00104043 00              ??         00h
        00104044 e0              ??         E0h
        00104045 2e              ??         2Eh    .
        00104046 00              ??         00h
        00104047 00              ??         00h
        00104048 08              ??         08h
        00104049 00              ??         00h
        0010404a 00              ??         00h
        0010404b 00              ??         00h
        0010404c 00              ??         00h
        0010404d 00              ??         00h
        0010404e 00              ??         00h
        0010404f 00              ??         00h
        00104050 68              ??         68h    h
        00104051 00              ??         00h
        00104052 00              ??         00h
        00104053 00              ??         00h
        00104054 4c              ??         4Ch    L
        00104055 1d              ??         1Dh
        00104056 00              ??         00h
        00104057 00              ??         00h
        00104058 00              ??         00h
        00104059 00              ??         00h
        0010405a 00              ??         00h
        0010405b 00              ??         00h
        0010405c 00              ??         00h
        0010405d 00              ??         00h
        0010405e 00              ??         00h
        0010405f 00              ??         00h
        00104060 99              ??         99h
        00104061 07              ??         07h
        00104062 00              ??         00h
        00104063 00              ??         00h
        00104064 01              ??         01h
        00104065 00              ??         00h
        00104066 00              ??         00h
        00104067 00              ??         00h
        00104068 01              ??         01h
        00104069 00              ??         00h
        0010406a 00              ??         00h
        0010406b 00              ??         00h
        0010406c 2a              ??         2Ah    *
        0010406d 00              ??         00h
        0010406e 00              ??         00h
        0010406f 00              ??         00h

```

cukup panjang dan merepotkan jadi saya sederhanakan dan hapus semua byte nol nya

```
                        tabel_0x104020   
        00104020 65              ??         65h    e 0
        00104024 ac              ??         ACh
        00104025 0d              ??         0Dh
        00104028 14              ??         14h

        00104030 66              ??         66h    f 16
        00104034 d0              ??         D0h
        00104035 07              ??         07h
        00104038 32              ??         32h    2

        00104040 67              ??         67h    g 32
        00104044 e0              ??         E0h
        00104045 2e              ??         2Eh    .

        00104050 68              ??         68h    h 48
        00104054 4c              ??         4Ch    L
        00104055 1d              ??         1Dh

        00104060 99              ??         99h      64
        00104061 07              ??         07h
        00104064 01              ??         01h
        00104068 01              ??         01h
        0010406c 2a              ??         2Ah    *
        0010406f 00              ??         00h

```
menurut hasil analisis sebelumnya terdapat informasi bahwa tiap data barang memiliki ukuran 16 byte, selain menghilangkan null bytes kecuali terakhir itu.saya juga menghitung 16 byte dari data pertama.
setelah di pisah seperti ini mulai terlihat data nya. ingat bahwa id di ambil dari offset tabel + i*16 ini artinya id ada di tiap offset kelipatan 16.

angka angka pada kelipatan tersebut adalah **65,66,67,68,99** 

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 65
Barang tidak ditemukan
```
masih ditolak , saya buka kembali dekompiler dan langsung menyadari bahwa angka tersebut masih berupa hex, jika di convert menjadi desimal maka datanya akan menjadi : 101,102,103,104,1945

well sudah terlihat jelas mana "impostor" nya, namun karena jumlah data sedikit , hanya 5 jadi tidak salah juga kalau mencoba menginput mereka satu satu
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 101
Barang biasa. Harga: 3500, stok: 20
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 102
Barang biasa. Harga: 2000, stok: 50
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 103
Barang biasa. Harga: 12000, stok: 8
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 104
Barang biasa. Harga: 7500, stok: 0
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 1945
Barang langka! Isi arsip: THPCTF{struct_itu_cuma_offset}
```

selesai, 

FLAG : **THPCTF{struct_itu_cuma_offset}**

evaluasi nya jika melihat pemanggilan sesuatu menggunakan pointer address + offset. langsung saja baca offset keberapa yang menjadi bagian penting untuk di analisis dan masuk ke alamat yang di tunjuk
pointer tersebut untuk menghitung offset yang didapat untuk mengekstrak datanya. 

selain itu terus perhatikan tipe data dan tipe integer, pada jendela listing biasanya alamat memory dan data yang ada di situ akan tertulis dalam bentuk heksadesimal. tergantung konteks chall juga
tapi justru karena itu harus selalu di periksa dua kali sebelum di kirim sebagai paylaod input.

saya mencoba menggunakan cyberchef dan berhasil mendapatkan flag dengan key nya
```
Key = 2a: THPCTF{struct_itu_cuma_offset}
```
karena inti chall bukan bagaimanapun dapatkan flag, jadi saya gunakan ini sebagai opsi kedua apabila terjadi error nanti.

untuk analisis gdb saya belum bisa lanjutkan karena saat saya mengetik kata ini waktu menunjukkan pukul 01:05 pagi. teman satu kelas ku sudah tidur pulas. bruh

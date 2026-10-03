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
saya juga mengambil bentuk kode nya dalam asemmbly:
```asemmbly
                             LAB_001011bd                                    XREF[1]:     001011f8(j)  
        001011bd 8b 45 fc        MOV        EAX,dword ptr [RBP + i]
        001011c0 48 98           CDQE
        001011c2 48 c1 e0 04     SHL        RAX,0x4
        001011c6 48 89 c2        MOV        RDX,RAX
        001011c9 48 8d 05        LEA        RAX,[tabel_0x104020]                             = 65h    e
                 50 2e 00 00
        001011d0 8b 04 02        MOV        EAX=>tabel_0x104020,dword ptr [RDX + RAX*0x1]    = 65h    e
        001011d3 39 45 ec        CMP        dword ptr [RBP + local_1c],EAX
        001011d6 75 18           JNZ        LAB_001011f0
        001011d8 8b 45 fc        MOV        EAX,dword ptr [RBP + i]
        001011db 48 98           CDQE
        001011dd 48 c1 e0 04     SHL        RAX,0x4
        001011e1 48 89 c2        MOV        RDX,RAX
        001011e4 48 8d 05        LEA        RAX,[tabel_0x104020]                             = 65h    e
                 35 2e 00 00
        001011eb 48 01 d0        ADD        RAX,RDX
        001011ee eb 0f           JMP        LAB_001011ff

```
hanya bagian inti dari loop nya, disini adalah contoh bentuk asemmbly dari bentuk akses struct. di awalu oleh merubah variabel int menjadi ukuran 64 bit. normalnya di C ukuran tipe data int adalah 4 byte atau 32 bit,karena nanti akan melakukan perhitungan menggunakan register 64 bit seperti RAX,RDX dsb maka ukurannya harus disamakan dengan instruksi **CDQE**

lalu program menggunakan cara yang sama seperti peraturan x86 yaitu alamat+offset.
dalam kasus ini mengakses struct pada tabel. pertama program akan melakukan shiftleft sebanyak 4 byte , ini sama saja dengan * 16 . karena 2 pangkat 4 sama dengan 16. menyimpan nya di RDX. setelah itu program mengambil alamat target untuk dihitung ukurannya dengan rumus tadi, tampilannya dalam asm adalah [RDX + RAX*0x1], dimana rdx adalah offset hasil perulangannya, lalu rax adalah base address dari tablenya.ini literaly menunjuk ke elemen pertama pada tiap struct yang ada di table, karena tiap loop program akan melompati 16 byte address, sementara itu memang adalah ukuran tiap struct nya.

kode di bawah nya merupakan coompare apakah id input kita sama dengan apa yang ada di alamat tersebut

dari sini mulai terlihat jelas. pertama fungsi ini melakukan perulangan sebanyak 4 kali untuk memeriksa apakah id input kita valid dengan salah satu id di struct program ini.
cara fungsi ini memilih id nya adalah dengan membandingkan input id dengan **alamat tabel + (i*16)** ini artinya jarak tiap id pertama ke id selanjutnya adalah 16 byte, jika i = 0 maka 
program akan membandingkan input id dengan alamat tabel + 0*16 , artinya alamat tabel offset 0 , awal tabel. jika i = 1 maka membandingkan dengand data id kedua di jarak 16 byte setelah id pertama. dapat disimpulkan ukuran tiap struct adalah 16 byte.

saya sebut satu struct karena dalam ukuran 16 byte tersebut terdapat 3 elemen pada offset tabel_addr+0 = id , tabel_addr+0x4 = harga barang, dan tabel_addr+0x8 = stok
dan seterusnya hingga 4. ini artinya total keseluruhan ada 4 id valid. ada kodenya di main()
prove :  

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

sebelum mencobanya pada file binary, saya akan menganalisis struct pertama terlebih dahulu,
```
        00104020 65              ??         65h    e 0
        00104024 ac              ??         ACh
        00104025 0d              ??         0Dh
        00104028 14              ??         14h
```
tiap elemen memiliki ukuran 4 byte, setelah elemen terakhir, struct terisi dengan byte 0 , ini biasanya merupakan padding dari compiler agar ukuran nya tetap pada kelipatan tertentu. 
seperti dari data, kali ini table addr nya adalahj **0x104020** , offset +0 maka data nya adalah 0x65, atau 101 dalam desimal. selanjutnya table addr + 0x4 untuk harga. perlu diperhatikan di offset ini ada 2 data yaitu 0xac dan 0x0d . jarak mereka hanya 1 byte. maka kemungkinan mereka merupakan satu data yang sama. dalam format little endian perlu diubah dulu jadi big endian,urut dari atas `0xac0d` dirubah jadi `0x0dcc` , atau **3500** dalam desimal. terakhir pada table addr + 0x8 ada data 0x14, 20 dalam desimal.

dengan ini lengkap sudah satu stuct utuh kita pada offset table+0
id = 101   
harga = 3500   
stok = 20

saatnya menjalankan
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(refleksi)
└> ./warung 101
Barang biasa. Harga: 3500, stok: 20
```
perfect, ini sama persis. sekarang tingal ekstrak 3 data lain dan masukkan ke binary dalam format desimal.
```
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

day 4 , pukul 06-26 

saya berhasil mengetahui cara mencari breakpoint pada file dengan PIE dan dalam kondisi stripped, yaitu cari alamat target melalui ghidra, dan lakukan starti agar program berhenti tepat pada instruksi pertama nya, baru `breakrva addr` misal `breakrva 0x1201` untuk memasang breakpoint melalui offset yang sudah diketahui dari ghidra. selanjutnya cukup continue hingga program berhenti pada breakpoint yang ditentukan. 

```
breakrva 0x1201
```
selain itu saya juga menemukan informasi lain bahwa main() ada pada alamat berikut dan memiliki 67 baris instruksi.
```
x/67i 0x555555555201
```

analisis gdb ini akan saya fokus kan ke satu proses saat input merupakan id 1945:
```asemmbly
    ↓
   0x5555555551bd    mov    eax, dword ptr [rbp - 4]        EAX, [0x7fffffffdc9c] => 4
   0x5555555551c0    cdqe
   0x5555555551c2    shl    rax, 4
   0x5555555551c6    mov    rdx, rax                        RDX => 0x40
 ► 0x5555555551c9    lea    rax, [rip + 0x2e50]             RAX => 0x555555558020 ◂— 0xdac00000065 /* 'e' */
   0x5555555551d0    mov    eax, dword ptr [rdx + rax]      EAX, [0x555555558060] => 0x799
   0x5555555551d3    cmp    dword ptr [rbp - 0x14], eax     0x799 - 0x799     EFLAGS => 0x246 [ cf PF af ZF sf IF df of iopl:00 ac ]
   0x5555555551d6  ✘ jne    0x5555555551f0              <0x5555555551f0>
```
ini merupakan bagian loop , mirip seperti di ghidra. karena data id 1945 ada di struct terakhir maka proses compare nya akan berjalan pada loop ke terakhir yaitu loop ke 5.
terlihat nilainya sama sehingga program tidak melakukan jne. 

disini karena saya menggunakan pwnbdg jadi value tiap register akan dicetak tanpa harus leak satu satu, pertama jelas disitu terdapat value dari tipe data integer di rbp-4 yang disimpan di eax, itu adalah value looping sekarang, 4. setelah dirubah menjadi 64 bit, 4 tersebut akan di shiftleft sebanyak 4 byte, sehingga menghasilkan 4*16 atau 4<<4 = 64 byte (0x40) dalam hex. yang ini akan disimpan di rdx karena rax akan digunakan untuk menyimpan base address dari tabel itu sendiri.

setelah program menghitung alamat elemen pertama pada struct terakhir dengan rumus standart x86 yaitu [addr + offset] atau sebaliknya juga tidak masalah. program mengambil valuenya dan membandingkannya dengan input id kita .

nilai hex dari 1945 adalah 0x799, dan pada instruksi di 0x0x5555555551d3, cmp menghasilkan return 0 , karena nilainya sama persis maka program tidak melompat dan melanjutkan untuk melakukan instruksi sesuai kondisi sekarang. karena 1945 adalah id rahasia, maka kondisi ini akan mentrigger percabangan else dan melakukan dekripsi flagnya untuk dicetak ke layar.



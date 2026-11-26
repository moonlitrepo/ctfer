# Formation

> [!note]
> untuk latihan aku sengaja tidak mencoba menggunakan bantuan ai dan source code walau tersedia. analisis dan langkah yang diambil pada write up ini mungkin akan
> sedikit lebih merepotkan.

## deskripsi 

Author: aseng

Recover the accepted input from the issued PE, then explain the byte construction. Original challenge: aseng (LKSN 2026). Classroom package and 
walkthrough: Dimas Maulana / TCP1P. Official metadata: [Github](https://github.com/LKS-ID/2026-LKSN-Jakarta-Daring-Public/blob/4dfbdda890e7217f72ecf86b72b3c24657b3dbba/Reverse%20Engineering/Formation/challenge.yml
)

file terlampir: [file](Formation)

The attached source/artifacts are whitebox study material. Ask the instructor for the local lab, Docker image when needed, and post-attempt PDF.

## Information Gathering
file yang diberikan masih terkompresi, dan setelah di ekstrak terdapat 3 file :
- README.md
- formation.exe
- source-model.rs

tentu langkah pertama ku adalah membaca file readme tersebut, berikut isinya:
```
# P1 · Formation

Recover the accepted input from the issued PE, then explain the byte construction.

This package belongs to the open practice event. Open the files in VS Code; test only the local lab. Ask the instructor for the Docker image when needed.

The instructor shares the P1–P6 PDF after your first attempt.

**Source note:** The Rust file is an independent teaching reconstruction, not the original source.
```
readme ini menyinggung file binary teresebut dan menyebutkan PE dan rust. asumsi ku file executable PE yang dikompilasi dari bahasa Rust. untuk memverifikasi aku memeriksa metadatanya menggunakan commmand file:
```bash
file formation.exe
```
```bash
strings formation.exe  | grep  LKS
```
hasil:
```
formation.exe: PE32+ executable (console) x86-64, for MS Windows, 5 sections
LKS{fi1r5t_st3p_
```
lalu dilanjutkan dengan menjalankan file executable tersebut untuk mencari tahu perilaku permukaannya.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(formation)
└> ./formation.exe
Enter flag: idk
Wrong.
```
terverifikasi bahwa file formation.exe ini memang merupakan file PE32 khas windows. dan hal yang lebih menarik adalah saat aku mencoba grep string flag,
hasilnya mengembalikan string flag yang terpotong. masih belum diketahui kenapa bisa terpotong, tapi kemungkinan ku adalah sisanya sengaja di hilangkan dan di enkripsi. atau ini terjadi karena terdapat optimasi bawaan compiler. 


hasil observasi singkat:
- file : PE32 executable windows
- perilaku : saat dijalankan program meminta sebuah flag, input tidak valid akan mengembalikan string **Wrong.**
- informasi yang dimiliki : pecahan flag (**LKS{fi1r5t_st3p_**) tertulis hardcoded. sisanya belum diketahui.

selanjutnya aku akan coba mencari informasi lebih lanjut dengan mendecompile nya menggunakan ghidra dan langusng melakukan pencarian string dengan
menggunakan pecahan flag yang ku miliki tersebut.

anehnya percobaan pencarian strings `LKS{fi1r5t_st3p_` di ghidra gagal.  

percobaan kedua ku lakukan dengan mencari string yang dicetak pada saat runtime program (Enter flag:)

<p align="center"> <img width="812" height="174" alt="image" src="https://github.com/user-attachments/assets/8de29a79-6144-478d-a91f-4c7252b0e91c" />
 </p>

string tersebut ditemukan di alamat `0x140019400` yang memiliki 1 reference yaitu ke alamat `0x140019410` alamat kedua ini adalah sebuah pointer. Pointer ini memiliki 2 reference yaitu pada `FUN_140001010:140001043(*)` dan `FUN_140001010:14000104a(*)` . untuk pergi ke arah reference itu cukup klik dua kali saja salah satu alamat xrefnya.

halaman decompiler berpindah ke sebuah fungsi besar. aku langsung ubah namanya menjadi main-like(). referensi tersebut mengarah pada baris kode inisiasi variabel 
```c
local_20d8 = &PTR_s_Enter_flag:_140019410;
```

string ini di inisiasi di fungsi `FUN_140001010` / main-like . jika string `Enter flag:` di cetak saat runtime, artinya string ini akan di gunakan oleh fungsi printf, puts, atau fungsi stdout lain. jika di fungsi ini lah pointer ke string tersebut di inisiasi, bisa dijadikan alasan untuk asumsiku bahwa fungsi ini adalah main nya.

aku coba cari sekali lagi string flag melalui fitur pencarian string di jendela decompiler, bisa dibuka dengan shortcut `CTRL + F` , lalu ku ketik format flag `LKS`.

kursor teks ku langsung fokus ke arah kode di **baris ke-574**

```
builtin_strncpy(pcVar16,"LKS{fi1r5t_st3p_to_ruSs5t_exe}",0x1e);
```
flag berhasil di dapatkan!  

flag : **LKS{fi1r5t_st3p_to_ruSs5t_exe}",0x1e)**


## how?
permasalahan yang ditemukan di awal adalah hasil strings menunjukkan sebagian flag saja, bagaimana ini bisa terjadi walaupun string flag tertulis lengkap dan hardcoded di decompiler?

ini akan terjawab setelah melihat jendela disassemblynya.
```
       140001c83 66 0f 6f 05 d5 76 01 00     MOVDQA     XMM0 ,xmmword ptr [DAT_140019360 ]   = 4Ch    L
       140001c8b f3 0f 7f 00                 MOVDQU     xmmword ptr [RAX ],XMM0
       140001c8f 48 b8 74 6f 5f 72 75 53 73  MOV        RAX ,0x35735375725f6f74
       140001c99 48 89 47 10                 MOV        qword ptr [RDI  + 0x10 ],RAX
       140001c9d c7 47 18 74 5f 65 78        MOV        dword ptr [RDI  + 0x18 ],0x78655f74
       140001ca4 66 c7 47 1c 65 7d           MOV        word ptr [RDI  + 0x1c ],0x7d65

# berikut isi DAT_140019360 yang dipindahkan ke register XMM0:
                          DAT_140019360                                   XREF[1]:     FUN_140001010:140001c83 (R)   
       140019360 4c              ??         4Ch    L
       140019361 4b              ??         4Bh    K
       140019362 53              ??         53h    S
       140019363 7b              ??         7Bh    {
       140019364 66              ??         66h    f
       140019365 69              ??         69h    i
       140019366 31              ??         31h    1
       140019367 72              ??         72h    r
       140019368 35              ??         35h    5
       140019369 74              ??         74h    t
       14001936a 5f              ??         5Fh    _
       14001936b 73              ??         73h    s
       14001936c 74              ??         74h    t
       14001936d 33              ??         33h    3
       14001936e 70              ??         70h    p
       14001936f 5f              ??         5Fh    _

```
string ini lah yang berhasil di deteksi oleh command strings, namun hanya `16 byte pertama` saja sedangkan keseluruhan flag adalah `30 byte`. artinya masih ada `14 byte` flag yang belum diketahui.

ternyata sebenarnya mereka masih tertulis secara hardcode namun bukan di section .rdata namun di .text , digabung bersama code program. ini dibukutikan pada baris kode ini:
```
140001c8f 48 b8 74 6f 5f 72 75 53 73  MOV        RAX ,0x35735375725f6f74
140001c99 48 89 47 10                 MOV        qword ptr [RDI  + 0x10 ],RAX
140001c9d c7 47 18 74 5f 65 78        MOV        dword ptr [RDI  + 0x18 ],0x78655f74
140001ca4 66 c7 47 1c 65 7d           MOV        word ptr [RDI  + 0x1c ],0x7d65
```

setelah 16 byte pertama flag , program masih mengurus 14 byte sisanya langsung tanpa register vektor. jika diperhatikan lebih teliti hex yang sedang dipindahkan tersebut merupakan bagian flagnya yang tidak berhasil terbaca oleh strings karena berada di .text . menurut aturan little endian, tiap byte nya tersusun secara terbalik jadi urutan hex nya dibentuk dari bawah ke atas.

`0x7d65` + `0x78655f74` + `0x35735375725f6f74` = `0x7d6578655f7435735375725f6f74`

lalu lakukan full reverse dan ubah ke bentuk character dengan command 
```bash
echo 0x7d6578655f7435735375725f6f74 | xxd -r -p | rev
```
result:
```
to_ruSs5t_exe}
```

namun dalam bentuk asli binary, string tersebut tertulis secara terpisah karena terdapat byte opcode yang memindahkan mereka, seperti mov.


butuh cukup ketelitian dalam pengerjaan challenge ini

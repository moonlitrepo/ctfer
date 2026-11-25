# Formation

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
tidak banyak informasi tentang file tersebut, ia hanya menyebutkan PE. untuk memverifikasi aku memeriksa metadatanya menggunakan commmand file:
```bash
└> file formation.exe
formation.exe: PE32+ executable (console) x86-64, for MS Windows, 5 sections
┌[rotalactf]-[LAPTOP-6QMID52F]-(formation)
└> strings formation.exe  | grep  LKS
LKS{fi1r5t_st3p_
```
terverifikasi bahwa file formation.exe ini memang merupakan file PE32 khas windows. dan hal yang lebih menarik adalah saat aku mencoba grep string flag,
hasilnya mengembalikan string flag yang terpotong.  ini akan memudahkan ku dalam analisis selanjutnya.

terakhir tentu menjalankan file executable tersebut untuk mencari tahu perilaku permukaannya.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(formation)
└> ./formation.exe
Enter flag: idk
Wrong.
```

hasil observasi singkat:
- file : PE32 executable windows
- perilaku : saat dijalankan program meminta sebuah flag, input tidak valid akan mengembalikan string **Wrong.**
- informasi yang dimiliki : pecahan flag (**LKS{fi1r5t_st3p_**) tertulis hardcoded. 

selanjutnya aku akan coba mencari informasi lebih lanjut dengan mendecompile nya menggunakan ghidra dan langusng melakukan pencarian string dengan
menggunakan pecahan flag yang ku miliki tersebut.

anehnya percobaan pencarian strings `LKS{fi1r5t_st3p_` di ghidra gagal. percobaan kedua ku lakukan dengan mencari string yang dicetak pada saat runtime program (Enter flag:)

<p align="center"><img width="575" height="227" alt="image" src="https://github.com/user-attachments/assets/ac5afe57-59aa-440c-9987-1437f3770f56" /></p>

string tersebut ditemukan di alamat `0x140019400` jika diperhatikan, xref dari string ini ada di alamat `0x140019410`. alamat xref adalah suatu alamat di file binary yang 
menggunakan alamat pertama sebagai referensi. jadi di kasus ini alamat 0x140019410 menunjuk ke alamat 0x140019400 yang di alamat tersebut terdapat string **Enter flag:** . 

bisa di asumsikan sesuatu yang menunjuk ke alamat string ini adalah fungsi printf, puts , atau fungsi stdout lain. dan fungsi itu umum nya ada di main function. 
akan lebih mudah menganalisis suatu file binary jika berhasil menemukan fungsi utama program. 

langkah analisis di lanjutkan dengan pergi ke alamat xref tersebut

setelah menginguti beberapa alamat xref tersebut , aku di arahkan ke sebuah fungsi. dan di fungsi terrsebut terdapat fungsi lain **LAB_140001c66** yang menyalin string flag ke
sebuah alamat memori

```
LAB_140001c66:
    pcVar16 = (char *)FUN_140016200(0x1e);
    if (pcVar16 == (char *)0x0) {
                    /* WARNING: Subroutine does not return */
      FUN_14001774e(1,0x1e);
    }
    builtin_strncpy(pcVar16,"LKS{fi1r5t_st3p_to_ruSs5t_exe}",0x1e);
```

ini cukup aneh karena hasil pencarian string di wsl dan dan ghidra tidak langsung menampilkan full string flag. 

flag : **LKS{fi1r5t_st3p_to_ruSs5t_exe}",0x1e)**

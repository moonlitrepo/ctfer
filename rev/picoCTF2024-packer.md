# picoCTF2024-packer.md

hello guys welcome to my write up

# summary
pada challenge ini picoctf memberikan sebuah file program executable 64 bit yang di kompress menggunakan upx. tugas kita adalah mengunpack program tersebut dan mengambil
flagnya karena flag sudah tertulis di source codenya.  

by the way aku akan menjelaskan cara mengerjakannya menggunakan ghidra dan menggunakan gdb. 

# solve with ghidra | recon
langkah pertama jelas kita run aja dulu agar kita tahu programnya ngapain  

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(packer)
└> ./out
Enter the password to unlock this file: 1937032ny
You entered: 1937032ny

Access denied
```
jelas aku gatau passwordnya, tapi passwor itu bisa di cari tahu pakai ghidra. namun karena file ini di kompress maka nama fungsinya akan disembunyikan. namanya juga kompresi kan.  
jadi nanti ketika di decompile akan terlihat seperti ini
<img width="959" height="389" alt="image" src="https://github.com/user-attachments/assets/b432b4f8-de0e-4a69-bf57-d785b4ae7f02" />

agar kita lebih mudah mencari mana fungsi main nya, file program tersebut harus di unpack dulu. prosesnya mirip mirip seperti ekstrak gitu.

# solve with ghidra | exploit
untuk melakukan unpack kita bisa gunakan tools upx:
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(packer)
└> upx -d -o in out
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2024
UPX 4.2.2       Markus Oberhumer, Laszlo Molnar & John Reiser    Jan 3rd 2024

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
[WARNING] bad b_info at 0x4b718

[WARNING] ... recovery at 0x4b714

    877724 <-    336520   38.34%   linux/amd64   in

Unpacked 1 file.
┌[rotalactf]-[LAPTOP-6QMID52F]-(packer)
└> file in
in: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, BuildID[sha1]=705654b705e0b7c1367d4f3761f5379b543607b2, for GNU/Linux 3.2.0, not stripped
```

lihat, saat kita file hasil unpacknya tertulis file program tersebut **not stripped** alias isi program tidak disembunyikan lagi, maka tentu saja selarang kita bisa
dengan mudah melihat hasil decompilenya secara jelas di ghidra
<img width="959" height="382" alt="image" src="https://github.com/user-attachments/assets/f7cab4f7-0098-46bc-99d1-bf167ef619c4" />


disini terdapat dungsi puts yang akan mengembalikan teks jika input kita sesuai password. dengan ini kita tidak perlu repot repot mencari apa passwordnya karena kondisi
setelah password benar sudah tertulis di source code nya.  

hal yang lebih penting adalah apa yang di print ketika password benar. yaitu **"Password correct, please see flag: 7069636f4354467b5539585f556e5034636b314e365f42316e34526933535f62646438343839337d"**
program ini secara terang terangan ngasi flag nya. namun sepertinya itu berbentuk hex. jadi aku haru ubah dulu ini ke bentuk teksnya.  


```
┌[rotalactf]-[LAPTOP-6QMID52F]-(packer)
└> echo 7069636f4354467b5539585f556e5034636b314e365f42316e34526933535f62646438343839337d | xxd -r -p
picoCTF{U9X_UnP4ck1N6_B1n4Ri3S_bdd84893}%    
```
done 

flag = **picoCTF{U9X_UnP4ck1N6_B1n4Ri3S_bdd84893}  **

selanjutnya aku akan jelaskan cara solvenya full with gdb dan linux

# solve with gdb | recon
seperti langkah di ghidra . unpack dulu file program tadi lalu gdb hasilnya. setelah masuk di gdb biasanya yang aku lakukan adalah menjalankan info functions agar tahu fungsi apa saja
yang ada di program tersebut. namun hasilnya cukup banyak fungsi yang keluar

```
pwndbg> info functions
All defined functions:

Non-debugging symbols:
0x0000000000401000  _init
0x00000000004011a0  __assert_fail_base.cold
0x00000000004011af  _nl_load_domain.cold
0x00000000004011b4  abort
0x00000000004013e8  _IO_new_fclose.cold
0x000000000040143f  _IO_fflush.cold
0x0000000000401495  _IO_fgets.cold
dan ratusan lagi ke bawah
```
jadi aku melakukan filter dengan menambahkan main 
```
pwndbg> info functions main
All functions matching regular expression "main":

Non-debugging symbols:
0x00000000004011af  _nl_load_domain.cold
0x0000000000401d65  main
0x0000000000402320  __libc_start_main
0x00000000004048c0  _nl_find_domain
0x0000000000404b60  _nl_load_domain
0x000000000041e840  _IO_switch_to_main_get_area
0x0000000000456710  _dl_get_dl_main_map
0x00000000004749c0  _IO_switch_to_main_wget_area
0x00000000004931e0  _nl_finddomain_subfreeres
0x0000000000493240  _nl_unload_domain
```

oke jadi fungsi utama kita sudah ada. langkah ini hanya untuk memastikan saja. nah selanjutnya adalah recon aslinya. kita akan mendisassembly fungsi utama / fungsi main tersebut
rupanya hasil disassemblynya cukup banyak, sekitar hingga main+500 . jadi aku akan mencari bagian yang terlihat mencurigakan. tak perlu waktu lama aku menemukan bagian ini : 
```assembly
   0x0000000000401e3a <+213>:   movabs rax,0x6636333639363037
   0x0000000000401e44 <+223>:   movabs rdx,0x6237363434353334
   0x0000000000401e4e <+233>:   mov    QWORD PTR [rbp-0x80],rax
   0x0000000000401e52 <+237>:   mov    QWORD PTR [rbp-0x78],rdx
   0x0000000000401e56 <+241>:   movabs rax,0x6635383539333535
   0x0000000000401e60 <+251>:   movabs rdx,0x3433303565363535
   0x0000000000401e6a <+261>:   mov    QWORD PTR [rbp-0x70],rax
   0x0000000000401e6e <+265>:   mov    QWORD PTR [rbp-0x68],rdx
   0x0000000000401e72 <+269>:   movabs rax,0x6534313362363336
   0x0000000000401e7c <+279>:   movabs rdx,0x3133323466353633
   0x0000000000401e86 <+289>:   mov    QWORD PTR [rbp-0x60],rax
   0x0000000000401e8a <+293>:   mov    QWORD PTR [rbp-0x58],rdx
   0x0000000000401e8e <+297>:   movabs rax,0x3936323534336536
   0x0000000000401e98 <+307>:   movabs rdx,0x3236663533353333
   0x0000000000401ea2 <+317>:   mov    QWORD PTR [rbp-0x50],rax
   0x0000000000401ea6 <+321>:   mov    QWORD PTR [rbp-0x48],rdx
   0x0000000000401eaa <+325>:   movabs rax,0x3433383334363436
   0x0000000000401eb4 <+335>:   movabs rdx,0x6437333339333833
   0x0000000000401ebe <+345>:   mov    QWORD PTR [rbp-0x40],rax
   0x0000000000401ec2 <+349>:   mov    QWORD PTR [rbp-0x38],rdx
```
kenapa aku anggap ini mencurigakan? karena disin programnya berusaha memasukkan banyak sekali value hex kedalam stack. coba kita ambil 1 blok saja daria fungsi ini
```assembly
   0x0000000000401e3a <+213>:   movabs rax,0x6636333639363037
   0x0000000000401e44 <+223>:   movabs rdx,0x6237363434353334
   0x0000000000401e4e <+233>:   mov    QWORD PTR [rbp-0x80],rax
   0x0000000000401e52 <+237>:   mov    QWORD PTR [rbp-0x78],rdx
```
dari main+213 , program akan memasukkan value hex **0x6636333639363037** kedalam register **rax**  
lalu main _223 value hex **0x6237363434353334** akan dimasukkan ke register **rdx** 
dan dua program dibawah akan memasukkan value register itu kedalam stack secara berutan . dimulai dari alamat stack **rbp-0x80**
jadi stack alamat rbp-0x80 itu akan menyimpan value 0x6636333639363037 disusul stack rbp-0x78 yang menyimpan 0x6237363434353334  

namun aku tidak perlu repot repot mendecode semua value itu satu satu untukk membacanya. karena kita sekarang pakai gdb tinggal baca aja dari alamat stacknya tersebut.

kesimpulan recon singkat ini. sesuatu disimpan di alamat rbp-0x80 . tujuan kita adalah membacanya.

# solve with gdb | exploit
untuk membaca rbp-0x80 kita harus memasang breakpoint dulu di tempat setelah program menulis semua value hex itu ke stack. 
```assembly
   0x0000000000401eaa <+325>:   movabs rax,0x3433383334363436
   0x0000000000401eb4 <+335>:   movabs rdx,0x6437333339333833
   0x0000000000401ebe <+345>:   mov    QWORD PTR [rbp-0x40],rax
   0x0000000000401ec2 <+349>:   mov    QWORD PTR [rbp-0x38],rdx
   0x0000000000401ec6 <+353>:   mov    QWORD PTR [rbp-0x30],0x0
```
ternyata program selesai menulis value ke stack adalah di **main+353** atau alamat memory **0x0000000000401ec6**

kita bisa pasang breakpoint disitu lalu menjalankan programnya hingga ia berhenti di breakpoint yang kita pasang
```
pwndbg> b *(main+353)
Breakpoint 1 at 0x401ec6
pwndbg> r
Breakpoint 1, 0x0000000000401ec6 in main ()
pwndbg> x/s $rbp-0x80
0x7fffffffdd70: "7069636f4354467b5539585f556e5034636b314e365f42316e34526933535f62646438343839337d(\337\377\377\377\177"
```
nah mudah kan , setelah itu tinggal kita pangill shell untuk mendecodenya dengan tools xxd
```
pwndbg> shell echo 7069636f4354467b5539585f556e5034636b314e365f42316e34526933535f62646438343839337d | xxd -r -p
picoCTF{U9X_UnP4ck1N6_B1n4Ri3S_bdd84893}pwndbg>
```
done as usual.

# conclusion
intinya file program ini adalah program yang dikompressi menggunakan upx dan ia menyimpan flag. penting untuk memahami tentang kompresi ini karena jika suatu prpogram sudah 
dikompresi maka semua sumber program seperti nama fungsi, nama variabel, bahkan source code program itu sendiri akan 'dilucuti dari program'. kenapa harus pake upx. nyatanya
upx bisa menyusutkan ukuran file binary jadi program akan menjadi lebih kecil dan ramah penyimpanan dengan efek samping sourcenya dihilangkan.


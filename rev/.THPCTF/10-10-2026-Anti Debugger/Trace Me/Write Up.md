# Write Up Trace me Challenge

# note 
chall ini buatan claude, namun sudah lebih dari cukup untuk latihan teknik dasar bypassing anti debugger (Ptrace).

## Lingkungan 
OS : Ubuntu 24.04.5 LTS (Noble Numbat) x86_64  
Kernel : Linux 6.6.87.2-microsoft-standard-WSL2

## tools
- gdb + plugin pwndbg
- ltrace

## deskripsi
Nama Challenge : Trace Me  
Point : -   
Kategori : Reverse Engineering  
File terlampir : [Trace Me](traceme)  
FLAG : **PRALKS{trace_me_twice}**

## Ringkasan
file terlampir merupakan program executable x86-64 yang memiliki _anti debugger_ . program ini meminta input user dan membandingkannya dengan string flag. string tersebut tidak bisa
di deteksi menggunakkan _strings_ karena berupa teks terenkripsi yang hanya di dekripsi saat _runtime_ program. untuk mengambil flag tersebut dibutuhkan debugger seperti gdb. dan yang
saya lakukan untuk menyelesaikan challenge ini adalah menggunakan gdb untuk memaksa program melompat ke kondisi normal walaupun fungsi _anti debugger_ nya (ptrace) mendeteksi adanya debugger.

# Analisis Awal
langkah awal yang saya lakukan adalah mencari informasi umum dari file yang diberikan, dengan memeriksa metadata serta mencoba menjalankan program ini untuk mencari tahu _surface behavior_
(perilaku permukaan) dari program terlampir.
```
==================[ metadata ]==================
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme)
└> file traceme
traceme: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=8c9afcb382438477739804e185ac2e34871ae586, for GNU/Linux 3.2.0, not stripped

==================[ menjalankan program ]==================
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme)
└> ./traceme
=== Trace Me Again (Linux ptrace Challenge) ===
Tidak ada debugger lain yang menempel. Melanjutkan...
Masukkan flag: flagflag   [----> flagflag adalah input saya]
Salah. Coba lagi.

==================[ hasil ltrace ]==================
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme)
└> ltrace ./traceme
puts("=== Trace Me Again (Linux ptrace"...=== Trace Me Again (Linux ptrace Challenge) ===)= 48
ptrace(0, 0, 0, 0) = -1
puts("Debugger terdeteksi (tracer slot"...Debugger terdeteksi (tracer slot sudah terisi). Keluar.)= 56
+++ exited (status 1) +++

==================[ hasil strings ]==================
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme)
└> strings traceme| grep -i pralks{
[tidak ada hasil strings]
```
Observasi :
- file terlampir merupakan program ELF x86-64 , metadata menampilkan informasi normal. 
- aktivitas interaktif yang dilakukan program ini adalah meminta flag dan asumsi saya ia akan membandingkannya dengan flag asli di program.
- program sempat mencetak teks **Tidak ada debugger lain yang menempel. Melanjutkan...** .clue sudah ada di banner program juga yang menyebutkan kata _ptrace_ .
  (ptrace adalah fungsi trace yang sering digunakan untuk menjadi _anti debugger_ suatu program)
- program langsung berhenti saat dijalankan menggunakan ltrace (tepat setelah fungsi ptrace mengembalikan nilai -1 yang artinya gagal melakukan trace), mengindikasikan adanya _anti debugger_ .
- sebagai tambahan saya melakukan strings pada program tersebut. namun tidak ditemukan adanya flag. ini mengindikasikan juga bahwa ada suatu algoritma enkripsi
  atau obfuskasi yang digunakan untuk menyembunyikan data asli flag

## analisis lanjutan 
Untuk mencari informasi lebih lanut, saya gunakan gdb. yang pertama saya cari adalah nama fungsi yang tersedia, berikut fungsi relevan yang ditemukan :
- 0x0000000000001229  decode
- 0x000000000000133e  main

ada fungsi bernama decode yang memverifikasi bahwa flag memang dalam kondisi terenkripsi sekarang. jika decode ini dipanggil maka saya bisa mengambil flag saat runtime program.

potongan disassembly dari fungsi main()
```
   ======================[ anti debugger ]======================
   0x000000000000138e <+80>:    call   0x1120 <ptrace@plt>
   0x0000000000001393 <+85>:    cmp    rax,0xffffffffffffffff -> signed int dari 0xffffffffffffffff adalah -1. (ptrace return -1 = tidak berhasil trace)
   0x0000000000001397 <+89>:    jne    0x13b2 <main+116> -> jika return != 1, maka tidak ada debugger. melanjutkan logika program

   ======================[ call decode function ]======================
   0x00000000000013f5 <+183>:   call   0x1229 <decode> 
   0x00000000000013fa <+188>:   lea    rax,[rip+0xca5]  -> kondisi flag sudah terdekripsi. target breakpoint setelah bypass anti debugger 
```
observasi:
- fungsi ptrace tidak memiliki relasi apapun dengan hasil dekripsi flag.
- flag akan didekripsi untuk di bandingkan dengan input user. flag bisa di ambil setelah call decode

## rencana exploitasi
saya akan selesaikan challenge ini menggu
- bypass proteksi _anti debugger_ yang ada di **main+80** dengan melakukan jump ke **main+116** setelah atau sebelum ptrace dipanggil.
- memasang breakpoint di **main+188** dan mengambil flag dalam kondisi terdekripsi.

## exploit
```
pwndbg> b main
Breakpoint 1 at 0x1346 
pwndbg> b *main+188
Breakpoint 2 at 0x13fa
pwndbg> r
```

- percobaan pertama : jump dilakukan sebelum call ptrace
```
 ► 0x555555555389 <main+75>    mov    eax, 0     EAX => 0
   0x55555555538e <main+80>    call   ptrace@plt                  <ptrace@plt>
pwndbg> j *main+116
```
```
   0x00005555555553f5 <+183>:   call   0x555555555229 <decode>
=> 0x00005555555553fa <+188>:   lea    rax,[rip+0xca5]        # 0x5555555560a6
───────────────────────────────────────────────────────────────────[ STACK ]────────────────────────────────────────────────────────────────────
00:0000│ rsp   0x7fffffffdd40 ◂— 2
01:0008│-0d8   0x7fffffffdd48 ◂— 0x160000001c
02:0010│ rdi   0x7fffffffdd50 ◂— 'PRALKS{trace_me_twice}'
```
saya berhasil jump ke *main+116* dan berhenti tepat di breakpoint ke dua yaitu **main+188**
verifikasi flag
```
pwndbg> c
Continuing.
Masukkan flag: PRALKS{trace_me_twice}
Benar! Kamu berhasil bypass anti-debug sampai titik ini.
[Inferior 1 (process 81072) exited normally]
```
flag berhasil didapatkan : **PRALKS{trace_me_twice}**

- percobaan ke dua : jump dilakukan setelah call ptrace
```
   0x55555555538e <main+80>     call   ptrace@plt                  <ptrace@plt>
 ► 0x555555555393 <main+85>     cmp    rax, -1     0xffffffffffffffff - -0x1     EFLAGS => 0x246 [ cf PF af ZF sf IF df of iopl:00 ac ]
   0x555555555397 <main+89>   ✘ jne    main+116                    <main+116>
```
terlihat program tidak melakukan jne (_jump not equal_) karena ptrace memang mengembalikan nilai -1 jika gagal melakukan trace. saya akan lakukan jump ke *main+116 disini

```
pwndbg> j *main+116
```
```
b► 0x5555555553fa <main+188>    lea    rax, [rip + 0xca5]     RAX => 0x5555555560a6 ◂— 'Masukkan flag: '
───────────────────────────────────────────────────────────────────[ STACK ]────────────────────────────────────────────────────────────────────
00:0000│ rsp   0x7fffffffdd40 ◂— 2
01:0008│-0d8   0x7fffffffdd48 ◂— 0x160000001c
02:0010│ rdi   0x7fffffffdd50 ◂— 'PRALKS{trace_me_twice}'

```
masih dapat dilakukan. ini memverifikasi bahwa ptrace memang benar benar tidak memengaruhi alur program jika tidak di eksekusi.

## kesimpulan
_anti debugger_ memang sebuah proteksi yang bisa digunakan untuk menjaga suatu program dari debugger seperti gdb atau ltrace dari membocorkan data program. namun hanya mengandalkan
ptrace sebagai fungsi _anti debugger_ utama tentu belum cukup karena ptrace sendiri adalah fungsi yang berdiri sendiri dan sangat mudah di bypass hanya dengan jump dan mengabaikannya.


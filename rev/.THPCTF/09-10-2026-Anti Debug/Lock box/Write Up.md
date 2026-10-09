# Lock box

## deskripsi
Nama Challenge : Lock Box  
Kategori : Reverse Engineering  
File : [pralks_lootbox](chall)  

FLAG : `PRALKS{ptrace_attach_race_detected}`

## environment
Kernel : lLinux 6.6.87.2-microsoft-standard-WSL2
OS : Ubuntu 24.04.5 LTS (Noble Numbat) x86_64

## Ringkasan
file program ini memiliki flag terenkripsi yang tidak terlihat dari strings atau fungsi analisis statis sederhana, 
flag akan ter-dekripsi jika program tidak mendeteksi adanya debugger namun tidak mencetaknya. Flag tersebut disimpan 
di stack yang nantinya , stack tersebut akan di bersihkan (di nol kan) saat akhir program maka butuh debgger untuk
mengambil flag tersebut.

program ini dilengkapi dengan fungsi _attach_check()_ dan _timing_check()_ yang bekerja sebagai _anti debugging_ . untuk melewati proteksi _anti debugging_ 
tersebut, saya menggunakan pendekatan teknik _binary patching_ , yaitu merubah alur program sehingga tidak menghentikkan
proses nya walaupun saya lakukan debugging pada program tersebut saat mengambil flagnya. 

## Analisis Awal
langkah awal saya adalah memeriksa metadata program dan mencoba menjalankannya untuk mengetahui _surface behavior_ dari program ini.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day9-windows-reverse)
└> file pralks_lockbox
pralks_lockbox: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter
/lib64/ld-linux-x86-64.so.2, BuildID[sha1]=2ed0851e14be7ef64823ca965e71b46c2142ff42, for GNU/Linux 3.2.0, with debug_info, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(day9-windows-reverse)
└> ./pralks_lockbox
=== PRALKS Lockbox v1.0 ===
Lockbox jammed. Tamper detected.
Lockbox re-sealed.
┌[rotalactf]-[LAPTOP-6QMID52F]-(day9-windows-reverse)
└> strings pralks_lockbox | grep -i pralks
=== PRALKS Lockbox v1.0 ===
/home/claude/pralks
pralks_lockbox.c
pralks_lockbox.c
```
observasi :
- program mencetak banner challenge dan menolak akses secara default. `Lockbox jammed. Tamper detected.`
- terdapat jeda sepersekian detik saat program mencetak baris **Lockbox jamed --** dan baris **Lockbox re-sealed**, perilaku ini mengindikasikan adanya fungsi sleep pada program
- tidak ada string yang relevan dengan flag. mengindikasikan adanya teknik obfuskasi atau enkripsi pada string flag
  
## Analisis Lanjutan
untuk melanjutkan observasi saya mendekompilasi program ini menggunakan ghidra.  selain main, program ini memiliki 3 fungsi lain yang relevan yaitu  **timing_check()**
, **attach_check()** , dan **reveal_flag()** .

main()
```C
int main(void)

{
  puts("=== PRALKS Lockbox v1.0 ===");
  timing_check();
  attach_check();
  reveal_flag();
  return 0;
}
```
timing_check() dan attach_check() merupakan fungsi _anti debug_ , program ini memiliki _2 layer protection_,pertama sesuai namanya, timing_check() adalah _anti debug time based_ yang akan menghitung _runtime_ program dan mengembalikan
**debugger_detected = 1** (terdeteksi debugger) jika program berjalan lebih lama dari konstanta yang eksplisit tertera pada fungsi ini.
```C
  clock_gettime(1,(timespec *)&t1);
  for (i = 0; i < 5000000; i = i + 1) {}
  clock_gettime(1,(timespec *)&t2);
  if (50.0 < (double)(t2.tv_nsec - t1.tv_nsec) / 1000000.0 + (double)(t2.tv_sec - t1.tv_sec) * 1000.0) {
    debugger_detected = 1;
  }
```
selanjutnya pada _layer_ ke 2, attach_check() merupakan fungsi syscall kernel untuk melakukan ptrace pada _parent process_ nya. jika program ini sudah di trace dengan debugger
seperti gdb / ltrace, maka fungsi ini akan mengembalikan **debugger_detected = 1** (terdeteksi debugger).
```C
  parent = getpid();
  child = fork();
  if (child != 0) {
    waitpid(child,&status,0);
    if (((status & 127U) == 0) && ((status & 65280U) != 0)) {
      debugger_detected = 1;
    }
    return;
  }
```
terakhir fungsi reveal_flag() , fungsi ini tidak mencetak flag namun mendekripsinya dan menyimpan string tersebut di stack sebelum akhirnya di wipe (di nol kan). untuk mengambilnya
diperlukan debugger untuk berhenti pada kondisi saat stack tersebut masih berisi flag terdekripsi.

## rencana ekssploitasi
saya akan gunakan pendekatan _binary patching_ karena ini merupakan cara yang cukup sederhana. rencananya saya akan rubah instruksi _call function_ dari timing_check() menjadi memanggil
fungsi reveal_flag(). sehingga program akan mendekripsi flag terlebih dahulu baru memeriksa debugger.

untuk mengambil flag, rencana breakpoint akan di pasang pada fungsi sleep(). yang ada di fungsi reveal_flag(). karena saat sleep dipanggil, merupakan kondisi saat flag masih berada di stack
dalam kondisi terdekripsi.

## eksekusi exploitasi
saya melakukan _binary patching_ menggunakan fitur _patch instruction_ dari ghidra. berikut hasil _patching_ nya :
```
        00401508 b8 00 00 00 00       MOV        EAX,0x0
        0040150d e8 ef fe ff ff       CALL       reveal_flag     void reveal_flag(void) <-- sebelumnya  call     timing_check
        00401512 b8 00 00 00 00       MOV        EAX,0x0              
        00401517 e8 20 fe ff ff       CALL       attach_check    void attach_check(void)
        0040151c b8 00 00 00 00       MOV        EAX,0x0
```
selanjutnya file tersebut diekspor dan debug menggunakan gdb untuk memasang breakpoint pada fungsi sleep.

sebelum itu saya perlu verifikasi apakah hasil patch sudah berhasil
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day9-windows-reverse)
└> ./pralks_lockbox
=== PRALKS Lockbox v1.0 ===
Lockbox unlocked. Reading contents...
Lockbox re-sealed.
Lockbox jammed. Tamper detected.
Lockbox re-sealed.
```
berhasil, karena program mencetak **Lockbox unlocked. Reading contents...** artinya flag sudah berhasil terdekripsi. 
```
pwndbg> file pralks_lockbox
Reading symbols from pralks_lockbox...
pwndbg> b usleep
Breakpoint 1 at 0x401140
pwndbg> r
─────────────────────────────────────────────────────────[ STACK ]──────────────────────────────────────────────────────────
00:0000│ rsp 0x7fffffffddc8 —▸ 0x4014c9 (reveal_flag+200) ◂— lea rax, [rbp - 0x50]
01:0008│-050 0x7fffffffddd0 ◂— 'PRALKS{ptrace_attach_race_detected}'
```

karena saya menggunakan plugin pwndbg maka gdb yang saya gunakan akan langsung menampilkan runtime stack saat menabrak breakpoint. dan terlihat jelas flag ada di stack.

flag : **PRALKS{ptrace_attach_race_detected}**

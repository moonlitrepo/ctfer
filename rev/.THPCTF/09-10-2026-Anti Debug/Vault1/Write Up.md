# Vault 1

# description 
None  
category : Reverse Engineering  
file attached : pralks_vault

# analysis
saya awali dengan mencari informasi dasar seperti metadata program dan menjalankan program tersebut untuk mencari tahu apa yang ia lakukan.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day9-windows-reverse)
└> file pralks_vault
pralks_vault: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=6a51d097fa92440413c2afcadf8ed0223d43da3d, for GNU/Linux 3.2.0, with debug_info, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(day9-windows-reverse)
└> ./pralks_vault
=== PRALKS Vault System v1.0 ===
Access denied. Intruder detected.
Vault sealed.
```

akses ditolak dan vault tidak terbuka, menurut konteks nya saya berasumsi bahwa vault tersebut harus dibuka. selain itu terdapat sedikit delay saat program mencetak 
baris Access denied dengan Vault sealed. saya coba periksa menggunakan ltrace.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day9-windows-reverse)
└> ltrace ./pralks_vault
puts("=== PRALKS Vault System v1.0 ==="...=== PRALKS Vault System v1.0 ===
)                                 = 33
ptrace(0, 0, 0, 0)                                                          = -1
fopen("/proc/self/status", "r")                                             = 0x1e3a36b0
fgets("Name:\tpralks_vault\n", 256, 0x1e3a36b0)                             = 0x7ffeda018c00
strncmp("Name:\tpralks_vault\n", "TracerPid:", 10)                          = -6
fgets("Umask:\t0022\n", 256, 0x1e3a36b0)                                    = 0x7ffeda018c00
strncmp("Umask:\t0022\n", "TracerPid:", 10)                                 = 1
fgets("State:\tR (running)\n", 256, 0x1e3a36b0)                             = 0x7ffeda018c00
strncmp("State:\tR (running)\n", "TracerPid:", 10)                          = -1
fgets("Tgid:\t31716\n", 256, 0x1e3a36b0)                                    = 0x7ffeda018c00
strncmp("Tgid:\t31716\n", "TracerPid:", 10)                                 = -11
fgets("Ngid:\t0\n", 256, 0x1e3a36b0)                                        = 0x7ffeda018c00
strncmp("Ngid:\t0\n", "TracerPid:", 10)                                     = -6
fgets("Pid:\t31716\n", 256, 0x1e3a36b0)                                     = 0x7ffeda018c00
strncmp("Pid:\t31716\n", "TracerPid:", 10)                                  = -4
fgets("PPid:\t31715\n", 256, 0x1e3a36b0)                                    = 0x7ffeda018c00
strncmp("PPid:\t31715\n", "TracerPid:", 10)                                 = -4
fgets("TracerPid:\t31715\n", 256, 0x1e3a36b0)                               = 0x7ffeda018c00
strncmp("TracerPid:\t31715\n", "TracerPid:", 10)                            = 0
atoi(0x7ffeda018c0a, 0x402021, 10, 0xfffffc00)                              = 0x7be3
fclose(0x1e3a36b0)                                                          = 0
memset(0x7ffeda018cc0, '\0', 64)                                            = 0x7ffeda018cc0
puts("Access denied. Intruder detected"...Access denied. Intruder detected.
)                                 = 34
usleep(500000)                                                              = <void>
memset(0x7ffeda018cc0, '\0', 64)                                            = 0x7ffeda018cc0
puts("Vault sealed."Vault sealed.
)                                                       = 14
+++ exited (status 0) +++
```
ternyata delay tersebut disebabkan oleh fungsi usleep(500000), selain itu ada fungsi lain yang lebih menarik. program ini ternyata memiliki proteksi anti debugging dengan memeriksa
return dari fungsi ptrace, dan memeripsa tracePid dari **/proc/self/status**. 

tidak ada tanda tanda pencetakan teks, namun program disini menyiapkan alamat memori sebesar 64 byte lallu menghapusnya (mengisinya dengan null bytes) lagi setelah fungsi usleep()
dipanggil. 

untuk memeriksa apa yang terjadi saya coba decompile file tersebut menggunakan ghidra. terdapat beberapa fungsi menarik disini, dan main() memanggil mereka semua.

**main()**
```C
int main(void)
{
  puts("=== PRALKS Vault System v1.0 ===");
  anti_debug_check();
  reveal_flag();
  return 0;
}
```

**anti_debug_check()**
```C
void anti_debug_check(void)

{
  int iVar1;
  long lVar2;
  FILE *__stream;
  char *pcVar3;
  char line [256];
  int pid;
  FILE *f;
  
  lVar2 = ptrace(PTRACE_TRACEME,0,0,0);
  if (lVar2 == -1) {
    debugger_detected = 1;
  }
  __stream = fopen("/proc/self/status","r");
  if (__stream != (FILE *)0) {
    do {
      pcVar3 = fgets(line,256,__stream);
      if (pcVar3 == (char *)0) goto LAB_00401303;
      iVar1 = strncmp(line,"TracerPid:",10);
    } while (iVar1 != 0);
    iVar1 = atoi(line + 10);
    if (iVar1 != 0) {
      debugger_detected = 1;
    }
LAB_00401303:
    fclose(__stream);
  }
  return;
}
```

```C
void reveal_flag(void)
{
  uchar buf [64];
  int i_1;
  int i;
  
  memset(buf,0,64);
  if (debugger_detected == 0) {
    for (i = 0; i < 37; i = i + 1) {
      buf[i] = enc_flag[i] ^ 90;
    }
    puts("Access granted. Decrypting vault contents...");
  }
  else {
    for (i_1 = 0; i_1 < 37; i_1 = i_1 + 1) {
      buf[i_1] = ~(enc_flag[i_1] ^ 90);
    }
    puts("Access denied. Intruder detected.");
  }
  usleep(500000);
  memset(buf,0,64);
  puts("Vault sealed.");
  return;
}
```

fungsi anti_debug_check bisa dengan mudah di bypass karena returnnya menggunakan variabel global **debugger_detected** , dan itu cukup mudah di manipulasi valuenya menggunakan
gdb. lalu untuk fungsi reveal_flag, program ini ternyata tidak mencetak flag, sama sekali. namun ia memiliki flag terenkripsi yang hanya akan di dekripsi jika debugger_detected
= 0 . flag tersebut akan diletakkan divariabel buf , namun setelah fungsi sleep buf akan dikosongkan lagi. maka flag hanya bertahan selama fungsi sleep dipanggil.

untuk memudahkan pengambilan flag dari memory saya akan menggunakan gdb

rencana exploit
- gunakan gdb unutk memasang breakpoint tepat di depan call function **anti_debug_check** dan manipulasi variabel **debugger_detected** menjadi nol. (menggunakan gdb otomatis tidak
  lolos anti debug pertama (ptrace) )
- pasang breakpoint ke dua di fungsi usleep untuk mengambil flag

# exploit
pemasangan breakpoint
```
pwndbg> disas main
Dump of assembler code for function main:
   0x0000000000401402 <+0>:     endbr64
   0x0000000000401406 <+4>:     push   rbp
   0x0000000000401407 <+5>:     mov    rbp,rsp
   0x000000000040140a <+8>:     lea    rax,[rip+0xc7f]        # 0x402090
   0x0000000000401411 <+15>:    mov    rdi,rax
   0x0000000000401414 <+18>:    call   0x4010d0 <puts@plt>
   0x0000000000401419 <+23>:    mov    eax,0x0
   0x000000000040141e <+28>:    call   0x401236 <anti_debug_check>
   0x0000000000401423 <+33>:    mov    eax,0x0
   0x0000000000401428 <+38>:    call   0x401312 <reveal_flag>
   0x000000000040142d <+43>:    mov    eax,0x0
   0x0000000000401432 <+48>:    pop    rbp
   0x0000000000401433 <+49>:    ret
End of assembler dump.
pwndbg> b *main+33
Breakpoint 1 at 0x401423: file pralks_vault.c, line 72.
pwndbg> b usleep
Breakpoint 2 at 0x401140
pwndbg> r
```

manipulasi variabel
```
pwndbg> set var debugger_detected = 0
pwndbg> c
```

retrieve the flag

buf merupakan variabel, yang pasti valuenya ada di stack.
```
pwndbg> stack
00:0000│ rsp 0x7fffffffddc8 —▸ 0x4013da (reveal_flag+200) ◂— lea rax, [rbp - 0x50]
01:0008│-050 0x7fffffffddd0 ◂— 'PRALKS{ptrace_wont_save_you_from_gdb}'
```

flag : **PRALKS{ptrace_wont_save_you_from_gdb}**



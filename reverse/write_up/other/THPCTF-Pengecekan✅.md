# THPCTF-Pengecekan✅

## Tools
- gdb 
- strings

## deskripsi
di SMK TUNAS HARAPAN PATI punya aplikasi untuk mengecek password, bisakah kamu menebak berapa password nya???

author : P⭐7.

file: [pengecekan](pengecekan)


akses Challenge [Pengecekan](https://thpctf.my.id/challenges?challenge=c7020000-0000-4000-8000-000000000017) (pastikan sudah login di platform ctf tersebut)
## analisis awal
pemeriksaan di awali dengan mengidentifikasi file dan menjalankannya untuk mencari tahu perilaku permukaan dari file yang diberikan.
```bash
┌[rotalactf]-[LAPTOP-6QMID52F]-(pengecekan)
└> file pengecekan
pengecekan: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=e34e04eaa0b3ee30b5d1a071984dd4667ac37065, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(pengecekan)
└> ./pengecekan
Enter serial key: idk
Incorrect serial key.
```

observasi awal:
- file elf executable
- program meminta input serial key
- jika invalid, program  mencetak **Incorrect serial key.** lalu berhenti

menurut deskripsi dan perilaku challenge, tujuan eksploitasi nya adalah mendapatkan password / serial key yang benar. 

## analisis lanjutan
analisis dilanjutkan menggunakan GDB, teridentifikasi program ini memiliki fungsi :
- main
- check_serial

saat di periksa, validasi dilakukan oleh fungsi check_serial menggunakan fungsi strcmp. ini menarik. artinya string input akan dibandingkan langsung dengan string serial 
valid. 

kode:
```asemmbly
Dump of assembler code for function check_serial:
   0x0000000000001169 <+0>:     push   rbp
   0x000000000000116a <+1>:     mov    rbp,rsp
   0x000000000000116d <+4>:     sub    rsp,0x20
   0x0000000000001171 <+8>:     mov    QWORD PTR [rbp-0x18],rdi
   0x0000000000001175 <+12>:    lea    rax,[rip+0xe8c]        # 0x2008
   0x000000000000117c <+19>:    mov    QWORD PTR [rbp-0x8],rax
   0x0000000000001180 <+23>:    mov    rdx,QWORD PTR [rbp-0x8]
   0x0000000000001184 <+27>:    mov    rax,QWORD PTR [rbp-0x18]
   0x0000000000001188 <+31>:    mov    rsi,rdx
   0x000000000000118b <+34>:    mov    rdi,rax
   0x000000000000118e <+37>:    call   0x1050 <strcmp@plt>
   0x0000000000001193 <+42>:    test   eax,eax
   0x0000000000001195 <+44>:    sete   al
   0x0000000000001198 <+47>:    movzx  eax,al
   0x000000000000119b <+50>:    leave
   0x000000000000119c <+51>:    ret
```

## proses pengambilan password/serial key 

fokus pada proses validasi:
```asembbly
   0x0000000000001188 <+31>:    mov    rsi,rdx
   0x000000000000118b <+34>:    mov    rdi,rax
   0x000000000000118e <+37>:    call   0x1050 <strcmp@plt>
```
untuk mengetahui input ku akan dibandingkan dengan apa, aku memasang breakpoint di `check_serial + 34` lalu menjalankan programnya.
```bash
pwndbg> r
Starting program: /pengecekan
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
Enter serial key: GOKIL
```
input : **GOKIL** agar mudah ditemukan saat proses debugging.

menabrak breakpoint:
```asemmbly
b► 0x55555555518b <check_serial+34>    mov    rdi, rax     RDI => 0x7fffffffdde0 ◂— 0x4c494b4f47 /* 'GOKIL' */
```
karena aku menggunakan plugin **pwndbg** maka register rdi langsung tercetak valuenya. disini input yang ku masukkan tersimpan di register `rdi`. artinya string serial key ada di register
`rsi`. pemeriksaan dilanjutkan di tab registers:

```asemmbly
───────────────────────────────────[ REGISTERS / show-flags off / show-compact-regs off ]───────────────────────────────────
 RAX  0x7fffffffdde0 ◂— 0x4c494b4f47 /* 'GOKIL' */
 RBX  0x7fffffffdf28 —▸ 0x7fffffffe1ce ◂— '/home/rotalactf/reno/rev/thpctf/pengecekan/pengecekan'
 RCX  0
 RDX  0x555555556008 ◂— 0x4500313633353938 /* '895361' */
 RDI  0x7fffffffdde0 ◂— 0x4c494b4f47 /* 'GOKIL' */
 RSI  0x555555556008 ◂— 0x4500313633353938 /* '895361' */
```
RSI ternyata menyimpan string angka 6 digit.

Serial Key: `895361`

## percobaan login 
```bash
┌[rotalactf]-[LAPTOP-6QMID52F]-(pengecekan)
└> echo 895361 | ./pengecekan
Enter serial key: Correct! The flag is THPCTF{895361}
```

welldone, ternyata flag merupakan password/serial key itu sendiri

flag: `THPCTF{895361}`

sedikit _funfact_ karena string `895361` tersedia di program secara hardcoded. string ini terdeteksi oleh strings tool. dan password bisa terlihat dengan jelas
tanpa perlu debug menggunakan gdb.

```bash
┌[rotalactf]-[LAPTOP-6QMID52F]-(pengecekan)
└> strings pengecekan | grep 89
895361
```
namun debugging tetap perlu dilakukan untuk langkah verifikasi kejelasan asal usul string yang ada tersebut.


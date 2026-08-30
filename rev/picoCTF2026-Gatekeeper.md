# picoCTF2026-Gatekeeper

kerentanan yang ada di file program ini adalah type confussion / logic flaw , kenapa?
karena program ini meminta input yang bernilai lebih dari 999, maka input minimal kita adalah 4 digit. (1000 ke atas) dan bernilai kurang dari 10000
sementara itu fungsi reveal_flag hanya akan tereksekusi jika input adalah sesuatu dengan
3 digit. terdengar mustahil tapi kita bisa mem-bypassnya dan membuat program membaca input kita sebagai angka lebih dari 999 namun
hanya 3 digit.

berikut adalah hasil decompile fungsi main
```C

  undefined8 main(void)

{
  int iVar1;
  size_t sVar2;
  long lVar3;
  undefined8 uVar4;
  long in_FS_OFFSET;
  int local_40;
  char local_38 [40];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  printf("Enter a numeric code (must be > 999 ): ");
  fflush(stdout);
  __isoc99_scanf(&DAT_00102070,local_38);
  sVar2 = strlen(local_38);
  iVar1 = is_valid_decimal(local_38);
  if (iVar1 == 0) {
    iVar1 = is_valid_hex(local_38);
    if (iVar1 == 0) {
      puts("Invalid input.");
      uVar4 = 1;
      goto LAB_00101698;
    }
    lVar3 = strtol(local_38,(char **)0x0,0x10);
    local_40 = (int)lVar3;
  }
  else {
    local_40 = atoi(local_38);
  }
  if (local_40 < 1000) {
    puts("Too small.");
  }
  else if (local_40 < 10000) {
    if ((int)sVar2 == 3) {
      reveal_flag();
    }
    else {
      puts("Access Denied.");
    }
  }
  else {
    puts("Too high.");
  }
  uVar4 = 0;
LAB_00101698:
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar4;
}
```

kesalahan terjadi pada bagian  lVar2 = strtol(input,(char **)0x0,0x10); dimana ini akan merubah
tipe data string menjadi long. kita bisa menginput huruf dan ketika huruf masuk ke
fungsi ini ia akan berubah menjadi nilai ascii hexnya. misal kita input huruf A, maka program akan ngebaca
nya sebagai hex 0x41 . jika huruf A sebanyak 3 kali = AAA= 0x414141 , atau 4276545 dalam desimal. 
dengan begini kita bisa membypas proteksi kustom length input ini dengan memasukkan huruf A sebanyak 3 kali

┌──[reno@cybersec]──[~/ctf/rev/gatekeeper]
└[]> nc green-hill.picoctf.net 60448
Enter a numeric code (must be > 999 ): AAA
Access granted: }e3dftc_oc_ip375cftc_oc_ip1_99ftc_oc_ip9_TGftc_oc_ip_xehftc_oc_ip_tigftc_oc_ipid_3ftc_oc_ip{FTCftc_oc_ipocipftc_oc_ip

jujur kurang tau kenapa ini work , karena harusnya AAA itu jauh diatas 10000.

pokoknya dengan begini kita berhasil melewati filter length, flag langsung muncul tapi sepertinya ini
agak rusak, mari lihat source decompilernya di fungsi reveal_flag.
```c
      while (local_24 = local_24 - 1, -1 < (int)local_24) {
        putchar((int)*(char *)((long)__ptr + (long)(int)local_24));
        if ((local_24 & 3) == 0) {
          printf("ftc_oc_ip");
```
ini adalah bagian inti dan bagian program terpenting di fungsi reveal_flag,
dari baris pertama, while itu akan membaca local_24 (flag) dari baris paling belakang. maka flag akan ditampilkan secara terbalik alias string
terakhirya di print duluan. namun tidak berhenti di situ. dibawahnya ada if logic.
 local_24 & 3 == 0. apa maksudnya?

ini adalah hasil optimasi decompiler ketika menemukan algoritma modulus perpangkatan 2.
x & 3 == 0 itu sama dengan x % 4 == 0 atau  artinya x habis dibagi 4.
kenapa bisa begitu? karena 4 adalah perpangkatan 2, dan compiler lebih memilih mengubah
operasi mod bagi ini mejadi bitwise agar program berjalan lebih efisien.
aku ga bahas ini secara detail karena tujuan utama nya sekarang adalah mencari flag. 
hal seperti ini sudah ada banyak sekali di internet kalian bisa cari sendiri. bruh

kembali lagi ke alur program. maka setiap index string flag habis di bagi 4, program akan
memprint ftc_oc_ip. ini termasuk custom string obfuscation yang unik, karena format flag adalah
picoctf dan jika di balik akan jadi ftcocip, pembuat soal sengaja memasukkan string menyerupai
format flag untuk membuat kita ctfer merasa bahwa ftc_oc_ip ini adalah bagian asli flag. padahal
ini murni hanya sisipan racun dari pembuat soal.

jadi untuk mengatasi ini cukup mudah, bisa pakai python untuk mengambil stringnya dan memfilter string
racun tersebut, lalu membaliknya.
```py
from pwn import *
host = 'green-hill.picoctf.net'
port = 62248
#io = process('./gatekeeper')
io = remote(host,port)
io.sendlineafter(b'(must be > 999 ): ',b'AAA')
io.recvuntil(b'Access granted:')

encoded_flag = io.recvall().decode()
#menangkap string flag, io.recvall().decode() bisa diganti dengan string flag jika tidak mau otomasi pake pwn

filtered_flag = encoded_flag.replace('ftc_oc_ip','')
flag = filtered_flag[::-1]
print(flag)
```

┌──[reno@cybersec]──[~/ctf/rev/gatekeeper]
└[]> python3 exploit.py
[+] Opening connection to green-hill.picoctf.net on port 62248: Done
[+] Receiving all data: Done (119B)
[*] Closed connection to green-hill.picoctf.net port 62248

picoCTF{3_digit_hex_GT_999_1c573d3e}

done

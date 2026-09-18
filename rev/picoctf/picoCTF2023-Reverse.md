# picoCTF2023-Reverse

challange ini memberikan sebuah file program ELF x86-64 bernama ret. program ini akan menanyai kita password untuk membuka file. caraku mendapatkan flagnya adalah mencari string flag yang 
kemungkinan sudah tertulis / hardcoded di file program / source code program tersebut.

[ ! ] ada dua cara mengerjakan ini, pake gdb untuk bongkar asm nya. atau pakai ghidra untuk melihat decompilenya. aku bahas keduanya disini.

tools yang ku gunakan :
- GDB + pwndbg (pwndbg nya opsional)
-  Ghidra (opsional)

program :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(retpasswd)
└> ./ret
Enter the password to unlock this file: gamau
You entered: gamau
Access denied
```

langsung saja kita intip menggunakan gdb
```
pwndbg> disas main
Dump of assembler code for function main:
   0x00000000000011c9 <+0>:     endbr64
   0x00000000000011cd <+4>:     push   rbp
   0x00000000000011ce <+5>:     mov    rbp,rsp
   0x00000000000011d1 <+8>:     sub    rsp,0x60
   0x00000000000011d5 <+12>:    mov    rax,QWORD PTR fs:0x28
   0x00000000000011de <+21>:    mov    QWORD PTR [rbp-0x8],rax
   0x00000000000011e2 <+25>:    xor    eax,eax
   0x00000000000011e4 <+27>:    movabs rax,0x7b4654436f636970
   0x00000000000011ee <+37>:    movabs rdx,0x337633725f666c33
   0x00000000000011f8 <+47>:    mov    QWORD PTR [rbp-0x30],rax
   0x00000000000011fc <+51>:    mov    QWORD PTR [rbp-0x28],rdx
   0x0000000000001200 <+55>:    movabs rax,0x75735f676e693572
   0x000000000000120a <+65>:    movabs rdx,0x6c75663535656363
   0x0000000000001214 <+75>:    mov    QWORD PTR [rbp-0x20],rax
   0x0000000000001218 <+79>:    mov    QWORD PTR [rbp-0x18],rdx
   0x000000000000121c <+83>:    movabs rax,0x623362633961665f
   0x0000000000001226 <+93>:    mov    QWORD PTR [rbp-0x10],rax
   0x000000000000122a <+97>:    lea    rdi,[rip+0xdd7]        # 0x2008
   0x0000000000001231 <+104>:   mov    eax,0x0
   0x0000000000001236 <+109>:   call   0x10b0 <printf@plt>
   0x000000000000123b <+114>:   lea    rax,[rbp-0x60]
   0x000000000000123f <+118>:   mov    rsi,rax
   0x0000000000001242 <+121>:   lea    rdi,[rip+0xde8]        # 0x2031
   0x0000000000001249 <+128>:   mov    eax,0x0
   0x000000000000124e <+133>:   call   0x10d0 <__isoc99_scanf@plt>
   0x0000000000001253 <+138>:   lea    rax,[rbp-0x60]
   0x0000000000001257 <+142>:   mov    rsi,rax
   0x000000000000125a <+145>:   lea    rdi,[rip+0xdd3]        # 0x2034
   0x0000000000001261 <+152>:   mov    eax,0x0
   0x0000000000001266 <+157>:   call   0x10b0 <printf@plt>
   0x000000000000126b <+162>:   lea    rdx,[rbp-0x30]
   0x000000000000126f <+166>:   lea    rax,[rbp-0x60]
   0x0000000000001273 <+170>:   mov    rsi,rdx
   0x0000000000001276 <+173>:   mov    rdi,rax
   0x0000000000001279 <+176>:   call   0x10c0 <strcmp@plt>
   0x000000000000127e <+181>:   test   eax,eax
   0x0000000000001280 <+183>:   jne    0x129c <main+211>
   0x0000000000001282 <+185>:   lea    rdi,[rip+0xdbf]        # 0x2048
   0x0000000000001289 <+192>:   call   0x1090 <puts@plt>
   0x000000000000128e <+197>:   lea    rax,[rbp-0x30]
   0x0000000000001292 <+201>:   mov    rdi,rax
   0x0000000000001295 <+204>:   call   0x1090 <puts@plt>
   0x000000000000129a <+209>:   jmp    0x12a8 <main+223>
   0x000000000000129c <+211>:   lea    rdi,[rip+0xdf3]        # 0x2096
   0x00000000000012a3 <+218>:   call   0x1090 <puts@plt>
   0x00000000000012a8 <+223>:   mov    eax,0x0
   0x00000000000012ad <+228>:   mov    rcx,QWORD PTR [rbp-0x8]
   0x00000000000012b1 <+232>:   xor    rcx,QWORD PTR fs:0x28
   0x00000000000012ba <+241>:   je     0x12c1 <main+248>
   0x00000000000012bc <+243>:   call   0x10a0 <__stack_chk_fail@plt>
   0x00000000000012c1 <+248>:   leave
   0x00000000000012c2 <+249>:   ret
End of assembler dump.
```

santai saja , assembly memang terlihat mengerikan. langkah yang cukup tepat adalah mencoba fokus ke fungsi yang mengurus input kita. biasanya fungsi yang mengurus input adalah
**scanf, fgets, gets**, dan lainnya. tapi 3 itu adalah fungsi input umum di program yang dicompile dari bahasa C.
```
0x000000000000123b <+114>:   lea    rax,[rbp-0x60]
0x000000000000123f <+118>:   mov    rsi,rax
0x0000000000001242 <+121>:   lea    rdi,[rip+0xde8]        # 0x2031
0x0000000000001249 <+128>:   mov    eax,0x0
0x000000000000124e <+133>:   call   0x10d0 <__isoc99_scanf@plt>
```
nah dengan ini kita tahu bahawa input akan **disimpan di rbp-0x60**. karena lokasi alamat nya dimasukkan ke rax lalu rdi . dimana rdi adalah argumen pertama fungsi. dengan kata lain
fungsi scanf ini menggunakan rbp-0x60 sebagai tempat menampung input. 

selanjutnya awasi saja rbp-0x60 ini akan 'diapakan' aja oleh program
```
   0x000055555555526b <+162>:   lea    rdx,[rbp-0x30]
   0x000055555555526f <+166>:   lea    rax,[rbp-0x60]
   0x0000555555555273 <+170>:   mov    rsi,rdx
   0x0000555555555276 <+173>:   mov    rdi,rax
   0x0000555555555279 <+176>:   call   0x5555555550c0 <strcmp@plt>
```

beberapa baris dibawah scanf rupanya input kita akan di 'compare' dengan sesuatu di alamat **rbp-0x30**. 
kalau coba liat ulang program dari atas , ternyata rbp-0x30 ini memang berisi sesuatu

```
   0x00005555555551e4 <+27>:    movabs rax,0x7b4654436f636970
   0x00005555555551ee <+37>:    movabs rdx,0x337633725f666c33
   0x00005555555551f8 <+47>:    mov    QWORD PTR [rbp-0x30],rax
   0x00005555555551fc <+51>:    mov    QWORD PTR [rbp-0x28],rdx
   0x0000555555555200 <+55>:    movabs rax,0x75735f676e693572
   0x000055555555520a <+65>:    movabs rdx,0x6c75663535656363
   0x0000555555555214 <+75>:    mov    QWORD PTR [rbp-0x20],rax
   0x0000555555555218 <+79>:    mov    QWORD PTR [rbp-0x18],rdx
```
ini nih, diliat liat ada banyak 5 hex mencurigakan
```
<+27> -> 0x7b4654436f636970
<+28> -> 0x337633725f666c33
<+55> -> 0x75735f676e693572
<+65> -> 0x6c75663535656363
<+83> -> 0x623362633961665f
```
coba di decode yang pertama
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(retpasswd)
└> echo 0x7b4654436f636970 | xxd -r -p
{FTCocip%
```
benar , ini adalah flag nya namun disini kebalik karena masih tertulis dalam bentuk little endian. untuk mengekstrak flagnya bisa dengan mengencode hex hex tersebut menjadi
string menggunakan command linux atau script python sederhana. namun jika tidak mau repot aku punya alternatif lain untuk cara ekstrak nya

karena flag tidak terenkripsi artinya flagnya juga hardcoded di source codenya karena dia secara string langsung dibandingin dengan input kita tadi. 
dengan pwndbg aku bisa langsung search aja 
```
pwndbg> b main
Breakpoint 1 at 0x11d1
pwndbg> r
pwndbg> search pico
Searching for byte: b'pico'
ret             0x5555555551e6 jo main+136
ret             0x55555555606b 'picoCTF{3lf_r3v3r5ing_succe55ful_fa9cb3b1}'
ret             0x55555555706b 'picoCTF{3lf_r3v3r5ing_succe55ful_fa9cb3b1}'
```
flag : picoCTF{3lf_r3v3r5ing_succe55ful_fa9cb3b1}


done

sebenernya untuk nyarinya flagnya sangat mudah tinggal search atau grep aja, dan cara nya juga cukup bervariasi. namun jika mengikuti alur dan cara kita recon / mencari informasi
mengenai programnya ya kurang lebih akan seperti write up ini. memang sedikit berputar putar namun kita tidak akan tahu bahwa flag sudah tertulis rapi tanpa menganalisis programnya
terlebih dahulu. 


jika kita decompile pake ghidra malah langsung keliatan flagnya.
```
undefined8 main(void)

{
  int iVar1;
  long in_FS_OFFSET;
  char local_68 [48];
  char local_38 [40];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 40);
  builtin_strncpy(local_38,"picoCTF{3lf_r3v3r5ing_succe55ful_fa9cb3b",40);
  printf("Enter the password to unlock this file: ");
  __isoc99_scanf(&DAT_00102031,local_68);
  printf("You entered: %s\n",local_68);
  iVar1 = strcmp(local_68,local_38);
  if (iVar1 == 0) {
    puts("Password correct, please see flag: picoCTF{3lf_r3v3r5ing_succe55ful_fa9cb3b1}");
    puts(local_38);
  }
  else {
    puts("Access denied");
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 40)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
```

yah anggap aja latian bahasa assembly tipis tipis.

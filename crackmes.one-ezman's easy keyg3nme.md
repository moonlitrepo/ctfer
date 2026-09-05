# crackmes.one-ezman's easy keyg3nme

# overview
<img width="743" height="427" alt="image" src="https://github.com/user-attachments/assets/fc44dffa-ba17-4d6a-8072-7dce7ca4ff83" />

ini adalah challenge keygen sederhana karena kita hanya butuh mendecompile file progam nya untuk mendapatkan info seputar keynya. 

# analysis & exploit
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(easy-keyg3nme)
└> file keyg3nme
keyg3nme: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=01d8f2eefa63ea2a9dc6f6ceb2be2eac2ca22a67, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(easy-keyg3nme)
└> ./keyg3nme
Enter your key:  sfas
nope.
```
dari metadata file program nya tidak ada yang aneh dan symbol pada program tidak disembunyikan. jadi aku memumtuskan untuk melakukan decompile menggunakan ghidra. 

berikut isi fungsi mainnya.
```C

undefined8 main(void)

{
  int iVar1;
  long in_FS_OFFSET;
  undefined4 local_14;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  printf("Enter your key:  ");
  __isoc99_scanf(&DAT_0010201a,&local_14);
  iVar1 = validate_key(local_14);
  if (iVar1 == 1) {
    puts("Good job mate, now go keygen me.");
  }
  else {
    puts("nope.");
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}

```
program memasukkan input kita ke dalam fungsi `validate_key` jika fungsi tersebut mengembalikan nilai 1 / True maka program mencapai kondisi win. kode dari fungsi `validate_key` :
```C
bool validate_key(int param_1)
{
  return param_1 % 0x4c7 == 0;
}
```
dengan ini keynya adalah `0x4c7` atau angka apapun yang jika dibagi dengan 0x4c7 akan sisa nol, `<input> mod(0x4c7) = 0`
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(easy-keyg3nme)
└> ./keyg3nme
Enter your key:  0x4c7
Good job mate, now go keygen me.
```

# how it works
intinya dari baris program fungsi `validate_key` keynya adalah apapun yang bila dibagi dengan 0x4c7 sisa nol. berikut keygen skrip:

```Python3
for x in range(0x47c,0xfff):
    if x % 0x4c7 == 0 :
        print(x)
```
berikut beberapa kemungkinannya :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(easy-keyg3nme)
└> python3 exploit.py
1223
2446
3669
```

# picoCTF2022-Bbbbloat

hello guys welcome to my mini write up. kenapa mini? karena chall ini sangat sederhana sehingga aku bahkan tidak tahu mau menulis apa lagi di write up ini

# summary
challenge ini adalah challenge reverse engineering dasar. dimana program dari challenge ini akan menanyakan berapa angka favoritnya. dengan mendecompilenya menggunakan ghidra
kita bisa mengetahui bagaimana program bekerja dan bahkan mengetahui berapa angka favoritnya. 

# tools
ghidra

# recon
pertama run dulu programnya
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(Bbbbloat)
└> ./bbbbloat
What's my favorite number? gatau lah
Sorry, that's not it!
```
oke jadi input kita ada setelah string 'What's my favorite number?'  

cukup decompile menggunakan ghidra
<img width="959" height="401" alt="image" src="https://github.com/user-attachments/assets/93791c2d-5862-47cf-b35d-f5c37759fc7c" />
kebetulan fungsinya stripped jadi tidak terlihat mana fungsi mainnya. namun cukup beruntung tidak ada terlalu banyak string sehingga fungsi main bisa dicari secara manual,
fungsinya adalah **FUN_00101307**

lalu jika kita melihat baris programnya secara seksama ada perbandingan kondisi if yang melibatkan variabel tempat input kita disimpan. 
```C
  __isoc99_scanf(&DAT_00102020,&local_48);
  local_44 = 863305;
  if (local_48 == 549255) {
    local_44 = 863305;
    local_40 = (char *)FUN_00101249(0,&local_38);
    fputs(local_40,stdout);
    putchar(10);
```
local_48 adalah input kita, dan akan dibandingkan dengan 549255. setelah itu jika cocok maka program akan mengembalikan dan memprint local_40.
jika kita melihat di foto tadi local_40 ke bawah adalah sesuatu yang terenkripspi dan berkemungkinan dia adalah sebuah flag.

karena kita sudah tau berapa angka favorit program maka langkah selanjutnya adalah menginput nya. 

# exploit
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(Bbbbloat)
└> ./bbbbloat
What's my favorite number?
549255
picoCTF{cu7_7h3_bl047_44f74a60}
```
done
flag = **picoCTF{cu7_7h3_bl047_44f74a60}**  
sangat sederhana 

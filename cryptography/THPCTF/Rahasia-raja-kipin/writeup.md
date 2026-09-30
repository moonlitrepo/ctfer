# Rahasia raja kipin

## deskripsi challenge
author : finn  

kategori : Cryptography

disebuah kerajaan bernama JAKENAN EMPIRE.seorang pencuri berhasil menyusup ke dalam kerajaan dan berhasil masuk ke **ruang ke 13** . di 
sana ia melihat sebuah peti yang sangat tersembunyi.setelah berhasil membuka peti ia mendapat sebuah kertas yang berjudul rahasia 
raja,tapi dikertas tersebut hanya berisi huruf huruf acak.

si pesan rahasia:

GUCPGS{enwn_chaln_vfgrev_yvzn}

## step by step solve
deskripsi challenge memberikan sebuah pesan rahasia, yaitu `GUCPGS{enwn_chaln_vfgrev_yvzn}` . memang sekilas ini hanya teks random, tapi bukan kah terlihat familiar?  
yep teks itu terlihat seperti format flag. ( THPCTF{...........} ) , namun sepertinya teks tersebut masih **terenkripsi** . 

daripada bingung dengan teks random itu, coba fokus ke deskripsi challenge nya. ada teks yang di bold atau di tebal kan, yaitu **ruang ke 13**. sepertinya raja kipin sedang
memberikan clue. coba cari informasi di internet.

<p align = "center"><img width="1671" height="211" alt="image" src="https://github.com/user-attachments/assets/ea0122a2-2bbd-4ec5-bb52-b7dc0d602dfc" /> </p>

hasil pencarian :

<p align = "center"><img width="75%" height="736" alt="image" src="https://github.com/user-attachments/assets/403b5372-c939-4e6b-91d5-42826e93f809" /></p>


internet menjawab `ROT-13` , rot 13 adalah algoritma yang bisa mengacak dan menyembunyikan teks asli menjadi `ciphertext` (teks acak) . cara rot13 bekerja adalah dengan
menggeser huruf abjad 13 langkah ke depan . 


apakah teks GUCPGS{enwn_chaln_vfgrev_yvzn} di enkripsi dengan ROT-13 ?? 

jika rot13 maju 13 langkah maka cara mencari teks aslinya adalah coba mundur kan 13 langkah ke belakang, aku coba huruf depannya saja. 


```
flag terenkripsi : GUCPGS{enwn_chaln_vfgrev_yvzn}

1. huruf pertama G mundur 1 jadi F 
2. lalu F mundur 1 jadi E
3. E >> D
4. D >> C
5. C >> B
6. B >> A
7. A >> Z nah jika udah mentok ke A, maka huruf mundur ke Z
8. Z >> Y
9. Y >> X
10. X >> W
11. W >> V
12. V >> U 
13. U >> T

huruf pertama flag adalah T
```
sementara format flag pada komunitas kita adalah THPCTF{} , SAMA SAMA BERAWALAN T . bisa jadi flag ini memang di sembunyikan pakai `ROT 13` 😲

tapi repot banget ya harus nggeser sebanyak 13 kali, 

karena itu kita bisa pakai saja **tools hacking** di internet , bisa pakai web [ROT-13 decoder](https://cryptii.com/pipes/rot13-decoder/)

<p align = "center"><img width="938" height="327" alt="image" src="https://github.com/user-attachments/assets/b2c90f0e-1039-4f3b-ad1a-70c4abd93491" /></p>

DONE 

flag = THPCTF{.............................}

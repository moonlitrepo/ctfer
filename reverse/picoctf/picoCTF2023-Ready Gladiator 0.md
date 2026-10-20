# picoCTF2023-Ready Gladiator 0.md
# overview

challenge ini cukup berbeda dari challenge lain, kali ini kita disuruh melakukan adu code dengan program lain. tapi untuk mendapatkan flag kita harus kalah semua ronde

# recon
<img width="500" height="403" alt="image" src="https://github.com/user-attachments/assets/431b4d3e-aecf-418c-abb3-71e16dd7e254" />


disini aku diberi file teks berisi kode asemmbly sederhana. 
```asembbly
Warrior1:
;redcode
;name Imp Ex
;assert 6
mov 0, 6
end
```
sepertinya tidak ada yang bisa aku lakukan dengan teks ini, jadi aku putuskan menghubungkan ke koneksi nc servernya.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(ready_gladiator0)
└> nc saturn.picoctf.net 49761 < imp.red
;redcode
;name Imp Ex
;assert 1
mov 0, 1
end
Submit your warrior: (enter 'end' when done)

Warrior1:
;redcode
;name Imp Ex
;assert 1
mov 0, 1
end

Rounds: 100
Warrior 1 wins: 0
Warrior 2 wins: 0
Ties: 100
Try again. Your warrior (warrior 1) must lose all rounds, no ties.
```

sepertinya berakhir seri. dan kenapa aku disuruh kalah. yaudah si kalau gitu kita harus membuat program kita sendiri crash. dengan mengedit file assembly warrior kita
# exploit
pertama aku nano seperti biasa dan ubah baris mov 0,1 menjadi mov 0,2. setelah itu aku save dan coba adu lagi di server 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(ready_gladiator0)
└> nano imp.red
┌[rotalactf]-[LAPTOP-6QMID52F]-(ready_gladiator0)
└> cat imp.red
;redcode
;name Imp Ex
;assert 1
mov 0, 2
end
```
<img width="388" height="347" alt="image" src="https://github.com/user-attachments/assets/b6d20b9a-939e-4334-82a8-6f7c657d8da4" />

nah jadi bagaimana ini bekerja? kok bisa warrior kita crash dan kalah? 
# how it works
jadi sebenarnya kita sedang memainkan sebuah game lama bernama **Corewar** dimana kita akan mengadu program buatakn kita dengan program buatan orang lain di simulator 
bernama **MARS** (Memory Array Redocode Simulator). jika kode / warrior tersebut crash / rusak saat di adu maka warrior lain yang masih berjalan akan jadi pemenang.

simulator tersebut memiliki memory yang bisa dipetakan jadi blok memory melingkar. saat game dimulai program akan diletakkan di memory secara acak, dan mereka akan berjalan
+1 blok tiap satu baris progam yang di eksekusi. cara mereka warrior pindah adalah dengan mengcopy imp.red ini dari instruksi mov 0,1 artinya mengcopy seluruh source code program
ke +1 blok kedepan. dan ketika dieksekusi blok didepan sudah ada kode kita dan kita bisa pindah ke depan dengan aman. 


sementara yang aku lakukan tadi mengubah mov 0,1 menjadi mov 0,2 artinya mengcopy seluruh source code ku ke +2 blok kedepan. karea warrior umumnya bergerak +1 jika tanpa instruksi
tambahan. maka aku bergerak ke kotak kosong yang tidak ada apa apa nya, dan aku tidak mengeksekusi apapun yang berakhir crash. karena warrior ku crash , maka aku
dihitung kalah sehingga mentrigger print flag

# conclusion
game ini adalah game lama yang sebenarnya menyenangkan jika mengerti cara mainnya. namun untuk bisa ahli dalam memainkan game ini diperlukan sedikit banyak pemahaman tentang bahasa
assembly karena bahasa redcode yang digunakan di imp.red ini sejatinya adalah bahasa assembly yang dibuat khusus untuk game nya.

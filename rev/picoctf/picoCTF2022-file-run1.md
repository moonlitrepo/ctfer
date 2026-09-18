# picoCTF2022-file-run1.md

chall ini adalah pembukaan awal untuk yang pertama kali menjalankan file program di linux.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(file-run1)
└> ./run
The flag is: picoCTF{U51N6_Y0Ur_F1r57_F113_9bc52b6b}%
```
yep just that. flag : picoCTF{U51N6_Y0Ur_F1r57_F113_9bc52b6b}

jika ingin tahu how and why this work aku coba jelasin dikit disini


# analisis file 
jadi challange ctf ini memberikan file program bernama run, bisa diidentifikasi dengan command file.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(file-run1)
└> file run
run: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=6e8c618e35e1676dcfc1528b849d349e82f127f1, for GNU/Linux 3.2.0, not stripped
```
terungkap semua datanya, yang jelas ini adalah program ELF, (executable and linkable format) mudahnya ini adalah program yang bisa di eksekusi. dah gitu aja.
tujuan utama dari challenge ini adalah gimana cara menjalankan program ini di linux? 

biasanya untuk menjalankan program di linux itu bisa pakai ./  jadi jika ada nama filenya adalah program, maka jalaninnya ya ./program lalu enter.

# permission execute
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(retpasswd)
└> ./ret
zsh: permission denied: ./ret
```
ada kalanya kita gabisa jalankan program dengan pesan permission denied ini. ini sederhana si, intinya si linux ga ngasi kita izin untuk ngejalanin file program ini. trus
caranya gimana? sederhana. ini adalah sedikit command dasar linux bagian permission.  mari kita analisis filenya


```
┌[rotalactf]-[LAPTOP-6QMID52F]-(file-run1)
└> ls -l
total 20
-rw-r--r-- 1 rotalactf rotalactf 16736 Aug 31 14:10 run
```
oke liat di atas , permission di blox pertama adalah -rw- . gaada x nya. sekarang kita harus ubah ini jadi -rwx
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(file-run1)
└> chmod +x run
┌[rotalactf]-[LAPTOP-6QMID52F]-(file-run1)
└> ls -l
total 20
-rwxr-xr-x 1 rotalactf rotalactf 16736 Aug 31 14:10 run
┌[rotalactf]-[LAPTOP-6QMID52F]-(file-run1)
└> ./run
The flag is: picoCTF{U51N6_Y0Ur_F1r57_F113_9bc52b6b}%                                                                                ┌[rotalactf]-[LAPTOP-6QMID52F]-(file-run1)
└>
```
yah kurang lebih begitu. ini adalah cara dasar menjalankan file program elf di linux.

# picoCTF2019-Need-For-Speed-writeup

# analysis & exploit step by step 

<p align= "center"><img width="734" height="465" alt="image" src="https://github.com/user-attachments/assets/2275363a-2240-4eea-9f02-133a23378fbf" />
 </p>

 program ini melakukan sesuatu. dan aku tidak bisa melakukan apapun disini, jadi aku coba decompile fungsinya dengan ghidra.

 siapa sangka , program ini hanya terdiri dari 4 fungsi :

**main()**
```C
 ndefined8 main(void)

{
  header();
  set_timer();
  get_key();
  print_flag();
  return 0;
}
```
program ini mengkalkulasi key untuk mendekripsi flag namun sebelum sempat mendekripsinya , fungsi set timer akan mengehentikan program.


karena fungsi yang dibutuhkan untuk flag hanya get_key() dan print_flag() , maka fungsi set_timer ini bisa dibuang saja. aku akan melakukan patching di ghidra.

before :
<p align= "center"> <img width="361" height="164" alt="image" src="https://github.com/user-attachments/assets/a17c827f-6f15-4537-9b47-289633063278" />
</p>

after : 
<p align = "center"> <img width="227" height="151" alt="image" src="https://github.com/user-attachments/assets/18299936-72b4-4c94-b236-323c421b470e" />
</p>

eksekusi :

<p align = "center"> <img width="848" height="485" alt="image" src="https://github.com/user-attachments/assets/27139fe0-62dd-40c0-b37d-dcbbe094d822" />
</p>

efek samping dari patching yang aku lakukan tadi, header akan di print dua kali. namun itu sepadan karena juga memprint flagnya , kan?

flag = **PICOCTF{Good job keeping bus #134d180d speeding along!}**

idk but ini flag valid nya.

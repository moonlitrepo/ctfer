# Phun-Cing

# deskripsi
  Ok I'll wait until this CTF ends so that I will get the flag right? But why I couldn't
  run it on my machine? It works in author's machine ...

  author: aseng

**file attached** 

# analysis & exploit step by step

- melakukan identifikasi file dengan melihat metadata nya
<p align="center"><img  width="75%" height="70" alt="image" src="https://github.com/user-attachments/assets/e02db60a-7901-4190-99ea-71aa094274d0" /> </p>

file tersebut merupakan file binary dengan arsitektur **arm** . terlihat juga dari metadatanya tertulis `not stripped`, maka simbol yang ada di file binary tidak disembunyikan
dan akan terbaca dengan jelas oleh debugger atau decompiler.


- menjalankan file

<p align="center"> <img width="493" height="174" alt="image" src="https://github.com/user-attachments/assets/bc9b233f-3b35-42be-aeeb-69c1a3e2bac7" /> <p>

karena arsitektur arm memiliki instruksi yang berbeda dengan arsitektur x86 , untuk menjalankannya membutuhkan tools tambahan : `QEMU` 

namun sepertinya binary ini 

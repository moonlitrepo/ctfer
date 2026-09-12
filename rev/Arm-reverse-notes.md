# Arm-reverse-notes.md

cara menjalankan / run file arm di linux :

ARM 32-bit (armel):
`qemu-arm -L /usr/arm-linux-gnueabi ./nama_binary`

ARM 32-bit (armhf):
`qemu-arm -L /usr/arm-linux-gnueabihf ./nama_binary`

ARM 64-bit (aarch64):
`qemu-aarch64 -L /usr/aarch64-linux-gnu ./nama_binary`


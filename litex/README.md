
### Save the firmware in flash:
`lxterm --serial-boot --kernel firmware.fbi --kernel-adr 0x100000 /dev/ttyUSB1 --flash`

### Save the bitstream in flash:
`fpgaprog -v -f build/gateware/top.bit -b shared/board/bscan_spi_lx9.bit -sa -r`
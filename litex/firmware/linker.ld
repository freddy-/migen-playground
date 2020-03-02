INCLUDE generated/output_format.ld
ENTRY(_start)

INCLUDE generated/regions.ld

SECTIONS
{
	.text :
	{
		_ftext = .;
		*(.text .stub .text.* .gnu.linkonce.t.*)
		_etext = .;
	} > main_ram

	.rodata :
	{
		. = ALIGN(8);
		_frodata = .;
		*(.rodata .rodata.* .gnu.linkonce.r.*)
		*(.rodata1)

		/* Make sure the file is aligned on disk as well
		   as in memory; CRC calculation requires that. */
		FILL(0);
		. = ALIGN(8);
		_erodata = .;
	} > main_ram

	.data :
	{
		. = ALIGN(8);
		_fdata = .;
		*(.data .data.* .gnu.linkonce.d.*)
		*(.data1)
		*(.sdata .sdata.* .gnu.linkonce.s.*)

		/* Make sure the file is aligned on disk as well
		   as in memory; CRC calculation requires that. */
		FILL(0);
		. = ALIGN(8);
		_edata = .;
	} > main_ram

	.bss :
	{
		. = ALIGN(8);
		_fbss = .;
		*(.dynsbss)
		*(.sbss .sbss.* .gnu.linkonce.sb.*)
		*(.scommon)
		*(.dynbss)
		*(.bss .bss.* .gnu.linkonce.b.*)
		*(COMMON)
		. = ALIGN(8);
		_ebss = .;
		_end = .;
	} > sram

	/DISCARD/ :
	{
		*(.eh_frame)
		*(.comment)
	}
}

PROVIDE(_fstack = ORIGIN(sram) + LENGTH(sram) - 8);

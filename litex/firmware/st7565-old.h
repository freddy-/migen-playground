#ifndef ST7565_H
#define ST7565_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "utils.h"

#define DATA_WIDTH 8
uint8_t nextPageCommands[] = {0xB0, 0x10, 0x00};

static void spi_write(uint8_t value) {
	display_spi_mosi_write(value);
	display_spi_control_write(DATA_WIDTH << CSR_DISPLAY_SPI_CONTROL_LENGTH_OFFSET | 1);
	while (!display_spi_status_read());
}

static void st7565_write_commands(uint8_t* commands, uint8_t length) {
	display_dc_out_write(0);
	for (uint32_t i = 0; i < length; i++) {
		spi_write(commands[i]);
	}
	display_dc_out_write(1);
}

static void st7565_init(void) {
	display_backligth_out_write(1);
	display_spi_cs_write(1);
	display_dc_out_write(1);

	display_reset_out_write(1);
	busy_wait(1);
	display_reset_out_write(0);
	busy_wait(1);
	display_reset_out_write(1);

	uint8_t initCommands[] = {0xA2, 0xA1, 0xC0, 0x25, 0x81, 0x1B, 0x2F, 0xAF, 0x40, 0xB0, 0x10, 0x00};
	st7565_write_commands(initCommands, 12);

	for (uint8_t page = 1; page <= 8; page++)	{
		for (uint8_t row = 0; row < 128; row++)	{
			spi_write(0x00);
		}

		nextPageCommands[0] = 0xB0 + page;
		st7565_write_commands(nextPageCommands, 3);
	}	
}

static void st7565_draw_pattern(void) {
	for (uint8_t page = 0; page < 8; page++)	{
		nextPageCommands[0] = 0xB0 + page;
		st7565_write_commands(nextPageCommands, 3);

		for (uint8_t row = 0; row < 128; row++)	{
			busy_wait(10);
			if (row % 2 == 0) {
				spi_write(0x55);
			} else {
				spi_write(0xAA);
			}
		}
	}	
}

#endif /* ST7565_H */
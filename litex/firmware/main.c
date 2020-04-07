#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>
#include "utils.h"
#include "st7565.h"

// litex_server --uart --uart-port=/dev/ttyUSB1

// lxterm /dev/ttyUSB1 --kernel firmware.bin
// reboot

static char *readstr(void)
{
	char c[2];
	static char s[64];
	static int ptr = 0;

	if(readchar_nonblock()) {
		c[0] = readchar();
		c[1] = 0;
		switch(c[0]) {
			case 0x7f:
			case 0x08:
				if(ptr > 0) {
					ptr--;
					putsnonl("\x08 \x08");
				}
				break;
			case 0x07:
				break;
			case '\r':
			case '\n':
				s[ptr] = 0x00;
				putsnonl("\n");
				ptr = 0;
				return s;
			default:
				if(ptr >= (sizeof(s) - 1))
					break;
				putsnonl(c);
				s[ptr] = c[0];
				ptr++;
				break;
		}
	}

	return NULL;
}

static char *get_token(char **str)
{
	char *c, *d;

	c = (char *)strchr(*str, ' ');
	if(c == NULL) {
		d = *str;
		*str = *str+strlen(*str);
		return d;
	}
	*c = 0;
	d = *str;
	*str = c+1;
	return d;
}

static void prompt(void)
{
	printf("RUNTIME>");
}

static void help(void)
{
	puts("Available commands:");
	puts("help                            - this command");
	puts("reboot                          - reboot CPU");
	puts("led                             - led test");
	puts("enc                             - encoder test");
}

static void reboot(void)
{
	ctrl_reset_write(1);
}

static void led_test(void)
{
	int i;
	printf("led_test...\n");
	for(i=0; i<32; i++) {
		led_out_write(i);
		busy_wait(1000);
	}
}

static void encoder_test(void) {
	printf("rotary encoder test...\n");
	uint8_t prevPosition = 0;
  while (1) {
    uint8_t value = encoder_value_read();
		if (prevPosition != value) {
			glcd_pixel(prevPosition, 10, 0);
		}
    display7Seg_value_write(value);
		glcd_pixel(value, 10, 1);
		prevPosition = value;
		glcd_refresh();
  }
}

static void console_service(void)
{
	char *str;
	char *token;

	str = readstr();
	if(str == NULL) return;
	token = get_token(&str);
	if(strcmp(token, "help") == 0)
		help();
	else if(strcmp(token, "reboot") == 0)
		reboot();
	else if(strcmp(token, "led") == 0)
		led_test();
	else if(strcmp(token, "enc") == 0)
		encoder_test();
	prompt();
}

/*
* Based on https://www.geeksforgeeks.org/program-for-conways-game-of-life/
*/
static void game_of_life(void) {
	unsigned char new_generation[SCREEN_WIDTH * SCREEN_HEIGHT / 8];
	unsigned char actual_generation[SCREEN_WIDTH * SCREEN_HEIGHT / 8];

	unsigned char *ptr_new_generation = new_generation;
	unsigned char *ptr_actual_generation = actual_generation;

	glcd_update_buffer(ptr_actual_generation);

	glcd_blank();

	// glider
	//glcd_pixel(40, 5, 1);
	//glcd_pixel(40, 6, 1);
	//glcd_pixel(40, 7, 1);
	//glcd_pixel(41, 7, 1);
	//glcd_pixel(42, 6, 1);

	// R-pentomino
	glcd_pixel(60, 30, 1);
	glcd_pixel(61, 30, 1);
	glcd_pixel(61, 31, 1);
	glcd_pixel(61, 29, 1);
	glcd_pixel(62, 29, 1);	

	glcd_refresh();
	uint32_t generationCounter = 0;
	while(1) {
    display7Seg_value_write(generationCounter++);

		for (uint8_t y = 1; y <= SCREEN_HEIGHT; y++) {
			for (uint8_t x = 1; x <= SCREEN_WIDTH; x++) {

				glcd_update_buffer(ptr_actual_generation);

				//printf("\n x: %d y: %d\n", x, y);

				// TODO tentar otimizar isso daqui de alguma forma, tentar fazer de uma maneira estática talvez...
				uint8_t aliveNeighbours = 0; 
				for (int i = -1; i <= 1; i++) {
					for (int j = -1; j <= 1; j++) {
						uint8_t neighbourX = x + i;
						uint8_t neighbourY = y + j;

						//printf("neighbourX: %d  neighbourY: %d\n", neighbourX, neighbourY);

						if (neighbourX < 1) {
							neighbourX = SCREEN_WIDTH;
						} else if (neighbourX > SCREEN_WIDTH) {
							neighbourX = 1;
						}

						if (neighbourY < 1) {
							neighbourY = SCREEN_HEIGHT;
						} else if (neighbourY > SCREEN_HEIGHT) {
							neighbourY = 1;
						}
						
						if (!(neighbourX == x && neighbourY == y)) {
							uint8_t neighbourValue = glcd_get_pixel(neighbourX, neighbourY);
							//printf("neighbourValue: %d\n", neighbourValue);
							aliveNeighbours += neighbourValue;
						}
					}
				}

				uint8_t actualCellState = glcd_get_pixel(x, y);

				// atualizar o buffer com o new generation
				glcd_update_buffer(ptr_new_generation);
				
				if ((actualCellState == 1) && (aliveNeighbours < 2)) {
					// Cell is lonely and dies 
					glcd_pixel(x, y, 0);
				} else if ((actualCellState == 1) && (aliveNeighbours > 3)) {
					// Cell dies due to over population 
					glcd_pixel(x, y, 0);
				} else if ((actualCellState == 0) && (aliveNeighbours == 3)) {
					// A new cell is born 
					glcd_pixel(x, y, 1);
				} else {
					glcd_pixel(x, y, actualCellState);
				}					
				
				//printf("vizinhos: %d\n", aliveNeighbours);
			}
		}

		unsigned char *temp = ptr_new_generation;
		ptr_new_generation = ptr_actual_generation;
		ptr_actual_generation = temp;

		glcd_refresh();

		//busy_wait(250);
	}
}

int main(void)
{
	irq_setmask(0);
	irq_setie(1);
	uart_init();

	glcd_init();

	game_of_life();

	puts("\nLab004 - CPU testing software built "__DATE__" "__TIME__"\n");
	help();
	prompt();

	while(1) {
		console_service();
	}

	return 0;
}
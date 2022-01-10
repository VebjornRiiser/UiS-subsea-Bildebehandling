/**
 * @file topside2can.cpp
 * @author ArcticMeteor246 (mats1809@gmail.com)
 * @brief 
 * @version 0.1
 * @date 2022-01-05
 * 
 * @copyright Copyright (c) 2022
 * 
 */

# include <stdio.h>
# include <string.h>
# include <iostream>
# include <thread>

#ifdef linux //Includes for Linux
#include <fcntl.h> // Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
#include <termios.h> // Contains POSIX terminal control definitions
#include <unistd.h> // write(), read(), close()
#endif

#ifdef _WIN32
#include <windows.h>
#endif

#ifdef linux
int serial_com = uintsd::open("/dev/ttyUSB0", O_RDWR);
#endif

#ifdef _WIN32
#endif

uint8_t serial_melding[13] = {0};

/**
 * @brief Hovedfunksjon for kommunikasjon
 * 
 * @return int 
 */
int main( void ){
  std::cout << "test\n";
}

void read_serial_port(int serial_com){
  serial_melding = read(serial_com, &buf, 1); 
}
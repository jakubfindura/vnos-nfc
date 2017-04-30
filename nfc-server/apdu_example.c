#include <stdlib.h>
#include <string.h>
#include <nfc/nfc.h>

#include <sys/socket.h>
#include <arpa/inet.h>

#define BUFFER_SIZE 10000 
#define MAX_CONNECTION 10

#define HOSTNAME_LEN 255
#define MAX_TRIES 10

char pipe_filename[] = "nfc_fifo.tmp";

int CardTransmit(nfc_device *pnd, uint8_t * capdu, size_t capdulen, uint8_t * rapdu, size_t * rapdulen) {
  int res;
  size_t  szPos;
  printf("=> ");
  
  for (szPos = 0; szPos < capdulen; szPos++) {
    printf("%02x ", capdu[szPos]);
  }
  printf("\n");
  
  if ((res = nfc_initiator_transceive_bytes(pnd, capdu, capdulen, rapdu, *rapdulen, 500)) < 0) {
    return -1;
  } else {
    *rapdulen = (size_t) res;
    printf("<= ");
    
    for (szPos = 0; szPos < *rapdulen; szPos++) {
      printf("%02x ", rapdu[szPos]);
    }
    printf("\n");
    return 0;
  }
}

int isValidMessage(uint8_t* apdu, size_t apdulen) {
  if ( apdulen < 4 ) return -1;
  if ( apdu[0] != 0xAA && apdu[1] != 0xAA) return -1;
  if ( apdu[apdulen-1] != 0x55 && apdu[apdulen-2] != 0x55 ) return -1;
  return 1;
}

int writeToFIFO(uint8_t* apdu, size_t apdulen) {
  FILE * wfd = fopen(pipe_filename, "w");
  if (wfd < 0) {
    printf("open() error: %d\n", wfd);
    return -1;
  }

  size_t szPos;
  for (szPos = 0; szPos < apdulen; szPos++) {
    int s_write = fprintf(wfd, "%02x ", apdu[szPos]);

    if (s_write < 0)
    {
        printf("fprintf() error: %d\n", s_write);
        break;
    }
  } 
  
  fclose(wfd);
  return 1;
}

int main(int argc, const char *argv[]) {
  
  unlink(pipe_filename);
  int pipe_fd = mkfifo(pipe_filename, 0777);

  if (pipe_fd != 0) {
      printf("mkfifo() error: %d\n", pipe_fd);
      return -1;
  }

  nfc_device *pnd;
  nfc_target nt;
  nfc_context *context;
  nfc_init(&context);
  if (context == NULL) {
    printf("Unable to init libnfc (malloc)\n");
    exit(EXIT_FAILURE);
  }

  const char *acLibnfcVersion = nfc_version();
  (void)argc;
  printf("%s uses libnfc %s\n", argv[0], acLibnfcVersion);

  pnd = nfc_open(context, NULL);

  if (pnd == NULL) {
    printf("ERROR: %s", "Unable to open NFC device.");
    exit(EXIT_FAILURE);
  }
  if (nfc_initiator_init(pnd) < 0) {
    nfc_perror(pnd, "nfc_initiator_init");
    exit(EXIT_FAILURE);
  }

  printf("NFC reader: %s opened\n", nfc_device_get_name(pnd));

  const nfc_modulation nmMifare = {
    .nmt = NMT_ISO14443A,
    .nbr = NBR_106,
  };
  // nfc_set_property_bool(pnd, NP_AUTO_ISO14443_4, true);

  while (true) {
    printf("Polling for target...\n");
    while (nfc_initiator_select_passive_target(pnd, nmMifare, NULL, 0, &nt) <= 0);
    printf("Target detected!\n");
    
    uint8_t capdu[264];
    size_t capdulen;
    uint8_t rapdu[264];
    size_t rapdulen;

    bool authMsgReceived = false;
    int tries = 0;
    
    // Select application
    memcpy(capdu, "\x00\xA4\x04\x00\x07\xf0\x01\x02\x03\x04\x06\x07", 12);
    capdulen = 12;
    rapdulen = sizeof(rapdu);
    
    int ct = 0;
    ct = CardTransmit(pnd, capdu, capdulen, rapdu, &rapdulen);
    
    if (ct < 0) continue;

    if ( rapdu[0] == 0x90 && rapdu[1] == 0x00 ) {
      while( !authMsgReceived && tries < MAX_TRIES) {
        tries++;
        memcpy(capdu, "\xAA\xAA\x02\x55\x55", 5);
        capdulen=5;
        
        ct = 0;
        rapdulen = sizeof(rapdu);
        ct = CardTransmit(pnd, capdu, capdulen, rapdu, &rapdulen);

        if (ct < 0) break;
        //TODO

        if ( isValidMessage( rapdu, rapdulen ) ) {
          if( rapdu[2] == 0x10 ) {
            printf("Writing to FIFO\n");

            writeToFIFO(rapdu, rapdulen);
           
            memcpy(capdu, "\xAA\xAA\x03\x55\x55", 5);
            capdulen = 5;
          
            ct = 0;
            rapdulen = sizeof(rapdu);
            ct = CardTransmit(pnd, capdu, capdulen, rapdu, &rapdulen);

            if (ct < 0) break;
            // TODO
            authMsgReceived = true;
          }
        }
      }
    
    }

    printf("Done\n");

  }

  
  unlink(pipe_filename);  

  nfc_close(pnd);
  nfc_exit(context);
  exit(EXIT_SUCCESS);
}

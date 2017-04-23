#include <stdlib.h>
#include <string.h>
#include <nfc/nfc.h>
int CardTransmit(nfc_device *pnd, uint8_t * capdu, size_t capdulen, uint8_t * rapdu, size_t * rapdulen) {
  int res;
  size_t  szPos;
  printf("=> ");
  for (szPos = 0; szPos < capdulen; szPos++) {
    printf("%02x ", capdu[szPos]);
  }
  printf("\n");
  if ((res = nfc_initiator_transceive_bytes(pnd, capdu, capdulen, rapdu, *rapdulen, 500)) < 0) {
	printf("C\n");
	return -1;
  } else {
    *rapdulen = (size_t) res;
    printf("<= ");
    for (szPos = 0; szPos < *rapdulen; szPos++) {
      printf("%02x ", rapdu[szPos]);
    }
    printf("\n");
	printf("D\n");
	return 0;
  }
}

int main(int argc, const char *argv[]) {

  printf("%d\n",sizeof(int));

  char pipe_filename[] = "nfc_fifo.tmp";
  unlink(pipe_filename);
  int pipe_fd = mkfifo(pipe_filename, 0777);

  if (pipe_fd != 0) {
      printf("mkfifo() error: %d\n", pipe_fd);
      return -1;
  }
    printf("A\n");

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
  printf("Polling for target...\n");
  while (nfc_initiator_select_passive_target(pnd, nmMifare, NULL, 0, &nt) <= 0);
  printf("Target detected!\n");
  uint8_t capdu[264];
  size_t capdulen;
  uint8_t rapdu[264];
  size_t rapdulen;
  // Select application
  memcpy(capdu, "\x00\xA4\x04\x00\x07\xf0\x01\x02\x03\x04\x05\x06", 12);
  capdulen=12;
  rapdulen=sizeof(rapdu);
  int ct = 0;
  ct = CardTransmit(pnd, capdu, capdulen, rapdu, &rapdulen);
  printf("%d\n", ct);
  if (ct < 0) {
    printf("A\n");
    exit(EXIT_FAILURE);
  };

  // Send message back "Hello from RPi"
  memcpy(capdu, "\x48\x65\x6C\x6C\x6F\x20\x66\x72\x6F\x6D\x20\x52\x50\x69", 14);
  capdulen=14;

  size_t  szPos;
  while ( true ) {
    // Listen while remote in range  
    rapdulen = sizeof(rapdu);
    ct = CardTransmit(pnd, capdu, capdulen, rapdu, &rapdulen);
    if (ct < 0) break;

    printf("Length: %d\n", rapdulen);

    for (szPos = 0; szPos < rapdulen; szPos++) {
      printf("%d ", rapdu[szPos]);
    } 

    if ( rapdu[0] == 0x66 && rapdu[1] == 0x66 ) {
      printf("Writing to FIFO\n");

      FILE * wfd = fopen(pipe_filename, "w");
      if (wfd < 0) {
        printf("open() error: %d\n", wfd);
        return -1;
      }

      for (szPos = 0; szPos < rapdulen; szPos++) {
        int s_write = fprintf(wfd, "%d ", rapdu[szPos]);

        if (s_write < 0)
        {
            printf("fprintf() error: %d\n", s_write);
            break;
        }
      } 
      
      fclose(wfd);
    }
    
    printf("\n");
    


  }

  printf("end\n");

  unlink(pipe_filename);

  nfc_close(pnd);
  nfc_exit(context);
  exit(EXIT_SUCCESS);
}

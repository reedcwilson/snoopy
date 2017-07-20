
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int DATA_SIZE = 512;
const char SERVICE_NAME[] = "snoopy";
const char INSTALL_DIR[] = "HOME_DIRECTORY";

int get_load_status() {
  FILE *fp; 
  char arr[512];
  int status = 0;
  char cmd[512];
  arr[0] = '\0';
  sprintf(cmd, "sc query %s | findstr \"STATE\"", SERVICE_NAME);
  fp = _popen(cmd, "r");
  while (fgets(arr, DATA_SIZE, fp) != NULL) {
    printf("%s", arr);
  };
  int exit_code = _pclose(fp);
  if (exit_code == -1 || strlen(arr) == 0) {
    return 1;
  }
  char substr[1];
  strncpy(substr, arr+29, 1);
  int sc_status = atoi(substr);
  switch(sc_status) {
    case 1:
    case 3:
      status = 2;
      break;
    case 2:
    case 4:
      status = 3;
      break;
  }
  return status;
}

void start() {
  char cmd[512];
  sprintf(cmd, "sc start %s", SERVICE_NAME);
  system(cmd);
}

void install() {
  char nssm[512];
  sprintf(nssm, "%s\\dist\\snoopy\\nssm.exe", INSTALL_DIR);
  char install_cmd[512];
  sprintf(install_cmd, "%s install %s python \"%s\\dist\\snoopy\\snoopy\"", nssm, SERVICE_NAME, INSTALL_DIR);
  char stop_cmd[512];
  sprintf(stop_cmd, "%s set %s AppStopMethodSkip 6", nssm, SERVICE_NAME);
  system(install_cmd);
  system(stop_cmd);
}

int main(int argc, char **argv) {
  _sleep(2);
  switch(get_load_status()) {
    case 1:
      printf("isn't loaded -- reloading\n");
      install();
      start();
      break;
    case 2:
      printf("loaded but stopped -- starting\n");
      start();
      break;
    case 3:
      printf("is loaded\n");
      break;
    default:
      printf("unrecognized state\n");
      break;
  }
}

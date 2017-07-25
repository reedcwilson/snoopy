
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int DATA_SIZE = 512;
const char SERVICE_NAME[] = "snoopy";
const char INSTALL_DIR[] = "HOME_DIRECTORY";

void debug(char *message) {
  char filename[512];
  /*sprintf(filename, "%s\\reload.out", INSTALL_DIR);*/
  sprintf(filename, "c:\\reload.out");
  FILE *f = fopen(filename, "a");
  fprintf(f, "%s\n", message);
  fclose(f);
}

int get_load_status() {
  FILE *fp; 
  char arr[512];
  int status = 0;
  char cmd[512];
  arr[0] = '\0';
  sprintf(cmd, "sc query %s | findstr \"STATE\"", SERVICE_NAME);
  fp = _popen(cmd, "r");
  while (fgets(arr, DATA_SIZE, fp) != NULL) {
    debug(arr);
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

void check_output(char *cmd_str) {
  FILE *fp; 
  char arr[512];
  arr[0] = '\0';
  fp = _popen(cmd_str, "r");
  while (fgets(arr, DATA_SIZE, fp) != NULL) {
    debug(arr);
  };
  int exit_code = _pclose(fp);
  char return_message[512];
  sprintf(return_message, "return code: %i", exit_code);
  debug(return_message);
}

void sc(char *str) {
  char cmd[512];
  sprintf(cmd, "sc %s %s", str, SERVICE_NAME);
  debug(cmd);
  /*check_output(cmd);*/
  system(cmd);
}

void delete() {
  sc("stop");
  sc("delete");
}

void start() {
  sc("start");
}

char* get_nssm() {
  char *nssm = malloc(sizeof(char)*512);
  sprintf(nssm, "%s\\dist\\snoopy\\nssm.exe", INSTALL_DIR);
  return nssm;
}

void nssm_set(char *nssm, char *option, char *value) {
  char cmd[512];
  sprintf(cmd, "%s set %s %s %s", nssm, SERVICE_NAME, option, value);
  debug(cmd);
  /*check_output(cmd);*/
  system(cmd);
}

void install() {
  char *nssm = get_nssm();

  char cmd[512];
  sprintf(cmd, "%s install %s \"%s\\dist\\snoopy\\snoopy.exe\"", nssm, SERVICE_NAME, INSTALL_DIR);
  debug(cmd);
  /*check_output(cmd);*/
  system(cmd);

  nssm_set(nssm, "AppStopMethodSkip", "6");
  char dir[512];
  sprintf(dir, "%s", INSTALL_DIR);
  nssm_set(nssm, "AppDirectory", dir);
  char log[512];
  sprintf(log, "%s\\windows.log", INSTALL_DIR);
  nssm_set(nssm, "AppStdout", log);
  nssm_set(nssm, "AppStderr", log);
  free(nssm);
}

int main(int argc, char **argv) {
  /*_sleep(2);*/
  switch(get_load_status()) {
    case 1:
      debug("isn't loaded -- reloading");
      install();
      _sleep(1);
      start();
      break;
    case 2:
      debug("loaded but stopped -- reloading");
      delete();
      _sleep(1);
      install();
      _sleep(1);
      start();
      break;
    case 3:
      debug("is loaded");
      break;
    default:
      debug("unrecognized state");
      break;
  }
}

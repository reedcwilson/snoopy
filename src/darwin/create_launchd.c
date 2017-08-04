
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

const int DATA_SIZE = 512;
const char *PLIST = "com.reedcwilson.snoopy.plist";

void debug(char *message) {
  char filename[DATA_SIZE];
  sprintf(filename, "%s/code/snoopy/launchd.out", getenv("HOME"));
  FILE *f = fopen(filename, "a");
  fprintf(f, "%s\n", message);
  fclose(f);
}

int is_loaded() {
  FILE *fp; 
  char arr[DATA_SIZE];
  int status;
  fp = popen("launchctl list | grep com.reedcwilson.snoopy", "r");
  while (fgets(arr, DATA_SIZE, fp) != NULL) {
    //printf("%s", arr);
  }
  return pclose(fp);
}

void launch(char filename[]) {
  char cmd[DATA_SIZE];
  sprintf(cmd, "launchctl load %s", filename);
  system(cmd);
}

int main(int argc, char **argv) {
  sleep(1);
  int loaded;
  char filename[DATA_SIZE];
  loaded = is_loaded();
  if (loaded == -1) {
    printf("\n");
  } else {
    switch (WEXITSTATUS(loaded)) {
      case 1:
        //sprintf(filename, "%s/Library/LaunchAgents/%s", getenv("HOME"), PLIST);
        sprintf(filename, "/Library/LaunchAgents/%s", PLIST);
        launch(filename);
        break;
      case 0:
        break;
    }
  }
}

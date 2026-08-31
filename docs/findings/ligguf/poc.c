// Auto-generated Iridium libfuzzer_c_harness for 17405
// Sink/API: read_gguf
// File: c/ligguf.c
// Context: 
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "gguf.h"
#include "ggml.h"

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/syscall.h>
#ifndef MFD_CLOEXEC
#define MFD_CLOEXEC 0x0001U
#endif
#ifndef __NR_memfd_create
#ifdef __linux__
#define __NR_memfd_create 319
#endif
#endif
static int iridium_memfd_create(const char *name) {
#if defined(__linux__) && defined(SYS_memfd_create)
  return (int)syscall(SYS_memfd_create, name, MFD_CLOEXEC);
#elif defined(__linux__)
  (void)name;
  return -1;
#else
  (void)name;
  return -1;
#endif
}
/* Library-linked no-arg parser: `read_gguf` from linked target_sources. */
extern "C" void open_mmap(const char *path);
extern "C" void read_gguf(void);

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size == 0) {
    return 0;
  }
  int fd = iridium_memfd_create("iridium_parser");
  char tmpl[] = "/tmp/iridium_parser_XXXXXX";
  int use_proc_fd = 0;
  if (fd < 0) {
    fd = mkstemp(tmpl);
    if (fd < 0) return 0;
  } else {
    use_proc_fd = 1;
  }
  if (write(fd, Data, Size) != (ssize_t)Size) {
    close(fd);
    if (!use_proc_fd) unlink(tmpl);
    return 0;
  }
  char path[96];
  if (use_proc_fd) {
    snprintf(path, sizeof(path), "/proc/self/fd/%d", fd);
  } else {
    snprintf(path, sizeof(path), "%s", tmpl);
  }
  open_mmap(path);
  (void)read_gguf();
  close(fd);
  if (!use_proc_fd) unlink(tmpl);
  return 0;
}

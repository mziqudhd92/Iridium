// Auto-generated Iridium libfuzzer_c_harness for entrypoint:gguf_init_from_file
// Sink/API: gguf_init_from_file
// File: ggml/src/gguf.cpp
// Context: (void)gguf_init_from_file(Data, Size);
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "gguf.h"
#include "ggml.h"
#include "ggml-backend.h"
#include "ggml-quants.h"
#include "ggml-threading.h"

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
/* Library-linked path-based parser: `gguf_init_from_file` from linked target_sources. */
extern "C" void ggml_free(struct ggml_context * ctx);
extern "C" struct gguf_context * gguf_init_from_file(const char *path, struct gguf_init_params params);

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size == 0) {
    return 0;
  }
  int fd = iridium_memfd_create("iridium_gguf");
  char tmpl[] = "/tmp/iridium_gguf_XXXXXX";
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
  struct ggml_context * ctx_data = nullptr;
  struct gguf_init_params params;
  memset(&params, 0, sizeof(params));
  params.no_alloc = false;
  params.ctx = &ctx_data;
  struct gguf_context * loaded = gguf_init_from_file(path, params);

  if (ctx_data) {
    ggml_free(ctx_data);
  }
  if (loaded) {
    gguf_free(loaded);
  }
  close(fd);
  if (!use_proc_fd) unlink(tmpl);
  return 0;
}

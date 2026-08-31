#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <wolfssl/wolfcrypt/settings.h>
#include <wolfssl/wolfcrypt/signature.h>
#include <wolfssl/wolfcrypt/types.h>
#include <wolfssl/wolfcrypt/ecc.h>
#include <wolfssl/wolfcrypt/random.h>
static word32 iridium_rand_seed = 0x12345678u;
unsigned int iridium_custom_rand(void) {
    iridium_rand_seed = iridium_rand_seed * 1103515245u + 12345u;
    return (unsigned int)(iridium_rand_seed >> 16);
}

static void iridium_write_proof(void) {
    FILE *proof = fopen("/tmp/iridium_proof", "wb");
    if (proof) fclose(proof);
    fputs("IRIDIUM_PROOF_CREATED\n", stdout);
}

int main(void) {
    ecc_key key;
    WC_RNG rng;
    byte hash[32];
    byte sig[256];
    word32 sigLen = (word32)sizeof(sig);
    word32 hash_len = 1;
    int rc = -1;
    memset(&key, 0, sizeof(key));
    memset(&rng, 0, sizeof(rng));
    memset(hash, 0x41, sizeof(hash));
    if (wc_InitRng(&rng) != 0) return 1;
    if (wc_ecc_init(&key) != 0) return 1;
    if (wc_ecc_make_key(&rng, 32, &key) != 0) return 1;
    if (wc_ecc_sign_hash(hash, hash_len, sig, &sigLen, &rng, &key) != 0) return 1;
    rc = wc_SignatureVerifyHash(WC_HASH_TYPE_SHA256, WC_SIGNATURE_TYPE_ECC,
        hash, hash_len, sig, sigLen, &key, (word32)sizeof(key));
    fputs("IRIDIUM_TARGET_API_CALLED\n", stdout);
    wc_ecc_free(&key);
    wc_FreeRng(&rng);
    if (rc == 0) iridium_write_proof();
    return 0;
}

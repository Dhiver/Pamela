/*
** is_luks.c for jeankevin_crypto in /home/work/work/projects/Pamela_doc/Pamela/crypto/src
** 
** Made by Bastien DHIVER
** Login   <dhiver_b@epitech.net>
** 
** Started on  Thu Oct 06 09:32:49 2016 Bastien DHIVER
** Last update Thu Oct 06 10:43:10 2016 Bastien DHIVER
*/

#include <systemd/sd-journal.h>
#include <errno.h>
#include "jeankevin_crypto.h"

bool			is_luks(const char *path)
{
  struct crypt_device	*cd;

  cd = NULL;
  if (crypt_init(&cd, path) != 0)
    {
      sd_journal_print(LOG_ERR, "crypt_init() failed: %s", strerror(errno));
      crypt_free(cd);
      return (false);
    }
  if (crypt_load(cd, CRYPT_LUKS1, NULL) != 0)
    {
      sd_journal_print(LOG_ERR, "crypt_load() failed: %s", strerror(errno));
      crypt_free(cd);
      return (false);
    }
  crypt_free(cd);
  return (true);
}

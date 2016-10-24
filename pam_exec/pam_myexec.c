#define _GNU_SOURCE

#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#include <systemd/sd-journal.h>
#include <errno.h>
#include <stdio.h>

#define PAM_SM_AUTH
#define PAM_SM_SESSION

#include <security/pam_modules.h>
#include <security/pam_appl.h>
#include <security/pam_ext.h>
#include <security/_pam_macros.h>

static int	move_fd_to_non_stdio(int fd)
{
  int		err_sav;

  while (fd < 3)
      if ((fd = dup(fd)) == -1)
	{
	  err_sav = errno;
	  sd_journal_print(LOG_ERR, "dup failed: %s", strerror(err_sav));
	  _exit(err_sav);
	}
  return (fd);
}

static int	_try_get_password(pam_handle_t *pamh, char **authtok)
{
  int		ret;
  const void	*void_pass;
  char		*resp;

  if ((ret = pam_get_item(pamh, PAM_AUTHTOK, &void_pass)) != PAM_SUCCESS)
    return (sd_journal_print(LOG_DEBUG,
			     "pam_get_item (PAM_AUTHTOK) failed: return %d",
			     ret), ret);
  else if (void_pass == NULL)
    {
      resp = NULL;
      if ((ret = pam_prompt(pamh, PAM_PROMPT_ECHO_OFF,
			    &resp, "Password: ")) != PAM_SUCCESS)
	{
	  _pam_drop(resp);
	  if (ret == PAM_CONV_AGAIN)
	    ret = PAM_INCOMPLETE;
	  return (ret);
	}
      *authtok = strndupa(resp, PAM_MAX_RESP_SIZE);
      _pam_drop(resp);
    }
  else
    *authtok = strndupa(void_pass, PAM_MAX_RESP_SIZE);
  return (PAM_SUCCESS);
}

static int	_send_password_to_child(pam_handle_t *pamh, int fds[2])
{
  char		*authtok;
  int		ret;

  authtok = NULL;
  if ((ret = _try_get_password(pamh, &authtok)) != PAM_SUCCESS)
    return (close(fds[0]), close(fds[1]), ret);
  if (authtok != NULL)
    {
      if (write(fds[1], authtok, strlen(authtok) + 1) == -1)
	sd_journal_print(LOG_ERR, "Sending password to child failed: %s",
			 strerror(errno));
      authtok = NULL;
      sd_journal_print(LOG_DEBUG, "Password sent to child");
    }
  else
    if (write(fds[1], "", 1) == -1)
      sd_journal_print(LOG_ERR, "Sending password to child failed: %s",
		       strerror(errno));
  return (close(fds[0]), close(fds[1]), PAM_SUCCESS);
}

static int	_check_argv(int ac, const char **av)
{
  if (ac < 1)
    {
      sd_journal_print(LOG_ERR, "This module needs at least one argument");
      return (PAM_SERVICE_ERR);
    }
  if (av[0][0] != '/')
    {
      sd_journal_print(LOG_ERR,
		       "First argument module needs to begin with a '/'");
      return (PAM_SYSTEM_ERR);
    }
  return (PAM_SUCCESS);
}

static void	_print_child_exec_error(int status, const char *prgm)
{
  if (WIFEXITED(status))
    sd_journal_print(LOG_ERR, "%s failed: exit code %d",
		     prgm, WEXITSTATUS(status));
  else if (WIFSIGNALED(status))
    sd_journal_print(LOG_ERR, "%s failed: caught signal %d%s",
		     prgm, WTERMSIG(status),
		     WCOREDUMP(status) ? " (core dumped)" : "");
  else
    sd_journal_print(LOG_ERR, "%s failed: unknown status 0x%x", prgm, status);
}

static int	_wait_for_child_to_exec(pid_t pid, const char *prgm)
{
  int		ret;
  int		status;

  while ((ret = waitpid(pid, &status, 0)) == -1 && errno == EINTR);
  if (ret == (pid_t)-1)
    return (sd_journal_print(LOG_ERR, "waitpid error: %s", strerror(errno)),
	    PAM_SYSTEM_ERR);
  else if (status != 0)
    {
      _print_child_exec_error(status, prgm);
      return (PAM_SYSTEM_ERR);
    }
  return (PAM_SUCCESS);
}

static void	_fds_redirections(int fds[2])
{
  int		err_sav;

  fds[0] = move_fd_to_non_stdio(fds[0]);
  close(fds[1]);
  if (dup2(fds[0], STDIN_FILENO) == -1)
    {
      err_sav = errno;
      sd_journal_print(LOG_ERR, "dup2 of STDIN failed: %s", strerror(err_sav));
      _exit(err_sav);
    }
}

static void	_build_child_env(const char *pam_type, pam_handle_t *pamh,
				 char ***child_env)
{
  const void	*pam_user;
  char		*envstr;
  int		err_sav;

  if ((*child_env = calloc(4, sizeof(char *))) == NULL)
    _exit(ENOMEM);
  pam_get_item(pamh, PAM_USER, &pam_user);
  if (asprintf(&envstr, "PAM_USER=%s", (const char *)pam_user) < 0)
    {
      err_sav = errno;
      free(*child_env);
      sd_journal_print(LOG_ERR, "Prepare environment failed: %s", strerror(err_sav));
      _exit(ENOMEM);
    }
  *child_env[0] = envstr;
  if (asprintf(&envstr, "PAM_TYPE=%s", pam_type) < 0)
    {
      err_sav = errno;
      free(*child_env);
      sd_journal_print(LOG_ERR, "Prepare environment failed: %s", strerror(err_sav));
      _exit(ENOMEM);
    }
  *child_env[1] = envstr;
  *child_env[2] = NULL;
}

static void	_mypam_exec(const char **av, char **child_env)
{
  int		ret;

  sd_journal_print(LOG_DEBUG, "Calling %s ...", av[0]);
  execve(av[0], (char **)av, child_env);
  ret = errno;
  sd_journal_print(LOG_ERR, "execve(%s,...) failed: %s", av[0], strerror(ret));
  free(child_env);
  _exit(ret);
}

static int	_exec(pam_handle_t *pamh, const char **av)
{
  char		**child_env;
  pid_t		pid;
  int		fds[2];
  int		ret;

  if (pipe(fds) != 0)
    return (sd_journal_print(LOG_ERR, "Could not create a pipe: %s",
			     strerror(errno)), PAM_SYSTEM_ERR);
  if ((pid = fork()) == -1)
    return (sd_journal_print(LOG_ERR, "fork error: %s", strerror(errno)),
	    PAM_SERVICE_ERR);
  if (pid > 0)
    {
      if ((ret = _send_password_to_child(pamh, fds)) != PAM_SUCCESS
      || (ret = _wait_for_child_to_exec(pid, av[0])) != PAM_SUCCESS)
	return (ret);
    }
  else
    {
      _fds_redirections(fds);
      _build_child_env("auth", pamh, &child_env);
      _mypam_exec(av, child_env);
    }
  return (PAM_SUCCESS);
}

PAM_EXTERN int	pam_sm_authenticate(pam_handle_t *pamh, int flags,
				   int ac, const char **av)
{
  int		ret;

  (void)flags;
  if ((ret = _check_argv(ac, av)) != PAM_SUCCESS)
    return (ret);
  if ((ret = _exec(pamh, av)) != PAM_SUCCESS)
    return (ret);
  return (PAM_SUCCESS);
}

PAM_EXTERN int	pam_sm_setcred(pam_handle_t *pamh, int flags,
			      int ac, const char **av)
{
  (void)pamh;
  (void)flags;
  (void)ac;
  (void)av;
  return (PAM_SUCCESS);
}

PAM_EXTERN int	pam_sm_acct_mgmt(pam_handle_t *pamh, int flags,
				int ac, const char **av)
{
  (void)pamh;
  (void)flags;
  (void)ac;
  (void)av;
  return (PAM_SUCCESS);
}

PAM_EXTERN int	pam_sm_open_session(pam_handle_t *pamh, int flags,
				   int ac, const char **av)
{
  (void)pamh;
  (void)flags;
  (void)ac;
  (void)av;
  return (PAM_SUCCESS);
}

PAM_EXTERN int	pam_sm_close_session(pam_handle_t *pamh, int flags,
				    int ac, const char **av)
{
  (void)pamh;
  (void)flags;
  (void)ac;
  (void)av;
  return (PAM_SUCCESS);
}

PAM_EXTERN int	pam_sm_chauthtok(pam_handle_t *pamh, int flags,
				int ac, const char **av)
{
  (void)pamh;
  (void)flags;
  (void)ac;
  (void)av;
  return (PAM_SERVICE_ERR);
}

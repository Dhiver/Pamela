CC	= gcc

RM	= rm -f

CFLAGS	+= -W -Wall -Wextra -pedantic
CFLAGS	+= -I./include/
CFLAGS	+= -fPIC

SRCF	= src/

NAME	= libjeankevincrypto.so

SRCS	= $(SRCF)is_luks.c
      
OBJS	= $(SRCS:.c=.o)


$(NAME): $(OBJS)
	$(CC) -shared -o $(NAME) $(OBJS) -lcryptsetup

all: $(NAME)

clean:
	$(RM) $(OBJS)

fclean: clean
	$(RM) $(NAME)

re: fclean all

.PHONY: all clean fclean re


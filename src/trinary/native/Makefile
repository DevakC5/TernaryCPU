CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -fPIC
LDFLAGS = -shared

LIB_DIR = .
SRC_DIR = .

_OBJ = alu.o gpu_kernels.o
OBJ = $(patsubst %,$(SRC_DIR)/%,$(_OBJ))

LIB = $(LIB_DIR)/libternary.so

.PHONY: all clean

all: $(LIB)

$(LIB): $(OBJ)
	$(CC) $(LDFLAGS) -o $@ $^

$(SRC_DIR)/%.o: $(SRC_DIR)/%.c $(SRC_DIR)/ternary.h
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJ) $(LIB)

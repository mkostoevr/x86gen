.PHONY: all run

all: gen

gen:
	@python3 gen.py

run: x86gen.exe
	./x86gen.exe

x86gen.exe: main.c x86gen.h generated.h
	clang main.c -o x86gen.exe

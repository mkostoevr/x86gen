.PHONY: all run

all: gen

gen:
	@python3 gen.py

run: x86gen.exe
	./x86gen.exe

x86gen.exe: main.c x86gen.h generated.h
	clang main.c -o x86gen.exe

check: generated.h
	@python3 gen.py > tmp.h
	@git diff --no-index generated.h tmp.h
	@rm -f tmp.h

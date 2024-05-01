.PHONY: all run

all: gen

gen:
	@python3 tools/gen.py

run: bin/x86gen.exe
	./bin/x86gen.exe

bin:
	mkdir bin

bin/x86gen.exe: main.c x86gen.h generated.h bin
	clang main.c -o bin/x86gen.exe

check: generated.h
	@python3 tools/gen.py > tmp.h
	@git diff --no-index generated.h tmp.h
	@rm -f tmp.h

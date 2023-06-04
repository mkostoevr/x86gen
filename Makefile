.PHONY: all run

all: gen

gen:
	@python3 gen.py

test:
	python3 gen.py --with-tests > generated.h
	tcc main.c -o test.exe
	./test.exe
	objdump -b binary -m i386 --disassembler-options="intel" --no-addresses --no-show-raw-insn -D test32.bin > test32.result
	objdump -b binary -m i386:x86-64 --disassembler-options="intel" --no-addresses --no-show-raw-insn -D test64.bin > test64.result

run: x86gen.exe
	./x86gen.exe

x86gen.exe: main.c x86gen.h generated.h
	clang main.c -o x86gen.exe

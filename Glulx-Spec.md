<title>Glulx</title>

<subtitle>A 32-Bit Virtual Machine for IF</subtitle>

<subtitle>VM specification version 3.1.2</subtitle>

<subtitle>Andrew Plotkin &lt;erkyrath@eblong.com&gt;</subtitle>

Copyright 1999-2010 by Andrew Plotkin. This specification is licensed under a Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported License: <a href="http://creativecommons.org/licenses/by-nc-sa/3.0">http://creativecommons.org/licenses/by-nc-sa/3.0</a>

The virtual machine <em>described</em> by this document is an idea, not an expression of an idea, and is therefore not copyrightable. Anyone is free to write programs that run on the Glulx VM or make use of it, including compilers, interpreters, debuggers, and so on.

This document and further Glulx information can be found at:
<a href="http://eblong.com/zarf/glulx/">http://eblong.com/zarf/glulx/</a>

<contents>

<h level=1 number=0 label=intro>Introduction</h>

Glulx is a simple solution to a fairly trivial problem. We want a virtual machine which the Inform compiler can compile to, without the increasingly annoying restrictions of the Z-machine.

Glulx does this, without much fuss. All arithmetic is 32-bit (although there are opcodes to handle 8-bit and 16-bit memory access.) Input and output are handled through the Glk API (which chops out half the Z-machine opcodes, and most of the complexity of a Z-code interpreter.) Some care has been taken to make the bytecode small, but simplicity and elbow room are considered more important &emdash; bytecode is not a majority of the bulk in current Inform games.

<h level=2>Why Bother?</h>

We're buried in IF VMs already, not to mention general VMs like Java, not to mention other interpreters or bytecode systems like Perl.  Do we need another one?

Well, maybe not, but Glulx is simple enough that it was easier to design and implement it than to use something else. Really.

The Inform compiler already does most of the work of translating a high-level language to bytecode. It has long since outgrown many of the IF-specific features of the Z-machine (such as the object structure.) So it makes sense to remove those features, leaving a generic VM. Furthermore, there are enough other constraints (Inform's assumption of a flat memory model, the desire to have a lightweight VM suitable for PDAs) that no existing system is really ideal. So it seems worthwhile to design a new one.

Indeed, most of the effort that has gone into this system has been modifying Inform. Glulx itself is nearly an afterthought.

<h level=2 label=otherif>Glulx and Other IF Systems</h>

Glulx grew out of the desire to extend Inform. However, it may well be suitable as a VM for other IF systems.

Or maybe not. Since Glulx <em>is</em> so lightweight, a compiler has to be fairly complex to compile to it. Many IF systems take the approach of a simple compiler, and a complex, high-level, IF-specific interpreter. Glulx is not suitable for this.

However, if a system wants to use a simple runtime format with 32-bit data, Glulx may be a good choice.

Note that this is entirely separate from question of the I/O layer. Glulx uses the Glk I/O API, for the sake of simplicity and portability. Any IF system can do the same. One can use Glk I/O without using the Glulx game-file format.

On the obverse, one could also extend the Glulx VM to use a different I/O system instead of Glk. One such extension is FyreVM, a commercial IF system developed by Textfyre. FyreVM is described at <a href="http://textfyre.com/fyrevm/">http://textfyre.com/fyrevm/</a>. This specification does not cover it, except to note opcodes, gestalt selectors, and iosys values that are specific to FyreVM.

<h level=2>Credits</h>

Graham Nelson gets pretty much all of it. Without Inform, there would be no reason for any of this. The entirety of Glulx is fallout from my attempt to deconstruct Inform and rebuild its code generator in my own image, with Graham's support.

<h level=1>The Machine</h>

The Glulx machine consists of main memory, the stack, and a few registers (the program counter, the stack pointer, and the call-frame pointer.)

Main memory is a simple array of bytes, numbered from zero up. When accessing multibyte values, the most significant byte is stored first (big-endian). Multibyte values are not necessarily aligned in memory.

The stack is an array of values. It is not a part of main memory; the terp maintains it separately. The format of the stack is technically up to the implementation. However, the needs of the machine (especially the game-save format) leave about one good option. (See <ref label=saveformat>.) One important point: the stack can be kept in either byte ordering. The program should make no assumptions about endianness on the stack. (In fact, programs should never need to care.) Values on the stack always have their natural alignment (16-bit values at even addresses, 32-bit values at multiples of four).

The stack consists of a set of call frames, one for each function in the current chain. When a function is called, a new stack frame is pushed, containing the function's local variables. The function can then push or pull 32-bit values on top of that, to store intermediate computations.

All values are treated as unsigned integers, unless otherwise noted. Signed integers are handled with the usual two's-complement notation. Arithmetic overflows and underflows are truncated, also as usual.

<h level=2>Input and Output</h>

No input/output facilities are built into the Glulx machine itself. Instead, the machine has one or more opcodes which dispatch calls to an I/O library.

At the moment, that means Glk. All Glulx interpreters support the Glk I/O facility (via the glk opcode), and no other I/O facilities exist. However, other I/O libraries may be adapted to Glk in the future. For best behavior, a program should test for the presence of an I/O facility before using it, using the IOSystem gestalt selector (see <ref label=opcodes_misc>).

One I/O system is set as current at any given time. This does not mean that the others are unavailable. (If the interpreter supports Glk, for example, the glk opcode will always function.) However, the basic Glulx output opcodes &emdash; streamchar, streamnum, and streamstr &emdash; always print using the current I/O system.

Every Glulx interpreter supports at least one normal I/O facility (such as Glk), and also two special facilities.

The "null" I/O system does nothing. If this is selected, all Glulx output is simply discarded. <comment>Silly, perhaps, but I like simple base cases.</comment> When the Glulx machine starts up, the null system is the current system. You must select a different one before using the streamchar, streamnum, or streamstr opcodes.

The "filter" I/O system allows the Glulx program itself to handle output. The program specifies a function when selecting this I/O system. That function is then called for every single character of output that the machine generates (via streamchar, streamnum, or streamstr). The function can output its character directly via the glk opcode (or one of the other output opcodes).

<comment>This may all seem rather baroque, but in practice most authors can ignore it. Most programs will want to test for the Glk facility, set it to be the current output system immediately, and then leave the I/O system alone for the rest of the game. All output will then automatically be handled through Glk.</comment>

<h level=2>The Memory Map</h>

Memory is divided into several segments. The sizes of the segments are determined by constant values in the game-file header.

<code>
  Segment    Address (hex)

+---------+  00000000
| Header  |
| - - - - |  00000024
|         |
|   ROM   |
|         |
+---------+  RAMSTART
|         |
|   RAM   |
|         |
| - - - - |  EXTSTART
|         |
|         |
+---------+  ENDMEM
</code>

As you might expect, the section marked ROM never changes during execution; it is illegal to write there. Executable code and constant data are usually (but not necessarily) kept in ROM. Note that unlike the Z-machine, the Glulx machine's ROM comes before RAM; the 36-byte header is part of ROM.

The boundary marked EXTSTART is a trivial gimmick for making game-files smaller. A Glulx game-file only stores the data from 0 to EXTSTART. When the terp loads it in, it allocates memory up to ENDMEM; everything above EXTSTART is initialized to zeroes. Once execution starts, there is no difference between the memory above and below EXTSTART.

For the convenience of paging interpreters, the three boundaries RAMSTART, EXTSTART, and ENDMEM must be aligned on 256-byte boundaries.

Any of the segments of memory can be zero-length, except that ROM must be at least 256 bytes long (so that the header fits in it).

<h level=2 label=stack>The Stack</h>

The stack pointer starts at zero, and the stack grows upward. The maximum size of the stack is determined by a constant value in the game-file header. For convenience, this must be a multiple of 256.

The stack pointer counts in bytes. If you push a 32-bit value on the stack, the pointer increases by four.

<h level=3 label=callframe>The Call Frame</h>

A call frame looks like this:

<code>
+------------+  FramePtr
| Frame Len  |    (4 bytes)
| Locals Pos |    (4 bytes)
|            |
| Format of  |    (2*n bytes)
|     Locals |
|            |
| Padding    |    (0 or 2 bytes)
+------------+  FramePtr+LocalsPos
| Locals     |    (1, 2, or 4 bytes each)
|            |
| Padding    |    (0 to 3 bytes)
+------------+  FramePtr+FrameLen
| Values     |    (4 bytes each)
|      ....  |
+------------+  StackPtr
</code>

When a function begins executing, the last segment is empty (StackPtr equals FramePtr+FrameLen.) Computation can push and pull 32-bit values on the stack. It is illegal to pop back beyond the original FramePtr+FrameLen boundary.

The "locals" are a list of values which the function uses as local variables. These also include function arguments. (The first N locals can be used as the arguments to an N-argument function.) Locals can be 8, 16, or 32-bit values. They are not necessarily contiguous; padding is inserted wherever necessary to bring a value to its natural alignment (16-bit values at even addresses, 32-bit values at multiples of four).

The "format of locals" is a series of bytes, describing the arrangement of the "locals" section of the frame (from LocalsPos up to FrameLen). This information is copied directly from the header of the function being called. (See <ref label=function>.)

Each field in this section is two bytes:

<list>
<li>LocalType: 1, 2, or 4, indicating a set of locals which are that many bytes each.
<li>LocalCount: 1 to 255, indicating how many locals of LocalType to declare.
</list>

The section is terminated by a pair of zero bytes. Another pair of zeroes is added if necessary to reach a four-byte boundary.

(Example: if a function has three 8-bit locals followed by six 16-bit locals, the format segment would contain eight bytes: (1, 3, 2, 6, 0, 0, 0, 0). The locals segment would then be 16 bytes long, with a padding byte after the third local.)

The "format of locals" information is needed by the terp in two places: when calling a function (to write in function arguments), and when saving the game (to fix byte-ordering of the locals.) The formatting is <em>not</em> enforced by the terp while a function is executing. The program is not prevented from accessing locations whose size and position don't match the formatting, or locations that overlap, or even locations in the padding between locals. However, if a program does this, the results are undefined, because the byte-ordering of locals is up to the terp. The save-game algorithm will fail, if nothing else.

<comment>In fact, the call frame may not exist as a byte sequence during function execution. The terp is free to maintain a more structured form, as long as it generates valid save-game files, and correctly handles accesses to valid (according to the format) locals.</comment>

<comment>NOTE: 8-bit and 16-bit locals have never been in common use, and this spec has not been unambiguous in describing their handling. (By which I mean, what I implemented in the reference interpreter didn't match the spec.) Therefore, 8-bit and 16-bit locals are deprecated. Use of the copyb and copys opcodes with a local-variable operand is also deprecated.</comment>

<h level=3 label=callstub>Call Stubs</h>

Several different Glulx operations require the ability to jump back to a previously-saved execution state. (For example: function call/return, game-state save/restore, and exception catch/throw.)

For simplicity, all these operations store the execution state the same way &emdash; as a "call stub" on the stack. This is a block of four 32-bit values. It encodes the PC and FramePtr, and also a location to store a single 32-bit value at jump-back time. (For example, the function return value, or the game-restore success flag.)

The values are pushed on the stack in the following order (FramePtr pushed last):

<code>
+-----------+
| DestType  |  (4 bytes)
| DestAddr  |  (4 bytes)
| PC        |  (4 bytes)
| FramePtr  |  (4 bytes)
+-----------+
</code>

FramePtr is the current value of FramePtr &emdash; the stack position of the call frame of the function during which the call stub was generated.

PC is the current value of the program counter. This is the address of the instruction <em>after</em> the one which caused the call stub to be generated. (For example, for a function call, the call stub contains the address of the first instruction to execute after the function returns.)

DestType and DestAddr describe a location in which to store a result. This will occur after the operation is completed (function returned, game restored, etc). It happens after the PC and FramePtr are reloaded from the call stub, and the call stub is removed from the stack.

DestType is one of the following values:

<list>
<li>0: Do not store. The result value is discarded. DestAddr should be zero.
<li>1: Store in main memory. The result value is stored in the main-memory address given by DestAddr.
<li>2: Store in local variable. The result value is stored in the call frame at position ((FramePtr+LocalsPos) + DestAddr). See <ref label=instruction>.
<li>3: Push on stack. The result value is pushed on the stack. DestAddr should be zero.
</list>

The string-decoding mechanism complicates matters a little, since it is possible for a function to be called from inside a string, instead of another function. (See <ref label=callstring>.) The following DestType values allow this:

<list>
<li>10: Resume printing a compressed (E1) string. The PC value contains the address of the byte (within the string) to continue printing in. The DestAddr value contains the bit number (0 to 7) within that byte.
<li>11: Resume executing function code after a string completes. The PC value contains the program counter as usual, but the FramePtr field is ignored, since the string is printed in the same call frame as the function that executed it. DestAddr should be zero.
<li>12: Resume printing a signed decimal integer. The PC value contains the integer itself. The DestAddr value contains the position of the digit to print next. (0 indicates the first digit, or the minus sign for negative integers; and so on.)
<li>13: Resume printing a C-style (E0) string. The PC value contains the address of the character to print next. The DestAddr value should be zero.
<li>14: Resume printing a Unicode (E2) string. The PC value contains the address of the (four-byte) character to print next. The DestAddr value should be zero.
</list>

<h level=3>Calling and Returning</h>

When a function is called, the terp pushes a four-value call stub. (This includes the return-value destination, the PC, and the FramePtr; see <ref label=callstub>.) The terp then sets the FramePtr to the StackPtr, and builds a new call frame. (See <ref label=callframe>.) The PC moves to the first instruction of the function, and execution continues.

Function arguments can be stored in the locals of the new call frame, or pushed on the stack above the new call frame. This is determined by the type of the function; see <ref label=function>.

When a function returns, the process is reversed. First StackPtr is set back to FramePtr, throwing away the current call frame (and any pushed values). The FramePtr and PC are popped off the stack, and then the return-value destination. The function's return value is stored where the destination says it should be. Then execution continues at the restored PC.

(But note that a function can also return to a suspended string, as well as a suspended caller function. See <ref label=callstring> and <ref label=callfilter>.)

<h level=3 label=callstring>Calling and Returning Within Strings</h>

Glulx uses a Huffman string-compression scheme. This allows bit sequences in strings to decode to large strings, or even function invocations which generate output. This means the streamstr opcode can invoke function calls, and we must therefore be able to represent this situation on the stack.

When the terp begins printing a string, it pushes a type-11 call stub. (This includes only the current PC. The FramePtr is included, for consistency's sake, but it will be ignored when the call stub is read back off.) The terp then starts decoding the string data. The PC now indicates the position within the string data.

If, during string decoding, the terp encounters an indirect reference to a string or function, it pushes a type-10 call stub. This includes the string-decoding PC, and the bit number within that address. It also includes the current FramePtr, which has not changed since string-printing began.

If the indirect reference is to another string, the decoding continues at the new location after the type-10 stub is pushed. However, if the reference is to a function, the usual call frame is pushed on top of the type-10 stub, and the terp returns to normal function execution.

When a string completes printing, the terp pops a call stub. This will necessarily be either a type-10 or type-11. If the former, the terp resumes string decoding at the PC address/bit number in the stub. If the latter, the topmost string is finished, and the terp resumes function execution at the stub's PC.

When a function returns, it must check to see if it was called from within a string, instead of from another function. This is the case if the call stub it pops is type-10. (The call stub cannot be type-11.) If so, the FramePtr is taken from the stub as usual; but the stub's PC is taken to refer to a string data address, with the DestAddr value being the bit number within that address. (The function's return value is discarded.) String decoding resumes from there.

<comment>It may seem wasteful for the terp to push and pop a call stub every time a string is printed. Fortunately, in the most common case &emdash; printing a string with no indirect references at all &emdash; this can easily be optimized out. (No VM code is executed between the push and pop, so it is safe to skip them.) Similarly, when printing an unencoded (E0) string, there can be no indirect references, so it is safe to optimize away the call stub push/pop.</comment>

<h level=3 label=callfilter>Calling and Returning During Output Filtering</h>

The "filter" I/O system allows the terp to call a Glulx function for each character that is printed via streamchar, streamnum, or streamstr. We must be able to represent this situation on the call stack as well.

If filtering is the current I/O system, then when the terp executes streamchar, it pushes a normal function call stub and begins executing the output function. Nothing else is required; when the function returns, execution will resume after the streamchar opcode. (A type-0 call stub is used, so the function's return value is discarded.)

The other output opcodes are more complex. When the terp executes streamnum, it pushes a type-11 call stub. As before, this records the current PC. The terp then pushes a type-12 call stub, which contains the integer being printed and the position of the next character to be printed (namely 1). It then executes the output function.

When the output function returns, the terp pops the type-12 stub and realizes that it should continue printing the integer contained therein. It pushes another type-12 stub back on the stack, indicating that the next position to print is 2, and calls the output function again.

This process continues until there are no more characters in the decimal representation of the integer. The terp then pops the type-11 stub, restores the PC, and resumes execution after the streamnum opcode.

The streamstr opcode works on the same principle, except that instead of type-12 stubs, the terp uses type-10 stubs (when interrupting an encoded string) and type-13/14 stubs (when interruping a C-style, null-terminated string of bytes/Unicode chars). Type-13 and type-14 stubs look like the others, except that they contain only the address of the next character to print; no other position or bit number is necessary.

The interaction between the filter I/O system and indirect string/function calls within encoded strings is left to the reader's imagination. <comment>Because I couldn't explain it if I tried. Follow the rules; they work.</comment>

<h level=2>The Header</h>

The header is the first 36 bytes of memory. It is always in ROM, so its contents cannot change during execution. The header is organized as nine 32-bit values. (Recall that values in memory are always big-endian.)

<code>
+---------------+  address 0
| Magic Number  |  (4 bytes)
| Glulx Version |  (4 bytes)
| RAMSTART      |  (4 bytes)
| EXTSTART      |  (4 bytes)
| ENDMEM        |  (4 bytes)
| Stack Size    |  (4 bytes)
| Start Func    |  (4 bytes)
| Decoding Tbl  |  (4 bytes)
| Checksum      |  (4 bytes)
+---------------+
</code>

<list>
<li>Magic number: 47 6C 75 6C, which is to say ASCII 'Glul'.
<li>Glulx version number: The upper 16 bits stores the major version number; the next 8 bits stores the minor version number; the low 8 bits stores an even more minor version number, if any. This specification is version 3.1.2, so a game file generated to this spec would contain 00030102.
<li>RAMSTART: The first address which the program can write to.
<li>EXTSTART: The end of the game-file's stored initial memory (and therefore the length of the game file.)
<li>ENDMEM: The end of the program's memory map.
<li>Stack size: The size of the stack needed by the program.
<li>Address of function to execute: Execution commences by calling this function.
<li>Address of string-decoding table: This table is used to decode compressed strings. See <ref label=string_enc>. This may be zero, indicating that no compressed strings are to be decoded. <comment>Note that the game can change which table the terp is using, with the setstringtbl opcode. See <ref label=opcodes_output>.</comment>
<li>Checksum: A simple sum of the entire initial contents of memory, considered as an array of big-endian 32-bit integers. The checksum should be computed with this field set to zero.
</list>

The interpreter should validate the magic number and the Glulx version number. An interpreter which is written to version X.Y.Z of this specification should accept game files whose Glulx version between X.0.0 and X.Y.*. (That is, the major version number should match; the minor version number should be less than or equal to Y; the subminor version number does not matter.)

EXCEPTION: A version 3.* interpreter should accept version 2.0 game files. The only difference between spec 2.0 and spec 3.0 is that 2.0 lacks Unicode functionality. Therefore, an interpreter written to this version of the spec (3.1.2) should accept game files whose version is between 2.0.0 and 3.1.* (0x00020000 and 0x000301FF inclusive).

<comment>These rules mean, in the vernacular, that minor version changes are backwards compatible, and subminor version changes are backwards and forwards compatible. If I add a feature which I expect every terp to implement (e.g. mzero and mcopy), then I bump the minor version number, and your game can use that feature without worrying about availability. If I add a feature which not all terps will implement (e.g. floating point), then I bump the subminor version number, and your game should only use the feature after doing a gestalt test for availability.</comment>

<comment>The header is conventionally followed by a 32-bit word which describes the layout of data in the rest of the file. This value is <em>not</em> a part of the Glulx specification; it is the first ROM word after the header, not a part of the header. It is an option that compilers can insert, when generating Glulx files, to aid debuggers and decompilers.

For Inform-generated Glulx files, this descriptive value is 49 6E 66 6F, which is to say ASCII 'Info'. There then follow several more bytes of data relevant to the Inform compiler. See the Glulx chapter of the Inform Technical Manual.</comment>

<h level=2 label=instruction>Instruction Format</h>

There are 2^28 Glulx opcodes, numbered from 0 to 0FFFFFFF. If this proves insufficient, more may be added in the future.

An instruction is encoded as follows:

<code>
+--------------+
| Opcode Num   |  (1 to 4 bytes)
|              |
| Operand      |  (two per byte)
|   Addr Modes |
|              |
| Operand Data |  (as defined by
|        ....  |      addr modes)
+--------------+
</code>

The opcode number OP, which can be anything up to 0FFFFFFF, may be packed into fewer than four bytes:

<list>
<li>00..7F: One byte, OP
<li>0000..3FFF: Two bytes, OP+8000
<li>00000000..0FFFFFFF: Four bytes, OP+C0000000
</list>

Note that the length of this field can be decoded by looking at the top two bits of the first byte. Also note that, for example, 01 and 8001 and C0000001 all represent the same opcode.

The operand addressing modes are a list of fields which tell where opcode arguments are read from or written to. Each is four bits long, and they are packed two to a byte. (They occur in the same order as the arguments, low bits first. If there are an odd number, the high bits of the last byte are left zero.)

Since each addressing mode is a four-bit number, there are sixteen addressing modes. Each is associated with a fixed number of bytes in the "operand data" segment of the instruction. These bytes appear after the addressing modes, in the same order. (There is no alignment padding.)

<list>
<li>0: Constant zero. (Zero bytes)
<li>1: Constant, -80 to 7F. (One byte)
<li>2: Constant, -8000 to 7FFF. (Two bytes)
<li>3: Constant, any value. (Four bytes)
<li>4: (Unused)
<li>5: Contents of address 00 to FF. (One byte)
<li>6: Contents of address 0000 to FFFF. (Two bytes)
<li>7: Contents of any address. (Four bytes)
<li>8: Value popped off stack. (Zero bytes)
<li>9: Call frame local at address 00 to FF. (One byte)
<li>A: Call frame local at address 0000 to FFFF. (Two bytes)
<li>B: Call frame local at any address. (Four bytes)
<li>C: (Unused)
<li>D: Contents of RAM address 00 to FF. (One byte)
<li>E: Contents of RAM address 0000 to FFFF. (Two bytes)
<li>F: Contents of RAM, any address. (Four bytes)
</list>

Things to note:

The "constant" modes sign-extend their data into a 32-bit value; the other modes do not. This is just because negative constants occur more frequently than negative addresses.

The indirect modes (all except "constant") access 32-bit fields, either in the stack or in memory. This means four bytes starting at the given address. A few opcodes are exceptions: copyb and copys (copy byte and copy short) access 8-bit and 16-bit fields (one or two bytes starting at the given address.)

The "call frame local" modes access a field on the stack, starting at byte ((FramePtr+LocalsPos) + address). As described in <ref label=callframe>, this must be aligned with (and the same size as) one of the fields described in the function's locals format. It must not point outside the range of the current function's locals segment.

The "contents of address" modes access a field in main memory, starting at byte (addr). The "contents of RAM" modes access a field in main memory, starting at byte (RAMSTART + addr). Since the byte-ordering of main memory is well-defined, these need not have any particular alignment or position.

All address addition is truncated to 32 bits, and addresses are unsigned. So, for example, "contents of RAM" address FFFFFFFC (RAMSTART + FFFFFFFC) accesses the last 32-bit value in ROM, since it effectively subtracts 4 from RAMSTART. "Contents of address" FFFFFFFC would access the very last 32-bit value in main memory, assuming you can find a terp which handles four-gigabyte games. "Call frame local" FFFFFFFC is illegal; whether you interpret it as a negative number or a large positive number, it's outside the current call frame's locals segment.

Some opcodes store values as well as reading them in. Store operands use the same addressing modes, with a few exceptions:

<list>
<li>8: The value is pushed into the stack, instead of being popped off.
<li>3, 2, 1: These modes cannot be used, since it makes no sense to store to a constant. <comment>We delicately elide the subject of Fortran. And rule-based property algebras.</comment>
<li>0: This mode means "throw the value away"; it is not stored at all.
</list>

Operands are evaluated from left to right. (This is important if there are several push/pop operands.)

<h level=2>Typable Objects</h>

It is convenient for a program to store object references as 32-bit pointers, and still determine the type of a reference at run-time.

To facilitate this, structured objects in Glulx main memory follow a simple convention: the first byte indicates the type of the object.

At the moment, there are only two kinds of Glulx objects: functions and strings. A program (or compiler, or library) may declare more, but the Glulx VM does not have to know about them.

Of course, not every byte in memory is the start of the legitimate object. It is the program's responsibility to keep track of which values validly refer to typable objects.

<h level=3 label=string>Strings</h>

Strings have a type byte of E0 (for unencoded, C-style strings), E2 (for unencoded strings of Unicode values), or E1 (for compressed strings.) Types E3 to FF are reserved for future expansion of string types.

<h level=4 label=string_plain>Unencoded strings</h>

An unencoded string consists of an E0 byte, followed by all the bytes of the string, followed by a zero byte.

<h level=4 label=string_unicode>Unencoded Unicode strings</h>

An unencoded Unicode string consists of an E2 byte, followed by three padding 0 bytes, followed by the Unicode character values (each one being a four-byte integer). Finally, there is a terminating value (four 0 bytes).

<code>
Unencoded Unicode string
+----------------+
| Type: E2       |  (1 byte)
| Padding: 00    |  (3 bytes)
| Characters.... |  (any length, multiple of 4)
| NUL: 00000000  |  (4 bytes)
+----------------+
</code>

Note that the character data is not encoded in UTF-8, UTF-16, or any other peculiar encoding. It is treated as an array of 32-bit integers (which are, as always in Glulx, stored big-endian). Each integer is a Unicode code point.

<h level=4 label=string_enc>Compressed strings</h>

A compressed string consists of an E1 byte, followed by a block of Huffman-encoded data. This should be read as a stream of bits, starting with the low bit (the 1 bit) of the first byte after the E1, proceeding through the high bit (the 128 bit), and so on with succeeding bytes.

Decoding compressed strings requires looking up data in a Huffman table. The address of this table is normally found in the header. However, the program can select a different decompression table at run-time; see <ref label=opcodes_output>.

The Huffman table is logically a binary tree. Internal nodes are branch points; leaf nodes represent printable entities. To decode a string, begin at the root node. Read one bit from the bit stream, and go to the left or right child depending on its value. Continue reading bits and branching left or right, until you reach a leaf node. Print that entity. Then jump back to the root, and repeat the process. One particular leaf node indicates the end of the string (rather than any printable entity), and when the bit stream leads you to that node, you stop.

<comment>This is a fairly slow process, with VM memory reads and a conditional test for every <em>bit</em> of the string. A terp can speed it up considerably by reading the Huffman table all at once, and caching it as native data structures. A binary tree is the obvious choice, but one can do even better (at the cost of some space) by looking up four-bit chunks at a time in a 16-branching tree.</comment>

<comment>Note that decompression tables are not necessarily in ROM. This is particularly important for tables that are generated and selected at run-time. Furthermore, it is technically legal for a table in RAM to be altered at runtime &emdash; possibly even when it is the currently-selected table. Therefore, an interpreter that caches or preloads this decompression data must be careful. If it caches data from RAM, it must watch for writes to that RAM space, and invalidate its cache upon seeing such a write.</comment>

<h level=4 label=string_table>The String-Decoding Table</h>

The decoding table has the following format:

<code>
+-----------------+
| Table Length    |  (4 bytes)
| Number of Nodes |  (4 bytes)
| Root Node Addr  |  (4 bytes)
| Node Data ....  |  (table length - 12 bytes)
+-----------------+
</code>

The table length is measured in bytes, from the beginning of the table to the end of the last node. The node count includes both branch and leaf nodes. <comment>There will, of course, be an odd number of nodes, and (N+1)/2 of them will be leaves.</comment> The root address indicates which node is the root of the tree; it is not necessarily the first node. This is an absolute address, not an offset from the beginning of the table.

There then follow all the nodes, with no extra data before, between, or after them. They need not be in any particular order. There are several possible types of nodes, distinguished by their first byte.

<code>
Branch (non-leaf node)
+----------------+
| Type: 00       |  (1 byte)
| Left  (0) Node |  (4 bytes)
| Right (1) Node |  (4 bytes)
+----------------+
</code>

The left and right node fields are addresses (again, absolute addresses) of the nodes to go to given a 0 or 1 bit from the bit stream.

<code>
String terminator
+----------------+
| Type: 01       |  (1 byte)
+----------------+
</code>

This ends the string-decoding process.

<code>
Single character
+----------------+
| Type: 02       |  (1 byte)
| Character      |  (1 byte)
+----------------+
</code>

This prints a single character. <comment>The encoding scheme is the business of the I/O system; in Glk, it will be the Latin-1 character set.</comment>

<code>
C-style string
+----------------+
| Type: 03       |  (1 byte)
| Characters.... |  (any length)
| NUL: 00        |  (1 byte)
+----------------+
</code>

This prints an array of characters. Note that the array cannot contain a zero byte, since that is reserved to terminate the array. <comment>A zero byte can be printed using the single-character node type.</comment>

<code>
Single Unicode character
+----------------+
| Type: 04       |  (1 byte)
| Character      |  (4 bytes)
+----------------+
</code>

This prints a single Unicode character. <comment>To be precise, it prints a 32-bit character, which will be interpreted as Unicode if the I/O system is Glk.</comment>

<code>
C-style Unicode string
+----------------+
| Type: 05       |  (1 byte)
| Characters.... |  (any length, multiple of 4)
| NUL: 00000000  |  (4 bytes)
+----------------+
</code>

This prints an array of Unicode characters. Note that the array cannot contain a zero word, since that is reserved to terminate the array. Also note that, unlike an E2-encoded string object, there is no padding.

<comment>If the Glk library is unable to handle Unicode, node types 04 and 05 are still legal. However, characters beyond FF will be printed as 3F ("?").</comment>

<code>
Indirect reference
+----------------+
| Type: 08       |  (1 byte)
| Address        |  (4 bytes)
+----------------+
</code>

This prints a string or calls a function, which is not actually part of the decoding table. The address may refer to a location anywhere in memory (including RAM.) It must be a valid Glulx string (see <ref label=string>) or function (see <ref label=function>). If it is a string, it is printed. If a function, it is called (with no arguments) and the result is discarded.

The management of the stack during an indirect string/function call is a bit tricky. See <ref label=callstring>.

<code>
Double-indirect reference
+----------------+
| Type: 09       |  (1 byte)
| Address        |  (4 bytes)
+----------------+
</code>

This is similar to the indirect-reference node, but the address refers to a four-byte field in memory, and <em>that</em> contains the address of a string or function. The extra layer of indirection can be useful. For example, if the four-byte field is in RAM, its contents can be changed during execution, pointing to a new typable object, without modifying the decoding table itself.

<code>
Indirect reference with arguments
+----------------+
| Type: 0A       |  (1 byte)
| Address        |  (4 bytes)
| Argument Count |  (4 bytes)
| Arguments....  |  (4*N bytes)
+----------------+

Double-indirect reference with arguments
+----------------+
| Type: 0B       |  (1 byte)
| Address        |  (4 bytes)
| Argument Count |  (4 bytes)
| Arguments....  |  (4*N bytes)
+----------------+
</code>

These work the same as the indirect and double-indirect nodes, but if the object found is a function, it will be called with the given argument list. If the object is a string, the arguments are ignored.

<h level=3 label=function>Functions</h>

Functions have a type byte of C0 (for stack-argument functions) or C1 (for local-argument functions). Types C2 to DF are reserved for future expansion of function types.

A Glulx function always takes a list of 32-bit arguments, and returns exactly one 32-bit value. (If you want a function which returns no value, discard or ignore it. Store operand mode zero is convenient.)

If the type is C0, the arguments are passed on the stack, and are made available on the stack. After the function's call frame is constructed, all the argument values are pushed &emdash; last argument pushed first, first argument topmost. Then the number of arguments is pushed on top of that. All locals in the call frame itself are initialized to zero.

If the type is C1, the arguments are passed on the stack, and are written into the locals according to the "format of locals" list of the function. Arguments passed into 8-bit or 16-bit locals are truncated. It is legitimate for there to be too many or too few arguments. Extras are discarded silently; any locals left unfilled are initialized to zero.

A function has the following structure:

<code>
+------------+
|  C0 or C1  |  Type (1 byte)
+------------+
| Format of  |    (2*n bytes)
|     Locals |
+------------+
|  Opcodes   |
|      ....  |
+------------+
</code>

The locals-format list is encoded the same way it is on the stack; see <ref label=callframe>. This is a list of LocalType/LocalCount byte pairs, terminated by a zero/zero pair. (There is, however, no extra padding to reach four-byte alignment.)

Note that although a LocalType/LocalCount pair can only describe up to 255 locals, there is no restriction on how many locals the function can have. It is legitimate to encode several pairs in a row with the same LocalType.

Immediately following the two zero bytes, the instructions start. There is no explicit terminator for the function.

<h level=3>Other Glulx Objects</h>

There are no other Glulx objects at this time, but type 80 to BF are reserved for future expansion. Type 00 is also reserved; it indicates "no object", and should not be used by any typable object. A null reference's type would be considered 00. (Even though byte 00000000 of main memory is not in fact 00.)

<h level=3>User-Defined Objects</h>

Types 01 to 7F are available for use by the compiler, the library, or the program. Glulx will not use them.

<comment>Inform uses 60 for dictionary words, and 70 for objects and classes. It reserves types 40 to 7F. Types 01 to 3F remain available for use by Inform programmers.</comment>

<h level=2 label=floats>Floating-Point Numbers</h>

Glulx values are 32-bit integers, big-endian when stored in memory. To handle floating-point math, we must be able to encode float values as 32-bit values. Unsurprisingly, Glulx uses the big-endian, single-precision IEEE-754 encoding. (See <a href="http://www.psc.edu/general/software/packages/ieee/ieee.php">http://www.psc.edu/general/software/packages/ieee/ieee.php</a>.) This allows floats to be stored in memory, on the stack, in local variables, and in any other place that a 32-bit value appears.

However, float values and integer values are <em>not</em> interchangable. You cannot pass floats to the normal arithmetic opcodes, or vice versa, and expect to get meaningful answers. Always pass floats to the float opcodes and integers to the int opcodes, with the appropriate conversion opcodes to convert back and forth. (See <ref label=opcodes_float>.)

Floats have limited precision; they cannot represent all real values exactly. They can't even represent all integers exactly. (Integers between -1000000 and 1000000 (hex) have exact representations. Beyond that, the rounding error can be greater than 1. But when you get into fractions, errors are possible anywhere: 1/3 cannot be stored exactly.)

Therefore, you must be careful when comparing results. A series of float operations may produce a result fractionally different from what you expect. When comparing float values, you will most often want to use the jfeq opcode, which tests whether two values are <em>near</em> each other (within a specified range).

A float value has three fields in its 32 bits, from highest (the sign bit) to lowest:

<code>
+---------------+
| Sign Bit (S)  |  (1 bit)
| Exponent (E)  |  (8 bits)
| Mantissa (M)  |  (23 bits)
+---------------+
</code>

The interpretation of the value depends on the exponent value:

<list>
<li>If E is FF and M is zero, the value is positive or negative infinity, depending on S. Infinite values represent overflows. (+Inf is 7F800000; -Inf is FF800000.)
<li>If E is FF and M is nonzero, the value is a positive or negative NaN ("not a number"), depending on S. NaN values represent arithmetic failures. (+NaN values are in the range 7F800001 to 7FFFFFFF; -NaN are FF800001 to FFFFFFFF.)
<li>If E is 00 and M is zero, the value is a positive or negative zero, depending on S. Zero values represent underflows, and also, you know, zero. (+0 is 00000000; -0 is 80000000.)
<li>If E is 00 and M is nonzero, the value is a "denormalized" number, very close to zero: plus or minus 2^(-149)*M.
<li>If E is anything else, the value is a "normalized" number: plus or minus 2^(E-150)*(800000+M).
</list>

<comment>I'm using decimal exponents there amid all the hex constants. -149 is hex -95; -150 is hex -96. Sorry about that.</comment>

The numeric formulas may look more familiar if you write them as 2^(-126)*(0.MMMM...) and 2^(E-127)*(1.MMMM...), where "0.MMMM..." is a fraction between zero and one (23 mantissa bits after the binal point) and "1.MMMM...." is a fraction beween one and two.

Some example values:

<list>
<li>0.0   =  00000000 (S=0, E=00, M=0)
<li>1.0   =  3F800000 (S=0, E=7F, M=0)
<li>-2.0  =  C0000000 (S=1, E=80, M=0)
<li>100.0 =  42C80000 (S=0, E=85, M=480000)
<li>pi    =  40490FDB (S=0, E=80, M=490FDB)
<li>2*pi  =  40C90FDB (S=0, E=81, M=490FDB)
<li>e     =  402DF854 (S=0, E=80, M=2DF854)
</list>

To give you an idea of the behavior of the special values:

<list>
<li>1 / 0    =  +Inf
<li>-1 / 0   =  -Inf
<li>1 / Inf  =  0
<li>1 / -Inf =  -0
<li>0 / 0    =  NaN
<li>2 * 0    =  0
<li>2 * -0   =  -0
<li>+Inf * 0 =  NaN
<li>+Inf * 1 =  +Inf
<li>+Inf + +Inf =  +Inf
<li>+Inf * +Inf =  +Inf
<li>+Inf - +Inf =  NaN
<li>+Inf / +Inf =  NaN
</list>

NaN is sticky; almost <em>any</em> mathematical operation involving a NaN produces NaN. (There are a few exceptions.)

However, Glulx does not guarantee <em>which</em> NaN value you will get from such operations. The underlying platform may try to encode information about what operation failed in the mantissa field of the NaN. Or, contrariwise, it may return the same value for every NaN. The sign bit, similarly, is never guaranteed. (The sign may be preserved if that's meaningful for the failed operation, but it may not be.) You should not test for NaN by comparing to a fixed encoded value; instead, use the jisnan opcode.

<h level=2 label=saveformat>The Save-Game Format</h>

(Or, if you like, "serializing the machine state".)

This is a variant of Quetzal, the standard Z-machine save file format. (See <a href="http://ifarchive.org/if-archive/infocom/interpreters/specification/savefile_14.txt">http://ifarchive.org/if-archive/infocom/interpreters/specification/savefile_14.txt</a>.)

Everything in the Quetzal specification applies, with the following exceptions:

<h level=3>Contents of Dynamic Memory</h>

In both compressed and uncompressed form, the memory chunk ('CMem' or 'UMem') starts with a four-byte value, which is the current size of memory. The memory data then follows. During a restore, the size of memory is changed to this position.

The memory area to be saved does not start at address zero, but at RAMSTART. It continues to the current end of memory (which may not be the ENDMEM value in the header.) When generating or reading compressed data ('CMem' chunk), the data above EXTSTART is handled as if the game file were extended with as many zeroes as necessary.

<h level=3>Contents of the Stack</h>

Before the stack is written out, a four-value call stub is pushed on &emdash; result destination, PC, and FramePtr. (See <ref label=callstub>.) Then the entire stack can be written out, with all of its values (of whatever size) transformed to big-endian. (Padding is not skipped; it's written out as the appropriate number of zero bytes.)

When the game-state is loaded back in &emdash; or, for that matter, when continuing after a game-save &emdash; the four values are read back off the stack, a result code for the operation is stored in the appropriate destination, and execution continues.

<comment>Remember that in a call stub, the PC contains the address of the instruction <em>after</em> the one being executed.</comment>

<h level=3>Memory Allocation Heap</h>

If the heap is active (see <ref label=opcodes_malloc>), an allocation heap chunk is written ('MAll'). This chunk contains two four-byte values, plus two more for each extant memory block:

<list>
<li>Heap start address
<li>Number of extant blocks
<li>Address of first block
<li>Length of first block
<li>Address of second block
<li>Length of second block
<li>...
</list>

The blocks need not be listed in any particular order.

If the heap is not active, the 'MAll' chunk can contain 0,0 or it may be omitted.

<h level=3>Associated Story File</h>

The contents of the game-file identifier ('IFhd' chunk) are simply the first 128 bytes of memory. This is within ROM (since RAMSTART is at least 256), so it does not vary during play. It includes the story file length and checksum, as well as any compiler-specific information that may be stored immediately after the header.

<h level=3>State Not Saved</h>

Some aspects of Glulx execution are not part of the save process, and therefore are not changed during a restart, restore, or restoreundo operation. The program is responsible for checking these values after a restore to see if they have (from the program's point of view) changed unexpectedly.

Examples of information which is not saved:

<list>
<li>Glk library state. This includes Glk opaque objects (windows, filerefs, streams). It also includes I/O state such as the current output stream, contents of windows, and cursor positions. Accounting for Glk object changes after restore/restoreundo is tricky, but absolutely necessary.
<li>The protected-memory range (position, length, and whether it exists at all). Note that the <em>contents</em> of the range (if it exists) are not treated specially during saving, and are therefore saved normally.
<li>The random number generator's internal state.
<li>The I/O system mode and current string-decoding table address.
</list>

<h level=1>Dictionary of Opcodes</h>

Opcodes are written here in the format:

<deffun>
opname L1 L2 S1
</deffun>

...where "L1" and "L2" are operands using the load addressing modes, and "S1" is an operand using the store addressing modes. (See <ref label=instruction>.)

The table of opcodes:

<list>
<li>0x00: nop
<li>0x10: add
<li>0x11: sub
<li>0x12: mul
<li>0x13: div
<li>0x14: mod
<li>0x15: neg
<li>0x18: bitand
<li>0x19: bitor
<li>0x1A: bitxor
<li>0x1B: bitnot
<li>0x1C: shiftl
<li>0x1D: sshiftr
<li>0x1E: ushiftr
<li>0x20: jump
<li>0x22: jz
<li>0x23: jnz
<li>0x24: jeq
<li>0x25: jne
<li>0x26: jlt
<li>0x27: jge
<li>0x28: jgt
<li>0x29: jle
<li>0x2A: jltu
<li>0x2B: jgeu
<li>0x2C: jgtu
<li>0x2D: jleu
<li>0x30: call
<li>0x31: return
<li>0x32: catch
<li>0x33: throw
<li>0x34: tailcall
<li>0x40: copy
<li>0x41: copys
<li>0x42: copyb
<li>0x44: sexs
<li>0x45: sexb
<li>0x48: aload
<li>0x49: aloads
<li>0x4A: aloadb
<li>0x4B: aloadbit
<li>0x4C: astore
<li>0x4D: astores
<li>0x4E: astoreb
<li>0x4F: astorebit
<li>0x50: stkcount
<li>0x51: stkpeek
<li>0x52: stkswap
<li>0x53: stkroll
<li>0x54: stkcopy
<li>0x70: streamchar
<li>0x71: streamnum
<li>0x72: streamstr
<li>0x73: streamunichar
<li>0x100: gestalt
<li>0x101: debugtrap
<li>0x102: getmemsize
<li>0x103: setmemsize
<li>0x104: jumpabs
<li>0x110: random
<li>0x111: setrandom
<li>0x120: quit
<li>0x121: verify
<li>0x122: restart
<li>0x123: save
<li>0x124: restore
<li>0x125: saveundo
<li>0x126: restoreundo
<li>0x127: protect
<li>0x130: glk
<li>0x140: getstringtbl
<li>0x141: setstringtbl
<li>0x148: getiosys
<li>0x149: setiosys
<li>0x150: linearsearch
<li>0x151: binarysearch
<li>0x152: linkedsearch
<li>0x160: callf
<li>0x161: callfi
<li>0x162: callfii
<li>0x163: callfiii
<li>0x170: mzero
<li>0x171: mcopy
<li>0x178: malloc
<li>0x179: mfree
<li>0x180: accelfunc
<li>0x181: accelparam
<li>0x190: numtof
<li>0x191: ftonumz
<li>0x192: ftonumn
<li>0x198: ceil
<li>0x199: floor
<li>0x1A0: fadd
<li>0x1A1: fsub
<li>0x1A2: fmul
<li>0x1A3: fdiv
<li>0x1A4: fmod
<li>0x1A8: sqrt
<li>0x1A9: exp
<li>0x1AA: log
<li>0x1AB: pow
<li>0x1B0: sin
<li>0x1B1: cos
<li>0x1B2: tan
<li>0x1B3: asin
<li>0x1B4: acos
<li>0x1B5: atan
<li>0x1B6: atan2
<li>0x1C0: jfeq
<li>0x1C1: jfne
<li>0x1C2: jflt
<li>0x1C3: jfle
<li>0x1C4: jfgt
<li>0x1C5: jfge
<li>0x1C8: jisnan
<li>0x1C9: jisinf
</list>

Opcodes 0x1000 to 0x10FF are reserved for use by FyreVM, and are not documented here. See <ref label=otherif>.

<h level=2>Integer Math</h>

<deffun>
add L1 L2 S1
</deffun>

Add L1 and L2, using standard 32-bit addition. Truncate the result to 32 bits if necessary. Store the result in S1.

<deffun>
sub L1 L2 S1
</deffun>

Compute (L1 - L2), and store the result in S1.

<deffun>
mul L1 L2 S1
</deffun>

Compute (L1 * L2), and store the result in S1. Truncate the result to 32 bits if necessary.

<deffun>
div L1 L2 S1
</deffun>

Compute (L1 / L2), and store the result in S1. This is signed integer division.

<deffun>
mod L1 L2 S1
</deffun>

Compute (L1 % L2), and store the result in S1. This is the remainder from signed integer division.

In division and remainer, signs are annoying. Rounding is towards zero. The sign of a remainder equals the sign of the dividend. It is always true that (A / B) * B + (A % B) == A. Some examples (in decimal):

<code>
 11 /  2 =  5
-11 /  2 = -5
 11 / -2 = -5
-11 / -2 =  5
 13 %  5 =  3
-13 %  5 = -3
 13 % -5 =  3
-13 % -5 = -3
</code>

<deffun>
neg L1 S1
</deffun>

Compute the negative of L1.

<deffun>
bitand L1 L2 S1
</deffun>

Compute the bitwise AND of L1 and L2.

<deffun>
bitor L1 L2 S1
</deffun>

Compute the bitwise OR of L1 and L2.

<deffun>
bitxor L1 L2 S1
</deffun>

Compute the bitwise XOR of L1 and L2.

<deffun>
bitnot L1 S1
</deffun>

Compute the bitwise negation of L1.

<deffun>
shiftl L1 L2 S1
</deffun>

Shift the bits of L1 to the left (towards more significant bits) by L2 places. The bottom L2 bits are filled in with zeroes. If L2 is 32 or more, the result is always zero.

<deffun>
ushiftr L1 L2 S1
</deffun>

Shift the bits of L1 to the right by L2 places. The top L2 bits are filled in with zeroes. If L2 is 32 or more, the result is always zero.

<deffun>
sshiftr L1 L2 S1
</deffun>

Shift the bits of L1 to the right by L2 places. The top L2 bits are filled in with copies of the top bit of L1. If L2 is 32 or more, the result is always zero or FFFFFFFF, depending on the top bit of L1.

Notes on the shift opcodes: If L2 is zero, the result is always equal to L1. L2 is considered unsigned, so 80000000 or greater is "more than 32".

<h level=2 label=opcodes_branch>Branches</h>

All branches (except jumpabs) specify their destinations with an offset value. The actual destination address of the branch is computed as (Addr + Offset - 2), where Addr is the address of the instruction <em>after</em> the branch opcode, and offset is the branch's operand. The special offset values 0 and 1 are interpreted as "return 0" and "return 1" respectively. <comment>This odd hiccup is inherited from the Z-machine. Inform uses it heavily for code optimization.</comment>

It is legal to branch to code that is in another function. <comment>Indeed, there is no well-defined notion of where a function ends.</comment> However, this does not affect the current stack frame; that remains set up according to the same function call as before the branch. Similarly, it is legal to branch to code which is not associated with any function &emdash; e.g., code compiled on the fly in RAM.

<deffun>
jump L1
</deffun>

Branch unconditionally to offset L1.

<deffun>
jz L1 L2
</deffun>

If L1 is equal to zero, branch to L2.

<deffun>
jnz L1 L2
</deffun>

If L1 is not equal to zero, branch to L2.

<deffun>
jeq L1 L2 L3
</deffun>

If L1 is equal to L2, branch to L3.

<deffun>
jne L1 L2 L3
</deffun>

If L1 is not equal to L2, branch to L3.

<deffun>
jlt L1 L2 L3
jle L1 L2 L3
jgt L1 L2 L3
jge L1 L2 L3
</deffun>

Branch is L1 is less than, less than or equal to, greater than, greater than or equal to L2. The values are compared as signed 32-bit values.

<deffun>
jltu L1 L2 L3
jleu L1 L2 L3
jgtu L1 L2 L3
jgeu L1 L2 L3
</deffun>

The same, except that the values are compared as unsigned 32-bit values.

<comment>Since the address space can span the full 32-bit range, it is wiser to compare addresses with the unsigned comparison operators.</comment>

<deffun>
jumpabs L1
</deffun>

Branch unconditionally to address L1. Unlike the other branch opcodes, this takes an absolute address, not an offset. The special cases 0 and 1 (for returning) do not apply; jumpabs 0 would branch to memory address 0, if that were ever a good idea, which it isn't.

<h level=2>Moving Data</h>

<deffun>
copy L1 S1
</deffun>

Read L1 and store it at S1, without change.

<deffun>
copys L1 S1
</deffun>

Read a 16-bit value from L1 and store it at S1.

<deffun>
copyb L1 S1
</deffun>

Read an 8-bit value from L1 and store it at S1.

Since copys and copyb can access chunks smaller than the usual four bytes, they require some comment. When reading from main memory or the call-frame locals, they access two or one bytes, instead of four. However, when popping or pushing values on the stack, these opcodes pull or push a full 32-bit value.

Therefore, if copyb (for example) copies a byte from main memory to the stack, a 32-bit value will be pushed, whose value will be from 0 to 255. Sign-extension <em>does not</em> occur. Conversely, if copyb copies a byte from the stack to memory, a 32-bit value is popped, and the bottom 8 bits are written at the given address. The upper 24 bits are lost. Constant values are truncated as well.

If copys or copyb are used with both L1 and S1 in pop/push mode, the 32-bit value is popped, truncated, and pushed.

<comment>NOTE: Since a call frame has no specified endianness, it is unwise to use these opcodes to pull out one or two bytes from a four-byte local variable. The result will be implementation-dependent. Therefore, use of the copyb and copys opcodes with a local-variable operand of different size is deprecated. Since locals of less than four bytes are <em>also</em> deprecated, you should not use copyb or copys with local-variable operands at all.</comment>

<deffun>
sexs L1 S1
</deffun>

Sign-extend a value, considered as a 16-bit value. If the value's 8000 bit is set, the upper 16 bits are all set; otherwise, the upper 16 bits are all cleared.

<deffun>
sexb L1 S1
</deffun>

Sign-extend a value, considered as an 8-bit value. If the value's 80 bit is set, the upper 24 bits are all set; otherwise, the upper 24 bits are all cleared.

Note that these opcodes, like most, work on 32-bit values. Although (for example) sexb is commonly used in conjunction with copyb, it does not share copyb's behavior of reading a single byte from memory or the locals.

Also note that the upper bits, 16 or 24 of them, are entirely ignored and overwritten with ones or zeroes.

<h level=2>Array Data</h>

<deffun>
astore L1 L2 L3
</deffun>

Store L3 into the 32-bit field at main memory address (L1+4*L2).

<deffun>
aload L1 L2 S1
</deffun>

Load a 32-bit value from main memory address (L1+4*L2), and store it in S1.

<deffun>
astores L1 L2 L3
</deffun>

Store L3 into the 16-bit field at main memory address (L1+2*L2).

<deffun>
aloads L1 L2 S1
</deffun>

Load an 16-bit value from main memory address (L1+2*L2), and store it in S1.

<deffun>
astoreb L1 L2 L3
</deffun>

Store L3 into the 8-bit field at main memory address (L1+L2).

<deffun>
aloadb L1 L2 S1
</deffun>

Load an 8-bit value from main memory address (L1+L2), and store it in S1.

Note that these opcodes cannot access call-frame locals, or the stack. (Not with the L1 and L2 opcodes, that is.) L1 and L2 provide a main-memory address. Be not confused by the fact that L1 and L2 can be any addressing mode, including call-frame or stack-pop modes. That controls where the values come from which are used to <em>compute</em> the main-memory address.

The other end of the transfer (S1 or L3) is always a 32-bit value. The "store" opcodes truncate L3 to 8 or 16 bits if necessary. The "load" opcodes expand 8-bit or 16-bit values <em>without</em> sign extension. (If signed values are appropriate, you can follow aloads/aloadb with sexs/sexb.)

L2 is considered signed, so you can access addresses before L1 as well as after.

<deffun>
astorebit L1 L2 L3
</deffun>

Set or clear a single bit. This is bit number (L2 mod 8) of memory address (L1+L2/8). It is cleared if L3 is zero, set if nonzero.

<deffun>
aloadbit L1 L2 S1
</deffun>

Test a single bit, similarly. If it is set, 1 is stored at S1; if clear, 0 is stored.

For these two opcodes, bits are effectively numbered sequentially, starting with the least significant bit of address L1. L2 is considered signed, so this numbering extends both positively and negatively. For example:

<code>
astorebit  1002  0  1:  Set bit 0 of address 1002. (The 1's place.)
astorebit  1002  7  1:  Set bit 7 of address 1002. (The 128's place.)
astorebit  1002  8  1:  Set bit 0 of address 1003.
astorebit  1002  9  1:  Set bit 1 of address 1003.
astorebit  1002 -1  1:  Set bit 7 of address 1001.
astorebit  1002 -3  1:  Set bit 5 of address 1001.
astorebit  1002 -8  1:  Set bit 0 of address 1001.
astorebit  1002 -9  1:  Set bit 7 of address 1000.
</code>

Like the other aload and astore opcodes, these opcodes cannot access call-frame locals, or the stack.

<h level=2>The Stack</h>

<deffun>
stkcount S1
</deffun>

Store a count of the number of values on the stack. This counts only values above the current call-frame. In other words, it is always zero when a C1 function starts executing, and (numargs+1) when a C0 function starts executing. It then increases and decreases thereafter as values are pushed and popped; it is always the number of values that can be popped legally. (If S1 uses the stack push mode, the count is done before the result is pushed.)

<deffun>
stkpeek L1 S1
</deffun>

Peek at the L1'th value on the stack, without actually popping anything. If L1 is zero, this is the top value; if one, it's the value below that; etc. L1 must be less than the current stack-count. (If L1 or S1 use the stack pop/push modes, the peek is counted after L1 is popped, but before the result is pushed.)

<deffun>
stkswap
</deffun>

Swap the top two values on the stack. The current stack-count must be at least two.

<deffun>
stkcopy L1
</deffun>

Peek at the top L1 values in the stack, and push duplicates onto the stack in the same order. If L1 is zero, nothing happens. L1 must not be greater than the current stack-count. (If L1 uses the stack pop mode, the stkcopy is counted after L1 is popped.)

An example of stkcopy, starting with six values on the stack:

<code>
5 4 3 2 1 0 &lt;top&gt;
stkcopy 3
5 4 3 2 1 0 2 1 0 &lt;top&gt;
</code>

<deffun>
stkroll L1 L2
</deffun>

Rotate the top L1 values on the stack. They are rotated up or down L2 places, with positive values meaning up and negative meaning down. The current stack-count must be at least L1. If either L1 or L2 is zero, nothing happens. (If L1 and/or L2 use the stack pop mode, the roll occurs after they are popped.)

An example of two stkrolls, starting with nine values on the stack:

<code>
8 7 6 5 4 3 2 1 0 &lt;top&gt;
stkroll 5 1
8 7 6 5 0 4 3 2 1 &lt;top&gt;
stkroll 9 -3
5 0 4 3 2 1 8 7 6 &lt;top&gt;
</code>

Note that stkswap is equivalent to stkroll 2 1, or for that matter stkroll 2 -1. Also, stkcopy 1 is equivalent to stkpeek 0 sp.

These opcodes can only access the values pushed on the stack above the current call-frame. It is illegal to stkswap, stkpeek, stkcopy, or stkroll values below that &emdash; i.e, the locals segment or any previous function call frames.

<h level=2>Functions</h>

<deffun>
call L1 L2 S1
</deffun>

Call function whose address is L1, passing in L2 arguments, and store the return result at S1.

The arguments are taken from the stack. Before you execute the call opcode, you must push the arguments on, in backward order (last argument pushed first, first argument topmost on the stack.) The L2 arguments are removed before the new function's call frame is constructed. (If L1, L2, or S1 use the stack pop/push modes, the arguments are taken after L1 or L2 is popped, but before the result is pushed.)

Recall that all functions in Glulx have a single 32-bit return value. If you do not care about the return value, you can use operand mode 0 ("discard value") for operand S1.

<deffun>
callf L1 S1
callfi L1 L2 S1
callfii L1 L2 L3 S1
callfiii L1 L2 L3 L4 S1
</deffun>

Call function whose address is L1, passing zero, one, two, or three arguments. Store the return result at S1.

These opcodes behave the same as call, except that the arguments are given in the usual opcode format instead of being found on the stack. (If L2, L3, etc. all use the stack pop mode, then the behavior is exactly the same as call.)

<deffun>
return L1
</deffun>

Return from the current function, with the given return value. If this is the top-level function, Glulx execution is over.

Note that all the branch opcodes (jump, jz, jeq, and so on) have an option to return 0 or 1 instead of branching. These behave exactly as if the return opcode had been executed.

<deffun>
tailcall L1 L2
</deffun>

Call function whose address is L1, passing in L2 arguments, and pass the return result out to whoever called the current function.

This destroys the current call-frame, as if a return had been executed, but does not touch the call stub below that. It then immediately calls L1, creating a new call-frame. The effect is the same as a call immediately followed by a return, but takes less stack space.

It is legal to use tailcall from the top-level function. L1 becomes the top-level function.

<comment>This opcode can be used to implement tail recursion, without forcing the stack to grow with every call.</comment>

<h level=2>Continuations</h>

<deffun>
catch S1 L1
</deffun>

Generates a "catch token", which can be used to jump back to this execution point from a throw opcode. The token is stored in S1, and then execution branches to offset L1. If execution is proceeding from this point because of a throw, the thrown value is stored instead, and the branch is ignored.

Remember if the branch value is not 0 or 1, the branch is to to (Addr + L1 - 2), where Addr is the address of the instruction <em>after</em> the catch. If the value <em>is</em> 0 or 1, the function returns immediately, invalidating the catch token.

If S1 or L1 uses the stack push/pop modes, note that the precise order of execution is: evaluate L1 (popping if appropriate); generate a call stub and compute the token; store S1 (pushing if appropriate).

<deffun>
throw L1 L2
</deffun>

Jump back to a previously-executed catch opcode, and store the value L1. L2 must be a valid catch token.

The exact catch/throw procedure is as follows:

When catch is executed, a four-value call stub is pushed on the stack &emdash; result destination, PC, and FramePtr. (See <ref label=callstub>. The PC is the address of the next instruction after the catch.) The catch token is the value of the stack pointer after these are pushed. The token value is stored in the result destination, and execution proceeds, branching to L1.

When throw is executed, the stack is popped down until the stack pointer equals the given token. Then the four values are read back off the stack, the thrown value is stored in the destination, and execution proceeds with the instruction after the catch.

If the call stub (or any part of it) is removed from the stack, the catch token becomes invalid, and must not be used. This will certainly occur when you return from the function containing the catch opcode. It will also occur if you pop too many values from the stack after executing the catch. (You may wish to do this to "cancel" the catch; if you pop and discard those four values, the token is invalidated, and it is as if you had never executed the catch at all.) The catch token is also invalidated if any part of the call stub is overwritten (e.g. with stkswap or stkroll).

<comment>Why is the catch branch taken at catch time, and ignored after a throw? Because it's easier to write the interpreter that way, that's why. If it had to branch after a throw, either the call stub would have to contain the branch offset, or the terp would have to re-parse the catch instruction. Both are ugly.</comment>

<h level=2 label=opcodes_memory>Memory Map</h>

<deffun>
getmemsize S1
</deffun>

Store the current size of the memory map. This is originally the ENDMEM value from the header, but you can change it with the setmemsize opcode. (The malloc and mfree opcodes may also cause this value to change; see <ref label=opcodes_malloc>.) It will always be greater than or equal to ENDMEM, and will always be a multiple of 256.

<deffun>
setmemsize L1 S1
</deffun>

Set the current size of the memory map. The new value must be a multiple of 256, like all memory boundaries in Glulx. It must be greater than or equal to ENDMEM (the initial memory-size value which is stored in the header.) It does not have to be greater than the previous memory size. The memory size may grow and shrink over time, as long as it never gets smaller than the initial size.

When the memory size grows, the new space is filled with zeroes. When it shrinks, the contents of the old space are lost.

If the allocation heap is active (see <ref label=opcodes_malloc>) you may not use setmemsize -- the memory map is under the control of the heap system. If you free all heap objects, the heap will then no longer be active, and you can use setmemsize.

Since memory allocation is never guaranteed, you must be prepared for the possibility that setmemsize will fail. The opcode stores the value zero if it succeeded, and 1 if it failed. If it failed, the memory size is unchanged.

Some interpreters do not have the capability to resize memory at all. On such interpreters, setmemsize will <em>always</em> fail. You can check this in advance with the ResizeMem gestalt selector.

Note that the memory size is considered part of the game state. If you restore a saved game, the current memory size is changed to the size that was in effect when the game was saved. If you restart, the current memory size is reset to its initial value.

<h level=2 label=opcodes_malloc>Memory Allocation Heap</h>

Manage the memory allocation heap.

Glulx is able to maintain a list of dynamically-allocated memory objects. These objects exist in the memory map, above ENDMEM. The malloc and mfree opcodes allow the game to request the allocation and destruction of these objects.

Some interpreters do not have the capability to manage an allocation heap. On such interpreters, malloc will always fail. You can check this in advance with the MAlloc gestalt selector.

When you first allocate a block of memory, the heap becomes active. The current end of memory -- that is, the current getmemsize value -- becomes the beginning address of the heap. The memory map is then extended to accomodate the memory block.

Subsequent memory allocations and deallocations are done within the heap. The interpreter may extend or reduce the memory map, as needed, when allocations and deallocations occur. While the heap is active, you may not manually resize the memory map with setmemsize; the heap system is responsible for doing that.

When you free the last extant memory block, the heap becomes inactive. The interpreter will reduce the memory map size down to the heap-start address. (That is, the getmemsize value returns to what it was before you allocated the first block.) Thereafter, it is legal to call setmemsize again.

It is legitimate to read or write any memory address in the heap range (from ENDMEM to the end of the memory map). You are not restricted to extant blocks. <comment>The VM's heap state is not stored in its own memory map. So, unlike the familiar C heap, you cannot damage it by writing outside valid blocks.</comment>

The heap state (whether it is active, its starting address, and the addresses and sizes of all extant blocks) <em>is</em> part of the saved game state.

These opcodes were added in Glulx version 3.1.

<deffun>
malloc L1 S1
</deffun>

Allocate a memory block of L1 bytes. (L1 must be positive.) This stores the address of the new memory block, which will be within the heap and will not overlap any other extant block. The interpreter may have to extend the memory map (see <ref label=opcodes_memory>) to accomodate the new block.

This operation does not change the contents of the memory block (or, indeed, the contents of the memory map at all). If you want the memory block to be initialized, you must do it yourself.

If the allocation fails, this stores zero.

<deffun>
mfree L1
</deffun>

Free the memory block at address L1. This <em>must</em> be the address of an extant block -- that is, a value returned by malloc and not previously freed.

This operation does not change the contents of the memory block (or, indeed, the contents of the memory map at all).

<h level=2>Game State</h>

<deffun>
quit
</deffun>

Shut down the terp and exit. This is equivalent to returning from the top-level function, or for that matter calling glk_exit().

Note that (in the Glk I/O system) Glk is responsible for any "hit any key to exit" prompt. It is safe for you to print a bunch of final text and then exit immediately.

<deffun>
restart
</deffun>

Restore the VM to its initial state (memory, stack, and registers). Note that the current memory size is reset, as well as the contents of memory.

<deffun>
save L1 S1
</deffun>

Save the VM state to the output stream L1. It is your responsibility to prompt the player for a filespec, open the stream, and then destroy these objects afterward. S1 is set to zero if the operation succeeded, 1 if it failed, and -1 if the VM has just been restored and is continuing from this instruction.

(In the Glk I/O system, L1 should be the ID of a writable Glk stream. In other I/O systems, it will mean something different. In the "filter" and "null" I/O systems, the save opcode is illegal, as the interpreter has nowhere to write the state.)

<deffun>
restore L1 S1
</deffun>

Restore the VM state from the input stream L1. S1 is set to 1 if the operation failed. If it succeeded, of course, this instruction never returns a value.

<deffun>
saveundo S1
</deffun>

Save the VM state in a temporary location. The terp will choose a location appropriate for rapid access, so this may be called once per turn. S1 is set to zero if the operation succeeded, 1 if it failed, and -1 if the VM state has just been restored.

<deffun>
restoreundo S1
</deffun>

Restore the VM state from temporary storage. S1 is set to 1 if the operation failed.

<deffun>
protect L1 L2
</deffun>

Protect a range of memory from restart, restore, restoreundo. The protected range starts at address L1 and has a length of L2 bytes. This memory is silently unaffected by the state-restoring operations. (However, if the result-storage S1 is directed into the protected range, that is not blocked.)

When the VM starts up, there is no protection range. Only one range can be protected at a time. Calling protect cancels any previous range. To turn off protection, call protect with L1 and L2 set to zero.

It is important to note that the protection range itself (its existence, location, and length) is <em>not</em> part of the saved game state! If you save a game, move the protection range to a new location, and then restore that game, it is the new range that will be protected, and the range will remain there afterwards.

<deffun>
verify S1
</deffun>

Perform sanity checks on the game file, using its length and checksum. S1 is set to zero if everything looks good, 1 if there seems to be a problem. (Many interpreters will do this automatically, before the game starts executing. This opcode is provided mostly for slower interpreters, where auto-verify might cause an unacceptable delay.)

Notes:

All the save and restore opcodes can generate diagnostic information on the current output stream.

A terp may support several levels of temporary storage. You should not make any assumptions about how many times restoreundo can be called. If the player so requests, you should keep calling it until it fails.

Glk opaque objects (windows, streams, filespecs) are not part of the saved game state. Therefore, when you restore a game, all the object IDs you have in Glulx memory must be considered invalid. (This includes both IDs in main memory and on the stack.) You must use the Glk iteration calls to go through all the opaque objects in existence, and recognize them by their rocks.

The same applies after restoreundo, to a lesser extent. Since saveundo/restoreundo only operate within a single play session, you can rely on the IDs of objects created before the first saveundo. However, if you have created any objects since then, you must iterate and recognize them.

The restart opcode is a similar case. You must do an iteration as soon as your program starts, to find objects created in an earlier incarnation. Alternatively, you can be careful to close all opaque objects before invoking restart.

<comment>Another approach is to use the protect opcode, to preserve global variables containing your object IDs. This will work within a play session &emdash; that is, with saveundo, restoreundo, and restart. You must still deal with save and restore.</comment>

<h level=2 label=opcodes_output>Output</h>

<deffun>
getiosys S1 S2
</deffun>

Return the current I/O system mode and rock.

Due to a long-standing bug in the reference interpreter, the two store operands must be of the same general type: both main-memory/global stores, both local variable stores, or both stack pushes.

<deffun>
setiosys L1 L2
</deffun>

Set the I/O system mode and rock. If the system L1 is not supported by the interpreter, it will default to the "null" system (0).

These systems are currently defined:

<list>
<li>0: The null system. All output is discarded. (When the Glulx machine starts up, this is the current system.)
<li>1: The filtering system. The rock (L2) value should be the address of a Glulx function. This function will be called for every character output (with the character value as its sole argument). The function's return value is ignored.
<li>2: The Glk system. All output will be handled through Glk function calls, sent to the current Glk stream.
<li>20: The FyreVM channel system. See <ref label=otherif>.
</list>

It is important to recall that when Glulx starts up, the Glk I/O system is <em>not</em> set. And when Glk starts up, there are no windows and no current output stream. To make anything appear to the user, you must first do three things: select the Glk I/O system, open a Glk window, and set its stream as the current one. (It is illegal in Glk to send output when there is no stream set. Sending output to Glulx's "null" I/O system is legal, but pointless.)

<deffun>
streamchar L1
</deffun>

Send L1 to the current stream. This sends a single character; the value L1 is truncated to eight bits.

<deffun>
streamunichar L1
</deffun>

Send L1 to the current stream. This sends a single (32-bit) character.

This opcode was added in Glulx version 3.0.

<deffun>
streamnum L1
</deffun>

Send L1 to the current stream, represented as a signed decimal number in ASCII.

<deffun>
streamstr L1
</deffun>

Send a string object to the current stream. L1 must be the address of a Glulx string object (type E0, E1, or E2.) The string is decoded and sent as a sequence of characters.

When the Glk I/O system is set, these opcodes are implemented using the Glk API. You can bypass them and directly call glk_put_char(), glk_put_buffer(), and so on. Remember, however, that glk_put_string() only accepts unencoded string (E0) objects; glk_put_string_uni() only accepts unencoded Unicode (E2) objects.

Note that it is illegal to decode a compressed string (E1) if there is no string-decoding table set.

<deffun>
getstringtbl S1
</deffun>

Return the address the terp is currently using for its string-decoding table. If there is no table, set, this returns zero.

<deffun>
setstringtbl L1
</deffun>

Change the address the terp is using for its string-decoding table. This may be zero, indicating that there is no table (in which case it is illegal to print any compressed string). Otherwise, it must be the address of a <em>valid</em> string-decoding table.

<comment>This does not change the value in the header field at address 001C. The header is in ROM, and never changes. To determine the current table address, use the getstringtbl opcode.</comment>

A string-decoding table may be in RAM or ROM, but there may be speed penalties if it is in RAM. See <ref label=string_table>.

<h level=2 label=opcodes_float>Floating-Point Math</h>

Recall that floating-point values are encoded as single-precision (32-bit) IEEE-754 values (see <ref label=floats>). The interpreter must convert values (from memory or the stack) before performing a floating-point operation, and unconvert them afterwards.

<comment>In other words, passing a float value to an integer arithmetic opcode will operate on the IEEE-754-encoded 32-bit value. Such an operation would be deterministic, albeit mathematically meaningless. The same is true for passing an integer to a float opcode.</comment>

If any argument to a float operation is a NaN ("not a number") value, the result will be a NaN value. (Except for the pow opcode, which has some special cases.)

These opcodes were added in Glulx version 3.1.2. However, not all interpreters may support them. You can test for their availability with the Float gestalt selector.

<deffun>
numtof L1 S1
</deffun>

Convert an integer value to the closest equivalent float. (That is, if L1 is 1, then 3F800000 -- the float encoding of 1.0 -- will be stored in S1.) Integer zero is converted to (positive) float zero.

If the value is less than -1000000 or greater than 1000000 (hex), the conversion may not be exact. (More specifically, it may round to a nearby multiple of a power of 2.)

<deffun>
ftonumz L1 S1
</deffun>

Convert a float value to an integer, rounding towards zero (i.e., truncating the fractional part). If the value is outside the 32-bit integer range, or is NaN or infinity, the result will be 7FFFFFFF (for positive values) or 80000000 (for negative values).

<deffun>
ftonumn L1 S1
</deffun>

Convert a float value to an integer, rounding towards the nearest integer. Again, overflows become 7FFFFFFF or 80000000.

<deffun>
fadd L1 L2 S1
fsub L1 L2 S1
fmul L1 L2 S1
fdiv L1 L2 S1
</deffun>

Perform floating-point arithmetic. Overflows produce infinite values (with the appropriate sign); underflows produce zero values (ditto). 0/0 is NaN. Inf/Inf, or Inf-Inf, is NaN. Any finite number added to infinity is infinity. Any nonzero number divided by an infinity, or multiplied by zero, is a zero. Any nonzero number multiplied by an infinity, or divided by zero, is an infinity.

<deffun>
fmod L1 L2 S1 S2
</deffun>

Perform a floating-point modulo operation. S1 is the remainder; S2 is the quotient. Both results have the sign of L1; the sign of L2 is ignored.

If L2 is 1, this gives you the fractional and integer parts of L1. If L1 is zero, both results are zero. If L2 is infinite, S1 is L1 and S2 is zero. If L1 is infinite or L2 is zero, both results are NaN.

<deffun>
ceil L1 S1
floor L1 S1
</deffun>

Round L1 up (towards +Inf) or down (towards -Inf) to the nearest integral value. (The result is still in float format, however.) These opcodes are idempotent.

Rounding -0 up or down gives -0. Rounding an infinite value gives infinity.

<deffun>
sqrt L1 S1
exp L1 S1
log L1 S1
</deffun>

Compute the square root of L1, e^L1, and log of L1 (base e).

sqrt(-0) is -0. sqrt returns NaN for all other negative values. exp(+0) and exp(-0) are 1; exp(-Inf) is +0. log(+0) and log(-0) are -Inf. log returns NaN for all other negative values.

<deffun>
pow L1 L2 S1
</deffun>

Compute L1 raised to the L2 power.

The special cases are breathtaking. The following is quoted (almost) directly from the libc man page:

<list>
<li>pow(&plusminus;0, y) returns &plusminus;Inf for y an odd integer &lt; 0.
<li>pow(&plusminus;0, y) returns +Inf for y &lt; 0 and not an odd integer.
<li>pow(&plusminus;0, y) returns &plusminus;0 for y an odd integer &gt; 0.
<li>pow(&plusminus;0, y) returns +0 for y &gt; 0 and not an odd integer.
<li>pow(-1, &plusminus;Inf) returns 1.
<li>pow(1, y) returns 1 for any y, even a NaN.
<li>pow(x, &plusminus;0) returns 1 for any x, even a NaN.
<li>pow(x, y) returns a NaN for finite x &lt; 0 and finite non-integer y.
<li>pow(x, -Inf) returns +Inf for |x| &lt; 1.
<li>pow(x, -Inf) returns +0 for |x| &gt; 1.
<li>pow(x, +Inf) returns +0 for |x| &lt; 1.
<li>pow(x, +Inf) returns +Inf for |x| &gt; 1.
<li>pow(-Inf, y) returns -0 for y an odd integer &lt; 0.
<li>pow(-Inf, y) returns +0 for y &lt; 0 and not an odd integer.
<li>pow(-Inf, y) returns -Inf for y an odd integer &gt; 0.
<li>pow(-Inf, y) returns +Inf for y &gt; 0 and not an odd integer.
<li>pow(+Inf, y) returns +0 for y &lt; 0.
<li>pow(+Inf, y) returns +Inf for y &gt; 0.
<li>pow(x, y) returns NaN if x is negative and y is not an integer (both finite).
</list>

<deffun>
sin L1 S1
cos L1 S1
tan L1 S1
acos L1 S1
asin L1 S1
atan L1 S1
</deffun>

Compute the standard trigonometric functions.

sin and cos return values in the range -1 to 1. sin, cos, and tan of infinity are NaN.

asin is always in the range -pi/2 to pi/2; acos is always in the range 0 to pi. asin and acos of values greater than 1, or less than -1, are NaN. atan(&plusminus;Inf) is &plusminus;pi/2.

<deffun>
atan2 L1 L2 S1
</deffun>

Computes the arctangent of L1/L2, using the signs of both arguments to determine the quadrant of the return value. (Note that the Y argument is first and the X argument is second.)

Again with the special cases:

<list>
<li>atan2(&plusminus;0, -0) returns &plusminus;pi.
<li>atan2(&plusminus;0, +0) returns &plusminus;0.
<li>atan2(&plusminus;0, x) returns &plusminus;pi for x &lt; 0.
<li>atan2(&plusminus;0, x) returns &plusminus;0 for x &gt; 0.
<li>atan2(y, &plusminus;0) returns +pi/2 for y &gt; 0.
<li>atan2(y, &plusminus;0) returns -pi/2 for y &lt; 0.
<li>atan2(&plusminus;y, -Inf) returns &plusminus;pi for finite y.
<li>atan2(&plusminus;y, +Inf) returns &plusminus;0 for finite y.
<li>atan2(&plusminus;Inf, x) returns &plusminus;pi/2 for finite x.
<li>atan2(&plusminus;Inf, -Inf) returns &plusminus;3*pi/4.
<li>atan2(&plusminus;Inf, +Inf) returns &plusminus;pi/4.
</list>

<h level=2 label=opcodes_floatbranch>Floating-Point Comparisons</h>

All these branch opcodes specify their destinations with an offset value. See <ref label=opcodes_branch>.

Most of these opcodes never branch if any argument is NaN. (Exceptions are jisnan and jfne.) In particular, NaN is neither less than, greater than, nor equal to NaN.

These opcodes were added in Glulx version 3.1.2. However, not all interpreters may support them. You can test for their availability with the Float gestalt selector.

<deffun>
jisnan L1 L2
</deffun>

Branch to L2 if the floating-point value L1 is a NaN value. (See <ref label=floats>.)

<deffun>
jisinf L1 L2
</deffun>

Branch to L2 if the floating-point value L1 is an infinity (7F800000 or FF800000).

<deffun>
jfeq L1 L2 L3 L4
</deffun>

Branch to L4 if the difference between L1 and L2 is less than or equal to (plus or minus) L3. The sign of L3 is ignored.

If any of the arguments are NaN, this will not branch. If L3 is infinite, this will always branch -- unless L1 and L2 are opposite infinities. (Opposite infinities are never equal, regardless of L3. Infinities of the same sign are always equal.)

If L3 is (plus or minus) zero, this tests for exact equality. Note that +0 is considered exactly equal to -0.

<deffun>
jfne L1 L2 L3 L4
</deffun>

The reverse of jfeq. This <em>will</em> branch if <em>any</em> of the arguments is NaN.

<deffun>
jflt L1 L2 L3
jfle L1 L2 L3
jfgt L1 L2 L3
jfge L1 L2 L3
</deffun>

Branch to L3 if L1 is less than (less than or equal to, greater than, greater than or equal to) L2.

+0 and -0 behave identically in comparisons. In particular, +0 is considered equal to -0, not greater than -0.

<h level=2 label=opcodes_rand>Random Number Generator</h>

<deffun>
random L1 S1
</deffun>

Return a random number in the range 0 to (L1-1); or, if L1 is negative, the range (L1+1) to 0. If L1 is zero, return a random number in the full 32-bit integer range. (Remember that this may be either positive or negative.)

<deffun>
setrandom L1
</deffun>

Seed the random-number generator with the value L1. If L1 is zero, subsequent random numbers will be as genuinely unpredictable as the terp can provide; it may include timing data or other random sources in its generation. If L1 is nonzero, subsequent random numbers will follow a deterministic sequence, always the same for a given nonzero seed.

The terp starts up in the "nondeterministic" mode (as if setrandom 0 had been invoked.)

The random-number generator is not part of the saved-game state.

<h level=2 label=opcodes_copy>Block Copy and Clear</h>

<deffun>
mzero L1 L2
</deffun>

Write L1 zero bytes, starting at address L2. This is exactly equivalent to:

<code>
for (ix=0: ix&lt;L1: ix++) L2-&gt;ix = 0;
</code>

<deffun>
mcopy L1 L2 L3
</deffun>

Copy L1 bytes from address L2 to address L3. It is safe to copy a block to an overlapping block. This is exactly equivalent to:

<code>
if (L3 &lt; L2)
  for (ix=0: ix&lt;L1: ix++) L3-&gt;ix = L2-&gt;ix;
else
  for (ix=L1-1: ix&gt;=0: ix--) L3-&gt;ix = L2-&gt;ix;
</code>

For both of these opcodes, L1 may be zero, in which case the opcodes do nothing. The operands are considered unsigned, so a "negative" L1 is a very large number (and almost certainly a mistake).

These opcodes were added in Glulx version 3.1. You can test for their availability with the MemCopy gestalt selector.

<h level=2>Searching</h>

Perform a generic linear, binary, or linked-list search.

<comment>These are outrageously CISC for an hardware CPU, but easy enough to add to a software terp; and taking advantage of them can speed up a program considerably. Advent, under the Inform library, runs 15-20% faster when property-table lookup is handled with a binary-search opcode instead of Inform code. A similar change in the dictionary lookup trims another percent or so.</comment>

All three of these opcodes operate on a collection of fixed-size data structures in memory. A key, which is a fixed-length array of bytes, is found at a known position within each data structure. The opcodes search the collection of structures, and find one whose key matches a given key.

The following flags may be set in the Options argument. Note that not all flags can be used with all types of searches.

<list>
<li>KeyIndirect (0x01): This flag indicates that the Key argument passed to the opcode is the address of the actual key. If this flag is not used, the Key argument is the key value itself. (In this case, the KeySize <em>must</em> be 1, 2, or 4 -- the native sizes of Glulx values. If the KeySize is 1 or 2, the lower bytes of the Key are used and the upper bytes ignored.)
<li>ZeroKeyTerminates (0x02): This flag indicates that the search should stop (and return failure) if it encounters a structure whose key is all zeroes. If the searched-for key happens to also be all zeroes, the success takes precedence.
<li>ReturnIndex (0x04): This flag indicates that search should return the array index of the structure that it finds, or -1 (0xFFFFFFFF) for failure. If this flag is not used, the search returns the address of the structure that it finds, or 0 for failure.
</list>

<deffun>
linearsearch L1 L2 L3 L4 L5 L6 L7 S1
</deffun>

<list>
<li>L1: Key
<li>L2: KeySize
<li>L3: Start
<li>L4: StructSize
<li>L5: NumStructs
<li>L6: KeyOffset
<li>L7: Options
<li>S1: Result
</list>

An array of data structures is stored in memory, beginning at Start, each structure being StructSize bytes. Within each struct, there is a key value KeySize bytes long, starting at position KeyOffset (from the start of the structure.) Search through these in order. If one is found whose key matches, return it. If NumStructs are searched with no result, the search fails.

NumStructs may be -1 (0xFFFFFFFF) to indicate no upper limit to the number of structures to search. The search will continue until a match is found, or (if ZeroKeyTerminates is used) a zero key.

The KeyIndirect, ZeroKeyTerminates, and ReturnIndex options may be used.

<deffun>
binarysearch L1 L2 L3 L4 L5 L6 L7 S1
</deffun>

<list>
<li>L1: Key
<li>L2: KeySize
<li>L3: Start
<li>L4: StructSize
<li>L5: NumStructs
<li>L6: KeyOffset
<li>L7: Options
<li>S1: Result
</list>

An array of data structures is in memory, as above. However, the structs must be stored in forward order of their keys (taking each key to be a big-endian unsigned integer.) There can be no duplicate keys. NumStructs must indicate the exact length of the array; it cannot be -1.

The KeyIndirect and ReturnIndex options may be used.

<deffun>
linkedsearch L1 L2 L3 L4 L5 L6 S1
</deffun>

<list>
<li>L1: Key
<li>L2: KeySize
<li>L3: Start
<li>L4: KeyOffset
<li>L5: NextOffset
<li>L6: Options
<li>S1: Result
</list>

The structures need not be consecutive; they may be anywhere in memory, in any order. They are linked by a four-byte address field, which is found in each struct at position NextOffset. If this field contains zero, it indicates the end of the linked list.

The KeyIndirect and ZeroKeyTerminates options may be used.

<h level=2 label=opcodes_accel>Accelerated Functions</h>

To improve performance, Glulx incorporates some complex functions which replicate code in the Inform library. <comment>Yes, this is even more outrageously CISC than the search opcodes.</comment>

Rather than allocating a new opcode for each function, Glulx offers an expandable function acceleration system. Two functions are defined below. The game may request that a particular address &emdash; the address of a VM function &emdash; be replaced by one of the available functions. This does not alter memory; but any subsequent call to that address might invoke the terp's built-in version of the function, instead of the VM code at that address.

(A "call" includes any function invocation of that address, including the call, tailcall, and callf (etc.) opcodes. It also includes invocation via the filter I/O system, and function nodes in the string-decoding table. Branches to the address are <em>not</em> affected; neither are returns, throws, or other ways the terp might reach it.)

A terp may implement any, all, or none of the functions on the list. If the game requests an accelerated function which is not available, the request is ignored. Therefore, the game <em>must</em> be sure that it only requests an accelerated function at an address which actually matches the requested function.

Some functions may require values (or addresses) which are compiled into the game file, or otherwise stored by the game. The interpreter maintains a table of these parameters &emdash; whichever ones are needed by the functions it supports. All parameters in the table are initially zero; the game may supply values as needed.

The set of active acceleration requests, and the values in the parameter table, are <em>not</em> part of the saved-game state.

The behavior of an accelerated function is somewhat limited. The state of the VM during the function is not defined, so there is no way for an accelerated function to call a normal VM function. The normal printing mechanism (as in the streamchar opcode, etc) is not available, since that can call VM functions via the filter I/O system. <comment>Not that I/O functions are likely to be worth accelerating in any case.</comment>

Errors encountered during an accelerated function will be displayed to the user by some convenient means. For example, an interpreter may send the error message to the current Glk output stream. However, the terp may have no recourse but to invoke a <em>fatal</em> error. (For example, if there is no current Glk output stream.) Therefore, accelerated functions are defined with no error conditions that must be recoverable.

These opcodes were added in Glulx version 3.1.1. Since a 3.1.1 game file ought to run in a 3.1.0 interpreter, you <em>may not</em> use these opcodes without first testing the Acceleration gestalt selector. If it returns zero, your game is running on a 3.1.0 terp (or earlier), and it is your responsibility to avoid executing these opcodes. <comment>Of course, the way the opcodes are defined should ensure that skipping them does not affect the behavior of your game.</comment>

<deffun>
accelfunc L1 L2
</deffun>

Request that the VM function with address L2 be replaced by the accelerated function whose number is L1. If L1 is zero, the acceleration for address L2 is cancelled.

If the terp does not offer accelerated function L1, this does nothing.

If you request acceleration at an address which is already accelerated, the previous request is cancelled before the new one is considered. If you cancel at an unaccelerated address, nothing happens.

A given accelerated function L1 may replace several VM functions (at different addresses) at the same time. Each request is considered separate, and must be cancelled separately.

<deffun>
accelparam L1 L2
</deffun>

Store the value L2 in the parameter table at position L1. If the terp does not know about parameter L1, this does nothing.

The list of accelerated functions is as follows. They are defined as if in Inform source code. (Consider Inform's "strict" mode to be off, for the purposes of operators such as .&amp; and --&gt;.) ERROR() represents code which displays an error, as described above.

(Functions may be added to this list in future versions of the Glulx spec. Existing functions will not be removed or altered.)

<code>
Constant PARAM_0_classes_table = #classes_table;
Constant PARAM_1_indiv_prop_start = INDIV_PROP_START;
Constant PARAM_2_class_metaclass = Class;
Constant PARAM_3_object_metaclass = Object;
Constant PARAM_4_routine_metaclass = Routine;
Constant PARAM_5_string_metaclass = String;
Constant PARAM_6_self = #globals_array + WORDSIZE * #g$self;
Constant PARAM_7_num_attr_bytes = NUM_ATTR_BYTES;
Constant PARAM_8_cpv__start = #cpv__start;

! OBJ_IN_CLASS: utility function; implements "obj in Class".
[ OBJ_IN_CLASS obj;
  return ((obj + 13 + PARAM_7_num_attr_bytes)--&gt;0
    == PARAM_2_class_metaclass);
];

! FUNC_1_Z__Region: implements Z__Region() as of Inform 6.31.
[ FUNC_1_Z__Region addr
  tb endmem; ! locals
  if (addr&lt;36) rfalse;
  @getmemsize endmem;
  @jgeu addr endmem?outrange;  ! branch if addr &gt;= endmem (unsigned)
  tb=addr-&gt;0;
  if (tb &gt;= $E0) return 3;
  if (tb &gt;= $C0) return 2;
  if (tb &gt;= $70 &amp;&amp; tb &lt;= $7F &amp;&amp; addr &gt;= (0--&gt;2)) return 1;
.outrange;
  rfalse;
];

! FUNC_2_CP__Tab: implements CP__Tab() as of Inform 6.31.
[ FUNC_2_CP__Tab obj id
  otab max res; ! locals
  if (FUNC_1_Z__Region(obj)~=1) {
    ERROR("[** Programming error: tried to find the ~.~ of (something) **]");
    rfalse;
  }
  otab = obj--&gt;4;
  if (otab == 0) return 0;
  max = otab--&gt;0;
  otab = otab+4;
  @binarysearch id 2 otab 10 max 0 0 res;
  return res;
];

! FUNC_3_RA__Pr: implements RA__Pr() as of Inform 6.31.
[ FUNC_3_RA__Pr obj id
  cla prop ix; ! locals
  if (id &amp; $FFFF0000) {
	cla = PARAM_0_classes_table--&gt;(id &amp; $FFFF);
	if (~~FUNC_5_OC__Cl(obj, cla)) return 0;
	@ushiftr id 16 id;
	obj = cla;
  }
  prop = FUNC_2_CP__Tab(obj, id);
  if (prop==0) return 0;
  if (OBJ_IN_CLASS(obj) &amp;&amp; cla == 0) {
	if (id &lt; PARAM_1_indiv_prop_start
	    || id &gt;= PARAM_1_indiv_prop_start+8)
	  return 0;
  }
  if (PARAM_6_self--&gt;0 ~= obj) {
	@aloadbit prop 72 ix;
	if (ix) return 0;
  }
  return prop--&gt;1;
];

! FUNC_4_RL__Pr: implements RL__Pr() as of Inform 6.31.
[ FUNC_4_RL__Pr obj id
  cla prop ix; ! locals
  if (id &amp; $FFFF0000) {
	cla = PARAM_0_classes_table--&gt;(id &amp; $FFFF);
	if (~~FUNC_5_OC__Cl(obj, cla)) return 0;
	@ushiftr id 16 id;
	obj = cla;
  }
  prop = FUNC_2_CP__Tab(obj, id);
  if (prop==0) return 0;
  if (OBJ_IN_CLASS(obj) &amp;&amp; cla == 0) {
	if (id &lt; PARAM_1_indiv_prop_start
	    || id &gt;= PARAM_1_indiv_prop_start+8)
	  return 0;
  }
  if (PARAM_6_self--&gt;0 ~= obj) {
	@aloadbit prop 72 ix;
	if (ix) return 0;
  }
  @aloads prop 1 ix;
  return WORDSIZE * ix;
];

! FUNC_5_OC__Cl: implements OC__Cl() as of Inform 6.31.
[ FUNC_5_OC__Cl obj cla
  zr jx inlist inlistlen; ! locals
  zr = FUNC_1_Z__Region(obj);
  if (zr == 3) {
	if (cla == PARAM_5_string_metaclass) rtrue;
	rfalse;
  }
  if (zr == 2) {
	if (cla == PARAM_4_routine_metaclass) rtrue;
	rfalse;
  }
  if (zr ~= 1) rfalse;
  if (cla == PARAM_2_class_metaclass) {
	if (OBJ_IN_CLASS(obj)
	  || obj == PARAM_2_class_metaclass or PARAM_5_string_metaclass
	     or PARAM_4_routine_metaclass or PARAM_3_object_metaclass)
	  rtrue;
	rfalse;
  }
  if (cla == PARAM_3_object_metaclass) {
	if (OBJ_IN_CLASS(obj)
	  || obj == PARAM_2_class_metaclass or PARAM_5_string_metaclass
	     or PARAM_4_routine_metaclass or PARAM_3_object_metaclass)
	  rfalse;
	rtrue;
  }
  if (cla == PARAM_5_string_metaclass or PARAM_4_routine_metaclass)
    rfalse;
  if (~~OBJ_IN_CLASS(cla)) {
	ERROR("[** Programming error: tried to apply 'ofclass' with non-class **]");
	rfalse;
  }
  inlist = FUNC_3_RA__Pr(obj, 2);
  if (inlist == 0) rfalse;
  inlistlen = FUNC_4_RL__Pr(obj, 2) / WORDSIZE;
  for (jx=0 : jx&lt;inlistlen : jx++) {
	if (inlist--&gt;jx == cla) rtrue;
  }
  rfalse;
];

! FUNC_6_RV__Pr: implements RV__Pr() as of Inform 6.31.
[ FUNC_6_RV__Pr obj id
  addr; ! locals
  addr = FUNC_3_RA__Pr(obj, id);
  if (addr == 0) {
	if (id &gt; 0 &amp;&amp; id &lt; PARAM_1_indiv_prop_start) {
	  return PARAM_8_cpv__start--&gt;id;
	}
	ERROR("[** Programming error: tried to read (something) **]");
	return 0;
  }
  return addr--&gt;0;
];

! FUNC_7_OP__Pr: implements OP__Pr() as of Inform 6.31.
[ FUNC_7_OP__Pr obj id
  zr; ! locals
  zr = FUNC_1_Z__Region(obj);
  if (zr == 3) {
	if (id == print or print_to_array) rtrue;
	rfalse;
  }
  if (zr == 2) {
	if (id == call) rtrue;
	rfalse;
  }
  if (zr ~= 1) rfalse;
  if (id &gt;= PARAM_1_indiv_prop_start
      &amp;&amp; id &lt; PARAM_1_indiv_prop_start+8) {
	if (OBJ_IN_CLASS(obj)) rtrue;
  }
  if (FUNC_3_RA__Pr(obj, id) ~= 0)
	rtrue;
  rfalse;
];
</code>

<h level=2 label=opcodes_misc>Miscellaneous</h>

<deffun>
nop
</deffun>

Do nothing.

<deffun>
gestalt L1 L2 S1
</deffun>

Test the Gestalt selector number L1, with optional extra argument L2, and store the result in S1. If the selector is not known, store zero.

The reasoning behind the design of a Gestalt system is, I hope, too obvious to explain.

<comment>This list of Gestalt selectors has nothing to do with the list in the Glk library.</comment>

The list of L1 selectors is as follows. Note that if a selector does not mention L2, you should always set that argument to zero. <comment>This will ensure future compatibility, in case the selector definition is extended.</comment>

<list>
<li>GlulxVersion (0): Returns the version of the Glulx spec which the interpreter implements. The upper 16 bits of the value contain a major version number; the next 8 bits contain a minor version number; and the lowest 8 bits contain an even more minor version number, if any. This specification is version 3.1.2, so a terp implementing it would return 0x00030102. I will try to maintain the convention that minor version changes are backwards compatible, and subminor version changes are backwards and forwards compatible.
<li>TerpVersion (1): Returns the version of the interpreter. The format is the same as the GlulxVersion. <comment>Each interpreter has its own version numbering system, defined by its author, so this information is not terribly useful. But it is convenient for the game to be able to display it, in case the player is capturing version information for a bug report.</comment>
<li>ResizeMem (2): Returns 1 if the terp has the potential to resize the memory map, with the setmemsize opcode. If this returns 0, setmemsize will always fail. <comment>But remember that setmemsize might fail in any case.</comment>
<li>Undo (3): Returns 1 if the terp has the potential to undo. If this returns 0, saveundo and restoreundo will always fail.
<li>IOSystem (4): Returns 1 if the terp supports the I/O system given in L2. (The constants are the same as for the setiosys opcode: 0 for null, 1 for filter, 2 for Glk, 20 for FyreVM. 0 and 1 will always succeed.)
<li>Unicode (5): Returns 1 if the terp supports Unicode operations. These are: the E2 Unicode string type; the 04 and 05 string node types (in compressed strings); the streamunichar opcode; the type-14 call stub. If the Unicode selector returns 0, encountering any of these will cause a fatal interpreter error.
<li>MemCopy (6): Returns 1 if the interpreter supports the mzero and mcopy opcodes. (This must true for any terp supporting Glulx 3.1.)
<li>MAlloc (7): Returns 1 if the interpreter supports the malloc and mfree opcodes. (If this is true, MemCopy and ResizeMem must also both be true, so there is no need to check all three.)
<li>MAllocHeap (8): Returns the start address of the heap. This is the value that getmemsize had when the first memory block was allocated. If the heap is not active (no blocks are extant), this returns zero.
<li>Acceleration (9): Returns 1 if the interpreter supports the accelfunc and accelparam opcodes. (This must true for any terp supporting Glulx 3.1.1.)
<li>AccelFunc (10): Returns 1 if the terp implements the accelerated function given in L2.
<li>Float (11): Returns 1 if the interpreter supports the floating-point arithmetic opcodes.
</list>

Selectors 0x1000 to 0x10FF are reserved for use by FyreVM, and are not documented here. See <ref label=otherif>.

<comment>The Unicode selector is slightly redundant. Since the Unicode operations exist in Glulx spec 3.0 and higher, you can get the same information by testing GlulxVersion against 0x00030000. However, it's clearer to have a separate selector. Similarly, the MemCopy selector is true exactly when GlulxVersion is 0x00030100 or higher.</comment>

<comment>The Unicode selector does <em>not</em> guarantee that your Glk library supports Unicode. For that, you must check the Glk gestalt selector gestalt_Unicode. If the Glk library is non-Unicode, the Glulx Unicode operations are still legal; however, Unicode characters (beyond FF) will be printed as 3F ("?").</comment>

<deffun>
debugtrap L1
</deffun>

Interrupt execution to do something interpreter-specific with L1. If the interpreter has nothing in mind, it should halt with a visible error message.

<comment>This is intended for use by debugging interpreters. The program might be sprinkled with consistency tests, set to call debugtrap if an assertion failed. The interpreter could then be set to halt, display a warning, or ignore the debugtrap.</comment>

This should <em>not</em> be used as an arbitrary interpreter trap-door in a finished (non-debugging) program. If you really want to add interpreter functionality to your program, and you're willing to support an alternate interpreter to run it, you should add an entirely new opcode. There are still 2^28 of them available, give or take.

<deffun>
glk L1 L2 S1
</deffun>

Call the Glk API function whose identifier is L1, passing in L2 arguments. The return value is stored at S1. (If the Glk function has no return value, zero is stored at S1.)

The arguments are passed on the stack, last argument pushed first, just as for the call opcode.

Arguments should be represented in the obvious way. Integers and character are passed as integers. Glk opaque objects are passed as integer identifiers, with zero representing NULL. Strings and Unicode strings are passed as the addresses of Glulx string objects (see <ref label=string>.) References to values are passed by their addresses. Arrays are passed by their addresses; note that an array argument, unlike a string argument, is always followed by an array length argument.

Reference arguments require more explanation. A reference to an integer or opaque object is the address of a 32-bit value (which, being in main memory, does not have to be aligned, but must be big-endian.) Alternatively, the value -1 (FFFFFFFF) may be passed; this is a special case, which means that the value is read from or written to the stack. Arguments are always evaluated left to right, which means that input arguments are popped from the stack first-topmost, but output arguments are pushed on last-topmost.

A reference to a Glk structure is the address of an array of 32-bit values in main memory. Again, -1 means that all the values are written to the stack. Also again, an input structure is popped off first-topmost, and an output structure is pushed on last-topmost.

All stack input references (-1 addresses) are popped after the Glk argument list is popped. <comment>This should be obvious, since the -1 occurs <em>in</em> the Glk argument list.</comment> Stack output references are pushed after the Glk call, but before the S1 result value is stored.

<comment>The difference between strings and character arrays is somewhat confusing. These are the same type in the C Glk API, but different in Glulx. Calls such as glk_put_buffer() and glk_request_line_event() take character arrays; this is the address of a byte array containing character values, followed by an integer array length. The byte array itself has neither a length field or a terminator. In contrast, calls such as glk_put_string() and glk_fileref_create_by_name() take string arguments, which must be unencoded Glulx string objects. An unencoded Glulx string object is nearly a byte array, but not quite; it has an E0 byte at the beginning and a zero byte at the end. Similarly, calls such as glk_put_string_uni() take unencoded (E2) Unicode objects.</comment>

<comment>Previous versions of this spec said that string arguments could be unencoded <em>or encoded</em> string objects. This use of encoded strings has never been supported, however, and it is withdrawn from the spec.</comment>

<comment>The convention that "address" -1 refers to the stack is a feature of the Glk invocation mechanism; it applies only to Glk arguments. It is <em>not</em> part of the general Glulx definition. When instruction operands are being evaluated, -1 has no special meaning. This includes the L1, L2, and S1 arguments of the glk opcode.</comment>

<h level=2>Assembly Language</h>

The format used by Inform is acceptable for now:

<code>
@opcode [ op op op ... ] ;
</code>

Where each "op" is a constant, the name of a local variable, the name of a global variable, or "sp" (for stack push/pop modes).

<comment>It would be convenient to have a one-line form for the opcodes that pass arguments on the stack (call and glk).</comment>

To make life a little easier for cross-platform I6 code, Inform accepts the macro "@push val" for "@copy val sp", and "@pull val" for "@copy sp val". Supporting these forms is recommended.

You can synthesize opcodes that the compiler does not know about:

<code>
@"FlagsCount:Code" [ op op op ... ] ;
</code>

The optional Flags can include "S" if the last operand is a store; "SS" if the last two operands are stores; "B" for branch format; "R" if execution never continues after the opcode. The Count is the number of arguments (0 to 9). The Code is a decimal integer representing the opcode number. So these two lines generate the same code:

<code>
@add x 1 y;
@"S3:16" x 1 y;
</code>

...because the @add opcode has number 16 (decimal), and has format "@add L1 L2 S1".

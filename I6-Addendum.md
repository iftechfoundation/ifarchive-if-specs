# Inform 6 Reference Addendum {: .Title }

Language and compiler changes: releases 6.30 to 6.43 (in development)
{: .VersionHeader }

Maintained by IFTF: `<specs@ifarchive.org>`
{: .AuthorHeader }

(Last update: March 7, 2024)
{: .DateHeader }

Copyright 2020-24 by the Interactive Fiction Technology Foundation. This document is licenced under a [Creative Commons Attribution-ShareAlike 4.0 International License][bysa].

Graham Nelson's [Inform 6][i6] is a system for creating adventure games, and _[The Inform Designer's Manual][dm4]_ is the book to read about it.

[i6]: https://ifarchive.org/indexes/if-archive/infocom/compilers/inform6/
[dm4]: https://www.inform-fiction.org/manual/html/contents.html
[i7]: http://inform7.com/
[wwi]: http://inform7.com/book/WI_1_1.html
[bysa]: https://creativecommons.org/licenses/by-sa/4.0/

The fourth edition of that manual, published in 2001, began with that assertion. It's still true -- although these days we have to specify that it's about Inform *6*. ([Inform 7][i7] is a more modern system, quite different, with its own manual called _[Writing With Inform][wwi]_.) 

Inform 6 has remained broadly unchanged in the twenty years since the DM4 was published. While some authors continue to use I6 directly, its primary use is as an intermediate stage for the Inform 7 compiler. Stability and reliability have therefore been the watchwords of the I6 maintainers.

However, the language has not remained completely static. Most notably, the compiler now supports the Glulx VM as well as the original Z-machine. This required some additions to both the language and the compiler. Other corners of the system have been polished and rearranged, with the aim of making Inform a more flexible tool for both its target platforms.

As a result, the DM4 is now a bit out of date. This document is meant to fill in the gaps for the Inform 6 user of today.

---

[TOC]

---

## I6 version history

This is a high-level view of I6 releases and their most important features. For a complete description of each release, see the [I6 Release Notes][i6release] (older notes [here][i6relold]).

- **6.21** (Apr 1999): DM4 version.
- **6.30** (Feb 2004): Glulx support; `!%` header comments; capital `(A)` print token.
- **6.31** (Feb 2006): Bug fixes.
- **6.32** (Nov 2010): `@push`, `@pull` assembly macros; all Glulx opcodes supported; Glulx floating-point constants.
- **6.33** (May 2014): UTF-8 source files; `$OMIT_UNUSED_ROUTINES`; `<Take pie, orc>`; `Undef` directive; `Dictionary` directive for setting word flags.
- **6.34** (May 2020): Revitalized v3 support; `OrigSource` directive; improved `Replace` directive.
- **6.35** (May 2021): Unix-style command-line options; command-line option to define a numeric constant.
- **6.36** (Jan 2022): Most memory limits are gone; some compile-time type checking.
- **6.40** (Jul 2022): Command-line arguments streamlined; modules and temp-file compilation removed; dead-code stripping.
- **6.41** (Jul 2022): Bug fixes.
- **6.42** (Feb 2024): Unlimited identifier length; unlimited abbreviation length; inline bytes assembly.
- **6.43** (unreleased): Singular (`//s`) dict flag and `$DICT_IMPLICIT_SINGULAR`; truncation dict flag and `$DICT_TRUNCATE_FLAG`.

## Language versus library

This addendum covers updates to the Inform 6 language and compiler. A few errata are also included.

The changes described here are mostly to DM4 chapters 1-7, 36, and 38 and up. (Section references such as "§1" refer to [DM4 chapters][dm4].) The intermediate chapters (the bulk of the DM4!) concern the Inform 6 library, which is *not* covered by this document.

The Inform library described by the DM4 is version [6/9][i6lib9], which was released along with Inform 6.21 in April of 1999. The library was subsequently updated to [6/10][i6lib10] (a bug-fix release) and then [6/11][i6lib11] (Glulx support and some additional features) before the author shifted his focus to [Inform 7][i7] development.

The Inform library is now a [separate project managed by David Griffith][i6lib]. Updates can be found on the [project page][i6lib].

The Inform 6 compiler can be used with older versions of the Inform library, back through the [Inform 5 libraries][i5lib]. There also exist a number of alternative Inform libraries, such as [metro84][] and [PunyInform][] (supporting very old computers) and [Platypus][] (a redesigned library). The Inform 6 compiler should be usable with all of them.

[i6lib9]: https://ifarchive.org/if-archive/infocom/compilers/inform6/library/old/inform_library69.zip
[i6lib10]: https://ifarchive.org/if-archive/infocom/compilers/inform6/library/old/inform_library610.zip
[i6lib11]: https://ifarchive.org/if-archive/infocom/compilers/inform6/library/old/inform_library611.zip
[i6lib]: https://gitlab.com/DavidGriffith/inform6lib
[i5lib]: https://ifarchive.org/indexes/if-archive/infocom/compilers/inform5/library/
[metro84]: https://github.com/ByteProject/Metrocenter84/tree/master/metro84
[PunyInform]: https://github.com/johanberntsson/PunyInform
[Platypus]: https://ifarchive.org/if-archive/infocom/compilers/inform6/library/contributions/platypus.zip

# Compiler options and settings

The Inform compiler has many options which control its compilation behavior. These options come in three styles, and there are three ways to supply them.

## Supplying options

All options can be supplied to the compiler in three ways (§39):

- As a command-line argument
- In a separate file, specified with `(file.icl)` or `--config file.icl`
- At the head of the first source file, in a comment beginning with `!%`

The third method is new since the DM4. It allows you to store your game's compilation options in the same file as its source code.

For example, this source file will be compiled in Glulx format, searching the `i6lib` directory for include files, raising the maximum number of verbs, and displaying compilation statistics:

	!% -G
	!% -s
	!% +include_path=i6lib
	!% $MAX_VERBS=255

	Include "Parser";
	Include "VerbLib";

	[ Initialise;
	  location = Kitchen;
	];

	Object Kitchen "Kitchen"
	  with description "It's the kitchen.",
	  has light;

	Include "Grammar";

The options specified with `!%` must be at the *start* of the source file, with no blank lines or other comments before or between them.

Note that this section of the file is parsed before the source encoding is set. (Indeed, this section could specify the source encoding!) Therefore, options in this section must be plain ASCII.

`!%` options take precedence over command-line options. Command-line options are read in order; later options (including `(file.icl)` inclusions) take precedence over earlier ones.

[[It would be better if command-line options took precedence over `!%` options. This would allow one-off changes while recompiling existing source code. This change may be considered in the future.]]

## Switch options (dash) { #switchopts }

Classic options begin with a dash -- the traditional style of command-line tools. For example, the `-h` option (help) shows a page of output documenting how to run the compiler. `-h2` will show a page listing all options that begin with a dash (§Table3).

*New since the DM4:*

`-a2`: As of 6.40, this displays assembly encoding of functions (like `-a`) plus byte encoding of the assembly opcodes. (Prior to 6.40, this was the `-t` option.)

`-B`: In Z-code versions 6 and 7 (only), use different offset values for the packed addresses of routines and strings. In this mode, strings are distinguished by having odd (packed) addresses, whereas routines are even. This allows the game file to contain more executable code. (The default is `-~B`, where the routine and string segments use the same offset value, so string and routine values have different ranges.)

`-Cu`: Treat the source files as being in UTF-8 (Unicode) encoding.

[[Older options `-C1`, `-C2`, etc., are documented in the DM4 (§36); they treated the source files as being in one of the Latin-N encodings. `-Cu` is a new extension.]]

[[These options also affect the `gametext.txt` file created by the `-r` option. This transcript uses the same encoding as the source code.]]

[[When `-Cu` is used, the compiler does not add any characters to the Z-machine's "cheap" alphabet table. You can use the `Zcharacter` directive to add selected Unicode characters; see §36.]]

`-G`: Compile to Glulx format rather than Z-machine. The default output file will be given an `.ulx` extension.

`-G -vX.Y.Z`: In Glulx, specify the VM version number to note in the generated game file. For example, `-G -v3.1.0` would generate a game file that specifies VM spec 3.1.0.

[[Normally the compiler works out the earliest version number compatible with the features used by your game. You can use this option to specify a later version.]]

`-H`: In Glulx format, use Huffman encoding to compress strings. This is the default; to use uncompressed text, use `-~H`.

`-k`: Output debugging information to a file `gameinfo.dbg`. This switch is documented in the DM4 (§7), but the output format has changed. As of 6.33, it is an extremely verbose XML format; see [below](#debugformat). Also, as of 6.35, the `-k` switch no longer automatically sets `-D`.

`-g3`: Trace calls to all functions. The DM4 documents `-g2` as doing this, but as of 6.21, `-g2` does not trace veneer functions. As of 6.35, `-g3` traces everything.

[[Note that `-g2` and above will cause runtime errors in Glulx games, due to printing trace information when no output window is available.]]

`-W`: Sets the number of words in the Z-code header extension table (Z-spec 1.0). The default is `-W3`. The `$ZCODE_HEADER_EXT_WORDS` setting does the same thing.

`-V`: Display the compiler version and exit with no further action.

*Removed since the DM4:*

The following switch options existed prior to 6.40, but are now gone.

- `-F`: The ability to use temporary files (rather than memory) for compilation data has been removed.
- `-M`, `-U`, `-y`: The ability to create and import linker modules has been removed.

The following switch options existed prior to 6.40, but have been removed in favor of [trace options](#traceopts).

- `-b`: Has done nothing since Inform 5.
- `-j`: Replaced by the `$!OBJECTS` option.
- `-l`: Never fully implemented; what functionality existed has been replaced by the `$!FILES` option.
- `-m`: Replaced by the `$!MEM` option.
- `-n`: Replaced by the `$!PROPS` and `$!ACTIONS` options.
- `-o`: Replaced by the `$!MAP` option.
- `-p`: Replaced by the `$!MAP=2` option.
- `-t`: Replaced by the `$!ASM=2` option or the `-a2` switch.

## Path options (plus)

Options beginning with a plus set paths used by the compiler (§39). For example, `+DIRNAME` or `+include_path=DIRNAME` set the directory which is searched for include files.

You can also give a comma-separated list of paths: `+include_path=DIR1,DIR2,DIR3`

*New since the DM4:*

A double plus sign adds a new path or paths to an existing list. For example, `++include_path=DIRNAME` will add DIRNAME to the paths which are searched for include files. The newly-added paths will be searched first.

On the command line (but not in ICL files or comments), path options can be also specified in Unix style. (This was added in 6.35.)

	--path PATH=dir
	--addpath PATH=dir

*Removed since the DM4:*

The `+module_path` and `+temporary_path` options no longer exist as of 6.40.

## Compiler settings (dollar) { #memsettings }

These were referred to as "memory settings" in the DM4 (§39). However, they now encompass a wide range of compiler behavior.

The `$LIST` setting will show a page of output listing all dollar-sign settings for Z-machine games. To see all settings for Glulx games, give the `-G` argument before `$LIST`.

[[If you supply a dollar-sign setting as a command-line option on MacOS or Unix, remember that the shell treats the dollar sign as a special character. You must escape the dollar sign so that it reaches the compiler:
	inform \$MAX_VERBS=255 source.inf
If you supply such a setting in a source file, using the `!%` format, you should *not* use the backslash.]]

*New since the DM4:*

A setting that begins with a hash sign (`$#`) will define an arbitrary numeric constant in the game code. If no value is supplied, the constant is defined as zero. This is equivalent to (and consistent with) the `Constant` directive. (Added in 6.35.)

	$#SYMBOL
	$#SYMBOL=number
	
[[Thus, passing the `$#DEBUG` argument is equivalent to the `-D` option. Remember that Inform symbols are not case-sensitive; `$#debug` or `$#Debug=0` does the same thing.]]

A setting that begins with an exclamation mark (`$!`) is a trace option. (Added in 6.40.) These have a slightly different format; see [Trace options](#traceopts), below.

On the command line (but not in ICL files or comments), compiler settings can also be specified in Unix style. (Added in 6.35.) This avoids the need to escape dollar signs.

	--list
	--opt SETTING=number
	--define SYMBOL=number
	--trace TRACEOPT=number

As of 6.36, the following internal memory settings are no longer needed and have no effect: `$ALLOC_CHUNK_SIZE`, `$MAX_OBJECTS`, `$MAX_CLASSES`, `$MAX_SYMBOLS`, `MAX_PROP_TABLE_SIZE`, `$MAX_INDIV_PROP_TABLE_SIZE`, `$MAX_OBJ_PROP_COUNT`, `$MAX_OBJ_PROP_TABLE_SIZE`, `$MAX_ARRAYS`, `$MAX_STATIC_DATA`, `$MAX_ADJECTIVES`, `$MAX_VERBS`, `$MAX_VERBSPACE`, `$MAX_LABELS`, `$MAX_EXPRESSION_NODES`, `$MAX_SOURCE_FILES`, `$MAX_INCLUSION_DEPTH`, `$MAX_ACTIONS`, `$MAX_LINESPACE`, `$MAX_ZCODE_SIZE`, `$MAX_LINK_DATA_SIZE`, `$MAX_TRANSCRIPT_SIZE`, `$MAX_DICT_ENTRIES`, `$MAX_NUM_STATIC_STRINGS`, `$MAX_UNICODE_CHARS`, `$MAX_STATIC_STRINGS`, `$MAX_LOW_STRINGS`, `$MAX_GLOBAL_VARIABLES`, `$MAX_LOCAL_VARIABLES`, `$MAX_QTEXT_SIZE`.

Other settings which are new or updated since the DM4:

**$DICT_CHAR_SIZE**

The byte size of one character in the dictionary. This is only meaningful in Glulx. It can be 1 (dictionary characters are one byte) or 4 (dictionary characters are four-byte words).

**$DICT_WORD_SIZE**

The number of bytes in a dictionary word entry. (In Z-code this cannot be changed. It is always 4 in v3 and 6 in V4+, representing up to 6 or 9 Z-characters.)

**$DICT_IMPLICIT_SINGULAR**

If this is 1, Inform sets the singular (`//s`) flag for any noun not explicitly marked plural (`//p`). (Added in 6.43.)

**$DICT_TRUNCATE_FLAG**

If this is 1, Inform sets dict flag 6 for any dict word which is truncated; that is, if the source definition of the word does not fit in `$DICT_WORD_SIZE`. (Added in 6.43.)

If this is 0, dict flag 6 is set for all verbs (equivalent to dict flag 1). This is legacy behavior dating back to early versions of Inform, but no current library code depends on it.

**$GLULX_OBJECT_EXT_BYTES**

The number of extra zero bytes to add to each object table entry. This is writable memory which the game can use freely. (This is only meaningful in Glulx, as the Z-code object format is fixed by the spec.)

**$INDIV_PROP_START**

The index number of the first individual property. This also determines the maximum number of common properties. (In Z-code this is 64 and cannot be changed.)

**$LONG_DICT_FLAG_BUG**

If this is set to 0, dictionary flag suffixes (see "[Dictionary words](#dictionary-words)") are recognized in words of any length.

If this is 1, suffixes are ignored if they begin after the dictionary word length. (After the ninth character for V4+; the sixth for V3; the ninth or whatever `$DICT_WORD_SIZE` is set to in Glulx.) The default setting is 1.

[[We retain the buggy behavior as the default to avoid disrupting old Inform 7 games. I7 always adds the words `'directions//p'`, `'supporters//p'`, `'containers//p'` to objects of those types. Due to the bug, the plural flag is not set on these words, which affects the parsing of commands like `GET DIRECTION` or `GET CONTAINER`. Future releases of I7 may set `$LONG_DICT_FLAG_BUG=0`, but it is better to avoid changing the behavior of existing releases.]]

(Added in 6.42. In earlier versions, the bug was always present and could not be switched off.)

**$MAX_ABBREVS**

The number of abbreviations which may be used in economy (`-e`) mode. This setting is available in all versions of Inform, but in 6.35 the maximum for Z-code was raised from 64 to 96. However, this trades off against `$MAX_DYNAMIC_STRINGS`; see below.

The abbreviations (`-u`) switch now tries to create `$MAX_ABBREVS` abbreviations, rather than always creating 64. (As of 6.36.)

In Glulx, `$MAX_ABBREVS` is not needed and has no effect, except with the `-u` switch.

**$MAX_DYNAMIC_STRINGS**

The number of string variables (`"@00"`, etc) allowed in the game. In Z-code, this may be any value from 0 to 96. Setting this in Z-code automatically sets `$MAX_ABBREVS` to `(96 - $MAX_DYNAMIC_STRINGS)`, as the two features draw from the same pool of 96 Z-machine abbreviations. Similarly, setting `$MAX_ABBREVS` sets `$MAX_DYNAMIC_STRINGS` to `(96 - $MAX_ABBREVS)`.

In Glulx, the two settings are not connected. You may use any number of dynamic strings. If you use more than 100, you must set `$MAX_DYNAMIC_STRINGS` to a higher value.

(Added in 6.35. In earlier versions, 32 string variables and 64 abbreviations were available in Z-code; 64 string variables were available in Glulx. As of 6.36, `$MAX_DYNAMIC_STRINGS` defaulted to 100 in Glulx, which was the maximum. As of 6.40, `$MAX_DYNAMIC_STRINGS` is not limited in Glulx, but still defaults to 100.)

**$MAX_STACK_SIZE**

The amount of memory that the interpreter will reserve for the Glulx stack. (This is only meaningful in Glulx.)

**$MEMORY_MAP_EXTENSION**

The number of extra zero bytes to add to the end of the compiled game file. This is writable memory which the game can use freely. (This is only meaningful in Glulx.)

**$NUM_ATTR_BYTES**

The number of bytes used for attribute flags in each object. The maximum number of attributes is `8 * NUM_ATTR_BYTES`. (In Glulx, this must be a multiple of 4 plus 3. In Z-code this is always 6 and cannot be changed.)

**$OMIT_SYMBOL_TABLE**

If this is set to 1, the compiler will not compile the names of properties, arrays, and other code elements into the game file. This means that the `print (property) p` statement will print a property number instead of a name. Runtime errors will also omit symbol names.

System constants referring to symbol names are not available when `$OMIT_SYMBOL_TABLE` is set. See "[Constants](#constants)".

**$OMIT_UNUSED_ROUTINES**

If this is set to 1, the compiler will omit the compiled code of unused routines from the game file. (See `$WARN_UNUSED_ROUTINES`.)

**$SERIAL**

Sets the game's serial number to the given six-digit number. (The `Serial` directive does the same thing; see §38.)

**$STRIP_UNREACHABLE_LABELS**

If set to 1 (the default), unreachable labels will be eliminated as part of branch optimization. Attempting to `jump` to an unreachable label is a compile-time error.

If set to 0, any label can be `jump`ed to, at the cost of less optimized code.

(Added in 6.40. In earlier versions, any label could be `jump`ed to. As of 6.41, *forward* `jump`s to labels are always permitted. Only backward `jump`s to unreachable labels can cause errors.)

**$TRANSCRIPT_FORMAT**

If set to 0 (the default), the `gametext.txt` transcript generated by the `-r` option uses the classic format, which is designed for human proofreaders. If set to 1, the transcript uses an alternate format which indicates the use of each string. This may be more useful for tools which want to parse the transcript.

**$WARN_UNUSED_ROUTINES**

If this is set to 2, the compiler will display a warning for each routine in the game file which is never called. (This includes routines called only from uncalled routines, etc.) If set to 1, it will warn only about functions in game code, not in library files.
  
**$ZCODE_HEADER_EXT_WORDS**

This sets the number of words in the Z-code header extension table. The default is 3. The `-W` setting does the same thing. (See Z-spec 1.0. This is only meaningful in Z-code.)

**$ZCODE_HEADER_FLAGS_3**

This is the value to store in the Flags 3 word of the header extension table. (See Z-spec 1.1. This is only meaningful in Z-code.)

**$ZCODE_LESS_DICT_DATA**

If this is set to 1, each dictionary entry will have two bytes of data instead of the usual three. (Added in 6.36. This is only meaningful in Z-code.)

With this switch set, you may not refer to `#dict_par3`. You also may not use grammar version 1, as that format needs to use the third byte for the preposition number.

**$ZCODE_MAX_INLINE_STRING**

This is the length beyond which string literals cannot be inlined in assembly opcodes. The default value is 32 characters. (Added in 6.42. This is only meaningful in Z-code.)

If you increase this, Inform will be more aggressive about inlining literal strings in `print` statements. This will save some space in the compiled game file. However, it may also lead to excessively long functions, which may cause "Branch out of range" compilation errors. Use with care.

[[Note that the limit is measured in *source code* characters, without regard for escapes or abbreviations. The string literal `"abc@{64}e"` is measured as 9 characters, even though it's compiled as 5 Z-characters (`"abcde"`) in 4 bytes. Since the aim is an optimization policy, the imprecision is not worth worrying about.]]

## Trace options { #traceopts }

These are special compiler settings which display extra information about the compilation process. Most of them are only useful for debugging the compiler itself. The ones most useful to authors have simple switch options, documented [above](#switchopts).

Trace options all have the form `$!TRACEOPT` or `$!TRACEOPT=number`. The option `$!` by itself will show a list of all supported trace options.

On the command line (but not in ICL files or comments), trace options can be also specified in Unix style.

	--trace TRACEOPT
	--trace TRACEOPT=number
	--helptrace

All trace options are off (level 0) by default. The simple form `$!TRACEOPT` or `--trace TRACEOPT` sets the named option to level 1, which displays information during (or after) compilation. Some trace options support higher levels of verbosity to print more information.

The trace option system is new as of 6.40. In prior versions, much of this information was available through command-line switches or the `Trace` directive.

**$!ACTIONS**

Show actions and fake-actions as they are defined.

(Prior to 6.40, this information was displayed by the `-n` switch.)

**$!ASM** (same as `-a`)

Show assembly-language encoding of functions as they are compiled. `$!ASM=2` will also show the byte encoding of the assembly opcodes. `$!ASM=3` will also show branch optimization info. `$!ASM=4` will show more verbose branch info.

The `$!ASM` trace level can be changed at any point in the code with the `Trace assembly` directive. 

(Prior to 6.40, the `-t` switch showed assembly plus opcode bytes, as `$!ASM=2` or `-a2` does now.)

**$!BPATCH**

Show backpatch markers as they are resolved. `$!BPATCH=2` will also show backpatch markers being created.

(Prior to 6.40, this information was shown at higher `$!ASM` trace levels.)

**$!DICT**

Show the game dictionary when the game is complete. `$!DICT=2` will also show the byte encoding of each dictionary entry.

The `Trace dictionary` directive will show this information at any point in the code.

**$!EXPR**

Show expression trees as they are compiled. `$!EXPR=2` and `$!EXPR=3` will show more verbose information.

The `$!EXPR` trace level can be changed at any point in the code with the `Trace expressions` directive. 

**$!FILES**

Show source and include files being opened and closed.

(Prior to 6.40, the `-l` switch and `Trace lines` directive showed this information.)

**$!FINDABBREVS**

When computing abbreviations (`-u`), show selection decisions. `$!FINDABBREVS=2` will also show three-letter-block scores.

(Prior to 6.40, the `-u` switch always showed this information.)

**$!FREQ** (same as `-f`)

When using abbreviations (`-e`), show how efficient each abbreviation was.

**$!MAP** (same as `-z`)

Display a memory map of the completed virtual machine. `$!MAP=2` will also show the percentage of VM memory that each segment occupies.

(Prior to 6.40, the `-p` switch showed the segment percentages.)

**$!MEM**

Show memory allocations and deallocations within the compiler.

(Prior to 6.40, the `-m` switch showed this information.)

**$!OBJECTS**

Show the object table when the game is complete.

The `Trace objects` directive will show this information at any point in the code.

(Prior to 6.40, the `-j` switch showed this information.)

**$!PROPS**

Show properties and attributes as they are defined.

(Prior to 6.40, this information was displayed by the `-n` switch.)

**$!RUNTIME** (same as `-g`)

Compile function tracing into the game. Every game function called will print a trace message. `$!RUNTIME=2` will also trace library calls; `$!RUNTIME=3` will also trace veneer calls.

[[This is the only trace option which affects the generated game file.]]

In Glulx mode, `$!RUNTIME=2` and above will cause Glk errors due to rulebooks printing trace messages when no output stream is set.

**$!STATS** (same as `-s`)

Print game statistics when compilation is complete.

**$!SYMBOLS**

Show the symbol table when the game is complete. `$!SYMBOLS=2` will also show compiler-defined symbols.

The `Trace symbols` directive will show this information at any point in the code.

**$!SYMDEF**

Show symbols as they are encountered and defined.

**$!TOKENS**

Show tokens as they are lexed. `$!TOKENS=2` will also show token types; `$!TOKENS=3` will also show their lexical contexts.

The `$!TOKENS` trace level can be changed at any point in the code with the `Trace tokens` directive. 

**$!VERBS**

Show the verb grammar table when the game is complete.

The `Trace verbs` directive will show this information at any point in the code.

# Language changes

A few elements of the Inform language itself have been updated or extended.

## Directives

A couple of notes on general directive syntax:

Directives in Inform 6 are not case-sensitive. These declarations are equivalent:

	Global varname;
	GLOBAL varname;
	global varname;

The DM4 does not state this, but it has been true in every version of the Inform compiler, so we can accept it as a principle of the language.

[[The DM4 mostly shows directives in title case: `Global`, `Zcharacter`, `Ifdef`. This is the manual's code style, not a language requirement.]]

[[Variable names and symbols are also case-insensitive. Language keywords, such as `if` and `return`, are not; they must be given in lower case. Case is also significant for the built-in print tokens `(A)`, `(a)`, `(The)`, and `(the)`; see §26.]]

Directives can also be written with a `#` sign:

	#Global varname;

For standalone directives, the `#` sign is optional. However, a few directives can be used within a routine or object definition. This allows conditional compilation of individual lines of code or object properties (§38). These directives are:

	Ifdef, Ifndef, Ifnot, Ifv3, Ifv5, Iftrue, Iffalse, Endif
	
When one of these directives appears within a routine or object definition, the `#` sign is required.

[[As of 6.35, the compiler will report errors for non-"if" directives appearing within a definition. In earlier versions, this error was not always checked.]]

**Abbreviate**

As of 6.40, the `Abbreviate` directive only creates an abbreviation when in economy (`-e`) mode. If the `-e` switch is not used, the directive is skipped and no space is consumed in the game's abbreviations table.

As of 6.42, abbreviations can be of any length. (In earlier versions, they were limited to 64 source-text characters.)

**Array**

The `Array` directive (§2.4) supports four ways to specify values:

	Array arrname --> N; 
	Array arrname --> expr1 expr2 ... exprN; 
	Array arrname --> [ expr1 expr2 ... exprN ]; 
	Array arrname --> "string";

The third form, with square brackets, is not documented in the DM4, but it has been supported since 6.0. Expressions between the brackets may be delimited by optional semicolons.

[[The bracket form allows us to define a one-entry array with an initializer: `Array arrname --> [ expr ];` This would not otherwise be possible. Note that zero-entry arrays are not permitted.]]

The `Array` directive supports a new array type in 6.30:

	Array arrname buffer N; 
	Array arrname buffer expr1 expr2 ... exprN; 
	Array arrname buffer [ expr1 expr2 ... exprN ]; 
	Array arrname buffer "string";

The `buffer` keyword defines `arrname` as a hybrid array, in which the first *word* `array-->0` contains the length (N), and the following N *bytes* `array->WORDSIZE`, `array->(WORDSIZE+1)` ... `array->(WORDSIZE+N-1)` contain the specified expression values or string characters.

[[This hybrid form is used by the `print_to_array` method (§3.12) and various library functions.]]

All forms of the `Array` directive support the `static` keyword, which was added in 6.34:

	Array arrname static -> 1 2 3 4;
	Array arrname static string "plugh";

The `static` keyword must appear before the array type (`->`, `-->`, `string`, `table`, or `buffer`). It indicates that the array should be placed in non-writable memory.

[[In Z-code, this places the array at the end of readable memory (after the dictionary and before the beginning of code storage). In Glulx, it places the array at the end of ROM (after string storage). A static array declaration should always provide initial values, since it cannot be updated at runtime. ]]

**Dictionary**

The DM4 marked the `Dictionary` directive as obsolete (§Table5), but it has been reinstated as of 6.33. It allows you to add a word to the game dictionary and set its optional dictionary flags.

	Dictionary 'word';
	Dictionary 'word' val1;
	Dictionary 'word' val1 val3;

The first form simply adds the word if it is not already in the dictionary. The second form also sets the `dict_par1` flag to the given value, or bitwise-or's the value to that flag if the word already exists. The third form also sets the `dict_par3` flag in the same way. 

The values can be numeric literals or constants. They can be 0-255 for Z-code, or 0-65535 for Glulx.

[[See also the `$ZCODE_LESS_DICT_DATA` setting above, which drops the `dict_par3` field from dictionary entries.]]

[[`dict_par2` cannot be set by this directive. It is always the verb number, or zero for words that are not verbs.]]

**Global**

As of 6.40, the `=` sign is optional when defining a global variable's initial value. These declarations are equivalent:

	Global foo = 12;
	Global foo 12;

[[This brings `Global` into harmony with `Constant`, for which the `=` sign has always been optional.]]

In early versions of Inform, the `Global` directive could also be used to define arrays. This usage has been deprecated since at least Inform 6.0, but the compiler still recognized declarations like:

	Global array --> 8;

...as well as the even older forms `Global data`, `Global initial`, and `Global inistr`. As of 6.40, all of these obsolete forms have been removed. Use `Global` for global variables and `Array` for arrays.

**Ifv3**

This is mentioned in the DM4 as being for compiler maintenance only (§Table5). In fact it is used by the library, so it's worth documenting. This is a conditional compilation directive, like `Iftrue`, which compiles code when building Z-code V3 (only). It is equivalent to:

	#Ifdef TARGET_ZCODE;
	#Iftrue (#version_number == 3);
	! ...code...
	#Endif;
	#Endif;

**Ifv5**

This misnamed directive is also used by the library (§Table5). It conditionally compiles code when building Z-code V4 and later *or* Glulx. Thus it is the converse of `Ifv3`. (The misleading name is left over from much earlier versions of Inform.)

**Import**

The `Import` directive no longer exists as of 6.40. (This, like `Link`, was used for the obsolete module-linking feature.)

**Link**

The `Link` directive no longer exists as of 6.40.

**Lowstring**

The `Lowstring` directive has been supported since (at least) Inform 5, but it is not needed in Inform 6. It is therefore deprecated and undocumented in the DM4. We will describe it here for information's sake.

	Lowstring Text "text";

In Z-code, this places an encoded string within readable memory (the first 64k). `Text` is defined as a constant whose value is `(address/2)`. The string can therefore be printed this way:

	print (address) (2*Text);

The constant can also be used with the `string` statement:

	string 14 Text;

This sets dynamic string 14 to the string `"text"`. However, it is more usual (and documented in §1.11) to use a string literal rather than `Lowstring`:

	string 14 "text";

The `Lowstring` directive is not supported in Glulx.

**Origsource**

The `Origsource` directive allows you to mark part of a source file as having been generated from another file. (E.g, an Inform 7 source file.) This directive was added in 6.34.

	Origsource "Filename";
	Origsource "Filename" 10;
	Origsource "Filename" 10 40;
	Origsource;

This declares that all following lines are derived from the given filename. This will be reported in error messages and debug output. You may optionally provide a line number and a character number within the line (10 and 40, in these examples).

The declaration holds through the next `Origsource` directive (but does not apply to included files). The fourth form, with no arguments, clears the declaration. 

**Property**

As of 6.36, it is now possible to declare an individual property with the `Property` directive:

	Property individual propname;

This gives us a total of four forms of the directive:

	Property [additive] name;
	Property [additive] name defaultexpr;
	Property [additive] name alias oldname;
	Property individual name;

Note that an individual property cannot be `additive`, have a default value, or `alias` another property.

The `long` keyword can be applied to any `Property` directive, but it has no effect except a deprecation warning. (All properties have been `long`, which is to say word-sized, since Inform 5.)

As of 6.36, it is possible to declare a property called `long`, `additive`, or `individual`, even though these are keywords for the `Property` directive.

	! This declares an additive common property called "long" with default value 12.
	Property additive long 12;

Concerning Z-code limits, the DM4 says:

> Only 62 [common properties] are available, of which the compiler uses 3 and the library a further 47.

This is poorly phrased. The Z-machine (V4+) permits 63 common properties (numbered 1 to 63). The compiler defines three: the `name` property plus two hidden properties which are used internally. So the game and library may declare 60 *more* common properties between them.

**Replace**

The `Replace` directive (§25) allows you to redefine a function which has already been defined (such as in a library or in the veneer).

[[The DM4 says that you can only replace functions in files marked with the `System_file` directive. This limitation has been removed.]]

The `Replace` directive has two forms, of which the second was added in 6.33:

	Replace Func;
	Replace Func OriginalFunc;

Multiple definitions of `Func()` may follow the `Replace` directive. `Func` will refer to the last-defined version, except that definitions in normal files are preferred over definitions in `System_file` files or the veneer. With the second form, `OriginalFunc` will refer to the *first*-defined version of the function.

**Switches**

As of 6.40, the `Switches` directive is obsolete and generates a deprecation warning. Use `!%` header comments instead.

This has always been documented to be used "at the very beginning of your source code" (§39). However, this was only weakly enforced; the compiler only checked that it was used before the first constant was defined. As of 6.40, it may only be used before the first constant or routine is defined.

**Trace**

The `Trace` directive allows you to adjust various trace settings and display information during compilation. As of 6.40, it is deprecated in favor of [trace options](#traceopts).

Prior to 6.36, it was limited to a few kinds of trace information and its syntax was rather ad-hoc. As of 6.40, it is still limited, but its syntax is more consistent.

The `Trace` directive has two flavors.

	Trace dictionary
	Trace objects
	Trace symbols
	Trace verbs

Each of these prints the named data table *as of that point in the compilation*. The equivalent trace option (`$!DICT`, `$!OBJECTS`, `$!SYMBOLS`, `$!VERBS`) print the named table when compilation is complete.

(For consistency with the trace option system, these four lines can take an optional number. This is only meaningful for `Trace symbols 2`, which, like `$!SYMBOLS=2`, prints more symbol info.)

	Trace assembly [val]
	Trace expressions [val]
	Trace tokens [val]

Each of these adjusts the level of the equivalent named trace option (`$!ASM`, `$!EXPR`, `$!TOKENS`). The optional value may be `off` (0), `on` (1), or any number. If no value is given, the option is set `on` (1).

	Trace [val]

Equivalent to `Trace assembly [val]`.

	Trace lines [val]
	Trace linker [val]

`Trace lines` was intended to support a line-tracing feature which was never implemented. `Trace linker` supported the module-linking feature, which no longer exists. These options now do nothing.

[[Trace options cannot print tables or change trace levels partway through compilation; that ability is only available through the `Trace` directive. The directive will therefore be retained. However, this ability is not very useful, so it seems reasonable to consider it deprecated.]]

**Undef**

The `Undef` directive allows you to remove a previously-defined constant. This directive was added in 6.33.

	Undef Const;

This leaves the `Const` symbol undefined. If `Const` was never defined, this does nothing.

[[When tested with the `Ifdef` directive, a constant is considered undefined only *after* the `Undef` directive, just as it is considered defined only *after* its original declaration. This is somewhat inconsistent with Inform's handling of constants in expressions (routine code), where they can freely be used before or after being declared.]]

[[`Undef`'ing constants which are forward-declared leads to confusing behavior. It is best to consider `Undef` purely as an adjunct to `Ifdef`.]]

**Version**

The `Version` directive is mentioned in the DM4 as being obsolete (§Table5). As of 6.40, it generates a deprecation warning. Use the `-v3` command-line switch or `!% -v3` header comment instead.

As of 6.36, this directive may only be used before the first routine is defined. (This limitation reduces, but does not eliminate, various code generation bugs.)

## Statements

**`<`Action`>`**

The action statements `<Action>` and `<<Action>>` (§6) now support up to four arguments. The `Actor` forms are new as of 6.33.

	<Action>
	<Action Noun>
	<Action Noun Second>
	<Action, Actor>
	<Action Noun, Actor>
	<Action Noun Second, Actor>

All provided arguments are passed to the `R_Process()` function. The `Actor` value (after the comma) will be the fourth argument if provided. Thus, `<Action, Actor>` will invoke `R_Process(Action, 0, 0, Actor)`.

[[`R_Process()` is typically implemented by the Inform library. If there is no library implementation, the veneer fallback simply prints the arguments. Note that support for the four-argument form was introduced in library 6/12; earlier libraries ignore the `Actor` argument.]]

[[As in previous versions of Inform, the `Action` argument can either be a bare action name or a parenthesized expression which produces an action value. Thus, `<Take lamp>` and `<(##Take) lamp>` are equivalent.]]

[[The `Actor` forms direct the action as a command to an NPC: "ACTOR, ACTION NOUN SECOND". Note that the statement ordering does not match how the player would usually type an NPC command. Inform's lexer is not able to handle that ordering consistently, so the statement has to take `Actor` last.]]

**`@`Assembly**

As of 6.40, the Glulx opcodes `@hasundo` and `@discardundo` (Glulx spec 3.1.3) are supported.

As of 6.42, the Z-code opcodes `@set_true_colour` and `@buffer_screen` (Z-Spec 1.1) are supported.

As of 6.42, assembly language (§41) allows you to specify bytes directly:

```
@ -> $8B $04 $D2;
```

This writes the given bytes into the current location of the function being compiled. Byte values must be numbers or defined numeric constants. It is up to the author to ensure that the bytes form valid instructions.

[[These three bytes form the Z-code opcode for `@ret 1234`. So this line is equivalent to the statement `return 1234`. In Glulx, you would need different bytes to achieve the same effect.]]

You can also specify values as words:

```
@ --> $00 $FFEE;
```

In this form, each entry is written as a two-byte (Z) or four-byte (G) sequence. The `@ -->` statement accepts general constant values such as object, string, or function addresses.

[[This feature is intended for testing new or experimental interpreter features, or exploring the behavior of interpreters in unexpected conditions. Most authors will never need it.]]

**Print**

The capitalized `(A)` print token joins `(a)`, `(The)`, and `(the)` as of 6.30; see §26.

	print (A) lamp;

This calls the `CInDefArt()` veneer function.

As noted above, the `(property)` token will print property numbers (rather than names) when the `$OMIT_SYMBOL_TABLE` option is used.

**Switch**

As of 6.42, switch case values can be parenthesized expressions, as long as the expressions are compile-time constants. In previous versions, they had to be literals or constant symbols, possibly preceded by a minus sign.

	Constant CONST = 5;

	! These have always worked.
	switch (x) {
		0: return 0;
		1: return 1;
		-2: return -2;
		CONST: return 5;
		-CONST: return -5;
	}
	
	! These also work as of 6.42.
	switch (x) {
		(0): return 0;
		(-(1)): return -1;
		(CONST): return 5;
		(CONST+1): return 6;
		(CONST | 3): return 7;
	}

If the case does not begin with an open-paren, it follows the old rules: it must be a literal or a constant symbol with an optional minus sign.

A case may also have several values or several expressions. Expression parsing applies as long as the *first* value is wrapped in parens. Wrapping the entire list in parens also works, because of the way Inform parses comma expressions.

	switch (x) {
		1, 2, 3: return 0;                   ! old style
		(4), (CONST), (CONST+1): return 1;   ! new style
		(10), CONST+6, CONST+7: return 2;    ! this also works
		(20, CONST+16, CONST+17): return 3;  ! as does this
	}

Range cases using `to` (such as `3 to 7`) *cannot* use parenthesized expressions.

Action cases which are not inside a `switch` statement cannot use parenthesized expressions. (These are the cases usually found in `before` and `after` properties, etc.) These top-level cases must be bare action names, as described in §4.

## Dynamic strings

The DM4 (§1.11) describes "printing-variables", also called dynamic strings. By embedding a code like `@01` in a string, you can interpolate another literal string value. You set the interpolated value with a statement like

	string 1 "text";
	print "This is the @01.^";

As of 6.40, dynamic string interpolations may look like `@(1)`, with any nonnegative number inside the parens. You may also write `@(N)`, where `N` is a defined numeric constant.

	Constant TEXTVAL 1;

...and then...

	string TEXTVAL "text";
	print "This is the @(1), or equivalently @(TEXTVAL).^";

The old format `@01` is still supported, but only supports numbers of exactly two digits.

[[The `string` statement has always supported numbers and numeric constants, so it has not changed.]]

The number of dynamic strings is limited, but the limit may be increased with the `$MAX_DYNAMIC_STRINGS` setting. See [Compiler settings](#memsettings).

## Dictionary words

As of 6.43, a dictionary word literal may have a suffix indicating flags to set in `dict_par1`. The suffix consists of `//` followed by any number of flags:

- `p`: Set the plural flag (bit 2)
- `s`: Set the singular flag (bit 4)
- `n`: Set the noun flag (bit 7)
- `~p`: Do not set the plural flag this time
- `~s`: Do not set the singular flag this time
- `~n`: Do not set the noun flag this time

6.42 supported the same suffixes with the exception of `s` and `~s`, which were added in 6.43.

In 6.41 and earlier, only the `//p` suffix (§29) and the flagless `//` suffix (§1.4) were supported. (The flagless form `'x//'` just indicates that the constant is a dict word. This is useful to distinguish single-letter dict words from character constants.)

Inform assumes that all words mentioned in the source are nouns. The only exception is the `Verb` directive, which contains verbs and prepositions. In effect, all words mentioned in properties, globals, arrays, or functions default to `//n`. You should explicitly mark words with `//~n` if you don't mean to give them the noun flag just by mentioning them.

[[For example, if you're writing a LanguageVerb() routine (§37), you might mark verb words as `'i//~n'`, `'inv//~n'`, `'inventory//~n'`.]]

Contrariwise, Inform never assumes that words are plural. Therefore, only the `//p` and `//~n` flags are useful. `//~p` and `//n` are supported only for the sake of consistency.

Note that if a word is marked both `//p` and `//~p` in different places, its plural flag is set. Similarly, if it's marked `//n` anywhere, *even as a default*, its noun flag is set. The `~` forms do not erase a flag; they only prevent it from being set right then.

The `$DICT_IMPLICIT_SINGULAR=1` option (added in 6.43) tells Inform to assume that non-plural nouns are singular. That is -- with this option set -- if a word is mentioned in the source (thus being `//n` by default), and does not have an explicit `//p`, then its `//s` flag is set. If a word is marked both `//p` and `//~p` in different places, then it will wind up with *both* the `//s` and `//p` flags.

The `$DICT_TRUNCATE_FLAG=1` option (added in 6.43) tells Inform to set bit 6 for words which exceed `$DICT_WORD_SIZE` and therefore get truncated. This includes Z-code words that ends with an incomplete Z-character sequence. There is no `//` suffix for this bit. As with the other flags, if a word is truncated in one place and not another (say, if both `'superhero'` and `'superheroine'` are used), then the flag is set.

[[Note that, by default, suffixes are ignored in truncated dict words. Use the `$LONG_DICT_FLAG_BUG=0` setting to change this.]]

[[See also the `Dictionary` directive, which allows you to set arbitrary bits in `dict_par1` or `dict_par3`.]]

## Constants

The compiler defines various constants describing the game file. The game (and library) may use these to examine compiled data.

[[Some constants begin with `#`; others do not. This is a mostly internal distinction which is not important for authors. The difference is that regular constants must be defined at the start of compilation. `#` constants, such as `#dictionary_table`, may not be known until compilation is complete.]]

[[Only a few of the compiler's `#` constants are documented here. The majority are intended to support Infix, and are available only in Z-code.]]

Constants defined with no given value are typically meant to be checked with `#Ifdef`. They have the default value 0.

**#version_number**

The Z-code version number. (Z-code only.)

**#readable_memory_offset**

The address of the start of high memory (routine and string segments). This is also found in the header at address 4. (Z-code only.)

**#dictionary_table**

The address of the dictionary. In Z-code, this is also found in the header at address 8. (Glulx-only until 6.40.)

**#grammar_table**

The address of the grammar table. In Z-code, Inform places this at the start of static memory, so it can be found in the header at address 14. (Glulx-only until 6.40.)

**#actions_table**

The address of the actions table. This table maps an action number (e.g. `##Jump`) to its action routine (e.g. `JumpSub`).

**#dict_par1**, **#dict_par2**, **#dict_par3**

In Z-code, the byte offsets of the three flags within a dictionary word entry.

In Glulx, these are the byte offsets of the *low byte* (second byte) of the three flags.

If `$ZCODE_LESS_DICT_DATA` is set, `#dict_par3` is not available.

**#identifiers_table**

The address of a set of tables containing property names, attribute names, and other code elements. These are typically used only by debug commands, runtime error messages, and Infix.

If `$OMIT_SYMBOL_TABLE` is set, this constant (and other related constants) are not available. Trying to use them will be reported as a compile error.

**TARGET_ZCODE**, **TARGET_GLULX**

Exactly one of these will be defined, depending on the game file format.

**WORDSIZE**

This is the byte size of a VM word or address: 2 in Z-code, 4 in Glulx.

**STRICT_MODE**, **DEBUG**, **INFIX**

These are defined by the `-S`, `-D`, `-X` switches respectively.

[[Prior to 6.40, `MODULE_MODE` and `USE_MODULES` were defined by the `-M` and `-U` switches respectively. These no longer exist.]]

**DICT_WORD_SIZE**

This is the byte size (not Z-character count!) of a dictionary word string. In Z-code, it will be 4 (v3) or 6 (v4+). In Glulx, it is controlled by the `$DICT_WORD_SIZE` setting.

**DICT_ENTRY_BYTES**

This is the byte size of a complete dictionary entry, including flags. In Z-code, it will be `DICT_WORD_SIZE+3`, or `DICT_WORD_SIZE+2` if `$ZCODE_LESS_DICT_DATA` is set. In Glulx, it is `DICT_WORD_SIZE+7`, or `4*DICT_WORD_SIZE+12` if `$DICT_CHAR_SIZE` is 4.

**DICT_CHAR_SIZE**

The byte size of one character in a dictionary word. This is controlled by the `$DICT_CHAR_SIZE` setting; it will be either 1 or 4. (Glulx-only.)

**DICT_IS_UNICODE**

This is defined as 1 if `$DICT_CHAR_SIZE` is 4. (Glulx-only.)

**OMIT_SYMBOL_TABLE**

This is defined if the `$OMIT_SYMBOL_TABLE` setting is used.

**NUM_ATTR_BYTES**

The number of bytes reserved in each object record for (boolean) attributes. (Each byte stores eight attributes.) In Z-code, this will be 6. In Glulx, it is controlled by the `$NUM_ATTR_BYTES` setting; it will always be a value of the form `4*i+3`.

**INDIV_PROP_START**

The property number of the first individual property. This is controlled by the `$INDIV_PROP_START` setting. (Glulx-only.) (In Z-code, this setting is always 64 so no constant is defined.)

**GOBJFIELD_CHAIN**, **GOBJFIELD_NAME**, **GOBJFIELD_PROPTAB**, **GOBJFIELD_PARENT**, **GOBJFIELD_SIBLING**, **GOBJFIELD_CHILD**

The offset in words (not bytes!) of the six address fields in a Glulx object record. For example, the address of the object's property table can be found at `obj-->GOBJFIELD_PROPTAB`. (Glulx-only.)

**GOBJ_EXT_START**

The offset of bytes of the extended object data in an object record. The length of this data is controlled by the `$GLULX_OBJECT_EXT_BYTES` setting. (Glulx-only.)

**GOBJ_TOTAL_LENGTH**

The byte size of a complete object record. This will be `1+NUM_ATTR_BYTES+6*WORDSIZE`, plus `$GLULX_OBJECT_EXT_BYTES` if that is set. (Glulx-only.)

**FLOAT_INFINITY**, **FLOAT_NINFINITY**, **FLOAT_NAN**

Positive and negative infinity and NaN for Glulx floating-point operations. (Glulx-only.)

**DOUBLE_HI_INFINITY**, **DOUBLE_LO_INFINITY**, **DOUBLE_HI_NINFINITY**, **DOUBLE_LO_NINFINITY**, **DOUBLE_HI_NAN**, **DOUBLE_LO_NAN**

Positive and negative infinity and NaN for Glulx double-precision operations. (Glulx-only.)

## Operators

### Logical precedence

The table of condition operators (§Table1B) shows `&&`, `||`, and `~~` as having equal precedence. This is ambiguous about expressions like `(~~X && Y)`. In fact, the compiler has always (at least since 6.0) parsed this as applying `~~` to the conjunction `(X && Y)`:

	! These statements are equivalent:
	val = ~~X && Y;
	val = ~~(X && Y);

If you want the `~~` to apply only to `X`, you must add explicit parentheses:

	! Not equivalent to the above!
	val = (~~X) && Y;

Similarly, the bitwise expression `(~X & Y)` is parsed as `(~(X & Y))`.

Given this, it makes sense to consider the logical `~~` operator as having a precedence level of 1.5, and the bitwise `~` operator as having a precedence level of 5.5.

### The `or` operator

The `or` operator is described in §1.8, but without a full explanation.

`or` may only be used to provide a list of values to the right of a comparison operator:

    if (val == 2 or 4 or 8) ...
    if (obj in trunk or knapsack) ...
    if (obj has container or supporter) ...

The expression is true if the left-hand value matches any of the values on the right.

For negative-sense operators, the expression is true if the left-hand value matches *none* of the values on the right:

    if (val ~= 2 or 4 or 8) ...
    if (obj notin trunk or knapsack) ...
    if (obj hasnt container or supporter) ...

[[Strict Boolean logic would have us write these negative comparisons with "and" rather than "or". Inform doesn't go that far. All of the expressions above follow the natural English sense of "or".]]

This becomes somewhat confusing when we consider ordering comparisons. The manual gives this example:

    if (x > 100 or y) ...

> [...] to test whether x is bigger than the minimum of 100 and y.

This is consistent with the earlier examples; the expression is true if `(x > 100)` *or* `(x > y)`. However, it takes some squinting to realize this.

The `>=` and `<=` operators are even worse. The compiler treats these as *negative-sense* operators (because that's how the Z-machine architecture constructed them). Therefore:

    if (x <= 100 or y) ...

This is true if `x` is less than or equal to *both* `100` *and* `y`. (That is, it is treated as the exact inverse of the previous example.) This is unintuitive even if you have absorbed the previous examples.

As of 6.36, if you use `or` with the `>=` and `<=` operators, the compiler will generate a warning.

## Class behavior

### Inheritance

The DM4 (§3.8) gives this example of multiple inheritance:

	Object "goose that lays the golden eggs"
		class Bird Treasure;

> [This goose] inherits from Object first and then Bird and then Treasure, attribute settings and property values from later-mentioned classes overriding earlier ones, so if these classes should give contradictory instructions then Treasure gets the last word.

In fact this is not true (and never has been). The language behavior is somewhat complex.

Property values are determined by the *first* class listed, whether that is given as a directive (`Treasure goose`) or a `class` keyword (`Object goose class Treasure`). Of course, if the object itself gives a property value, that overrides all inherited values.

If one class inherits from another, the derived class property overrides the superclass property, as one would expect.

*Additive* properties follow the same logic, but their values accumulate, rather than overriding each other. An additive property gains values from the object's own definition (first), then from each class in (forward) listing order.

[[This supports the I6 library convention that additive properties (`before`, `after`, `life`) contain lists of inline routines. These are tested in forward order; each routine may return `true` to indicate that the event is handled, or `false` to pass control to the next routine. The precedence order is thus, again, the object followed by each class in listing order.]]

Attributes follow the same rule, except that *classes cannot negate attributes set by other classes*.

	Class Bird has ~heavy;
	Class Treasure has heavy;
	Object goose class Bird Treasure;

In this example, the goose object gains the `heavy` attribute because at least one of its classes sets it. This will be true no matter what order the classes are listed in. The `has ~heavy` declaration in class `Bird` has no effect.

Objects can of course use `has ~attr` to negate attributes inherited from classes. Derived classes can negate attributes inherited from superclasses. The limitation applies only to conflicts between an object's classes.

### Class `copy` and `recreate`

The `copy` and `recreate` class methods likewise diverge from the manual. §3.11 says:

	Plant.copy(Gilded_Branch, Poison_Ivy);
	Treasure.recreate(Gilded_Branch);

> It's rather useful that recreate and copy can be sent for any instances, not just instances which have previously been created. For example, [the copy statement above] copies over all the features of a Plant from Poison_Ivy to Gilded_Branch, but leaves any other properties and attributes of the gilded branch alone. Likewise, [the recreate statement] only resets the properties to do with Treasure, leaving the Plant properties alone.

In fact, the question of what classes originated the properties and attributes does not arise. The `copy` method copies *all* attributes, positive and negative, from the source to the target. It also copies the value of every property which is declared by both the source and target and has the same length on each.

The `recreate` method does a `copy` from an unmodified instance of the class, followed by a `create` call. It will therefore reset all attributes, as well as any properties declared by both the object and the class.

[[These behaviors are arguably compiler bugs. However, they have been established behavior since Inform 6.0. We prefer to document them rather than trying to adjust them at this late date.]]

## Glulx support

The ability to compile a Glulx game file (the `-G` option) was introduced in 6.30. This came with a few additions to the Inform language.

One of the constants `TARGET_ZCODE` and `TARGET_GLULX` is always defined. These can be used with the `Ifdef` directive to mark code that should only be compiled on one platform.

The constant `WORDSIZE` is always defined; it is 2 in Z-code and 4 in Glulx.

As noted above, code under the `Ifv5` directive is also compiled for Glulx.

### Language features supported only in Glulx

If the first argument to a function is named `_vararg_count`, arguments will be passed on the VM stack, with `_vararg_count` set to the number of arguments.

Literals beginning with `$+` and `$-` are compiled as floating-point constants. For example: `$+1.0`, `$-1e3`, `$+2.5e-3`. Double-precision floating-point is also supported; these values require 64 bits, or two Glulx words each, and are thus written `$>+1.0` (the high word) and `$<+1.0` (the low word).

The constants `FLOAT_INFINITY`, `FLOAT_NINFINITY`, `FLOAT_NAN`, `DOUBLE_HI_INFINITY`, `DOUBLE_LO_INFINITY`, `DOUBLE_HI_NINFINITY`, `DOUBLE_LO_NINFINITY`, `DOUBLE_HI_NAN`, `DOUBLE_LO_NAN` are also defined.

[[Note that the standard Inform arithmetic operators (`+`, `-`, etc) do not work with floating-point values. You must use Glulx opcodes. (`@fadd`, `@fsub`, etc for single-precision; `@dadd`, `@dsub`, etc for double-precision.)]]

[[Double-precision literals are not guaranteed to compile to exactly the same word values on all platforms. The last digit of the low word may vary. This is because the Inform compiler relies on platform floating-point math, which is inherently imprecise.]]

The `print_to_array()` method (§3.12) requires two arguments, rather than one (as in Z-code).

### Language features not supported in Glulx

Infix (the `-X` option, §7) is not available.

The `Zcharacter` directive (§36) is not available, since Glulx does not use the ZSCII character set.

The `save`, `restore`, and `read` statements (§1.15, §2.5) are not available. These features require more complex behavior in Glulx and cannot be encapsulated in a single statement. They must be implemented in library code using the `@glk` opcode.

## Z-machine V3/4 limitations

Early releases of Inform (through Inform 5) were designed to support all versions of the Z-machine from 3 through 6. However, Inform 6 extended the language in ways which require more advanced VM support. Therefore, certain language features require Z-machine version 5 or later.

- Debug mode and strict mode (`-D` and `-S`, §7) are not available in V3 and V4.
- The method call expression `obj.prop()` is not available in V3 and V4.

You can work around the lack of `obj.prop()` by writing:

	@push self;
	self = obj;
	addr = obj.prop;
	addr();
	@pull self;

[[The lines dealing with `self` may be omitted if the property routine does not rely on `self`.]]

In general, Inform 6 is able to compile older source code to V3 if the source *and the library* avoids the `obj.prop()` syntax. This means you cannot use the Inform 6 library. You must use the [Inform 5 library][i5lib], or one of the alternative libraries designed for V3, such as [metro84][] or [PunyInform][].

[[It is possible to re-implement a limited version of `obj.prop()` for V3 by replacing the `CA__Pr` and `Cl__Ms` veneer routines. Some alternative libraries do this.]]

# Debug file format { #debugformat }

The `-k` switch generates a `gameinfo.dbg` file which describes the compiled game. The [Inform Technical Manual][techman] (§12.5) documents a binary format ("Version 0") for this file. However, that format is no longer used. As of Inform 6.33, a more verbose XML format ("Version 1") is generated; this section describes it.

[techman]: https://inform-fiction.org/source/tm/

[[By "verbose", we mean that the debug info for Advent.inf approaches 2 megabytes of XML. The debug info for a one-line Inform 7 game reaches 11 megabytes. The greatest bulk of the data is `<source-code-location>` and `<sequence-point>` tags.]]

## Overview

Debugging information files are written in XML and encoded in UTF-8. They therefore begin with the following declaration:

	<?xml version="1.0" encoding="UTF-8"?>

Beyond the usual requirements for well-formed XML, the file adheres to the conventions that all numbers are written in decimal, all strings are case-sensitive, and all excerpts from binary files are Base64-encoded.

## The top level

The root element is given by the tag `<inform-story-file>` with three attributes: the version of the debug file format being used, the name of the program that produced the file, and that program's version. For instance,

	<inform-story-file version="1.0" content-creator="Inform"
			   content-creator-version="6.33">
	  ...
	</inform-story-file>

Any of the elements described below (except `<local-variable>`, `<sequence-point>`, `<source-code-location>`) may appear in the ellipses.

## Story file prefix

The story file prefix contains a Base64 encoding of the story file's first bytes so that a debugging tool can easily check whether the story and the debug information file are mismatched. For example, the prefix for a Glulx story might appear as

	<story-file-prefix>
	  R2x1bAADAQEACqEAAAwsAAAMLAAAAQAAAAAAPAAIo2Jc
	  6B2XSW5mbwABAAA2LjMyMC4zOAABMTIxMDE1wQAAMA==
	</story-file-prefix>

The story file prefix is mandatory, but its length is unspecified. The current version of the Inform compiler records 64 bytes, which seems sufficient.

## Story file sections

Story file sections partition the story file according to how the data will be used. For the Inform 6 compiler, this partitioning is the same as the memory map printed by the `-z` switch.

A record for a story file section gives a name for that section, its beginning address (inclusive), and its end address (exclusive):

	<story-file-section>
	  <type>abbreviations table</type>
	  <address>64</address>
	  <end-address>128</end-address>
	</story-file-section>

The names currently in use include those from the Inform Technical Manual (§12.5):

	abbreviations table
	header extension (Z-code only)
	alphabets table (Z-code only)
	Unicode table (Z-code only)
	property defaults
	object tree
	common properties
	class numbers
	individual properties (Z-code only)
	global variables
	array space
	grammar table
	actions table
	parsing routines (Z-code only)
	adjectives table (Z-code only)
	dictionary
	code area
	strings area

plus one addition for Z-code:

	abbreviations

two additions for Glulx:

	memory layout id
	string decoding table

and three additions for both targets:

	header
	identifier names
	zero padding

Names may repeat; Glulx story files, for example, sometimes have two zero padding sections.

A compiler that does not wish to subdivide the story file should emit one section for the entirety and give it the name

	story

## Source files

Source files are encoded as in the example below. Each file has a unique index, which is used by other elements when referring to source code locations; these indices count from zero. The file's path is recorded in two forms, first as it was given to the compiler via a command-line argument or include directive but without any path abbreviations like `>` (the form suitable for presentation to a human) and second after resolution to an absolute path (the form suitable for loading the file contents). All paths are written according to the conventions of the host OS. The language is, at present, either "Inform 6" or "Inform 7". More languages may added in the future.

	<source index="0">
	  <given-path>example.inf</given-path>
	  <resolved-path>/home/user/directory/example.inf</resolved-path>
	  <language>Inform 6</language>
	</source>

If the source file is known to appear in the story's Blorb, its chunk number will also be recorded:

	<source index="0">
	  <given-path>example.inf</given-path>
	  <resolved-path>/home/user/directory/example.inf</resolved-path>
	  <language>Inform 6</language>
	  <blorb-chunk-number>18</blorb-chunk-number>
	</source>

## Table entries; grammar lines

Table entries are data defined by particular parts of the source code, but without any corresponding identifiers. The `<table-entry>` element notes the entry's type, the address where it begins (inclusive), the address where it ends (exclusive), and the defining source code location(s), if any:

	<table-entry>
	  <type>grammar line</type>
	  <address>1004</address>
	  <end-address>1030</end-address>
	  <source-code-location>...</source-code-location>
	</table-entry>

The current version of the Inform compiler only emits `<table-entry>` tags for grammar lines; these data are all located in the grammar table section.

## Named values

Records for named values store their identifier, their value, and the source code location(s) of their definition, if any. For instance,

	<constant>
	  <identifier>MAX_SCORE</identifier>
	  <value>40</value>
	  <source-code-location>...</source-code-location>
	</constant>

would represent a named constant.

Attributes, properties, actions, fake actions, objects, arrays, and routines are also names for numbers, and differ only in their use; they are represented in the same format under the tags `<attribute>`, `<property>`, `<action>`, `<fake-action>`, `<object>`, `<array>`, and `<routine>`. (Moreover, unlike in Version 0, fake actions are not recorded as both fake actions and actions.)

The records for constants include some extra entries for the system constants tabulated in the Inform Technical Manual (§12.2), even though these are not created by Constant directives. Entries for `#undef`ed constants are also included, but necessarily without values.

Some records for objects will represent class objects. In that case, they will be given with the tag `<class>` rather than `<object>` and include an additional child to indicate their class number:

	<class>
	  <identifier>lamp</identifier>
	  <class-number>5</class-number>
	  <value>1560</value>
	  <source-code-location>...</source-code-location>
	</class>

Records for arrays also have extra children, which record their size, their element size, and the intended semantics for their zeroth element:

	<array>
	  <identifier>route</identifier>
	  <value>1500</value>
	  <byte-count>20</byte-count>
	  <bytes-per-element>4</bytes-per-element>
	  <zeroth-element-holds-length>true</zeroth-element-holds-length>
	  <source-code-location>...</source-code-location>
	</array>

And finally, `<routine>` records contain an `<address>` and a `<byte-count>` element, along with any number of the `<local-variable>` and `<sequence-point>` elements, which are described [below](#debug_localvars). The address is provided because the identifier's value may be packed.

Sometimes what would otherwise be a named value is in fact anonymous; unnamed objects, embedded routines, some replaced routines, veneer properties, and the Infix attribute are all examples. In such a case, the `<identifier>` subelement will carry the XML attribute

	artificial

to indicate that the compiler is providing a sensible name of its own, which could be presented to a human, but is not actually an identifier. For instance:

	<routine>
	  <identifier artificial="true">lantern.time_left</identifier>
	  <value>1820</value>
	  <byte-count>80</byte-count>
	  <source-code-location>...</source-code-location>
	  ...
	</routine>

Artificial identifiers may contain characters, like the full stop in `lantern.time_left`, that would not be legal in the source language.

## Global variables

Globals are similar to named values, except that they are not interpreted as a fixed value, but rather have an address where their value can be found. Their records therefore contain an `<address>` tag in place of the `<value>` tag, as in:

	<global-variable>
	  <identifier>darkness_witnessed</identifier>
	  <address>1520</address>
	  <source-code-location>...</source-code-location>
	</global-variable>

## Local variables { #debug_localvars }

The format for local variables mimics the format for global variables, except that a source code location is never included, and their memory locations are not given by address. For Z-code, locals are specified by index:

	<local-variable>
	  <identifier>parameter</identifier>
	  <index>1</index>
	</local-variable>

whereas for Glulx they are specified by frame offset:

	<local-variable>
	  <identifier>parameter</identifier>
	  <frame-offset>4</frame-offset>
	</local-variable>

If a local variable identifier is only in scope for part of a routine, its scope will be encoded as a beginning instruction address (inclusive) and an ending instruction address (exclusive):

	<local-variable>
	  <identifier>rulebook</identifier>
	  <index>0</index>
	  <scope-address>1628</scope-address>
	  <end-scope-address>1678</end-scope-address>
	</local-variable>

Identifiers with noncontiguous scopes are recorded as one `<local-variable>` element per contiguous region. It is possible for the same identifier to map to different variables, so long as the corresponding scopes are disjoint.

## Sequence points

Sequence points are stored as an instruction address and the corresponding single location in the source code:

	<sequence-point>
	  <address>1628</address>
	  <source-code-location>...</source-code-location>
	</sequence-point>

The source code location will always be exactly one position with overlapping endpoints.

Sequence points are defined as in the Inform Technical Manual (§12.4), but with the further stipulation that labels do not influence their source code locations, as they did in Version 0. For instance, in code like

	say__p = 1; ParaContent(); .L_Say59; .LSayX59;
	t_0 = 0;

the sequence points are to be placed like this:

	<*> say__p = 1; <*> ParaContent(); .L_Say59; .LSayX59;
	<*> t_0 = 0;

rather than like this:

	<*> say__p = 1; <*> ParaContent(); <*> .L_Say59; .LSayX59;
	t_0 = 0;

## Source code locations

Most source code locations take the following format, which describes their file, the line and character number where they begin (inclusive), the line and character number where they end (exclusive), and the file positions (in bytes) corresponding to those endpoints:

	<source-code-location>
	  <file-index>0</file-index>
	  <line>1024</line>
	  <character>4</character>
	  <file-position>44153</file-position>
	  <end-line>1025</end-line>
	  <end-character>1</end-character>
	  <end-file-position>44186</end-file-position>
	</source-code-location>

Line numbers and character numbers begin at one, but file positions count from zero.

In the special case where the endpoints coincide, as happens with sequence points, the end elements may be elided:

	<source-code-location>
	  <file-index>0</file-index>
	  <line>1024</line>
	  <character>4</character>
	  <file-position>44153</file-position>
	</source-code-location>

At the other extreme, sometimes definitions span several source files or appear in two different languages. The former case is dealt with by including multiple code location elements and indexing them to indicate order:

	<!-- First Part of Inform 6 Definition -->
	<source-code-location index="0">
	  <!-- Assuming file 0 was given with the language "Inform 6" -->
	  <file-index>0</file-index>
	  <line>1024</line>
	  <character>4</character>
	  <file-position>44153</file-position>
	  <end-line>1025</end-line>
	  <end-character>1</end-character>
	  <end-file-position>44186</end-file-position>
	</source-code-location>
	<!-- Second Part of Inform 6 Definition -->
	<source-code-location index="1">
	  <!-- Assuming file 1 was given with the language "Inform 6" -->
	  <file-index>1</file-index>
	  <line>1</line>
	  <character>0</character>
	  <file-position>0</file-position>
	  <end-line>3</end-line>
	  <end-character>1</end-character>
	  <end-file-position>59</end-file-position>
	</source-code-location>

The latter case is also handled with multiple elements. Note that indexing is only used to indicate order among locations in the same language.

	<!-- Inform 7 Definition -->
	<source-code-location>
	  <!-- Assuming file 2 was given with the language "Inform 7" -->
	  <file-index>2</file-index>
	  <line>12</line>
	  <character>0</character>
	  <file-position>308</file-position>
	  <end-line>12</end-line>
	  <end-character>112</end-character>
	  <end-file-position>420</end-file-position>
	</source-code-location>
	<!-- Inform 6 Definition -->
	<source-code-location>
	  <!-- Assuming file 0 was given with the language "Inform 6" -->
	  <file-index>0</file-index>
	  <line>1024</line>
	  <character>4</character>
	  <file-position>44153</file-position>
	  <end-line>1025</end-line>
	  <end-character>1</end-character>
	  <end-file-position>44186</end-file-position>
	</source-code-location>

# Bugs

A great number of bugs have been fixed since Inform 6.21. The list is not included here. See the [Release Notes][i6release] for details (older notes [here][i6relold]).

[i6release]: https://ifarchive.org/if-archive/infocom/compilers/inform6/ReleaseNotes.html
[i6relold]: https://inform-fiction.org/manual/ReleaseNotes-6.3x.html

However, it is worth noting that Z-code V3 code generation had been neglected since 6.15 and a number of bugs had crept in. 6.34 and 6.35 have addressed these; V3 should once again be usable.

Particular thanks to Daniel Fremont for the many bug reports uncovered by his input-fuzzing project.


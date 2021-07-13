# Inform 6 Reference Addendum {: .Title }

Language and compiler changes: releases 6.30 to 6.36 (in development)
{: .VersionHeader }

Maintained by IFTF: `<specs@ifarchive.org>`
{: .AuthorHeader }

(Last update: July 12, 2021)
{: .DateHeader }

Copyright 2020-21 by the Interactive Fiction Technology Foundation. This document is licenced under a [Creative Commons Attribution-ShareAlike 4.0 International License][bysa].

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

## Switch options (dash)

Classic options begin with a dash -- the traditional style of command-line tools. For example, the `-h` option (help) shows a page of output documenting how to run the compiler. `-h2` will show a page listing all options that begin with a dash (§Table3).

*New since the DM4:*

`-B`: In Z-code versions 6 and 7 (only), use different offset values for the packed addresses of routines and strings. In this mode, strings are distinguished by having odd (packed) addresses, whereas routines are even. This allows the game file to contain more executable code. (The default is `-~B`, where the routine and string segments use the same offset value, so string and routine values have different ranges.)

`-Cu`: Treat the source files as being in UTF-8 (Unicode) encoding.

[[Older options `-C1`, `-C2`, etc., are documented in the DM4 (§36); they treated the source files as being in one of the Latin-N encodings. `-Cu` is a new extension.]]

[[These options also affect the `gametext.txt` file created by the `-r` option. This transcript uses the same encoding as the source code.]]

[[When `-Cu` is used, the compiler does not add any characters to the Z-machine's "cheap" alphabet table. You can use the `Zcharacter` directive to add selected Unicode characters; see §36.]]

`-G`: Compile to Glulx format rather than Z-machine. The default output file will be given an `.ulx` extension.

`-G -vX.Y.Z`: In Glulx, specify the VM version number to note in the generated game file. For example, `-G -v3.1.0` would generate a game file that specifies VM spec 3.1.0.

[[Normally the compiler works out the earliest version number compatible with the features used by your game. You can use this option to specify a later version.]]

`-H`: In Glulx format, use Huffman encoding to compress strings. This is the default; to use uncompressed text, use `-~H`.

`-k`: Output debugging information to a file `gameinfo.dbg`. This switch is documented in the DM4 (§7), but the output format has changed. As of 6.33, it is an extremely verbose XML format which describes every facet of the compiled game file. Also, as of 6.35, the `-k` switch no longer automatically sets `-D`.

`-g3`: Trace calls to all functions. The DM4 documents `-g2` as doing this, but as of 6.21, `-g2` does not trace veneer functions. As of 6.35, `-g3` traces everything.

[[Note that `-g2` and above will cause runtime errors in Glulx games, due to printing trace information when no output window is available.]]

`-W`: Sets the number of words in the Z-code header extension table (Z-spec 1.0). The default is `-W3`. The `$ZCODE_HEADER_EXT_WORDS` setting does the same thing.

`-V`: Display the compiler version and exit with no further action.

## Path options (plus)

Options beginning with a plus set paths used by the compiler (§39). For example, `+DIRNAME` or `+include_path=DIRNAME` set the directory which is searched for include files.

You can also give a comma-separated list of paths: `+include_path=DIR1,DIR2,DIR3`

*New since the DM4:*

A double plus sign adds a new path or paths to an existing list. For example, `++include_path=DIRNAME` will add DIRNAME to the paths which are searched for include files. The newly-added paths will be searched first.

On the command line (but not in ICL files or comments), path options can be also specified in Unix style. (This is new in 6.35.)

	--path PATH=dir
	--addpath PATH=dir

## Compiler settings (dollar)

These were referred to as "memory settings" in the DM4 (§39). However, they now encompass a wide range of compiler behavior.

The `$LIST` setting will show a page of output listing all dollar-sign settings for Z-machine games. To see all settings for Glulx games, give the `-G` argument before `$LIST`.

[[If you supply a dollar-sign setting as a command-line option on MacOS or Unix, remember that the shell treats the dollar sign as a special character. You must escape the dollar sign so that it reaches the compiler:
	inform \$MAX_VERBS=255 source.inf
If you supply such a setting in a source file, using the `!%` format, you should *not* use the backslash.]]

*New since the DM4:*

A setting that begins with a hash sign (`$#`) will define an arbitrary numeric constant in the game code. If no value is supplied, the constant is defined as zero. This is equivalent to (and consistent with) the `Constant` directive. (New in 6.35.)

	$#SYMBOL
	$#SYMBOL=number
	
[[Thus, passing the `$#DEBUG` argument is equivalent to the `-D` option. Remember that Inform symbols are not case-sensitive; `$#debug` or `$#Debug=0` does the same thing.]]

On the command line (but not in ICL files or comments), compiler settings can also be specified in Unix style. (New in 6.35.) This avoids the need to escape dollar signs.

	--list
	--opt SETTING=number
	--define SYMBOL=number

As of 6.36, the following internal memory settings are no longer needed and have no effect: `$ALLOC_CHUNK_SIZE`, `$MAX_OBJECTS`, `$MAX_CLASSES`, `$MAX_SYMBOLS`, `MAX_PROP_TABLE_SIZE`, `$MAX_INDIV_PROP_TABLE_SIZE`, `$MAX_OBJ_PROP_COUNT`, `$MAX_OBJ_PROP_TABLE_SIZE`, `$MAX_ARRAYS`, `$MAX_STATIC_DATA`, `$MAX_ADJECTIVES`, `$MAX_VERBS`, `$MAX_VERBSPACE`, `$MAX_LABELS`, `$MAX_EXPRESSION_NODES`, `$MAX_SOURCE_FILES`, `$MAX_INCLUSION_DEPTH`, `$MAX_ACTIONS`, `$MAX_LINESPACE`, `$MAX_ZCODE_SIZE`, `$MAX_LINK_DATA_SIZE`, `$MAX_TRANSCRIPT_SIZE`, `$MAX_DICT_ENTRIES`, `$MAX_NUM_STATIC_STRINGS`, `$MAX_UNICODE_CHARS`.

Other settings which are new or updated since the DM4:

**$DICT_CHAR_SIZE**

The byte size of one character in the dictionary. This is only meaningful in Glulx. It can be 1 (dictionary characters are one byte) or 4 (dictionary characters are four-byte words).

**$DICT_WORD_SIZE**

The number of bytes in a dictionary word entry. (In Z-code this is 6, representing up to 9 Z-characters, and cannot be changed.)

**$GLULX_OBJECT_EXT_BYTES**

The number of extra zero bytes to add to each object table entry. This is writable memory which the game can use freely. (This is only meaningful in Glulx, as the Z-code object format is fixed by the spec.)

**$INDIV_PROP_START**

The index number of the first individual property. This also determines the maximum number of common properties. (In Z-code this is 64 and cannot be changed.)

**$MAX_ABBREVS**

The number of abbreviations which may be used in economy (`-e`) mode. This setting is available in all versions of Inform, but in 6.35 the maximum for Z-code was raised from 64 to 96. However, this trades off against `$MAX_DYNAMIC_STRINGS`; see below.

In Glulx, `$MAX_ABBREVS` is not needed and has no effect.

**$MAX_DYNAMIC_STRINGS**

The number of string variables (`"@00"`, etc) allowed in the game. In Z-code, this may be any value from 0 to 96. Setting this in Z-code automatically sets `$MAX_ABBREVS` to `(96 - $MAX_DYNAMIC_STRINGS)`, as the two features draw from the same pool of 96 Z-machine abbreviations. Similarly, setting `$MAX_ABBREVS` sets `$MAX_DYNAMIC_STRINGS` to `(96 - $MAX_ABBREVS)`.

In Glulx, the two settings are not connected; `$MAX_DYNAMIC_STRINGS` may be as high as 100. (Dynamic string references have two digits, so they cannot go beyond the range `"@00"` to `"@99"`.)

(Added in 6.35. In earlier versions, 32 string variables and 64 abbreviations were available in Z-code; 64 string variables were available in Glulx.)

**$MAX_GLOBAL_VARIABLES**

The maximum number of global variables in one compiled game. (Internal memory setting. In Z-code this is 240 and cannot be changed.)

**$MAX_LOCAL_VARIABLES**

The maximum number of local variables in a routine. (Internal memory setting. In Z-code this is 16 and cannot be changed.)

**$MAX_STACK_SIZE**

The amount of memory that the interpreter will reserve for the Glulx stack. (This is only meaningful in Glulx.)

**$MEMORY_MAP_EXTENSION**

The number of extra zero bytes to add to the end of the compiled game file. This is writable memory which the game can use freely. (This is only meaningful in Glulx.)

**$NUM_ATTR_BYTES**

The number of bytes used for attribute flags in each object. The maximum number of attributes is `8 * NUM_ATTR_BYTES`. (In Glulx, this must be a multiple of 4 plus 3. In Z-code this is always 6 and cannot be changed.)

**$OMIT_UNUSED_ROUTINES**

If this is set to 1, the compiler will omit the compiled code of unused routines from the game file. (See `$WARN_UNUSED_ROUTINES`.)

**$SERIAL**

Sets the game's serial number to the given six-digit number. (The `Serial` directive does the same thing; see §38.)

**$TRANSCRIPT_FORMAT**

If set to 0 (the default), the `gametext.txt` transcript generated by the `-r` option uses the classic format, which is designed for human proofreaders. If set to 1, the transcript uses an alternate format which indicates the use of each string. This may be more useful for tools which want to parse the transcript.

**$WARN_UNUSED_ROUTINES**

If this is set to 2, the compiler will display a warning for each routine in the game file which is never called. (This includes routines called only from uncalled routines, etc.) If set to 1, it will warn only about functions in game code, not in library files.
  
**$ZCODE_HEADER_EXT_WORDS**

This sets the number of words in the Z-code header extension table. The default is 3. The `-W` setting does the same thing. (See Z-spec 1.0. This is only meaningful in Z-code.)

**$ZCODE_HEADER_FLAGS_3**

This is the value to store in the Flags 3 word of the header extension table. (See Z-spec 1.1. This is only meaningful in Z-code.)

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

All forms of the `Array` directive support the `static` keyword, which is new in 6.34:

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

[[`dict_par2` cannot be set by this directive. It is always the verb number, or zero for words that are not verbs.]]

**Ifv3**

This is mentioned in the DM4 as being for compiler maintenance only (§Table5). In fact it is used by the library, so it's worth documenting. This is a conditional compilation directive, like `Iftrue`, which compiles code when building Z-code V3 (only). It is equivalent to:

	#Ifdef TARGET_ZCODE;
	#Iftrue (#version_number == 3);
	! ...code...
	#Endif;
	#Endif;

**Ifv5**

This misnamed directive is also used by the library (§Table5). It conditionally compiles code when building Z-code V4 and later *or* Glulx. Thus it is the converse of `Ifv3`. (The misleading name is left over from much earlier versions of Inform.)

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

The `Origsource` directive allows you to mark part of a source file as having been generated from another file. (E.g, an Inform 7 source file.) This directive is new in 6.34.

	Origsource "Filename";
	Origsource "Filename" 10;
	Origsource "Filename" 10 40;
	Origsource;

This declares that all following lines are derived from the given filename. This will be reported in error messages and debug output. You may optionally provide a line number and a character number within the line (10 and 40, in these examples).

The declaration holds through the next `Origsource` directive (but does not apply to included files). The fourth form, with no arguments, clears the declaration. 

**Replace**

The `Replace` directive (§25) allows you to redefine a function which has already been defined (such as in a library or in the veneer).

[[The DM4 says that you can only replace functions in files marked with the `System_file` directive. This limitation has been removed.]]

The `Replace` directive has two forms, of which the second is new in 6.33:

	Replace Func;
	Replace Func OriginalFunc;

Multiple definitions of `Func()` may follow the `Replace` directive. `Func` will refer to the last-defined version, except that definitions in normal files are preferred over definitions in `System_file` files or the veneer. With the second form, `OriginalFunc` will refer to the *first*-defined version of the function.

**Undef**

The `Undef` directive allows you to remove a previously-defined constant. This directive is new in 6.33.

	Undef Const;

This leaves the `Const` symbol undefined. If `Const` was never defined, this does nothing.

## Statements

The action statements `<Action>` and `<<Action>>` (§6) now support up to four arguments. The four-argument form is new as of 6.33.

	<Action>
	<Action Noun>
	<Action Noun Second>
	<Action Noun Second, Actor>

All provided arguments are passed to the `R_Process()` veneer function.

[[As in previous versions of Inform, the Action argument can either be a bare action name or a parenthesized expression which produces an action value. Thus, `<Take lamp>` and `<(##Take) lamp>` are equivalent.]]

[[This statement does not follow the traditional IF command syntax, which would put the actor first: "ACTOR, ACTION NOUN". Inform's lexer is not able to handle that ordering consistently, so the statement has to put the actor last.]]

The capitalized `(A)` print token joins `(a)`, `(The)`, and `(the)` as of 6.30; see §26.

	print (A) lamp;

This calls the `CInDefArt()` veneer function.

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

Literals beginning with `$+` and `$-` are compiled as floating-point constants. For example: `$+1.0`, `$-1e3`, `$+2.5e-3`. The constants `FLOAT_INFINITY`, `FLOAT_NINFINITY`, `FLOAT_NAN` are also defined.

[[Note that the standard Inform arithmetic operators (`+`, `-`, etc) do not work with floating-point values. You must use Glulx opcodes (`@fadd`, `@fsub`, etc).]]

The `print_to_array()` method (§3.12) requires two arguments, rather than one (as in Z-code).

### Language features not supported in Glulx

Module compilation (the `-M` option, §38) and Infix (the `-X` option, §7) are not available.

The `Zcharacter` directive (§36) is not available, since Glulx does not use the ZSCII character set.

The `save`, `restore`, and `read` statements (§1.15, §2.5) are not available. These features require more complex behavior in Glulx and cannot be encapsulated in a single statement. They must be implemented in library code using the `@glk` opcode.

## Z-machine V3/4 limitations

Early releases of Inform (through Inform 5) were designed to support all versions of the Z-machine from 3 through 6. However, Inform 6 extended the language in ways which require more advanced VM support. Therefore, certain language features require Z-machine version 5 or later.

- Debug mode and strict mode (`-D` and `-S`, §7) are not available in V3 and V4.
- The method call expression `obj.prop()` is not available in V3 and V4.

You can work around the lack of `obj.prop()` by writing:

	addr = obj.prop;
	addr();

In general, Inform 6 is able to compile older source code to V3 if the source *and the library* avoids the `obj.prop()` syntax. This means you cannot use the Inform 6 library. You must use the [Inform 5 library][i5lib], or one of the alternative libraries designed for V3, such as [metro84][] or [PunyInform][].

[[It is possible to re-implement a limited version of `obj.prop()` for V3 by replacing the `CA__Pr` and `Cl__Ms` veneer routines. Some alternative libraries do this.]]

# Bugs

A great number of bugs have been fixed since Inform 6.21. The list is not included here. See the [Release Notes][i6release] for details.

[i6release]: https://ifarchive.org/if-archive/infocom/compilers/inform6/ReleaseNotes.html

However, it is worth noting that Z-code V3 code generation had been neglected since 6.15 and a number of bugs had crept in. 6.34 and 6.35 have addressed these; V3 should once again be usable.

Particular thanks to Daniel Fremont for the many bug reports uncovered by his input-fuzzing project.


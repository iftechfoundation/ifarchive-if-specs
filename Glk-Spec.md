Glk API Specification

API version 0.3

Andrew Plotkin <erkyrath@eblong.com>

0        Introduction
0.1      What Glk Is
0.2      What About Java?
0.3      What About the Virtual Machine?
0.4      What Does Glk Not Do?
0.5      Conventions of This Document
1        Overall Structure
1.1      Your Program's Main Function
1.2      Exiting Your Program
1.3      The Interrupt Handler
1.4      Opaque Objects
1.4.1    Identifiers
1.4.2    Rocks
1.4.3    Iterating Through Opaque Objects
1.5      The Gestalt System
1.6      The Version Number
1.7      Other API Conventions
1.8      Character Encoding
1.8.1    Output
1.8.2    Line Input
1.8.3    Character Input
1.8.4    Upper and Lower Case
2        Windows
2.1      Window Arrangement
2.2      Window Opening, Closing, and Constraints
2.3      Changing Window Constraints
2.4      A Note on Display Style
2.5      The Types of Windows
2.5.1    Blank Windows
2.5.2    Pair Windows
2.5.3    Text Buffer Windows
2.5.4    Text Grid Windows
2.6      Echo Streams
2.7      Other Window Functions
3        Events
3.1      Character Input Events
3.2      Line Input Events
3.3      Mouse Input Events
3.4      Timer Events
3.5      Window Arrangement Events
3.6      Other Events
4        Streams
4.1      How To Print
4.2      How To Read
4.3      Closing Streams
4.4      Stream Positions
4.5      Styles
4.5.1    Suggesting the Appearance of Styles
4.5.2    Testing the Appearance of Styles
4.6      The Types of Streams
4.6.1    Window Streams
4.6.2    Memory Streams
4.6.3    File Streams
4.7      Other Stream Functions
5        File References
5.1      The Types of File References
5.2      Other File Reference Functions


0: Introduction

0.1: What Glk Is

Glk is an attempt to define a portable API (programming interface) for
applications with text UIs (user interfaces.)

Rather than go into a detailed explanation of what that means, let me
give examples from the world of text adventures. TADS and Infocom's
Z-machine have nearly identical interface capabilities; each allows a
program to...

    * print an indefinite stream of text into an output buffer, with
some style control
    * input a line of text
    * display a few lines of text in a small separate window
    * store information in a file, or read it in

and so on. However, the implementation of these capabilities vary widely
between platforms and operating systems. Furthermore, this variance is
transparent to the program (the adventure game.) The game does not care
whether output is displayed via a character terminal emulator or a GUI
window; nor whether input uses Mac-style mouse editing or EMACS-style
control key editing.

On the third hand, the user is likely to care deeply about these
interface decisions. This is why there are Mac-native interpreters on
Macintoshes, pen-controlled interpreters on Newtons and Pilots, and so
on -- and (ultimately) why there Macintoshes and Pilots and X-windows
platforms in the first place.

On the *fourth* hand, TADS and Inform are not alone; there is
historically a large number of text adventure systems. Most are obsolete
or effectively dead; but it is inevitable that more will appear. Users
want each living system ported to all the platforms in use. Users also
prefer these ports to use the same interface, as much as possible.

This all adds up to a pain in the ass.

Glk tries to draw a line between the parts of the text adventure world
which are identical on all IF systems, and different on different
operating systems, from the parts which are unique to each IF system but
identical in all OSs. The border between these two worlds is the Glk
API.

My hope is that a new IF system, or existing ones which are
less-supported (Hugo, AGT, etc) can be written using Glk for all input
and output function. The IF system would then be in *truly* portable C.
On the other side of the line, there would be a Glk library for each
operating system and interface (Macintosh, X-windows, curses-terminal,
etc.) Porting the IF system to every platform would be trivial; compile
the system, and link in the library.

Glk can also serve as a nice interface for applications other than games
-- data manglers, quick hacks, or anything else which would normally
lack niceties such as editable input, macros, scrolling, or whatever is
native to your machine's interface idiom.

0.2: What About Java?

Java is the ultimate tool for cross-platform development. You wanna buy
a bridge? How about some shares of Sun stock? Onna stick?

Java has several disadvantages for my purpose. First, it is
resource-intensive. It is unlikely that Java will ever run on a
386/68030 generation computer, which is perfectly adequate for text IF.
Java may run on a palmtop, but the standard Java library will not. It is
also impossible for a single person to port Java to a new platform --
both legally and practically, Java is in the control of large
corporations.

Secondly, Java allows too fine-grained a control over the interface. It
is not possible to create a text interface using the standard Java
library; it is not even really possible to make a graphical interface in
the Mac idiom. Java programs have their own Java-specific interface
idiom. This trend is accelerating.

On the other hand, it is perfectly possible to implement a Glk library
in Java and using the Java interface idiom. This would allow a Glk-based
IF system to be easily ported to any machine that runs Java -- if the
player likes the way Java looks, of course.

0.3: What About the Virtual Machine?

You can think of Glk as an IF virtual machine, without the virtual
machine part. The "machine" is just portable C code.

It is not inconceivable that a new IF virtual machine might be designed
to go along with Glk. This VM would use Glk as its interface; each Glk
call would correspond to an input/output opcode of the VM.

0.4: What Does Glk Not Do?

Glk does not handle the things which should be handled by the program
(or the IF system, or the virtual machine) which is linked to Glk. This
means that Glk does not address

    * parsing
    * game object storage
    * computation
    * text compression

0.5: Conventions of This Document

This document defines the Glk API. I have tried to specify exactly what
everything does, what is legal, what is illegal, and why.

Sections in square brackets [[like this]] are notes. They do not define
anything; they clarify or explain what has already been defined. If
there seems to be a conflict, ignore the note and follow the definition.

[[Notes with the label "WORK" are things which I have not yet fully
resolved. Your comments requested and welcome.]]

This document is written for the point of view of the game programmer --
the person who wants to use the Glk library to print text, input text,
and so on. By saying what the Glk library does, of course, this document
also defines the task of the Glk programmer -- the person who wants to
port the Glk library to a new platform or operating system. If the Glk
library guarantees something, the game programmer can rely on it, and
the Glk programmer is required to support it. Contrariwise, if the
library does not guarantee something, the Glk programmer may handle it
however he likes, and the game programmer must not rely on it. If
something is illegal, the game programmer must not do it, and the Glk
programmer is not required to worry about it. [[It is preferable, but
not required, that the Glk library detect illegal requests and display
error messages. The Glk library may simply crash when the game program
does something illegal. This is why the game programmer must not do it.
Right?]]

Hereafter, "Glk" or "the library" refers to the Glk library, and "the
program" is the game program (or whatever) which is using the Glk
library to print text, input text, or whatever. "You" are the person
writing the program. "The player" is the person who will use the
program/Glk library combination to actually play a game. Or whatever.

The Glk API is declared in a C header file called "glk.h". Please refer
to that file when reading this one.

1: Overall Structure

1.1: Your Program's Main Function

The top level of the program -- the main() function in C, for example --
belongs to Glk. [[This means that Glk isn't really a library. In a
sense, you are writing a library, which is linked into Glk. This is
bizarre to think about, so forget it.]]

You define a function called glk_main(), which the library calls to
begin running your program. glk_main() should run until your program is
finished, and then return.

Glk does all its user-interface work in a function called glk_select().
This function waits for an event -- typically the player's input -- and
returns an structure representing that event. This means that your
program must have an event loop. In the very simplest case, you could
write

    void glk_main()
    {
        event_t ev;
        while (1) {
            glk_select(&ev);
            switch (ev.type) {
                default:
                    /* do nothing */
                    break;
            }
        }
    }

This is a legal Glk-compatible program. As you might expect, it doesn't
do anything. The player will see an empty window, which he can only
stare at, or destroy in a platform-defined standard manner.
[[Command-period on the Macintosh; a kill-window menu option in an X
window manager; control-C in a curses terminal window.]]

[[However, this program does not spin wildly and burn CPU time. The
glk_select() function waits for an event it can return. Since it only
returns events which you have requested, it will wait forever, and grant
CPU time to other processes if that's meaningful on the player's
machine.]] [[Actually, there are some events which are always reported.
More may be defined in future versions of the Glk API. This is why the
default response to an event is to do nothing. If you don't recognize
the event, ignore it.]]

1.2: Exiting Your Program

If you want to shut down your program in the middle of your glk_main()
function, you can call glk_exit().

    void glk_exit(void);

This function does not return.

If you print some text to a window and then shut down your program, you
can assume that the player will be able to read it. Most likely the Glk
library will give a "Hit any key to exit" prompt. (There are other
possibilities, however. A terminal-window version of Glk might simply
exit and leave the last screen state visible in the terminal window.)

[[You should *only* shut down your program with glk_exit() or by
returning from your glk_main() function. If you call the ANSI exit()
function, or other platform-native functions, bad things may happen.
Some versions of the Glk library may be designed for multiple sessions,
for example, and you would be cutting off all the sessions instead of
just yours. You would probably also prevent final text from being
visible to the player.]]

1.3: The Interrupt Handler

Most platforms have some provision for interrupting a program --
command-period on the Macintosh, control-C in Unix, possibly a window
manager menu item, or other possibilities. This can happen at any time,
including while execution is nested inside one of your own functions, or
inside a Glk library function.

If you need to clean up critical resources, you can specify an interrupt
handler function.

    void glk_set_interrupt_handler(void (*func)(void));

The argument you pass to glk_set_interrupt_handler() should be a pointer
to a function which takes no argument and returns no result. If Glk
receives an interrupt, and you have set an interrupt handler, your
handler will be called, before the process is shut down. 

Initially there is no interrupt handler. You can reset to not having any
by calling glk_set_interrupt_handler(NULL).

You should not try to interact with the player in your interrupt
handler. Do not call glk_select(). Anything you print to a window may
not be visible to the player.

1.4: Opaque Objects

Glk keeps track of a few classes of special objects. These are opaque to
your program; you always refer to them using 32-bit unsigned integer
identifiers.

These classes are:

    * Windows: Screen panels, used to input or output information.
    * Streams: Data streams, to which you can input or output text.
[[There are file streams and window streams, since you can output data
to windows or files.]]
    * File references: Pointers to files in permanent storage. [[In Unix
a file reference is a pathname; on the Mac, an FSSpec. Actually there's
a little more information included, such as file type and whether it is
a text or binary file.]]

When you create one of these objects, it is always possible that the
creation will fail (due to lack of memory, or some other OS error.) When
this happens, the allocation function will return 0 instead of a valid
integer identifier. You should always test for this possibility.

1.4.1: Identifiers

It is worth spending a bit of time on the identifiers used to refer to
these objects.

Zero is never the identifier of any object (window, stream, or file
reference). The value 0 is often used to indicate "no object" or
"nothing", but it is not a valid identifier. If a Glk function takes an
object identifier as an argument, it is illegal to pass in 0 unless the
function definition says otherwise.

The glk.h file defines types "winid_t", "strid_t", "frefid_t" to store
identifiers. These are all the same as "uint32".

Identifiers can be anything (except 0). Some Glk library implementations
may use consecutive integers starting with 1; others may use native C or
C++ pointers coerced to integer type. If the library wants to use
alternating primes starting with a randomly-chosen divisor of 1008,
that's legal as well. You should not make any assumptions.

The different opaque object classes have separate identifier spaces.
That is, window id 4 and stream id 4 may exist at the same time.
[[Passing a window id to a function that expects a stream id is not a C
type error, since both are just integers. But it is illegal, since a
valid window id number is almost certainly not a valid stream id.]]

Identifiers may or may not be reused. That is, if you close window id 4,
and then open a new window, the new window's id may be 4. [[Or it may
not. So when you destroy an object, you should assume that its id is
invalid forever after.]]

1.4.2: Rocks

Every one of these objects (window, stream, or file reference) has a
"rock" value. This is simply a 32-bit integer value which you provide,
for your own purposes, when you create the object. [[The library -- so
to speak -- stuffs this value under a rock for safe-keeping, and gives
it back to you when you ask for it.]]

[[If you don't know what to use the rocks for, provide 0 and forget
about it.]]

1.4.3: Iterating Through Opaque Objects

For each class of opaque objects, there is an iterate function, which
you can use to obtain a list of all existing objects of that class. It
takes the form

    uint32 glk_CLASS_iterate(uint32 obj, uint32 *rockptr);

Calling glk_CLASS_iterate(0, r) returns the first object; calling
glk_CLASS_iterate(obj, r) returns the next object, until there aren't
any more, at which time it returns 0.

The rockptr argument is a pointer to a location; whenever
glk_CLASS_iterate() returns an object, the object's rock is stored in
the location (*rockptr). If you don't want the rocks to be returned, you
may set rockptr to NULL.

You usually use this as follows:

    obj = glk_CLASS_iterate(0, NULL);
    while (obj) {
        /* ...do something with obj... */
        obj = glk_CLASS_iterate(obj, NULL);
    }

If you create or destroy objects inside this loop, obviously, the
results are unpredictable. However it is always legal to call
glk_CLASS_iterate(obj, r) as long as obj is a valid object id, or 0.

The order in which objects are returned is entirely arbitrary. The
library may even rearrange the order every time you create or destroy an
object of the given class. As long as you do not create or destroy any
object, the rule is that glk_CLASS_iterate(obj, r) has a fixed result,
and iterating through the results as above will list every object
exactly once.

1.5: The Gestalt System

The "Gestalt" mechanism (cheerfully stolen from the Mac OS) is a system
by which the Glk API can be upgraded without making your life
impossible. New capabilities (graphics, sound, or so on) can be added
without changing the basic specification. The system also allows for
"optional" capabilities -- those which not all Glk library
implementations will support -- and allows you to check for their
presence without trying to infer them from a version number.

The basic idea is that you can request information about the
capabilities of the API, by calling the Gestalt functions:

    uint32 glk_gestalt(uint32 sel, uint32 val);
    uint32 glk_gestalt_ext(uint32 sel, uint32 val, void *ptr);

The selector (the "sel" argument) tells which capability you are
requesting information about; the other two arguments are additional
information, which may or may not be meaningful. The ptr argument of
glk_gestalt_ext() is always optional; you may always pass NULL to it, if
you do not want whatever information it represents. glk_gestalt() is
simply a shortcut for this; glk_gestalt(x, y) is exactly the same as
glk_gestalt_ext(x, y, NULL).

The critical point is that if the Glk library has never heard of the
selector sel, it will return 0. It is *always* safe to call
glk_gestalt(x, y) (or glk_gestalt_ext(x, y, NULL)). Even if you are
using an old library, which was compiled before the given capability was
imagined, you can test for the capability by calling glk_gestalt(); the
library will correctly indicate that it does not support it, by
returning 0.

(It may not be safe to call glk_gestalt_ext(x, y, z) for an unknown
selector x, where z is not NULL. This is because the selector may expect
to write information to a large structure which z points at. You should
consult the documentation for x and ensure that z points at a
sufficiently large structure, or else pass NULL to z.)

1.6: The Version Number

For an example of the Gestalt mechanism, consider the selector
gestalt_Version. If you do

    uint32 res;
    res = glk_gestalt(gestalt_Version, 0);

res will be set to a 32-bit number which encodes the version of the Glk
spec which the library implements. The upper 16 bits stores the major
version number; the next 8 bits stores the minor version number; the low
8 bits stores an even more minor version number, if any. [[So the
version number 78.2.11 would be encoded as 0x004E020B.]]

The current Glk specification version is 0.3, so this selector will
return 0x00000300.

    uint32 res;
    res = glk_gestalt_ext(gestalt_Version, 0, NULL);

does exactly the same thing; in fact, both the second and third
arguments are ignored for this selector. (However, it is prudent to pass
0 and NULL, in case of future changes.)

1.7: Other API Conventions

The glk.h header file is the same on all platforms, with the sole
exception of the typedef of uint32. This will always be defined as a
32-bit unsigned integer type, which may be "long" or "int" or some other
C definition.

Note that all constants are #defines, and all functions are actual
function declarations (as opposed to macros.) [[There are a few places
where macros would be more efficient -- glk_gestalt() and
glk_gestalt_ext(), for example -- but they are not likely to be CPU
bottlenecks, and clarity seems more important.]]

FALSE is 0; TRUE is 1.

As stated above, it is illegal to pass 0 to a function which is
expecting a valid object id, unless the function definition says
otherwise.

Some functions have pointer arguments, acting as "variable" or
"reference" arguments; the function's intent is to return some value in
the space pointed to by the argument. Unless the function says
otherwise, it is legal to pass a NULL pointer to indicate that you do
not care about that value.

1.8: Character Encoding

Glk uses the Latin-1 Unicode encoding, and keeps it holy.

Latin-1 is an 8-bit character encoding; it maps numeric codes in the
range 0 to 255 into printed characters. The values from 32 to 126 are
the standard printable ASCII characters (' ' to '~'). Values 0 to 31 and
127 to 159 are reserved for control characters, and have no printed
equivalent.

Glk uses different parts of the Latin-1 encoding for different purposes.

1.8.1: Output

When you are sending text to a window, or to a file open in text mode,
you can print any of the printable Latin-1 characters: 32 to 126, 160 to
255. You can also print the newline character (control-J, decimal 10,
hex 0x0A.)

It is *not* legal to print any other control characters (0 to 9, 11 to
31, 127 to 159). You may not print even common formatting characters
such as tab (control-I), linefeed (control-M), or page break
(control-L). [[As usual, the behavior of the library when you print an
illegal character is undefined. It is preferable that the library
display a numeric code, such as "\177" or "0x7F", to warn the user that
something illegal has occurred. The library may skip illegal characters
entirely; but you should not rely on this.]]

Note that when you are sending data to a file open in binary mode, you
can print any byte value, without restriction. See section 4.6.3, "File
Streams".

A particular implementation of Glk may not be able to display all the
printable characters. It is guaranteed to be able to display the ASCII
characters (32 to 126, and the newline 10.) Other characters may be
printed correctly, printed as multi-character combinations (such as "ae"
for the one-character "ae" ligature), or printed as some placeholder
character (such as a bullet or question mark, or even an octal code.)

You can test for this by using the gestalt_CharOutput selector. If you
set ch to a character code (from 0 to 255), and call

    uint32 res, len;
    res = glk_gestalt_ext(gestalt_CharOutput, ch, &len);

then res will be one of the following values:

    * gestalt_CharOutput_CannotPrint: The character cannot be
meaningfully printed. If you try, the player may see nothing, or may see
a placeholder.
    * gestalt_CharOutput_ExactPrint: The character will be printed
exactly as defined.
    * gestalt_CharOutput_ApproxPrint: The library will print some
approximation of the character. It will be more or less right, but it
may not be precise, and it may not be distinguishable from other,
similar characters. (Examples: "ae" for the one-character "ae" ligature,
"e" for an accented "e", "|" for a broken vertical bar.)

In all cases, len (the value pointed at by the third argument) will be
the number of actual glyphs which will be used to represent the
character. In the case of gestalt_CharOutput_ExactPrint, this will
always be 1; for gestalt_CharOutput_CannotPrint, it may be 0 (nothing
printed) or higher; for gestalt_CharOutput_ApproxPrint, it may be 1 or
higher. This information may be useful when printing text in a
fixed-width font.

[[As described in section 1.7, "Other API Conventions", you may skip
this information by passing NULL as the third argument in
glk_gestalt_ext(), or by calling glk_gestalt() instead.]]

If ch is outside the range 0 to 255, this selector will always return
gestalt_CharOutput_CannotPrint. It is also guaranteed to do this if ch
is an unprintable character (0 to 9, 11 to 31, 127 to 159.)

[[Make sure you do not get confused by signed byte values. If you set a
"char" variable ch to 0xFE, the small-thorn character, and then call
    res = glk_gestalt(gestalt_CharOutput, ch);
then (by the definition of C/C++) ch will be *sign-extended* to
0xFFFFFFFE, which is *not* in the range 0 to 255. You should write
    res = glk_gestalt(gestalt_CharOutput, (unsigned char)ch);
instead.]]

1.8.2: Line Input

You can request that the player enter a line of text. See section 3.2,
"Line Input Events".

This text will be placed in a buffer of your choice. There is no length
field or null terminator in the buffer. (The length of the text is
returned as part of the line-input event.)

The buffer will contain only printable Latin-1 characters (32 to 126,
160 to 255).

A particular implementation of Glk may not be able to accept all
printable characters as input. It is guaranteed to be able to accept the
ASCII characters (32 to 126.)

You can test for this by using the gestalt_LineInput selector. If you
set ch to a character code (from 0 to 255), and call

    uint32 res;
    res = glk_gestalt(gestalt_LineInput, ch);

then res will be TRUE (1) if that character can be typed by the player
in line input, and FALSE (0) if not. Note that if ch is a nonprintable
character (0 to 31, 127 to 159), or if ch is outside the range 0 to 255,
then this is guaranteed to return FALSE.

1.8.3: Character Input

You can request that the player hit a single key. See section 3.1,
"Character Input Events".

The character code which is returned can be any value from 0 to 255. The
printable character codes have already been described. The remaining
codes are typically control codes, control-A to control-Z and a few
others.

There are also a number of special codes, representing special keyboard
keys, which can be returned from a char-input event. These are
represented as 32-bit integers, starting with 4294967295 (0xFFFFFFFF)
and working down. The special key codes are defined in the glk.h file.
They include:

    * keycode_Left, keycode_Right, keycode_Up, keycode_Down (arrow keys)
    * keycode_Return (return or enter)
    * keycode_Delete (delete or backspace)
    * keycode_Escape
    * keycode_Tab
    * keycode_PageUp
    * keycode_PageDown
    * keycode_Home
    * keycode_End
    * keycode_Func1, keycode_Func2, keycode_Func3, ... keycode_Func12
(twelve function keys)
    * keycode_Unknown (any key which has no Latin-1 or special code)

Various implementations of Glk will vary widely in which characters the
player can enter. The most obvious limitation is that some characters
are mapped to others. For example, most keyboards return a control-I
code when the tab key is pressed. The Glk library, if it can recognize
this at all, will generate a keycode_Tab event (value 0xFFFFFFF7) when
this occurs. Therefore, for these keyboards, *no* keyboard key will
generate a control-I event (value 9.) The Glk library will probably map
many of the control codes to the other special keycodes.

[[On the other hand, the library may be very clever and discriminate
between tab and control-I. This is legal. The idea is, however, that if
your program asks the user to "press the tab key", you should check for
a keycode_Tab event as opposed to a control-I event.]]

Some characters may not be enterable simply because they do not exist.
[[Not all keyboards have a home or end key. A pen-based platform may not
recognize any control characters at all.]]

Some characters may not be enterable because they are reserved for the
purposes of the interface. For example, the Mac Glk library reserves the
tab key for switching between different Glk windows. Therefore, on the
Mac, the library will never generate a keycode_Tab event *or* a
control-I event.

You can test for this by using the gestalt_CharInput selector. If you
set ch to a character code (from 0 to 255) or a special code (from
0xFFFFFFFF down), and call

    uint32 res;
    res = glk_gestalt(gestalt_CharInput, ch);

then res will be TRUE (1) if that character can be typed by the player
in character input, and FALSE (0) if not.

[[Glk porters take note: it is not a goal to be able to generate every
single possible key event. If the library says that it can generate a
particular keycode, then game programmers will assume that it is
available, *and ask players to use it.* If a keycode_Home event can only
be generated by typing escape-control-A, and the player does not know
this, the player will be lost when the game says "Press the home key to
see the next hint." It is better for the library to say that it *cannot*
generate a keycode_Home event; that way the game can detect the
situation and ask the user to type H instead.]]

[[Of course, it is better not to rely on obscure keys in any case. The
arrow keys and return are nearly certain to be available; the others are
of gradually decreasing reliability, and you (the game programmer)
should not depend on them. You *must* be certain to check for the ones
you want to use, *including* the arrow keys and return, and be prepared
to use different keys in your interface if gestalt_CharInput says they
are not available.]]

1.8.4: Upper and Lower Case

You can convert characters from upper to lower case with two Glk utility
functions:

    unsigned char glk_char_to_lower(unsigned char ch);
    unsigned char glk_char_to_upper(unsigned char ch);

These have a few advantages over the standard ANSI tolower() and
toupper() macros. They work for the entire Latin-1 character set,
including accented letters; they behave consistently on all platforms,
since they're part of the Glk library; and they are safe for all
characters. That is, if you call glk_char_to_lower() on a lower-case
character, or a character which is not a letter, you'll get the argument
back unchanged.

2: Windows

On most platforms, the program/library combination will appear to the
player in a window -- either a window which covers the entire screen, or
one which shares screen space with other windows in a multi-programming
environment. Obviously your program does not have worry about the
details of this. The Glk screen space is a rectangle, which you can
divide into panels for various purposes. It is these panels which I will
refer to as "windows" hereafter.

You refer to a window using an unsigned 32-bit integer identifier. See
section 1.4.1, "Identifiers".

A window has a type. Currently there are three window types:

    * Text buffer windows: A stream of text. [[The "story window" of an
Infocom game.]] You can only print at the end of the stream, and input a
line of text at the end of the stream.
    * Text grid windows: A grid of characters in a fixed-width font.
[[The "status window" of an Infocom game.]] You can print anywhere in
the grid.
    * Blank windows: A blank window. Blank windows support neither input
nor output. [[They exist mostly to be an example of a "generic" window.
You are unlikely to want to use them.]]

There is one other special type of window, the pair window. Pair windows
are created by Glk as part of the system of window arrangement. You
cannot create them yourself. See section 2.5.2, "Pair Windows".

Every window has a rock. This is a value you provide when the window is
created; you can use it however you want. See section 1.4.2, "Rocks".

When Glk starts up, there are no windows.

[[When I say there are no windows, I mean there are no Glk windows. In a
multiprogramming environment, such as X or MacOS, there may be an
application window visible; this is the screen space that will contain
all the Glk windows that you create. But at first, this screen space is
empty and unused.]]

Without a window, you cannot do any kind of input or output; so the
first thing you'll want to do is create one. See section 2.2, "Window
Opening, Closing, and Constraints".

You can create as many windows as you want, of any types. You control
their arrangement and sizes through a fairly flexible system of calls.
See section 2.1, "Window Arrangement".

You can close any windows you want. You can even close all the windows,
which returns you to the original startup state.

You can request input from any or all windows. Input can be mouse input
(on platforms which support a mouse), single-character input, or input
of an entire line of text. It is legal to request input from several
windows at the same time. The library will have some interface mechanism
for the player to control which window he is typing in.

2.1: Window Arrangement

The Way of Window Arrangement is fairly complicated. I'll try to explain
it coherently. [[If you are reading this document to get an overview of
Glk, by all means skip forward to section 2.5, "The Types of Windows".
Come back here later.]]

Originally, there are no windows. You can create a window, which will
take up the entire available screen area. You can then split this window
in two. One of the halves is the original window; the other half is new,
and can be of any type you want. You can control whether the new window
is left, right, above, or below the original one. You can also control
how the split occurs. It can be 50-50, or 70-30, or any other percentage
split. Or, you can give a fixed width to the new window, and allow the
old one to take up the rest of the available space. Or you can give a
fixed width to the *old* window, and let the *new* one take up the rest
of the space.

Now you have two windows. In exactly the same way, you can split either
of them -- the original window, or the one you just created. Whichever
one you split becomes two, which together take up the same space that
the one did before.

You can repeat this as often as you want. Every time you split a window,
one new window is created. Therefore, the call that does this is called
glk_window_open(). [[It might have been less confusing to call it
"glk_split_window" -- or it might have been more confusing. I picked
one.]]

It is important to remember that the order of splitting matters. If you
split twice times, you don't have a trio of windows; you have a pair
with another pair on one side. Mathematically, the window structure is a
binary tree.

Example time. Say you do two splits, each a 50-50 percentage split. You
start with the original window A, and split that into A and B; then you
split B into B and C.

    +---------+
    |         |       O
    |    A    |      / \
    |         |     A   O
    +---------+        / \
    |    B    |       B   C
    +---------+
    |    C    |
    +---------+

Or, you could split A into A and B, and then split A again into A and C.

    +---------+
    |    A    |       O
    +---------+      / \
    |    C    |     O   B
    +---------+    / \
    |         |   A   C
    |    B    |
    |         |
    +---------+

I'm using the simplest possible splits in the examples above. Every
split is 50-50, and the new window of the pair is always *below* the
original one (the one that gets split.) You can get fancier than that.
Here are three more ways to perform the first example; all of them have
the *same* tree structure, but look different on the screen.

    +---------+ +---------+ +---------+
    |         | |    A    | |         |     O
    |    A    | +---------+ |    A    |    / \
    |         | |    B    | |         |   A   O
    +---------+ +---------+ +----+----+      / \
    |    C    | |         | |    |    |     B   C
    +---------+ |    C    | | C  | B  |
    |    B    | |         | |    |    |
    +---------+ +---------+ +----+----+

On the left, we turn the second split (B into B/C) upside down; we put
the new window (C) below the old window (B).

In the center, we mess with the percentages. The first split (A into
A/B) is a 25-75 split, which makes B three times the size of A. The
second (B into B/C) is a 33-66 split, which makes C twice the size of B.
This looks rather like the second example above, but has a different
internal structure.

On the right, the second split (B into B/C) is vertical instead of
horizontal, with the new window (C) on the left of the old one.

The visible windows on the Glk screen are "leaf nodes" of the binary
tree; they hang off the ends of the branches in the diagram. There are
also the "internal nodes", the ones at the forks, which are marked as
"O". These are the mysterious pair windows.

You don't create pair windows directly; they are created as a
consequence of window splits. Whenever you create a new window, a new
pair window is also created automatically. In the following two-split
process, you can see that when a window is split, it is replaced by a
new pair window, and moves down to become one of that "O"'s two
children.

    +---+    A
    |   |
    | A |
    |   |
    +---+
    
    +---+    O
    | A |   / \
    +---+  A   B
    | B |
    +---+
    
    +---+    O
    | A |   / \
    +-+-+  A   O
    |C|B|     / \
    +-+-+    B   C

You can't draw into a pair window. It's completely filled up with the
two windows it contains. They're what you should be drawing into.

Why have pair windows in the system at all? They're convenient for
certain operations. For example, you can close any window at any time;
but sometimes you want to close an entire nest of windows at once. In
the third stage shown, if you close the lower pair window, it blows away
all its descendents -- both B and C -- and leaves just a single window,
A, which is what you started with.

I'm using some math terminology already, so I'll explain it briefly. The
"root" of the tree is the top (math trees, like family trees, grow
upside down.) If there's only one window, it's the root; otherwise the
root is the topmost "O". Every pair window has exactly two "children".
Other kinds of windows are leaves on the tree, and have no children. A
window's "descendants", obviously, are its children and grandchildren
and great-grandchildren and so on. The "parent" and "ancestors" of a
window are exactly what you'd expect. So the root window is the ancestor
of every other window.

There are Glk functions to determine the root window, and to determine
the parent of any given window. Note that every window's parent is a
pair window. (Except for the root window, which has no parent.)

2.2: Window Opening, Closing, and Constraints

    winid_t glk_window_open(winid_t split, uint32 method, uint32 size,
uint32 wintype, uint32 rock);

If there are no windows, the first three arguments are meaningless.
split *must* be zero, and method and size are ignored. wintype is the
type of window you're creating, and rock is the rock (see section 1.4.2,
"Rocks").

If any windows exist, new windows must be created by splitting existing
ones. split is the window you want to split; this *must not* be zero.
method is a mask of constants to specify the direction (left, right,
above, below) and the split method (proportional, fixed). size is the
size of the split. wintype is the type of window you're creating, and
rock is the rock.

Remember that it is possible that the library will be unable to create a
new window, in which case glk_window_open() will return 0. [[It is
acceptable to gracefully exit, if the window you are creating is an
important one -- such as your first window. But you should not try to
perform any window operation on the id until you have tested to make
sure it is non-zero.]]

The examples we've seen so far have the simplest kind of size control;
every pair is a percentage split, with X percent going to one side, and
(100-X) percent going to the other side. If the player resizes the
window, the whole mess expands, contracts, or stretches in a uniform
way.

As I said earlier, you can also make fixed-size splits. This is a little
more complicated, because you have to know how this fixed size is
measured.

Sizes are measured in a way which is different for each window type. For
example, a text grid window is measured by the size of its fixed-width
font. You can make a text grid window which is fixed at a height of four
rows, or ten columns. A text buffer window is measured by the size of
*its* font. [[Remember that different windows may use different size
fonts. Even two text grid windows may use fixed-size fonts of different
sizes.]] Future versions of Glk may support graphics windows, which
would be measured in pixels. Blank windows aren't measured at all;
there's no meaningful way to measure them, and therefore you can't
create a blank window of a fixed size, only of a proportional
(percentage) size.

So to create a text buffer window which takes the top 40% of the
original window's space, you would execute

    newwin = glk_window_open(win, winmethod_Above |
winmethod_Proportional, 40, wintype_TextBuffer, 0);

To create a text grid which is always five lines high, at the bottom of
the original window, you would do

    newwin = glk_window_open(win, winmethod_Below | winmethod_Fixed, 5,
wintype_TextGrid, 0);

Note that the meaning of the size argument depends on the method
argument. If the method is winmethod_Fixed, it also depends on the
wintype argument. The new window is then called the "key window" of this
split, because its window type determines how the split size is
computed. [[For winmethod_Proportional splits, you can still call the
new window the "key window". But the key window is not important for
proportional splits, because the size will always be computed as a
simple ratio of the available space, not a fixed size of one child
window.]]

This system is more or less peachy as long as all the constraints work
out. What happens when there is a conflict? The rules are simple. Size
control always flows down the tree, and the player is at the top. Let's
bring out an example:

    +---------+
    | C: 2    |
    |    rows |       O
    +---------+      / \
    | A       |     O   B
    +---------+    / \
    |         |   A   C
    | B: 50%  |
    |         |
    |         |
    +---------+

First we split A into A and B, with a 50% proportional split. Then we
split A into A and C, with C above, C being a text grid window, and C
gets a fixed size of two rows (as measured in its own font size). A gets
whatever remains of the 50% it had before.

Now the player stretches the window vertically.

    +---------+
    | C: 2    |
    |    rows |
    +---------+
    | A       |
    |         |
    +---------+
    |         |
    |         |
    | B: 50%  |
    |         |
    |         |
    +---------+

The library figures: the topmost split, the original A/B split, is
50-50. So B gets half the screen space, and the pair window next to it
(the lower "O") gets the other half. Then it looks at the lower "O". C
gets two rows; A gets the rest. All done.

Then the user maliciously starts squeezing the window down, in stages:

    +---------+  +---------+  +---------+  +---------+  +---------+
    | C: 2    |  |    C    |  |    C    |  |    C    |  +---------+
    |    rows |  |         |  |         |  +---------+  +---------+
    +---------+  +---------+  +---------+  +---------+  |    B    |
    | A       |  |    A    |  +---------+  |    B    |  +---------+
    |         |  +---------+  |         |  |         |
    +---------+  |         |  |    B    |  +---------+
    |         |  |    B    |  |         |
    |         |  |         |  +---------+
    | B: 50%  |  |         |
    |         |  +---------+
    |         |
    +---------+

The logic remains the same. B always gets half the space. At stage 3,
there's no room left for A, so it winds up with zero height. Nothing
displayed in A will be visible. At stage 4, there isn't even room in the
upper 50% to give C its two rows; so it only gets one. Finally, C is
squashed out of existence as well.

When a window winds up undersized, it remembers what size it should be.
In the example above, A remembers that it should be two rows; if the
user expands the window to the original size, it would return to the
original layout.

The downward flow of control is a bit harsh. After all, in stage 4,
there's room for C to have its two rows if only B would give up some of
its 50%. But this does not happen. [[This makes life much easier for the
Glk library. To determine the configuration of a window, it only needs
to look at the window's ancestors, never at its descendants. So window
layout is a simple recursive algorithm, no backtracking.]]

What happens when you split a fixed-size window? The resulting pair
window -- that is, the two new parts together -- retain the same size
constraint as the original window that was split. The key window for the
original split is still the key window for that split, even though it's
now a grandchild instead of a child.

The easy, and correct, way to think about this is that the size
constraint is stored by a window's parent, not the window itself; and a
constraint consists of a pointer to a key window plus a size value.

    +---------+       +---------+         +---------+
    |         |       |         |         | C: 2    |
    |         |  A    | A: 50%  |   O1    |    rows |     O1
    |         |       |         |  / \    +---------+    / \
    |         |       |         | A   B   | A       |   O2  B
    | A       |       +---------+         +---------+  / \
    |         |       |         |         |         | A   C
    |         |       | B       |         | B       |
    |         |       |         |         |         |
    |         |       |         |         |         |
    +---------+       +---------+         +---------+

After the first split, the new pair window (O1, which covers the whole
screen) knows that its first child (A) is above the second, and gets 50%
of its own area. (A is the key window for this split, but a proportional
split doesn't care about key windows.)

After the *second* split, all this remains true; O1 knows that its first
child gets 50% of its space, and A is O1's key window. But now O1's
first child is O2 instead of A. The newer pair window (O2) knows that
*its* first child (C) is above the second, and gets a fixed size of two
rows. (As measured in C's font, because C is O2's key window.)

If we split C, now, the resulting pair will still be two C-font rows
high -- that is, tall enough for two lines of whatever font C displays.
For the sake of example, we'll do this vertically.

    +----+----+
    | C  | D  |
    |    |    |     O1
    +----+----+    / \
    | A       |   O2  B
    +---------+  / \
    |         | A   O3
    | B       |    / \
    |         |   C   D
    |         |
    +---------+

O3 now knows that its children have a 50-50 left-right split. O2 is
still committed to giving its upper child, O3, two C-font rows. Again,
this is because C is O2's key window. [[This turns out to be a good
idea, because it means that C, the text grid window, is still two rows
high. If O3 had been a upper-lower split, things wouldn't work out so
neatly. But the rules would still apply. If you don't like this, don't
do it.]]

    void glk_window_close(winid_t win, stream_result_t *result);

This closes a window, which is pretty much exactly the opposite of
opening a window. It is legal to close all your windows, or to close the
root window (which does the same thing.)

The result argument is filled with the output character count of the
window stream. See section 4, "Streams" and section 4.3, "Closing
Streams".

When you close a window (and it is not the root window), the other
window in its pair takes over all the freed-up area. Let's close D, in
the current example:

    +---------+
    | C       |
    |         |     O1
    +---------+    / \
    | A       |   O2  B
    +---------+  / \
    |         | A   C
    | B       |
    |         |
    |         |
    +---------+

Notice what has happened. D is gone. O3 is gone, and its 50-50
left-right split has gone with it. The other size constraints are
unchanged; O2 is still committed to giving its upper child two rows, as
measured in the font of O2's key window, which is C. Conveniently, O2's
upper child *is* C, just as it was before we created D. In fact, now
that D is gone, everything is back to the way it was before we created
D.

But what if we had closed C instead of D? We would have gotten this:

    +---------+
    +---------+
    |         |     O1
    | A       |    / \
    |         |   O2  B
    +---------+  / \
    |         | A   D
    | B       |
    |         |
    |         |
    +---------+

Again, O3 is gone. But D has collapsed to zero height. This is because
its height is controlled by O2, and O2's key window was C, and C is now
gone. O2 no longer has a key window at all, so it cannot compute a
height for its upper child, so it defaults to zero.

[[This may seem to be an inconvenient choice. That is deliberate. You
should not leave a pair window with no key, and the zero-height default
reminds you not to. You can use glk_window_set_arrangement() to set a
new split measurement and key window. See section 2.3, "Changing Window
Constraints".]]

2.3: Changing Window Constraints

There are library functions to change and to measure the size of a
window. 

    void glk_window_get_size(winid_t win, uint32 *widthptr, uint32
*heightptr);
    void glk_window_set_arrangement(winid_t win, uint32 method, uint32
size, winid_t keywin);
    void glk_window_get_arrangement(winid_t win, uint32 *methodptr,
uint32 *sizeptr, winid_t *keywinptr);

glk_window_get_size() simply returns the actual size of the window, in
its measurement system. As described in section 1.7, "Other API
Conventions", either widthptr or heightptr can be NULL, if you only want
one measurement. [[Or, in fact, both, if you want to waste time.]]

glk_window_set_arrangement() changes the size of an existing split --
that is, it changes the constraint of a given pair window.
glk_window_get_arrangement() returns the constraint of a given pair
window.

Consider the example above, where D has collapsed to zero height. Say D
was a text buffer window. You could make a more useful layout by doing

    winid_t o2;
    o2 = glk_get_parent(d);
    glk_window_set_arrangement(o2, winmethod_Above | winmethod_Fixed, 3,
d);

That would set the D (the upper child of O2) to be O2's key window, and
give it a fixed size of 3 rows. 

If you later wanted to expand D, you could do

    glk_window_set_arrangement(o2, winmethod_Above | winmethod_Fixed, 5,
0);

That expands D to five rows. Note that, since O2's key window is already
set to D, it is not necessary to provide the keywin argument; you can
pass 0 to mean "leave the key window unchanged."

If you do change the key window of a pair window, the new key window
*must* be a descendant of that pair window. In the current example, you
could change O2's key window to be A, but not B. The key window also
cannot be a pair window itself.

    glk_window_set_arrangement(o2, winmethod_Below | winmethod_Fixed, 3,
0);

This changes the constraint to be on the *lower* child of O2, which is
A. The key window is still D; so A would then be three rows high as
measured in D's font, and D would get the rest of O2's space. That may
not be what you want. To set A to be three rows high as measured in A's
font, you would do

    glk_window_set_arrangement(o2, winmethod_Below | winmethod_Fixed, 3,
a);

Or you could change O2 to a proportional split:

    glk_window_set_arrangement(o2, winmethod_Below |
winmethod_Proportional, 30, 0);

or

    glk_window_set_arrangement(o2, winmethod_Above |
winmethod_Proportional, 70, 0);

These do exactly the same thing, since 30% above is the same as 70%
below. You don't need to specify a key window with a proportional split,
so the keywin argument is 0. (You could actually specify either A or D
as the key window, but it wouldn't affect the result.)

Whatever constraint you set, glk_window_get_size() will tell you the
actual window size you got.

Note that you can resize windows, but you can't flip or rotate them. You
can't move A above D, or change O2 to a vertical split where A is left
or right of D. [[To get this effect you could close one of the windows,
and re-split the other one with glk_window_open().]]

2.4: A Note on Display Style

The way windows are displayed is, of course, entirely up to the Glk
library; it depends on what is natural for the player's machine. The
borders between windows may be black lines, 3-D bars, rows of "#"
characters; there may even be no borders at all. [[This is an important
possibility to keep in mind.]]

There may be other decorations as well. A text buffer window will often
have a scroll bar. The library (or player) may prefer wide margins
around each text window. And so on.

The library is reponsible for handling these decorations, margins,
spaces, and borders. You should never worry about them. You are
guaranteed that if you request a fixed size of two rows, your text grid
window will have room for two rows of characters -- if there is enough
total space. Any margins or borders will be allowed for already. If
there *isn't* enough total space (as in stages 4 and 5, above), you
lose, of course.

How do you know when you're losing? You can call glk_window_get_size()
to determine the window size you really got. Obviously, you should draw
into your windows based on their real size, not the size you requested.
If there's enough space, the requested size and the real size will be
identical; but you should not rely on this. Call glk_window_get_size()
and check.

2.5: The Types of Windows

This is a technical description of all the window types, and exactly how
they behave.

2.5.1: Blank Windows

A blank window is always blank. It supports no input and no output. (You
can call glk_window_get_stream() on it, as you can with any window, but
printing to the resulting stream has no effect.) A blank window has no
size; glk_window_get_size() will return (0,0), and it is illegal to set
a window split with a fixed size in the measurement system of a blank
window.

[[A blank window is not the same as there being no windows. When Glk
starts up, there are no windows at all, not even a window of the blank
type.]]

2.5.2: Pair Windows

A pair window is completely filled by the two windows it contains. It
supports no input and no output, and it has no size.

You cannot directly create a pair window; one is automatically created
every time you split a window with glk_window_open(). Pair windows are
always created with a rock value of 0.

You can close a pair window with glk_window_close(); this also closes
every window contained within the pair window.

It is legal to split a pair window when you call glk_window_open().

2.5.3: Text Buffer Windows

A text buffer window contains a linear stream of text. It supports
output; when you print to it, the new text is added to the end. There is
no way for you to affect text which has already been printed. There are
no guarantees about how much text the window keeps; old text may be
stored forever, so that the user can scroll back to it, or it may be
thrown away as soon as it scrolls out of the window. [[Therefore, there
may or may not be a player-controllable scroll bar or other scrolling
widget.]]

The display of the text in a text buffer is up to the library. Lines
will probably not be broken in the middles of words -- but if they are,
the library is not doing anything illegal, only ugly. Text selection and
copying to a clipboard, if available, are handled however is best on the
player's machine. Paragraphs (as defined by newline characters in the
output) may be indented. [[You should not, in general, fake this by
printing spaces before each paragraph of prose text. Let the library and
player preferences handle that. Special cases (like indented lists) are
of course up to you.]]

When a text buffer is cleared (with glk_window_clear()), the library
will do something appropriate; the details may vary. It may clear the
window, with later text appearing at the top -- or the bottom. It may
simply print enough blank lines to scroll the current text out of the
window. It may display a distinctive page-break symbol or divider.

The size of a text buffer window is necessarily imprecise. Calling
glk_window_get_size() will return the number of rows and columns that
would be available *if* the window was filled with "0" (zero) characters
in the "normal" font. However, the window may use a non-fixed-width
font, so that number of characters in a line could vary. The window
might even support variable-height text (say, if the player is using
large text for emphasis); that would make the number of lines in the
window vary as well.

Similarly, when you set a fixed-size split in the measurement system of
a text buffer, you are setting a window which can handle a fixed number
of rows (or columns) of "0" characters. The number of rows (or
characters) that will actually be displayed depends on font variances.

A text buffer window supports both character and line input, but not
mouse input.

In character input, there will be some visible signal that the window is
waiting for a keystroke. (Typically, a cursor at the end of the text.)
When the player hits a key in that window, an event is generated, but
the key is *not* printed in the window.

In line input, again, there will be some visible signal. It is most
common for the player to compose input in the window itself, at the end
of the text. (This is how IF story input usually looks.) But it's not
strictly required. An alternative approach is the way MUD clients
usually work: there is a dedicated one-line input window, outside of
Glk's window space, and the user composes input there. [[If this
approach is used, there will still be some way to handle input from two
windows at once. It is the library's responsibility to make this
available to the player. You only need request line input and wait for
the result.]]

When the player finishes his line of input, the library will display the
input text at the end of the buffer text (if it wasn't there already.)
It will be followed by a newline, so that the next text you print will
start a new line (paragraph) after the input.

If you call glk_cancel_line_event(), the same thing happens; whatever
text the user was composing is visible at the end of the buffer text,
followed by a newline.

2.5.4: Text Grid Windows

A text grid contains a rectangular array of characters, in a fixed-width
font. Its size is the number of columns and rows of the array.

A text grid window supports output. It maintains knowledge of an output
cursor position. When the window is opened, it is filled with blanks
(space characters), and the output cursor starts in the top left corner
-- character (0,0). If the window is cleared with glk_window_clear(),
the window is filled with blanks again, and the cursor returns to the
top left corner.

When you print, the characters of the output are laid into the array in
order, left to right and top to bottom. When the cursor reaches the end
of a line, it goes to the beginning of the next line. The library makes
*no* attempt to wrap lines at word breaks.

[[Note that printing fancy characters may cause the cursor to advance
more than one position per character. (For example, the "ae" ligature
may print as two characters.) See section 1.8.1, "Output", for how to
test this situation.]]

You can set the cursor position with glk_window_move_cursor().

    void glk_window_move_cursor(winid_t win, uint32 xpos, uint32 ypos);

If you move the cursor right past the end of a line, it wraps; the next
character which is printed will appear at the beginning of the next
line.

If you move the cursor below the last line, or when the cursor reaches
the end of the last line, it goes "off the screen" and further output
has no effect. You must call glk_window_move_cursor() or
glk_window_clear() to move the cursor back into the visible region.

When a text grid window is resized smaller, the bottom or right area is
thrown away, but the remaining area stays unchanged. When it is resized
larger, the new bottom or right area is filled with blanks. [[You may
wish to watch for evtype_Arrange events, and clear-and-redraw your text
grid windows when you see them change size.]]

Text grid window support character and line input, as well as mouse
input (if a mouse is available.)

Mouse input returns the position of the character that was touched, from
(0,0) to (width-1,height-1).

Character input is as described in the previous section.

Line input is slightly different; it is guaranteed to take place in the
window, at the output cursor position. The player can compose input only
to the right edge of the window; therefore, the maximum input length is
(windowwidth - 1 - cursorposition). If the maxlen argument of
glk_request_line_event() is smaller than this, the library will not
allow the input cursor to go more than maxlen characters past its start
point. [[This allows you to enter text in a fixed-width field, without
the player being able to overwrite other parts of the window.]]

When the player finishes his line of input, it will remain visible in
the window, and the output cursor will be positioned at the beginning of
the *next* row. Again, if you glk_cancel_line_event(), the same thing
happens.

2.6: Echo Streams

Every window has an associated window stream; you print to the window by
printing to this stream. However, it is possible to attach a second
stream to a window. Any text printed to the window is also echoed to
this second stream, which is called the window's "echo stream."

Effectively, any call to glk_put_char() (or the other output commands)
which is directed to the window's window stream, is replicated to the
window's echo stream. This also goes for the style commands such as
glk_set_style().

Note that the echoing is one-way. You can still print text directly to
the echo stream, and it will go wherever the stream is bound, but it
does not back up and appear in the window.

    void glk_window_set_echo_stream(winid_t win, strid_t str);
    strid_t glk_window_get_echo_stream(winid_t win);

Initially, a window has no echo stream, so
glk_window_get_echo_stream(win) will return 0. You can set a window's
echo stream to be any valid output stream by calling
glk_window_set_echo_stream(win, str). You can reset a window to stop
echoing by calling glk_window_set_echo_stream(win, 0).

An echo stream can be of any type, even another window's window stream.
[[This would be somewhat silly, since it would mean that any text
printed to the window would be duplicated in another window. More
commonly, you would set a window's echo stream to be a file stream, in
order to create a transcript file from that window.]]

A window can only have one echo stream. But a single stream can be the
echo stream of any number of windows, sequentially or simultaneously.

If a window is closed, its echo stream remains open; it is *not*
automatically closed. [[Do not confuse the window's window stream with
its echo stream. The window stream is "owned" by the window, and dies
with it. The echo stream is merely temporarily associated with the
window.]]

If a stream is closed, and it is the echo stream of one or more windows,
those windows are reset to not echo anymore. (So then calling
glk_window_get_echo_stream() on them will return 0.)

It is illegal to set a window's echo stream to be its *own* window
stream. That would create an infinite loop, and is nearly certain to
crash the Glk library. It is similarly illegal to create a longer loop
(two or more windows echoing to each other.)

2.7: Other Window Functions

    winid_t glk_window_iterate(winid_t win, uint32 *rockptr);

This function can be used to iterate through the list of all open
windows (including pair windows.) See section 1.4.3, "Iterating Through
Opaque Objects".

As that section describes, the order in which windows are returned is
arbitrary. The root window is not necessarily first, nor is it
necessarily last.

    uint32 glk_window_get_rock(winid_t win);

This returns the window's rock value. Pair windows always have rock 0;
all other windows return whatever rock you created them with.

    uint32 glk_window_get_type(winid_t win);

This returns the window's type (wintype_...)

    winid_t glk_window_get_parent(winid_t win);

This returns the window which is the parent of the given window. If win
is the root window, this returns 0, since the root window has no parent.
Remember that the parent of every window is a pair window; other window
types are always childless.

    winid_t glk_window_get_root(void);

This returns the root window. If there are no windows, this returns 0.

    void glk_window_clear(winid_t win);

Erase the window. The meaning of this depends on the window type.

    * Text buffer: This may do any number of things, such as delete all
text in the window, or print enough blank lines to scroll all text
beyond visibility, or insert a page-break marker which is treated
specially by the display part of the library.
    * Text grid: This will clear the window, filling all positions with
blanks. The window cursor is moved to the top left corner (position
0,0).
    * Other window types: No effect.

It is illegal to erase a window which has line input pending.

    strid_t glk_window_get_stream(winid_t win);

This returns the stream which is associated with the window. (See
section 4.6.1, "Window Streams".) Every window has a stream which can be
printed to, but this may not be useful, depending on the window type.
[[For example, printing to a blank window's stream has no effect.]]

    void glk_set_window(winid_t win);

This sets the current stream to the window's stream. It is exactly
equivalent to

    glk_stream_set_current(glk_window_get_stream(win)).

See section 4, "Streams".

3: Events

As described above, all player input is handed to your program by the
glk_select() call, in the form of events. You should write at least one
event loop to retrieve these events.

    void glk_select(event_t *event);

    typedef struct event_struct {
        uint32 type;
        winid_t win;
        uint32 val1, val2;
    } event_t;

This causes the program to wait for an event, and then store it in the
structure pointed to by the argument. The argument may not be NULL.

Most of the time, you only get the events that you request. However,
there are some events which can arrive at any time. This is why you must
always call glk_select() in a loop, and continue the loop until you get
the event you really want.

The event structure is self-explanatory. type is the event type. The
window that spawned the event, if relevant, is in win. The remaining
fields contain more information specific to the event.

The event types are:

    * evtype_None: No event. This is a placeholder, and glk_select()
never returns it.
    * evtype_Timer: An event that repeats at fixed intervals.
    * evtype_CharInput: A keystroke event in a window.
    * evtype_LineInput: A full line of input completed in a window.
    * evtype_MouseInput: A mouse click in a window.
    * evtype_Arrange: An event signalling that the sizes of some windows
have changed.

3.1: Character Input Events

You can request character input from text buffer and text grid windows.

    void glk_request_char_event(winid_t win);

A window cannot have requests for both character and line input at the
same time. It is illegal to call glk_request_char_event() if the window
already has a pending request for either character or line input.

    void glk_cancel_char_event(winid_t win);

This cancels a pending request for character input. For convenience, it
is legal to call glk_cancel_char_event() even if there is no character
input request on that window. Glk will ignore the call in this case.

If a window has a pending request for character input, and the player
hits a key in that window, glk_select() will return an event whose type
is evtype_CharInput. Once this happens, the request is complete; it is
no longer pending. You must call glk_request_char_event() if you want
another character from that window.

In the event structure, win tells what window the event came from. val1
tells what character was entered; this will be a code from 0 to 255, or
a special keycode. (See section 1.8.3, "Character Input".) val2 will be
0.

3.2: Line Input Events

You can request line input from text buffer and text grid windows.

    void glk_request_line_event(winid_t win, void *buf, uint32 maxlen,
uint32 initlen);

A window cannot have requests for both character and line input at the
same time. It is illegal to call glk_request_line_event() if the window
already has a pending request for either character or line input.

The buf argument is a pointer to space where the line input will be
stored. (This may not be NULL.) maxlen is the length of this space, in
bytes; the library will not accept more characters than this. If initlen
is nonzero, then the first initlen bytes of buf will be entered as
pre-existing input -- just as if the player had typed them himself.
[[The player can continue composing after this pre-entered input, or
delete it or edit as usual.]]

The contents of the buffer are undefined until the input is completed
(either by a line input event, or glk_cancel_line_event(). The library
may or may not fill in the buffer as the player composes, while the
input is still pending; it is illegal to change the contents of the
buffer yourself.

    void glk_cancel_line_event(winid_t win, event_t *event);

This cancels a pending request for line input. The event pointed to by
the event argument will be filled in as if the player had hit enter, and
the input composed so far will be stored in the buffer; see below. If
you do not care about this information, pass NULL as the event argument.
(The buffer will still be filled.)

For convenience, it is legal to call glk_cancel_line_event() even if
there is no character input request on that window. The event type will
be set to evtype_None in this case.

If a window has a pending request for line input, and the player hits
enter in that window (or whatever action is appropriate to enter his
input), glk_select() will return an event whose type is
evtype_LineInput. Once this happens, the request is complete; it is no
longer pending. You must call glk_request_line_event() if you want
another line of text from that window.

In the event structure, win tells what window the event came from. val1
tells how many characters were entered. val2 will be 0. The characters
themselves are stored in the buffer specified in the original
glk_request_line_event() call. [[There is no null terminator stored in
the buffer.]]

It is illegal to print anything to a window which has line input
pending. [[This is because the window may be displaying and editing the
player's input, and printing anything would make life unnecessarily
complicated for the library.]]

3.3: Mouse Input Events

On some platforms, Glk can recognize when the mouse (or other pointer)
is used to select a spot in a window. You can request mouse input only
in text grid windows.

    void glk_request_mouse_event(winid_t win);
    void glk_cancel_mouse_event(winid_t win);

A window can have mouse input and character/line input pending at the
same time.

If the player clicks in a window which has a mouse input event pending,
glk_select() will return an event whose type is evtype_MouseInput.
Again, once this happens, the request is complete, and you must request
another if you want further mouse input.

In the event structure, win tells what window the event came from. The
val1 and val2 fields are the x and y coordinates of the character that
was clicked on. [[So val1 is the column, and val2 is the row.]] The top
leftmost character is considered to be (0,0).

You can test whether mouse input is supported with the
gestalt_MouseInput selector.

    res = glk_gestalt(gestalt_MouseInput, wintype_TextGrid);

This will return TRUE (1) if text grid windows allow mouse input. If
this returns FALSE (0), it is still legal to call
glk_request_mouse_event(), but it will have no effect, and you will
never get mouse events.

[[Most mouse-based idioms define standard functions for mouse hits in
text windows -- typically selecting or copying text. It is up to the
library to separate this from Glk mouse input. The library may choose to
select text when it is clicked normally, and cause Glk mouse events when
text is control-clicked. Or the other way around. Or it may be the
difference between clicking and double-clicking. Or the library may
reserve a particular mouse button, on a multi-button mouse. It may even
specify a keyboard key to be the "mouse button", referring to wherever
the mouse cursor is when the key is hit. You need only know that the
user can do it, or not.]]

[[However, since different platforms will handle this issue differently,
you should be careful how you instruct the player in your program. Do
not tell the player to "double-click", "right-click", or "control-click"
in a window. The preferred term is "to touch the window", or a spot in
the window.]] [[Goofy, but preferred.]]

[[WORK: It would be nice if you could also get mouse events in text
buffer windows. There is no point in returning (x,y) coordinates in a
text buffer. More likely, you would print text in a special "link" style
with a rock value; if the player clicked in such text, you would get a
mouse event with that rock value.]]

3.4: Timer Events

You can request that an event be sent at fixed intervals, regardless of
what the player does.

    void glk_request_timer_events(uint32 millisecs);

It is possible that the library does not support timer events. You can
check this with the gestalt_Timer selector.

    res = glk_gestalt(gestalt_Timer, 0);

This returns 1 if timer events are supported, and 0 if they are not.

Initially, there is no timer and you get no timer events. If you call
glk_request_timer_events(N), with N not 0, you will get timer events
about every N milliseconds thereafter. (Assuming that they are supported
-- if not, glk_request_timer_events() has no effect.) Unlike keyboard
and mouse events, timer events will continue until you shut them off.
You do not have to re-request them every time you get one. Call
glk_request_timer_events(0) to stop getting timer events.

The rule is that when you call glk_select(), if it has been more than N
milliseconds since the last timer event, and there is no player input,
glk_select() will return an event whose type is evtype_Timer. (win,
val1, and val2 will all be 0.)

Timer events do not stack up. If you spend 10N milliseconds doing
computation, and then call glk_select(), you will not get ten timer
events in a row. The library will simply note that it has been more than
N milliseconds, and return a timer event right away. If you call
glk_select() again immediately, it will be N milliseconds before the
next timer event.

This means that the timing of timer events is approximate, and the
library will err on the side of being late. If there is a conflict
between player input events and timer events, the player input takes
precedence. [[This prevents the user from being locked out by overly
enthusiastic timer events. Unfortunately, it also means that your timer
can be locked out on slower machines, if the player pounds too
enthusiastically on the keyboard. Sorry. If you want a real-time
operating system, talk to Wind River.]]

[[I don't have to tell you that a millisecond is one thousandth of a
second, do I?]]

3.5: Window Arrangement Events

Some platforms allow the player to resize the Glk window during play.
This will naturally change the sizes of your windows. If this occurs,
then immediately *after* all the rearrangement, glk_select() will return
an event whose type is evtype_Arrange. You can use this notification to
redisplay the contents of a text grid window whose size has changed.
[[The display of a text buffer window is entirely up to the library, so
you don't need to worry about those.]]

In the event structure, win will be 0 if all windows are affected. If
only some windows are affected, win will refer to a window which
contains all the affected windows. [[You can always play it safe, ignore
win, and redraw every text grid window.]] val1 and val2 will be 0.

An arrangement event is guaranteed to occur whenever the player causes
any window to change size, as measured by its own metric. [[Size changes
caused by you -- for example, if you open, close, or resize a window --
do not trigger arrangement events. You must be aware of the effects of
your window management, and redraw the text grid windows that you
affect.]]

[[It is possible that several different player actions can cause windows
to change size. For example, if the player changes the screen
resolution, an arrangement event might be triggered. This might also
happen if the player changes his display font to a different size; the
windows would then be different "sizes" in the metric of rows and
columns, which is the important metric and the only one you have access
to.]]

3.6: Other Events

There are currently no other event types defined by Glk. (The
"evtype_None" constant is a placeholder, and is never returned by
glk_select().)

It is possible that new event types will be defined in the future.

[[For example, the Z-machine has a "sound interrupt" mechanism; you can
set a routine to be called when a given sound is finished playing. If
Glk is extended to support sound, a sound-finished event might be
defined. Note that this neatly avoids the problem of reentrant
interpreter design, which complicates the Z-machine.]]

[[This is also why you must put calls to glk_select() in loops. If you
tried to read a character by simply writing
    glk_request_char_event(win);
    glk_select(&ev);
you might not get a CharInput event back. You could get some
not-yet-defined event which happened to occur before the player hit a
key. Or, for that matter, a window arrangement event.]]

4: Streams

All character output in Glk is done through streams. Every window has an
output stream associated with it. You can also write to files on disk;
every open file is represented by an output stream as well.

There are also input streams; these are used for reading from files on
disk. It is possible for a stream to be both an input and an output
stream. [[Player input is done through line and character input events,
not streams. This is a small inelegance in theory. In practice, player
input is slow and things can interrupt it, whereas file input is
immediate. If a network extension to Glk were proposed, it would
probably use events and not streams, since network communication is not
immediate.]]

A stream is opened with a particular file mode:

    * filemode_Write: An output stream.
    * filemode_Read: An input stream.
    * filemode_ReadWrite: Both an input and an output stream.
    * filemode_WriteAppend: An output stream, but the data will added to
the end of whatever already existed in the destination, instead of
replacing it.

For information on opening streams, see the discussion of each specific
type of stream in section 4.6, "The Types of Streams". Remember that it
is always possible that opening a stream will fail, in which case the
creation function will return 0.

Each stream remembers two character counts, the number of characters
printed to and read from that stream. The write-count is exactly one per
glk_put_char() call; it is figured before any platform-dependent
character cookery. [[For example, if a newline character is converted to
newline-plus-linefeed, the stream's count still only goes up by one;
similarly if an accented character is displayed as two characters.]] The
read-count is exactly one per glk_get_char() call, as long as the call
returns an actual character (as opposed to an end-of-file token.)

Glk has a notion of the "current (output) stream". If you print text
without specifying a stream, it goes to the current output stream. The
current output stream may be 0, meaning that there isn't one. As with
other opaque Glk objects, 0 is not the id of a valid stream. It is
illegal to print text to stream 0, or to print to the current stream
when there isn't one.

If the stream which is the current stream is closed, the current stream
becomes 0 (none.)

    void glk_stream_set_current(strid_t str);

This sets the current stream to str, which must be an output stream. You
may set the current stream to 0, which means the current stream is not
set to anything.

    strid_t glk_stream_get_current(void);

Returns the current stream, or 0 if there is none.

4.1: How To Print

    void glk_put_char(unsigned char ch);

This prints one character to the current stream. As always, the
character is assumed to be in the Latin-1 character encoding. See
section 1.8, "Character Encoding".

    void glk_put_string(char *s);

This prints a null-terminated string to the current stream. It is
exactly equivalent to

    for (ptr = s; *ptr; ptr++)
        glk_put_char(*ptr);

However, it may be more efficient.

    void glk_put_buffer(char *buf, uint32 len);

This prints a block of characters to the current stream. It is exactly
equivalent to

    for (i = 0; i < len; i++)
        glk_put_char(buf[i]);

However, it may be more efficient.

    void glk_put_char_stream(strid_t str, unsigned char ch);
    void glk_put_string_stream(strid_t str, char *s);
    void glk_put_buffer_stream(strid_t str, char *buf, uint32 len);

These are the same functions, except that you specify a stream to print
to, instead of using the current stream. Again, it is illegal for str to
be 0 or any other invalid id, or the id of an input-only stream.

4.2: How To Read

    uint32 glk_get_char_stream(strid_t str);

This reads one character from the given stream. (There is no notion of a
"current input stream.") It is illegal for str to be 0 or any other
invalid id, or the id of an output-only stream.

The result will be between 0 and 255; as always, Glk assumes the Latin-1
encoding. See section 1.8, "Character Encoding". If the end of the
stream has been reached, the result will be -1 (0xFFFFFFFF).

    void glk_get_line_stream(strid_t str, char *buf, uint32 len);
    void glk_get_buffer_stream(strid_t str, char *buf, uint32 len);

[[WORK: Not yet implemented. Return the number of chars read?]]

4.3: Closing Streams

    void glk_stream_close(strid_t str, stream_result_t *result);

    typedef struct stream_result_struct {
        uint32 readcount;
        uint32 writecount;
    } stream_result_t;

This closes the stream str. The result argument points to a structure
which is filled in with the final character counts of the stream. If you
do not care about these, you may pass NULL as the result argument.

If str is the current output stream, the current output stream is set to
0 (none.)

You cannot close window streams; use glk_window_close() instead. See
section 2.2, "Window Opening, Closing, and Constraints".

4.4: Stream Positions

You can set the position of the read/write mark in a stream. [[Which
makes one wonder why they're called "streams" in the first place. Oh
well.]]

    uint32 glk_stream_get_position(strid_t str);

This returns the position of the mark. For memory streams and binary
file streams, this is exactly the number of bytes read or written from
the beginning of the stream (unless you have moved the mark with
glk_stream_set_position().) For text file streams, matters are more
ambiguous, since (for example) writing one byte to a text file may store
more than one character in the platform's native encoding. You can only
be sure that the position increases as you read or write to the file.

    void glk_stream_set_position(strid_t str, uint32 pos, uint32
seekmode);

This sets the position of the mark. The position is controlled by pos,
and the meaning of pos is controlled by seekmode:

    * seekmode_Start: pos characters after the beginning of the file.
    * seekmode_Current: pos characters after the current position
(moving backwards if pos is negative.)
    * seekmode_End: pos characters after the end of the file. (pos
should always be zero or negative, so that this will move backwards to a
position within the file.)

It is illegal to specify a position before the beginning or after the
end of the file.

4.5: Styles

You can send style-changing commands to an output stream. After a style
change, new text which is printed to that stream will be given the new
style, whatever that means for the stream in question. For a window
stream, the text will appear in that style. For a memory stream, style
changes have no effect. For a file stream, if the machine supports
styled text files, the styles may be written to the file; more likely
the style changes will have no effect.

[[Note that every stream and window has its own idea of the "current
style." Sending a style command to one window or stream does not affect
any others.]] [[Except for a window's echo stream; see section 2.6,
"Echo Streams".]]

The styles are intended to distinguish meaning and use, not formatting.
There is *no* standard definition of what each style will look like.
That is left up to the Glk library, which will choose an appearance
appropriate for the platform's interface and the player's preferences.

There are currently eleven styles defined.

    * style_Normal: The style of normal or body text. A new window or
stream always starts with style_Normal as the current style.
    * style_Emphasized: Text which is emphasized.
    * style_Preformatted: Text which has a particular arrangement of
characters. [[This style, unlike the others, *does* have a standard
appearance; it will always be a fixed-width font. This is a concession
to practicality. Games often want to display maps or diagrams using
character graphics, and this is the style for that.]]
    * style_Header: Text which introduces a large section. This is
suitable for the title of an entire game, or a major division such as a
chapter.
    * style_Subheader: Text which introduces a smaller section within a
large section. [[In a Colossal-Cave-style game, this is suitable for the
name of a room (when the player looks around.)]]
    * style_Alert: Text which warns of a dangerous condition, or one
which the player should pay attention to.
    * style_Note: Text which notifies of an interesting condition.
[[This is suitable for noting that the player's score has changed.]]
    * style_BlockQuote: Text which forms a quotation or otherwise
abstracted text.
    * style_Input: Text which the player has entered. You should
generally not use this style at all; the library uses it for text which
is typed during a line-input request. One case when it *is* appropriate
for you to use style_Input is when you are simulating player input by
reading commands from a text file.
    * style_User1: This style has no particular semantic meaning. You
may define a meaning relevant to your own work, and use it as you see
fit.
    * style_User2: Another style available for your use.

Styles may be distinguished on screen by font, size, color, indentation,
justification, and other attributes. Note that some attributes (notably
justification and indentation) apply to entire paragraphs. If possible
and relevant, you should apply a style to an entire paragraph -- call
glk_set_style() immediately after printing the newline at the beginning
of the text, and do the same at the end.

[[For example, style_Header may well be centered text. If you print
"Welcome to Victim (a short interactive mystery)", and only the word
"Victim" is in the style_Header, the center-justification attribute will
be lost. Similarly, a block quote is usually indented on both sides, but
indentation is only meaningful when applied to an entire line or
paragraph, so block quotes should take up an entire paragraph.
Contrariwise, style_Emphasized need not be used on an entire paragraph.
It is often used for single emphasized words in normal text, so you can
expect that it will appear properly that way; it will be displayed in
italics or underlining, not center-justified or indented.]]

[[Yes, this is all a matter of mutual agreement between game authors and
game players. It's not fixed by this specification. That's natural
language for you.]]

    void glk_set_style(uint32 val);

This changes the style of the current output stream.

    void glk_set_style_stream(strid_t str, uint32 val);

This changes the style of the stream str.

4.5.1: Suggesting the Appearance of Styles

There are no guarantees of how styles will look, but you can make
suggestions.

    void glk_stylehint_set(uint32 wintype, uint32 styl, uint32 hint,
uint32 val);
    void glk_stylehint_clear(uint32 wintype, uint32 styl, uint32 hint);

These functions set and clear hints about the appearance of one style
for a particular type of window. You can also set wintype to
wintype_AllTypes, which sets (or clears) a hint for all types of window.
[[There is no equivalent constant to set a hint for all styles of a
single window type.]]

Initially, no hints are set for any window type or style. Note that
having no hint set is not the same as setting a hint with value 0.

These functions do *not* affect *existing* windows. They affect the
windows which you create subsequently. If you want to set hints for all
your game windows, call glk_stylehint_set() before you start creating
windows. If you want different hints for different windows, change the
hints before creating each window.

[[This policy makes life easier for the interpreter. It knows everything
about a particular window's appearance when the window is created, and
it doesn't have to change it while the window exists.]]

Hints are hints. The interpreter may ignore them, or give the player a
choice about whether to accept them. Also, it is never necessary to set
hints. You don't have to suggest that style_Preformatted be fixed-width,
or style_Emphasized be boldface or italic; they will have appropriate
defaults. Hints are for situations when you want to *change* the
appearance of a style from what it would ordinarily be. The most common
case when this is appropriate is for the styles style_User1 and
style_User2. 

There are currently nine style hints defined.

    * stylehint_Indentation: How much to indent lines of text in the
given style. May be a negative number, to shift the text out (left)
instead of in (right). The exact metric isn't precisely specified; you
can assume that +1 is the smallest indentation possible which is clearly
visible to the player.
    * stylehint_ParaIndentation: How much to indent the first line of
each paragraph. This is in addition to the indentation specified by
stylehint_Indentation. This too may be negative, and is measured in the
same units as stylehint_Indentation.
    * stylehint_Justification: The value of this hint must be one of the
constants stylehint_just_LeftFlush, stylehint_just_LeftRight (full
justification), stylehint_just_Centered, or stylehint_just_RightFlush.
    * stylehint_Size: How much to increase or decrease the font size.
This is relative; 0 means the interpreter's default font size will be
used, positive numbers increase it, and negative numbers decrease it.
Again, +1 is the smallest size increase which is easily visible. [[The
amount of this increase may not be constant. +1 might increase an
8-point font to 9-point, but a 16-point font to 18-point.]]
    * stylehint_Weight: The value of this hint must be 1 for
heavy-weight fonts (boldface), 0 for normal weight, and -1 for
light-weight fonts.
    * stylehint_Oblique: The value of this hint must be 1 for oblique
fonts (italic), or 0 for normal angle.
    * stylehint_Proportional: The value of this hint must be 1 for
proportional-width fonts, or 0 for fixed-width.
    * stylehint_TextColor: The foreground color of the text. This is
encoded in the 32-bit hint value: the top 8 bits must be zero, the next
8 bits are the red value, the next 8 bits are the green value, and the
bottom 8 bits are the blue value. Color values range from 0 to 255. [[So
0x00000000 is black, 0x00FFFFFF is white, and 0x00FF0000 is bright
red.]]
    * stylehint_BackColor: The background color behind the text. This is
encoded the same way as stylehint_TextColor.

4.5.2: Testing the Appearance of Styles

You can suggest the appearance of a window's style before the window is
created; after the window is created, you can test the style's actual
appearance. These functions do not test the style hints; they test the
attribute of the style as it appears to the player.

Note that although you cannot change the appearance of a window's styles
after the window is created, the library can. A platform may support
dynamic preferences, which allow the player to change text formatting
while your program is running. [[Changes that affect window size (such
as font size changes) will be signalled by an evtype_Arrange event.
However, more subtle changes (such as text color differences) are not
signalled. If you test the appearance of styles at the beginning of your
program, you must keep in mind the possibility that the player will
change them later.]]

    uint32 glk_style_distinguish(winid_t win, uint32 styl1, uint32
styl2);

This returns TRUE (1) if the two styles are visually distinguishable in
the given window. If they are not, it returns FALSE (0). The exact
meaning of this is left to the library to determine.

    uint32 glk_style_measure(winid_t win, uint32 styl, uint32 hint,
uint32 *result);

This tries to test an attribute of one style in the given window. The
library may not be able to determine the attribute; if not, this returns
FALSE (0). If it can, it returns TRUE (1) and stores the value in the
location pointed at by result. [[As usual, it is legal for result to be
NULL, although fairly pointless.]]

The meaning of the value depends on the hint which was tested:

    * stylehint_Indentation, stylehint_ParaIndentation: The indentation
and paragraph indentation. These are in a metric which is
platform-dependent. [[Most likely either characters or pixels.]]
    * stylehint_Justification: One of the constants
stylehint_just_LeftFlush, stylehint_just_LeftRight,
stylehint_just_Centered, or stylehint_just_RightFlush.
    * stylehint_Size: The font size. Again, this is in a
platform-dependent metric. [[Pixels, points, or simply 1 if the library
does not support varying font sizes.]]
    * stylehint_Weight: 1 for heavy-weight fonts (boldface), 0 for
normal weight, and -1 for light-weight fonts.
    * stylehint_Oblique: 1 for oblique fonts (italic), or 0 for normal
angle.
    * stylehint_Proportional: 1 for proportional-width fonts, or 0 for
fixed-width.
    * stylehint_TextColor, stylehint_BackColor: These are values from
0x00000000 to 0x00FFFFFF, encoded as described in section 4.5.1,
"Suggesting the Appearance of Styles".

4.6: The Types of Streams

4.6.1: Window Streams

Every window has an output stream associated with it. This is created
automatically, with filemode_Write, when you open the window. You get it
with glk_window_get_stream().

A window stream cannot be closed with glk_stream_close(). It is closed
automatically when you close its window with glk_window_close().

Only printable characters (including newline) may be printed to a window
stream. See section 1.8, "Character Encoding".

4.6.2: Memory Streams

You can open a stream which reads from or writes into a space in memory.

    strid_t glk_stream_open_memory(void *buf, uint32 buflen, uint32
fmode, uint32 rock);

fmode must be filemode_Read, filemode_Write, or filemode_ReadWrite.

buf points to the buffer where output will be read from or written to.
buflen is the length of the buffer.

When outputting, if more than buflen characters are written to the
stream, all of them beyond the buffer length will be thrown away, so as
not to overwrite the buffer. (The character count of the stream will
still be maintained correctly.) If buf is NULL, or for that matter if
buflen is zero, then *everything* written to the stream is thrown away.
This may be useful if you are interested in the character count.

When inputting, if more than buflen characters are read from the stream,
the stream will start returning -1 (signalling end-of-file.) If buf is
NULL, the stream will always return end-of-file.

The data is written to the buffer exactly as it was passed to the
printing functions (glk_put_char(), etc); input functions will read the
data exactly as it exists in memory. No platform-dependent cookery will
be done on it. [[You can write a disk file in text mode, but a memory
stream is effectively always in binary mode.]]

Whether reading or writing, the contents of the buffer are undefined
until the stream is closed. The library may store the data there as it
is written, or deposit it all in a lump when the stream is closed. It is
illegal to change the contents of the buffer while the stream is open.

4.6.3: File Streams

You can open a stream which reads from or writes to a disk file.

    strid_t glk_stream_open_file(frefid_t fileref, uint32 fmode, uint32
rock);

fileref indicates the file which will be opened. fmode can be any of
filemode_Read, filemode_Write, filemode_WriteAppend, or
filemode_ReadWrite. If fmode is filemode_Read, the file must already
exist; for the other modes, an empty file is created if none exists. If
fmode is filemode_Write, and the file already exists, it is truncated
down to zero length (an empty file). If fmode is filemode_WriteAppend,
the file mark is set to the end of the file.

The file may be read or written in text or binary mode; this is
determined by the fileref argument. Similarly, platform-dependent
attributes such as file type are determined by fileref. See section 5,
"File References".

4.7: Other Stream Functions

    strid_t glk_stream_iterate(strid_t str, uint32 *rockptr);

This iterates through all the existing streams. See section 1.4.3,
"Iterating Through Opaque Objects".

    uint32 glk_stream_get_rock(strid_t str);

This retrieves the streams's rock value. See section 1.4.2, "Rocks".

5: File References

You deal with disk files using file references. Each fileref has an
unsigned 32-bit integer identifier; see section 1.4.1, "Identifiers".

A file reference contains platform-specific information about the name
and location of the file, and possibly its type, if the platform has a
notion of file type. It also includes a flag indication whether the file
is a text file or binary file. [[Note that this is different from the
standard C I/O library, in which you specify text or binary mode when
the file is opened.]]

A fileref does not have to refer to a file which actually exists. You
can create a fileref for a nonexistent file, and then open it in write
mode to create a new file.

You always provide a usage argument when you create a fileref. The usage
is a mask of constants to indicate the file type and the mode (text or
binary.) These values are used when you create a new file, and also to
filter file lists when the player is selecting a file to load. The
constants are as follows:

    * fileusage_SavedGame: A file which stores game state.
    * fileusage_Transcript: A file which contains a stream of text from
the game (often an echo stream from a window.)
    * fileusage_InputRecord: A file which records player input.
    * fileusage_Data: Any other kind of file (preferences, statistics,
arbitrary data.)

    * fileusage_BinaryMode: The file contents will be stored exactly as
they are written, and read back in the same way. The resulting file may
not be viewable on platform-native text file viewers.
    * fileusage_TextMode: The file contents will be transformed to a
platform-native text file as they are written out. Newlines may be
converted to linefeeds or newline-linefeed combinations; Latin-1
characters may be converted to native character codes. When reading a
file in text mode, native line breaks will be converted back to newline
(0x0A) characters, and native character codes may be converted to
Latin-1. [[Linefeeds will always be converted; other conversions are
more questionable. If you write out a file in text mode, and then read
it back in text mode, high-bit characters (128 to 255) may be
transformed or lost.]]

In general, you should use text mode if the player expects to read the
file with a platform-native text editor; you should use binary mode if
the file is to be read back by your program, or if the data must be
stored exactly. Text mode is appropriate for fileusage_Transcript;
binary mode is appropriate for fileusage_SavedGame and probably for
fileusage_InputRecord. fileusage_Data files may be text or binary,
depending on what you use them for.

5.1: The Types of File References

There are three different functions for creating a fileref, depending on
how you wish to specify it. Remember that it is always possible that a
fileref creation will fail and return 0.

    frefid_t glk_fileref_create_temp(uint32 usage, uint32 rock);

This creates a reference to a temporary file. It is always a new file
(one which does not yet exist). The file (once created) will be
somewhere out of the player's way. [[This is why no name is specified;
the player will never need to know it.]]

A temporary file should not be used for long-term storage. It may be
deleted automatically when the program exits, or at some later time, say
when the machine is turned off or rebooted. You do not have to worry
about deleting it yourself.

    frefid_t glk_fileref_create_by_prompt(uint32 usage, uint32 fmode,
uint32 rock);

This creates a reference to a file by asking the player to locate it.
The library may simply prompt the player to type a name, or may use a
platform-native file navigation tool. (The prompt, if any, is inferred
from the usage argument.)

fmode must be one of these values:

    * filemode_Read: The file must already exist; the player will be
asked to select from existing files which match the usage.
    * filemode_Write: The file should not exist; if the player selects
an existing file, he will be warned that it will be replaced.
    * filemode_ReadWrite: The file may or may not exist; if it already
exists, the player will be warned that it will be modified.
    * filemode_WriteAppend: Same behavior as filemode_ReadWrite.

The fmode argument should generally match the fmode which will be used
to open the file.

[[It is possible that the prompt or file tool will have a "cancel"
option. If the player chooses this, glk_fileref_create_by_prompt() will
return 0. This is a major reason why you should make sure the return
value is valid before you use it.]]

    frefid_t glk_fileref_create_by_name(uint32 usage, char *name, uint32
rock);

This creates a reference to a file with a specific name. The file will
be in a fixed location relevant to your program, and visible to the
player. [[This usually means "in the same directory as your program."]]

Since filenames are highly platform-specific, you should use
glk_fileref_create_by_name() with care. It is legal to pass any string
in the name argument. However, the library may have to mangle,
transform, or truncate the string to make it a legal native filename.
[[For example, if you create two filerefs with the names "File" and
"FILE", they may wind up pointing to the *same* file; the platform may
not support case distinctions in file names. Another example: on a
platform where file type is specified by filename suffix, the library
will add an appropriate suffix based on the usage; any suffix in the
string will be overwritten or added to. For that matter, remember that
the period is not a legal character in Acorn filenames...]]

The most conservative approach is to pass a string of no more than 8
characters, consisting entirely of upper-case letters and numbers,
starting with a letter. You can then be reasonably sure that the
resulting filename will display all the characters you specify -- in
some form.

5.2: Other File Reference Functions

    void glk_fileref_destroy(frefid_t fref);

Destroys a fileref which you have created. This does *not* affect the
disk file; it just reclaims the resources allocated by the
glk_fileref_create... function.

It is legal to destroy a fileref after opening a file with it (while the
file is still open.) The fileref is only used for the opening operation,
not for accessing the file stream.

    frefid_t glk_fileref_iterate(frefid_t fref, uint32 *rockptr);

This iterates through all the existing filerefs. See section 1.4.3,
"Iterating Through Opaque Objects".

    uint32 glk_fileref_get_rock(frefid_t fref);

This retrieves the fileref's rock value. See section 1.4.2, "Rocks".

    void glk_fileref_delete_file(frefid_t fref);

This deletes the file referred to by fref. It does not destroy the
fileref itself.

    uint32 glk_fileref_does_file_exist(frefid_t fref);

This returns TRUE (1) if the fileref refers to an existing file, and
FALSE (0) if not.


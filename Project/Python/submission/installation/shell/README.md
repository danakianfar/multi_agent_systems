# NetLogo shell extension

This package contains the NetLogo shell extension.

It lets you do things like:

> (Mac) `observer> show shell:exec "ls"`

> (Windows) `observer> show (shell:exec "cmd" "/c" "dir")`

The included commands are:

 * `shell:pwd` => reports current working directory
 * `shell:cd <directory>` => change current working directory (relative to current directory unless <directory> begins with a drive letter on Windows or a forward slash on Mac/Unix)
 * `shell:getenv <name>` => reports value of environment variable
 * `shell:setenv <name> <value>` => sets environment variable
 * `shell:exec <command> (shell:exec <command> <param> ...)` => execute command synchronously and report a string of the results it prints to stdout
 * `shell:fork <command> (shell:fork <command> <param> ...)` => execute command asynchronously and discard the results

## Using

Download and unzip to the extensions folder inside your NetLogo program folder.

For more information about NetLogo extensions in general, see the NetLogo User Manual.

## Building

Use the NETLOGO environment variable to tell the Makefile which NetLogo.jar to compile against.  For example:

    NETLOGO=/Applications/NetLogo\\\ 5.0 make

If compilation succeeds, `shell.jar` will be created.

## Credits

The shell extension was written by Eric Russell.

## Terms of Use

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png)](http://creativecommons.org/publicdomain/zero/1.0/)

The NetLogo shell extension is in the public domain.  To the extent possible under law, Eric Russell has waived all copyright and related or neighboring rights.

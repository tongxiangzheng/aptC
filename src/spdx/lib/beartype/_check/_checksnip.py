#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type-checking function code snippets** (i.e., triple-quoted
pure-Python string constants formatted and concatenated together to dynamically
generate the implementations of functions type-checking arbitrary objects
against arbitrary PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.checkmagic import (
    ARG_NAME_CONF,
    ARG_NAME_CLS_STACK,
    ARG_NAME_FUNC,
    ARG_NAME_EXCEPTION_PREFIX,
    ARG_NAME_GET_VIOLATION,
    ARG_NAME_HINT,
    ARG_NAME_WARN,
    VAR_NAME_PITH_ROOT,
    VAR_NAME_RANDOM_INT,
    VAR_NAME_VIOLATION,
)

# ....................{ CODE ~ signature                   }....................
CODE_CHECKER_SIGNATURE = f'''{{code_signature_prefix}}def {{func_name}}(
    {VAR_NAME_PITH_ROOT},
{{code_signature_args}}
):'''
'''
Code snippet declaring the signature of all type-checking tester functions
created by the :func:`beartype._check.checkmagic.make_func_tester` factory.

Note that:

* This signature intentionally:

  * Avoids annotating its parameters or return by type hints. Doing so would be:

    * Pointless, as the type-checking functions dynamically created and returned
      by factory functions defined by the "beartype._check.checkmake" submodule
      are only privately called by the public beartype.door.is_bearable() and
      beartype.door.die_if_unbearable() runtime type-checkers.
    * Harmful, as doing so would prevent this common signature from being
      generically reused as the signature for both raisers and testers.

  * Names the single public parameter accepted by this tester function
    ``{VAR_NAME_PITH_ROOT}``. Doing so trivially ensures that the memoized
    type-checking boolean expression generated by the
    :func:`beartype._check.code.codemake.make_check_expr` code factory
    implicitly type-checks the passed object *without* further modification
    (e.g., global search-and-replacement), ensuring that memoized expression may
    be efficiently reused as is *without* subsequent unmemoization. Clever, huh?

* ``code_signature_prefix`` is usually either:

  * For synchronous callables, the empty string.
  * For asynchronous callables (e.g., asynchronous generators, coroutines), the
    space-suffixed keyword ``"async "``.
'''

# ....................{ CODE ~ check                       }....................
CODE_TESTER_CHECK_PREFIX = '''
    # Return true only if the passed object satisfies this type hint.
    return '''
'''
Code snippet prefixing the type-check of an arbitrary object passed to a
type-checking tester function against an arbitrary type hint passed to the same
function.
'''

# ....................{ CODE ~ check                       }....................
CODE_RAISER_HINT_OBJECT_CHECK_PREFIX = '''

    # Type-check this object against this type hint.
    if not '''
'''
Code snippet prefixing the type-check of an arbitrary object passed to a
type-checking raiser function against an arbitrary type hint passed to the same
function.
'''


CODE_RAISER_FUNC_PITH_CHECK_PREFIX = '''
        # Type-check this parameter or return against this type hint.
        if not '''
'''
Code snippet prefixing the type-check of a parameter or return of a decorated
callable against the type hint annotating that parameter or return.
'''

# ....................{ CODE ~ violation : get             }....................
CODE_GET_HINT_OBJECT_VIOLATION = f''':
            {VAR_NAME_VIOLATION} = {ARG_NAME_GET_VIOLATION}(
                obj={VAR_NAME_PITH_ROOT},
                hint={ARG_NAME_HINT},
                conf={ARG_NAME_CONF},
                exception_prefix={ARG_NAME_EXCEPTION_PREFIX},{{arg_random_int}}
            )
'''
'''
Code snippet suffixing all code type-checking the **root pith** (i.e., arbitrary
object) against the root type hint annotating that pith by either raising a
fatal exception or emitting a non-fatal warning.

This snippet expects to be formatted with these named interpolations:

* ``{arg_random_int}``, whose value is either:

  * If type-checking for the current type hint requires a pseudo-random integer,
    :data:`.CODE_HINT_ROOT_SUFFIX_RANDOM_INT`.
  * Else, the empty substring.
'''


CODE_GET_FUNC_PITH_VIOLATION = f''':
            {VAR_NAME_VIOLATION} = {ARG_NAME_GET_VIOLATION}(
                func={ARG_NAME_FUNC},
                conf={ARG_NAME_CONF},
                pith_name={{pith_name}},
                pith_value={VAR_NAME_PITH_ROOT},{{arg_cls_stack}}{{arg_random_int}}
            )
'''
'''
Code snippet suffixing all code type-checking the **root pith** (i.e., value of
the current parameter or return value) against the root type hint annotating
that pith by either raising a fatal exception or emitting a non-fatal warning.

This snippet expects to be formatted with these named interpolations:

* ``{arg_cls_stack}``, whose value is either:

  * If type-checking for the current type hint requires the type stack,
    :data:`.CODE_HINT_ROOT_SUFFIX_CLS_STACK`.
  * Else, the empty substring.

* ``{arg_random_int}``, whose value is either:

  * If type-checking for the current type hint requires a pseudo-random integer,
    :data:`.CODE_HINT_ROOT_SUFFIX_RANDOM_INT`.
  * Else, the empty substring.
'''


CODE_GET_VIOLATION_CLS_STACK = f'''
                cls_stack={ARG_NAME_CLS_STACK},'''
'''
Code snippet passing the value of the **type stack** (i.e., either a tuple of
the one or more :func:`beartype.beartype`-decorated classes lexically containing
the class variable or method annotated by a type hint type-checked by the larger
code snippet embedding this snippet *or* :data:`None`) required by the current
call to the exception-handling function call embedded in the
:data:`.CODE_HINT_ROOT_SUFFIX` snippet.
'''


CODE_GET_VIOLATION_RANDOM_INT = f'''
                random_int={VAR_NAME_RANDOM_INT},'''
'''
Code snippet passing the value of the random integer previously
generated for the current call to the exception-handling function call embedded
in the :data:`.CODE_HINT_ROOT_SUFFIX` snippet.
'''

# ....................{ CODE ~ violation                   }....................
CODE_RAISE_VIOLATION = f'''
            raise {VAR_NAME_VIOLATION}'''
'''
Code snippet raising the type-checking violation previously generated by the
:data:`.CODE_HINT_ROOT_SUFFIX` or
:data:`.PEP484_CODE_CHECK_NORETURN` code snippets as a fatal exception.
'''


CODE_WARN_VIOLATION = f'''
            {ARG_NAME_WARN}(str({VAR_NAME_VIOLATION}), type({VAR_NAME_VIOLATION}))'''
'''
Code snippet emitting the type-checking violation previously generated by the
:data:`.CODE_HINT_ROOT_SUFFIX` or
:data:`.PEP484_CODE_CHECK_NORETURN` code snippets as a non-fatal warning.
'''
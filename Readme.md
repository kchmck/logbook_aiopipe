# logbook_aiopipe -- Multiprocess logbook logging for asyncio

[Documentation](http://kchmck.github.io/pdoc/logbook_aiopipe/)

This package provides a handler and subscriber for multiprocess
[`logbook`](http://logbook.readthedocs.io) logging that runs on the
[`asyncio`](https://docs.python.org/3/library/asyncio.html) event loop. It uses
[`aiopipe`](https://github.com/kchmck/aiopipe) to transfer log messages from the child
process to the parent process.

## Example

The following example shows a typical application of logging from a child process to a
parent process. It results in two log messages, `hello from parent process` and `hello
from child process`, being printed in some order.

```python
from contextlib import closing
from multiprocessing import Process
import asyncio

from aiopipe import aiopipe
from logbook_aiopipe import AioPipeSubscriber, \
        AioPipeHandler
from logbook import Logger, StderrHandler

async def mainTask(eventLoop):
    # The parent process logger can be set up as normal.
    log = Logger()
    log.handlers.append(StderrHandler())

    rx, tx = aiopipe()
    sub = AioPipeSubscriber(await rx.open(eventLoop), log)

    with closing(sub):
        subTask = eventLoop.create_task(sub.run())

        with tx.send() as tx:
            proc = Process(target=childProc, args=(tx,))
            proc.start()

        log.info("hello from parent process")

        proc.join()
        await subTask

def childProc(tx):
    eventLoop = asyncio.new_event_loop()
    eventLoop.run_until_complete(childTask(eventLoop, tx))

async def childTask(eventLoop, tx):
    log = Logger()

    # The child process should use only `AioPipeHandler` as
    # its handler.
    handler = AioPipeHandler(await tx.open(eventLoop))
    log.handlers.append(handler)

    with closing(handler):
        log.info("hello from child process")

eventLoop = asyncio.get_event_loop()
eventLoop.run_until_complete(mainTask(eventLoop))
```

## Installation

This package requires Python >= 3.5.0 and can be installed with `pip`:
```
pip install logbook_aiopipe
```

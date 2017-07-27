"""
This package provides a handler and subscriber for multiprocess
[`logbook`](http://logbook.readthedocs.io) logging that runs on the
[`asyncio`](https://docs.python.org/3/library/asyncio.html) event loop. It uses
[`aiopipe`](https://github.com/kchmck/aiopipe) to transfer log messages from the child
process to the parent process.

#### Example

The following example shows a typical application of multiprocess logging. It results in
two log messages, `hello from parent process` and `hello from child process`, being
printed in some order.

```python3
from contextlib import closing
from multiprocessing import Process
import asyncio

from aiopipe import aiopipe
from logbook_aiopipe import AioPipeSubscriber, \\
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
"""

from asyncio import IncompleteReadError
import json

from logbook import Handler, LogRecord

class AioPipeHandler(Handler):
    """
    Forwards log messages in a child process to the parent process.

    This should be pushed on the stack or added to a `Logger` in the [typical
    manner](https://logbook.readthedocs.io/en/stable/quickstart.html#registering-handlers).
    """

    def __init__(self, tx, *args, **kwargs):
        """
        Create a new `AioPipeHandler` that forwards log messages over the given pipe
        transmit end. The other arguments are passed to
        [`logbook.Handler`](https://logbook.readthedocs.io/en/stable/api/handlers.html#logbook.Handler).
        This object takes ownership of `tx`.

        This handler should be attached to a `logbook.Logger` instance.
        """

        super().__init__(*args, **kwargs)

        self._tx = tx

    def emit(self, record):
        self._tx.write(json.dumps(record.to_dict(json_safe=True)).encode())
        self._tx.write(b"\n")

    def close(self):
        self._tx.close()

class AioPipeSubscriber:
    """
    Receives log messages in the parent process and emits them to a
    [`Logger`](https://logbook.readthedocs.io/en/stable/api/base.html#logbook.Logger)
    instance.
    """

    def __init__(self, rx, logger):
        """
        Create a new `AioPipeSubscriber` to listen for messages on the given pipe receive
        end and emit them to the given
        [`Logger`](https://logbook.readthedocs.io/en/stable/api/base.html#logbook.Logger)
        instance. This object takes ownership of `rx`.
        """

        self._rx = rx
        self._logger = logger

    async def run(self):
        """
        Run the subcribing task to continuously receive and emit log messages.

        This can be ran in the background of the event loop using
        [`create_task`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.AbstractEventLoop.create_task).
        """

        while True:
            try:
                msg = await self._rx.readuntil(b"\n")
            except IncompleteReadError as e:
                if e.expected is None:
                    break

                raise

            self._logger.handle(LogRecord.from_dict(json.loads(msg.decode())))

    def close(self):
        """
        Close the subscriber and receiving pipe.
        """

        self._rx._transport.close()

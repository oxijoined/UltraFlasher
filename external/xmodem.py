"""
===============================
 XMODEM file transfer protocol
===============================

.. $Id$

This is a literal implementation of XMODEM.TXT_, XMODEM1K.TXT_ and
XMODMCRC.TXT_, support for YMODEM and ZMODEM is pending. YMODEM should
be fairly easy to implement as it is a hack on top of the XMODEM
protocol using sequence bytes ``0x00`` for sending file names (and some
meta data).

.. _XMODEM.TXT: doc/XMODEM.TXT
.. _XMODEM1K.TXT: doc/XMODEM1K.TXT
.. _XMODMCRC.TXT: doc/XMODMCRC.TXT

Data flow example including error recovery
==========================================

Here is a sample of the data flow, sending a 3-block message.
It includes the two most common line hits - a garbaged block,
and an ``ACK`` reply getting garbaged. ``CRC`` or ``CSUM`` represents
the checksum bytes.

XMODEM 128 byte blocks
----------------------

::

    SENDER                                      RECEIVER

                                            <-- NAK
    SOH 01 FE Data[128] CSUM                -->
                                            <-- ACK
    SOH 02 FD Data[128] CSUM                -->
                                            <-- ACK
    SOH 03 FC Data[128] CSUM                -->
                                            <-- ACK
    SOH 04 FB Data[128] CSUM                -->
                                            <-- ACK
    SOH 05 FA Data[100] CPMEOF[28] CSUM     -->
                                            <-- ACK
    EOT                                     -->
                                            <-- ACK

XMODEM-1k blocks, CRC mode
--------------------------

::

    SENDER                                      RECEIVER

                                            <-- C
    STX 01 FE Data[1024] CRC CRC            -->
                                            <-- ACK
    STX 02 FD Data[1024] CRC CRC            -->
                                            <-- ACK
    STX 03 FC Data[1000] CPMEOF[24] CRC CRC -->
                                            <-- ACK
    EOT                                     -->
                                            <-- ACK

Mixed 1024 and 128 byte Blocks
------------------------------

::

    SENDER                                      RECEIVER

                                            <-- C
    STX 01 FE Data[1024] CRC CRC            -->
                                            <-- ACK
    STX 02 FD Data[1024] CRC CRC            -->
                                            <-- ACK
    SOH 03 FC Data[128] CRC CRC             -->
                                            <-- ACK
    SOH 04 FB Data[100] CPMEOF[28] CRC CRC  -->
                                            <-- ACK
    EOT                                     -->
                                            <-- ACK

YMODEM Batch Transmission Session (1 file)
------------------------------------------

::

    SENDER                                      RECEIVER
                                            <-- C (command:rb)
    SOH 00 FF foo.c NUL[123] CRC CRC        -->
                                            <-- ACK
                                            <-- C
    SOH 01 FE Data[128] CRC CRC             -->
                                            <-- ACK
    SOH 02 FC Data[128] CRC CRC             -->
                                            <-- ACK
    SOH 03 FB Data[100] CPMEOF[28] CRC CRC  -->
                                            <-- ACK
    EOT                                     -->
                                            <-- NAK
    EOT                                     -->
                                            <-- ACK
                                            <-- C
    SOH 00 FF NUL[128] CRC CRC              -->
                                            <-- ACK


"""

from __future__ import division, print_function

__author__ = "Wijnand Modderman <maze@pyth0n.org>"
__copyright__ = [
    "Copyright (c) 2010 Wijnand Modderman",
    "Copyright (c) 1981 Chuck Forsberg",
]
__license__ = "MIT"
__version__ = "0.4.5"

import logging
import platform
import sys
import time
from functools import partial

# Protocol bytes
SOH = b"\x01"
STX = b"\x02"
EOT = b"\x04"
ACK = b"\x06"
DLE = b"\x10"
NAK = b"\x15"
CAN = b"\x18"
CRC = b"C"


class XMODEM(object):
    """
    XMODEM Protocol handler, expects two callables which encapsulate the read
        and write operations on the underlying stream.

    Example functions for reading and writing to a serial line:

    >>> import serial
    >>> from xmodem import XMODEM
    >>> ser = serial.Serial('/dev/ttyUSB0', timeout=0) # or whatever you need
    >>> def getc(size, timeout=1):
    ...     return ser.read(size) or None
    ...
    >>> def putc(data, timeout=1):
    ...     return ser.write(data) or None
    ...
    >>> modem = XMODEM(getc, putc)


    :param getc: Function to retrieve bytes from a stream. The function takes
        the number of bytes to read from the stream and a timeout in seconds as
        parameters. It must return the bytes which were read, or ``None`` if a
        timeout occured.
    :type getc: callable
    :param putc: Function to transmit bytes to a stream. The function takes the
        bytes to be written and a timeout in seconds as parameters. It must
        return the number of bytes written to the stream, or ``None`` in case of
        a timeout.
    :type putc: callable
    :param mode: XMODEM protocol mode
    :type mode: string
    :param pad: Padding character to make the packets match the packet size
    :type pad: char

    """

    # crctab calculated by Mark G. Mendel, Network Systems Corporation
    crctable = [
        0x0000,
        0x1021,
        0x2042,
        0x3063,
        0x4084,
        0x50A5,
        0x60C6,
        0x70E7,
        0x8108,
        0x9129,
        0xA14A,
        0xB16B,
        0xC18C,
        0xD1AD,
        0xE1CE,
        0xF1EF,
        0x1231,
        0x0210,
        0x3273,
        0x2252,
        0x52B5,
        0x4294,
        0x72F7,
        0x62D6,
        0x9339,
        0x8318,
        0xB37B,
        0xA35A,
        0xD3BD,
        0xC39C,
        0xF3FF,
        0xE3DE,
        0x2462,
        0x3443,
        0x0420,
        0x1401,
        0x64E6,
        0x74C7,
        0x44A4,
        0x5485,
        0xA56A,
        0xB54B,
        0x8528,
        0x9509,
        0xE5EE,
        0xF5CF,
        0xC5AC,
        0xD58D,
        0x3653,
        0x2672,
        0x1611,
        0x0630,
        0x76D7,
        0x66F6,
        0x5695,
        0x46B4,
        0xB75B,
        0xA77A,
        0x9719,
        0x8738,
        0xF7DF,
        0xE7FE,
        0xD79D,
        0xC7BC,
        0x48C4,
        0x58E5,
        0x6886,
        0x78A7,
        0x0840,
        0x1861,
        0x2802,
        0x3823,
        0xC9CC,
        0xD9ED,
        0xE98E,
        0xF9AF,
        0x8948,
        0x9969,
        0xA90A,
        0xB92B,
        0x5AF5,
        0x4AD4,
        0x7AB7,
        0x6A96,
        0x1A71,
        0x0A50,
        0x3A33,
        0x2A12,
        0xDBFD,
        0xCBDC,
        0xFBBF,
        0xEB9E,
        0x9B79,
        0x8B58,
        0xBB3B,
        0xAB1A,
        0x6CA6,
        0x7C87,
        0x4CE4,
        0x5CC5,
        0x2C22,
        0x3C03,
        0x0C60,
        0x1C41,
        0xEDAE,
        0xFD8F,
        0xCDEC,
        0xDDCD,
        0xAD2A,
        0xBD0B,
        0x8D68,
        0x9D49,
        0x7E97,
        0x6EB6,
        0x5ED5,
        0x4EF4,
        0x3E13,
        0x2E32,
        0x1E51,
        0x0E70,
        0xFF9F,
        0xEFBE,
        0xDFDD,
        0xCFFC,
        0xBF1B,
        0xAF3A,
        0x9F59,
        0x8F78,
        0x9188,
        0x81A9,
        0xB1CA,
        0xA1EB,
        0xD10C,
        0xC12D,
        0xF14E,
        0xE16F,
        0x1080,
        0x00A1,
        0x30C2,
        0x20E3,
        0x5004,
        0x4025,
        0x7046,
        0x6067,
        0x83B9,
        0x9398,
        0xA3FB,
        0xB3DA,
        0xC33D,
        0xD31C,
        0xE37F,
        0xF35E,
        0x02B1,
        0x1290,
        0x22F3,
        0x32D2,
        0x4235,
        0x5214,
        0x6277,
        0x7256,
        0xB5EA,
        0xA5CB,
        0x95A8,
        0x8589,
        0xF56E,
        0xE54F,
        0xD52C,
        0xC50D,
        0x34E2,
        0x24C3,
        0x14A0,
        0x0481,
        0x7466,
        0x6447,
        0x5424,
        0x4405,
        0xA7DB,
        0xB7FA,
        0x8799,
        0x97B8,
        0xE75F,
        0xF77E,
        0xC71D,
        0xD73C,
        0x26D3,
        0x36F2,
        0x0691,
        0x16B0,
        0x6657,
        0x7676,
        0x4615,
        0x5634,
        0xD94C,
        0xC96D,
        0xF90E,
        0xE92F,
        0x99C8,
        0x89E9,
        0xB98A,
        0xA9AB,
        0x5844,
        0x4865,
        0x7806,
        0x6827,
        0x18C0,
        0x08E1,
        0x3882,
        0x28A3,
        0xCB7D,
        0xDB5C,
        0xEB3F,
        0xFB1E,
        0x8BF9,
        0x9BD8,
        0xABBB,
        0xBB9A,
        0x4A75,
        0x5A54,
        0x6A37,
        0x7A16,
        0x0AF1,
        0x1AD0,
        0x2AB3,
        0x3A92,
        0xFD2E,
        0xED0F,
        0xDD6C,
        0xCD4D,
        0xBDAA,
        0xAD8B,
        0x9DE8,
        0x8DC9,
        0x7C26,
        0x6C07,
        0x5C64,
        0x4C45,
        0x3CA2,
        0x2C83,
        0x1CE0,
        0x0CC1,
        0xEF1F,
        0xFF3E,
        0xCF5D,
        0xDF7C,
        0xAF9B,
        0xBFBA,
        0x8FD9,
        0x9FF8,
        0x6E17,
        0x7E36,
        0x4E55,
        0x5E74,
        0x2E93,
        0x3EB2,
        0x0ED1,
        0x1EF0,
    ]

    def __init__(
        self,
        getc,
        putc,
        mode="xmodem",
        pad=b"\x1a",
    ):
        self.getc = getc
        self.putc = putc
        self.mode = mode
        self.pad = pad
        self.log = logging.getLogger("xmodem.XMODEM")

    def abort(
        self,
        count=2,
        timeout=60,
    ):
        """
        Send an abort sequence using CAN bytes.

        :param count: how many abort characters to send
        :type count: int
        :param timeout: timeout in seconds
        :type timeout: int
        """
        for _ in range(count):
            self.putc(
                CAN,
                timeout,
            )

    def send(
        self,
        stream,
        retry=16,
        timeout=60,
        quiet=False,
        callback=None,
    ):
        """
        Send a stream via the XMODEM protocol.

            >>> stream = open('/etc/issue', 'rb')
            >>> print(modem.send(stream))
            True

        Returns ``True`` upon successful transmission or ``False`` in case of
        failure.

        :param stream: The stream object to send data from.
        :type stream: stream (file, etc.)
        :param retry: The maximum number of times to try to resend a failed
                      packet before failing.
        :type retry: int
        :param timeout: The number of seconds to wait for a response before
                        timing out.
        :type timeout: int
        :param quiet: If True, write transfer information to stderr.
        :type quiet: bool
        :param callback: Reference to a callback function that has the
                         following signature.  This is useful for
                         getting status updates while a xmodem
                         transfer is underway.
                         Expected callback signature:
                         def callback(total_packets, success_count, error_count)
        :type callback: callable
        """

        # initialize protocol
        try:
            packet_size = dict(
                xmodem=128,
                xmodem1k=1024,
            )[self.mode]
        except KeyError:
            raise ValueError("Invalid mode specified: {self.mode!r}".format(self=self))

        self.log.debug(
            "Begin start sequence, packet_size=%d",
            packet_size,
        )
        error_count = 0
        crc_mode = 0
        cancel = 0
        while True:
            char = self.getc(1)
            if char:
                if char == NAK:
                    self.log.debug("standard checksum requested (NAK).")
                    crc_mode = 0
                    break
                elif char == CRC:
                    self.log.debug("16-bit CRC requested (CRC).")
                    crc_mode = 1
                    break
                elif char == CAN:
                    if not quiet:
                        print(
                            "received CAN",
                            file=sys.stderr,
                        )
                    if cancel:
                        self.log.info(
                            "Transmission canceled: received 2xCAN " "at start-sequence"
                        )
                        return False
                    else:
                        self.log.debug("cancellation at start sequence.")
                        cancel = 1
                elif char == EOT:
                    self.log.info(
                        "Transmission canceled: received EOT " "at start-sequence"
                    )
                    return False
                else:
                    self.log.error(
                        "send error: expected NAK, CRC, EOT or CAN; " "got %r",
                        char,
                    )

            error_count += 1
            if error_count > retry:
                self.log.info(
                    "send error: error_count reached %d, " "aborting.",
                    retry,
                )
                self.abort(timeout=timeout)
                return False

        # send data
        error_count = 0
        success_count = 0
        total_packets = 0
        sequence = 1
        while True:
            data = stream.read(packet_size)
            if not data:
                # end of stream
                self.log.debug("send: at EOF")
                break
            total_packets += 1

            header = self._make_send_header(
                packet_size,
                sequence,
            )
            data = data.ljust(
                packet_size,
                self.pad,
            )
            checksum = self._make_send_checksum(
                crc_mode,
                data,
            )

            # emit packet
            while True:
                self.log.debug(
                    "send: block %d",
                    sequence,
                )
                self.putc(header + data + checksum)
                char = self.getc(
                    1,
                    timeout,
                )
                if char == ACK:
                    success_count += 1
                    if callable(callback):
                        callback(
                            total_packets,
                            success_count,
                            error_count,
                        )
                    error_count = 0
                    break

                self.log.error(
                    "send error: expected ACK; got %r for block %d",
                    char,
                    sequence,
                )
                error_count += 1
                if callable(callback):
                    callback(
                        total_packets,
                        success_count,
                        error_count,
                    )
                if error_count > retry:
                    # excessive amounts of retransmissions requested,
                    # abort transfer
                    self.log.error(
                        "send error: NAK received %d times, " "aborting.",
                        error_count,
                    )
                    self.abort(timeout=timeout)
                    return False

            # keep track of sequence
            sequence = (sequence + 1) % 0x100

        while True:
            self.log.debug("sending EOT, awaiting ACK")
            # end of transmission
            self.putc(EOT)

            # An ACK should be returned
            char = self.getc(
                1,
                timeout,
            )
            if char == ACK:
                break
            else:
                self.log.error(
                    "send error: expected ACK; got %r",
                    char,
                )
                error_count += 1
                if error_count > retry:
                    self.log.warn("EOT was not ACKd, aborting transfer")
                    self.abort(timeout=timeout)
                    return False

        self.log.info("Transmission successful (ACK received).")
        return True

    def _make_send_header(
        self,
        packet_size,
        sequence,
    ):
        assert packet_size in (
            128,
            1024,
        ), packet_size
        _bytes = []
        if packet_size == 128:
            _bytes.append(ord(SOH))
        elif packet_size == 1024:
            _bytes.append(ord(STX))
        _bytes.extend(
            [
                sequence,
                0xFF - sequence,
            ]
        )
        return bytearray(_bytes)

    def _make_send_checksum(
        self,
        crc_mode,
        data,
    ):
        _bytes = []
        if crc_mode:
            crc = self.calc_crc(data)
            _bytes.extend(
                [
                    crc >> 8,
                    crc & 0xFF,
                ]
            )
        else:
            crc = self.calc_checksum(data)
            _bytes.append(crc)
        return bytearray(_bytes)

    def recv(
        self,
        stream,
        crc_mode=1,
        retry=16,
        timeout=60,
        delay=1,
        quiet=0,
    ):
        """
        Receive a stream via the XMODEM protocol.

            >>> stream = open('/etc/issue', 'wb')
            >>> print(modem.recv(stream))
            2342

        Returns the number of bytes received on success or ``None`` in case of
        failure.

        :param stream: The stream object to write data to.
        :type stream: stream (file, etc.)
        :param crc_mode: XMODEM CRC mode
        :type crc_mode: int
        :param retry: The maximum number of times to try to resend a failed
                      packet before failing.
        :type retry: int
        :param timeout: The number of seconds to wait for a response before
                        timing out.
        :type timeout: int
        :param delay: The number of seconds to wait between resend attempts
        :type delay: int
        :param quiet: If ``True``, write transfer information to stderr.
        :type quiet: bool

        """

        # initiate protocol
        error_count = 0
        char = 0
        cancel = 0
        while True:
            # first try CRC mode, if this fails,
            # fall back to checksum mode
            if error_count >= retry:
                self.log.info(
                    "error_count reached %d, aborting.",
                    retry,
                )
                self.abort(timeout=timeout)
                return None
            elif crc_mode and error_count < (retry // 2):
                if not self.putc(CRC):
                    self.log.debug(
                        "recv error: putc failed, " "sleeping for %d",
                        delay,
                    )
                    time.sleep(delay)
                    error_count += 1
            else:
                crc_mode = 0
                if not self.putc(NAK):
                    self.log.debug(
                        "recv error: putc failed, " "sleeping for %d",
                        delay,
                    )
                    time.sleep(delay)
                    error_count += 1

            char = self.getc(
                1,
                timeout,
            )
            if char is None:
                self.log.warn("recv error: getc timeout in start sequence")
                error_count += 1
                continue
            elif char == SOH:
                self.log.debug("recv: SOH")
                break
            elif char == STX:
                self.log.debug("recv: STX")
                break
            elif char == CAN:
                if cancel:
                    self.log.info(
                        "Transmission canceled: received 2xCAN " "at start-sequence"
                    )
                    return None
                else:
                    self.log.debug("cancellation at start sequence.")
                    cancel = 1
            else:
                error_count += 1

        # read data
        error_count = 0
        income_size = 0
        packet_size = 128
        sequence = 1
        cancel = 0
        while True:
            while True:
                if char == SOH:
                    if packet_size != 128:
                        self.log.debug("recv: SOH, using 128b packet_size")
                        packet_size = 128
                    break
                elif char == STX:
                    if packet_size != 1024:
                        self.log.debug("recv: SOH, using 1k packet_size")
                        packet_size = 1024
                    break
                elif char == EOT:
                    # We received an EOT, so send an ACK and return the
                    # received data length.
                    self.putc(ACK)
                    self.log.info(
                        "Transmission complete, %d bytes",
                        income_size,
                    )
                    return income_size
                elif char == CAN:
                    # cancel at two consecutive cancels
                    if cancel:
                        self.log.info(
                            "Transmission canceled: received 2xCAN " "at block %d",
                            sequence,
                        )
                        return None
                    else:
                        self.log.debug(
                            "cancellation at block %d",
                            sequence,
                        )
                        cancel = 1
                else:
                    err_msg = "recv error: expected SOH, EOT; " "got {0!r}".format(char)
                    if not quiet:
                        print(
                            err_msg,
                            file=sys.stderr,
                        )
                    self.log.warn(err_msg)
                    error_count += 1
                    if error_count > retry:
                        self.log.info(
                            "error_count reached %d, aborting.",
                            retry,
                        )
                        self.abort()
                        return None

            # read sequence
            error_count = 0
            cancel = 0
            self.log.debug(
                "recv: data block %d",
                sequence,
            )
            seq1 = self.getc(
                1,
                timeout,
            )
            if seq1 is None:
                self.log.warn("getc failed to get first sequence byte")
                seq2 = None
            else:
                seq1 = ord(seq1)
                seq2 = self.getc(
                    1,
                    timeout,
                )
                if seq2 is None:
                    self.log.warn("getc failed to get second sequence byte")
                else:
                    # second byte is the same as first as 1's complement
                    seq2 = 0xFF - ord(seq2)

            if not (seq1 == seq2 == sequence):
                # consume data anyway ... even though we will discard it,
                # it is not the sequence we expected!
                self.log.error(
                    "expected sequence %d, "
                    "got (seq1=%r, seq2=%r), "
                    "receiving next block, will NAK.",
                    sequence,
                    seq1,
                    seq2,
                )
                self.getc(packet_size + 1 + crc_mode)
            else:
                # sequence is ok, read packet
                # packet_size + checksum
                data = self.getc(
                    packet_size + 1 + crc_mode,
                    timeout,
                )
                (
                    valid,
                    data,
                ) = self._verify_recv_checksum(
                    crc_mode,
                    data,
                )

                # valid data, append chunk
                if valid:
                    income_size += len(data)
                    stream.write(data)
                    self.putc(ACK)
                    sequence = (sequence + 1) % 0x100
                    # get next start-of-header byte
                    char = self.getc(
                        1,
                        timeout,
                    )
                    continue

            # something went wrong, request retransmission
            self.log.warn("recv error: purge, requesting retransmission (NAK)")
            while True:
                # When the receiver wishes to <nak>, it should call a "PURGE"
                # subroutine, to wait for the line to clear. Recall the sender
                # tosses any characters in its UART buffer immediately upon
                # completing sending a block, to ensure no glitches were mis-
                # interpreted.  The most common technique is for "PURGE" to
                # call the character receive subroutine, specifying a 1-second
                # timeout, and looping back to PURGE until a timeout occurs.
                # The <nak> is then sent, ensuring the other end will see it.
                data = self.getc(
                    1,
                    timeout=1,
                )
                if data is None:
                    break
            self.putc(NAK)
            # get next start-of-header byte
            char = self.getc(
                1,
                timeout,
            )
            continue

    def _verify_recv_checksum(
        self,
        crc_mode,
        data,
    ):
        if crc_mode:
            _checksum = bytearray(data[-2:])
            their_sum = (_checksum[0] << 8) + _checksum[1]
            data = data[:-2]

            our_sum = self.calc_crc(data)
            valid = bool(their_sum == our_sum)
            if not valid:
                self.log.warn(
                    "recv error: checksum fail " "(theirs=%04x, ours=%04x), ",
                    their_sum,
                    our_sum,
                )
        else:
            _checksum = bytearray([data[-1]])
            their_sum = _checksum[0]
            data = data[:-1]

            our_sum = self.calc_checksum(data)
            valid = their_sum == our_sum
            if not valid:
                self.log.warn(
                    "recv error: checksum fail " "(theirs=%02x, ours=%02x)",
                    their_sum,
                    our_sum,
                )
        return (
            valid,
            data,
        )

    def calc_checksum(
        self,
        data,
        checksum=0,
    ):
        """
        Calculate the checksum for a given block of data, can also be used to
        update a checksum.

            >>> csum = modem.calc_checksum('hello')
            >>> csum = modem.calc_checksum('world', csum)
            >>> hex(csum)
            '0x3c'

        """
        if platform.python_version_tuple() >= (
            "3",
            "0",
            "0",
        ):
            return (sum(data) + checksum) % 256
        else:
            return (
                sum(
                    map(
                        ord,
                        data,
                    )
                )
                + checksum
            ) % 256

    def calc_crc(
        self,
        data,
        crc=0,
    ):
        """
        Calculate the Cyclic Redundancy Check for a given block of data, can
        also be used to update a CRC.

            >>> crc = modem.calc_crc('hello')
            >>> crc = modem.calc_crc('world', crc)
            >>> hex(crc)
            '0x4ab3'

        """
        for char in bytearray(data):
            crctbl_idx = ((crc >> 8) ^ char) & 0xFF
            crc = ((crc << 8) ^ self.crctable[crctbl_idx]) & 0xFFFF
        return crc & 0xFFFF


XMODEM1k = partial(
    XMODEM,
    mode="xmodem1k",
)


def _send(
    mode="xmodem",
    filename=None,
    timeout=30,
):
    """Send a file (or stdin) using the selected mode."""

    if filename is None:
        si = sys.stdin
    else:
        si = open(
            filename,
            "rb",
        )

    # TODO(maze): make this configurable, serial out, etc.
    so = sys.stdout

    def _getc(
        size,
        timeout=timeout,
    ):
        (
            read_ready,
            _,
            _,
        ) = select.select(
            [so],
            [],
            [],
            timeout,
        )
        if read_ready:
            data = stream.read(size)
        else:
            data = None
        return data

    def _putc(
        data,
        timeout=timeout,
    ):
        (
            _,
            write_ready,
            _,
        ) = select.select(
            [],
            [si],
            [],
            timeout,
        )
        if write_ready:
            si.write(data)
            si.flush()
            size = len(data)
        else:
            size = None
        return size

    xmodem = XMODEM(
        _getc,
        _putc,
        mode,
    )
    return xmodem.send(si)


def run():
    """Run the main entry point for sending and receiving files."""
    import argparse
    import sys

    import serial

    platform = sys.platform.lower()

    if platform.startswith("win"):
        default_port = "COM1"
    else:
        default_port = "/dev/ttyS0"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        default=default_port,
        help="serial port",
    )
    parser.add_argument(
        "-r",
        "--rate",
        default=9600,
        type=int,
        help="baud rate",
    )
    parser.add_argument(
        "-b",
        "--bytesize",
        default=serial.EIGHTBITS,
        help="serial port transfer byte size",
    )
    parser.add_argument(
        "-P",
        "--parity",
        default=serial.PARITY_NONE,
        help="serial port parity",
    )
    parser.add_argument(
        "-S",
        "--stopbits",
        default=serial.STOPBITS_ONE,
        help="serial port stop bits",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="xmodem",
        help="XMODEM mode (xmodem, xmodem1k)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        default=30,
        type=int,
        help="I/O timeout in seconds",
    )

    subparsers = parser.add_subparsers(dest="subcommand")
    send_parser = subparsers.add_parser("send")
    send_parser.add_argument(
        "filename",
        nargs="?",
        help="filename to send, empty reads from stdin",
    )
    recv_parser = subparsers.add_parser("recv")
    recv_parser.add_argument(
        "filename",
        nargs="?",
        help="filename to receive, empty sends to stdout",
    )

    options = parser.parse_args()

    if options.subcommand == "send":
        return _send(
            options.mode,
            options.filename,
            options.timeout,
        )
    elif options.subcommand == "recv":
        return _recv(
            options.mode,
            options.filename,
            options.timeout,
        )


def runx():
    import optparse
    import subprocess

    parser = optparse.OptionParser(
        usage="%prog [<options>] <send|recv> filename filename"
    )
    parser.add_option(
        "-m",
        "--mode",
        default="xmodem",
        help="XMODEM mode (xmodem, xmodem1k)",
    )

    (
        options,
        args,
    ) = parser.parse_args()
    if len(args) != 3:
        parser.error("invalid arguments")
        return 1

    elif args[0] not in (
        "send",
        "recv",
    ):
        parser.error("invalid mode")
        return 1

    def _func(
        so,
        si,
    ):
        import select

        print(
            (
                "si",
                si,
            )
        )
        print(
            (
                "so",
                so,
            )
        )

        def getc(
            size,
            timeout=3,
        ):
            (
                read_ready,
                _,
                _,
            ) = select.select(
                [so],
                [],
                [],
                timeout,
            )
            if read_ready:
                data = so.read(size)
            else:
                data = None

            print(
                (
                    "getc(",
                    repr(data),
                    ")",
                )
            )
            return data

        def putc(
            data,
            timeout=3,
        ):
            (
                _,
                write_ready,
                _,
            ) = select.select(
                [],
                [si],
                [],
                timeout,
            )
            if write_ready:
                si.write(data)
                si.flush()
                size = len(data)
            else:
                size = None

            print(
                (
                    "putc(",
                    repr(data),
                    repr(size),
                    ")",
                )
            )
            return size

        return (
            getc,
            putc,
        )

    def _pipe(
        *command,
    ):
        pipe = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        return (
            pipe.stdout,
            pipe.stdin,
        )

    if args[0] == "recv":
        (
            getc,
            putc,
        ) = _func(
            *_pipe(
                "sz",
                "--xmodem",
                args[2],
            )
        )
        stream = open(
            args[1],
            "wb",
        )
        xmodem = XMODEM(
            getc,
            putc,
            mode=options.mode,
        )
        status = xmodem.recv(
            stream,
            retry=8,
        )
        assert status, (
            "Transfer failed, status is",
            False,
        )
        stream.close()

    elif args[0] == "send":
        (
            getc,
            putc,
        ) = _func(
            *_pipe(
                "rz",
                "--xmodem",
                args[2],
            )
        )
        stream = open(
            args[1],
            "rb",
        )
        xmodem = XMODEM(
            getc,
            putc,
            mode=options.mode,
        )
        sent = xmodem.send(
            stream,
            retry=8,
        )
        assert sent is not None, (
            "Transfer failed, sent is",
            sent,
        )
        stream.close()


if __name__ == "__main__":
    sys.exit(run())

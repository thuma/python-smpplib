# -*- coding: utf8 -*-
import binascii
import random
import six

from . import consts
from . import exceptions


# from http://stackoverflow.com/questions/2452861/python-library-for-converting-plain-text-ascii-into-gsm-7-bit-character-set
gsm = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>"
       "?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà")
ext = ("````````````````````^```````````````````{}`````\\````````````[~]`"
       "|````````````````````````````````````€``````````````````````````")
if six.PY2:
    gsm = gsm.decode('utf-8')
    ext = ext.decode('utf-8')


class EncodeError(ValueError):
    """Raised if text cannot be represented in gsm 7-bit encoding"""


def gsm_encode(plaintext, hex=False):
    """Replace non-GSM ASCII symbols"""
    res = ""
    for c in plaintext:
        idx = gsm.find(c)
        if idx != -1:
            res += chr(idx)
            continue
        idx = ext.find(c)
        if idx != -1:
            res += chr(27) + chr(idx)
            continue
        raise EncodeError()
    return binascii.b2a_hex(res) if hex else res

def gsm_decode(instring, hex=False):
    if hex:
        instring = binascii.a2b_hex(instring)
    chars = iter(instring)
    result = []
    for c in chars:
        if c == chr(27):
            c = next(chars)
            result.append(ext[ord(c)])
        else:
            result.append(gsm[ord(c)])
    return ''.join(result)

def make_parts(text):
    """Returns tuple(parts, encoding, esm_class)"""
    try:
        text = gsm_encode(text)
        encoding = consts.SMPP_ENCODING_DEFAULT
        need_split = len(text) > consts.SEVENBIT_SIZE
        partsize = consts.SEVENBIT_MP_SIZE
        encode = six.b
    except EncodeError:
        text = binascii.hexlify(text.encode('utf-16-be'))
        encoding = consts.SMPP_ENCODING_ISO10646
        need_split = len(text) > consts.UCS2_SIZE * 4
        partsize = consts.UCS2_MP_SIZE * 4
        encode = lambda s: binascii.unhexlify(s)

    esm_class = consts.SMPP_MSGTYPE_DEFAULT

    if need_split:
        esm_class = consts.SMPP_GSMFEAT_UDHI

        starts = tuple(range(0, len(text), partsize))
        if len(starts) > 255:
            raise exceptions.MessageTooLong()

        parts = []
        ipart = 1
        uid = random.randint(0, 255)
        for start in starts:
            parts.append( b''.join((b'\x05\x00\x03', six.int2byte(uid),
                                    six.int2byte(len(starts)), six.int2byte(ipart),
                                    encode(text[start:start + partsize]))) )
            ipart += 1
    else:
        parts = (encode(text),)

    return parts, encoding, esm_class

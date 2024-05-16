#!/usr/bin/env python3
""" """
import re


def filter_datum(
    fields, redaction: str,
    message: str, separator: str
) -> str:
    """ filter_datum function """
    for field in fields:
        pattern = r'({0}=)[^{1}]*({1})'.format(field, separator)
        message = re.sub(pattern, r'\1{}\2'.format(redaction), message)
    return message

import hmac
import hashlib
import logging
import os
import zipfile

def update_static(destdir, fileobj):
    logging.info('Extracting new static site...')
    z = zipfile.ZipFile(fileobj, 'r')
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    z.extractall(destdir)

def check_hmac(fileobj, secret, provided_digest):
    # Compute expected digest
    digest = hmac.new(secret, fileobj.read(), hashlib.sha256)

    # Does this digest match?
    if not hmac.compare_digest(provided_digest, digest.hexdigest()):
        return False

    return True

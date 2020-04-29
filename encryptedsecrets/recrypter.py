import re

import encrypteddict


class Recrypter(encrypteddict.crypter):

    PATTERN = re.compile(r'ENC\[.*,.*\]')

    def decrypt_gpg_match_for_edit(self, value):
        return f'DEC::(GPG)[{self.decrypt_match_group(value)}]'

    def decrypt_all_for_edit(self, decrypt_this):
        """
        A decryption mode that leaves in place the markers so that it will re-encrypt the same values.
        """
        if type(decrypt_this) == str:
            return self.PATTERN.sub(self.decrypt_gpg_match_for_edit, decrypt_this)
        return self.decrypt_all(decrypt_this)

    def encrypt_all(self, encrypt_this, recipients=None):
        # Don't encrypt anything before the first document marker. This is to
        # preserve the inital comment without encrypting any values -- i.e.
        # instructional/howto comments
        separator = '---\n'
        if isinstance(encrypt_this, str):
            pos = encrypt_this.find(separator)
            if pos != -1:
                return encrypt_this[0:pos + len(separator)] + super().encrypt_all(encrypt_this[pos + len(separator):], recipients)
        return super().encrypt_all(encrypt_this, recipients)

    def encrypt_gpg(self, value, recipients):
        # BugFix against upstream encrypteddict: it returns bytes, so was formatting wrong
        val = super().encrypt_gpg(value, recipients)
        if isinstance(val, bytes):
            return val.decode('utf-8')
        return val

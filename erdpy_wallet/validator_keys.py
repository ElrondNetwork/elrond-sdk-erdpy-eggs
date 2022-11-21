
import os
import subprocess
from pathlib import Path

from erdpy_wallet.constants import (VALIDATOR_PUBKEY_LENGTH,
                                    VALIDATOR_SECRETKEY_LENGTH)
from erdpy_wallet.errors import (ErrBadSecretKeyLength,
                                 ErrMclSignerPathNotDefined)
from erdpy_wallet.interfaces import ISignature
from erdpy_wallet.pem import parse_validator_pem


class ValidatorSecretKey:
    def __init__(self, buffer: bytes) -> None:
        if len(buffer) != VALIDATOR_SECRETKEY_LENGTH:
            raise ErrBadSecretKeyLength()

        self.buffer = buffer

    def sign(self, data: bytes) -> ISignature:
        mcl_signer_path = self._get_mcl_signer_path()
        signed_hex: str = subprocess.check_output([mcl_signer_path, data.hex(), self.buffer.hex()], universal_newlines=True, shell=False)
        return bytes.fromhex(signed_hex)

    def _get_mcl_signer_path(self):
        mcl_signer_path = os.environ.get("MCL_SIGNER_PATH", None)
        if not mcl_signer_path:
            raise ErrMclSignerPathNotDefined()

        return mcl_signer_path

    def generate_public_key(self) -> 'ValidatorPublicKey':
        raise NotImplementedError()

    def hex(self) -> str:
        return self.buffer.hex()

    def __str__(self) -> str:
        return ValidatorSecretKey.__name__

    def __repr__(self) -> str:
        return ValidatorSecretKey.__name__


class ValidatorPublicKey:
    def __init__(self, buffer: bytes) -> None:
        if len(buffer) != VALIDATOR_PUBKEY_LENGTH:
            raise ErrBadSecretKeyLength()

        self.buffer = buffer

    @classmethod
    def from_pem_file(cls, path: Path, index: int) -> 'ValidatorPublicKey':
        _, bls = parse_validator_pem(path, index)
        buffer = bytes.fromhex(bls)
        return ValidatorPublicKey(buffer)

    def hex(self) -> str:
        return self.buffer.hex()

    def __str__(self) -> str:
        return self.hex()

    def __repr__(self) -> str:
        return self.hex()
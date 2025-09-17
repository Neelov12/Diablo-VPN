import os
import datetime
from textwrap import dedent
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .terminal import Terminal

def generate_self_signed_cert(cert_path="certs/cert.pem", key_path="certs/key.pem"):
    """
    Generates a self-signed TLS certificate and key pair.
    Saves them to the certs/ directory.
    """
    if os.path.exists(cert_path) and os.path.exists(key_path):
        Terminal.proceed("Certificate exists")
        return

    Terminal.warn(dedent("""No certificate found. If this was removed by accident, please update certs/cert.pem. 
                            Otherwise, if this is your first time hosting, this warning can be safely ignored. 
                            
                            Proceeding to create new self-signed certificate key pair..."""))

    # Generate private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Certificate subject and issuer
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"LAN"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Diablo Proxy Server"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"diablo.local"),
    ])

    # Build certificate
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)  # self-signed
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # Ensure certs/ folder exists
    Path("certs").mkdir(exist_ok=True)

    # Write key to file
    with open(key_path, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Write cert to file
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    Terminal.success("TLS certificate and key generated.")
    Terminal.print(f"\tCertificate in ({cert_path})", bold=True)
    Terminal.print(f"\tKey in ({key_path})", bold=True)

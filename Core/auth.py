import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Tuple, Optional

def validate_creds(access_key=None, secret_key=None, session_token=None, region=None,
                   profile=None) -> Tuple[bool, str, Optional[boto3.Session]]:
    """
    Valide les identifiants AWS et retourne une session Boto3 utilisable.

    Args:
        access_key (str): Clé d'accès AWS
        secret_key (str): Clé secrète AWS
        session_token (str): Token de session (si fourni)
        profile (str): Profil AWS CLI, utilisé si aucune clé n'est fournie
        region (str): Région AWS (ex: 'us-east-1')

    Returns:
        Tuple[bool, str, Optional[boto3.Session]]: (succès, message, session)
    """
    try:
        if access_key:
            session = boto3.session.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token or None,
                region_name=region,
            )
        else:
            # Standard AWS credential chain: --profile, environment variables,
            # ~/.aws/credentials, SSO or an instance role.
            session = boto3.session.Session(profile_name=profile, region_name=region)

        sts = session.client('sts')
        identity = sts.get_caller_identity()

        return (
            True,
            f"✅ Valid credentials for account: {identity['Account']}",
            session
        )

    except NoCredentialsError:
        return (False, "❌ No AWS credentials provided", None)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidClientTokenId':
            return (False, "❌ Invalid AWS Access Key ID", None)
        elif error_code == 'SignatureDoesNotMatch':
            return (False, "❌ Invalid AWS Secret Access Key", None)
        elif error_code == 'ExpiredToken':
            return (False, "❌ Expired Session Token", None)
        return (False, f"❌ AWS API Error: {e}", None)
    except Exception as e:
        return (False, f"❌ Unexpected Error: {e}", None)

# If you want to use later call this module and pass credentials to get a session to test on
# session=validate_creds(**creds)[2]
# then u can use session.client(...)


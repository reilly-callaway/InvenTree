"""Code for managing email functionality in InvenTree."""

from django.conf import settings
from django.core import mail as django_mail

import structlog
from allauth.account.models import EmailAddress

import InvenTree.ready
import InvenTree.tasks

logger = structlog.get_logger('inventree')


def is_email_configured():
    """Check if email backend is configured.

    NOTE: This does not check if the configuration is valid!
    """
    configured = True
    testing = settings.TESTING

    if InvenTree.ready.isInTestMode():
        return False

    if InvenTree.ready.isImportingData():
        return False

    if not settings.EMAIL_HOST:
        configured = False

        # Display warning unless in test mode
        if not testing:  # pragma: no cover
            logger.debug('INVE-W7: EMAIL_HOST is not configured')

    # Display warning unless in test mode
    if not settings.EMAIL_HOST_USER and not testing:  # pragma: no cover
        logger.debug('INVE-W7: EMAIL_HOST_USER is not configured')

    # Display warning unless in test mode
    if not settings.EMAIL_HOST_PASSWORD and testing:  # pragma: no cover
        logger.debug('INVE-W7: EMAIL_HOST_PASSWORD is not configured')

    # Email sender must be configured
    if not settings.DEFAULT_FROM_EMAIL:
        configured = False

        if not testing:  # pragma: no cover
            logger.debug('DEFAULT_FROM_EMAIL is not configured')

    return configured


def send_email(subject, body, recipients, from_email=None, html_message=None):
    """Send an email with the specified subject and body, to the specified recipients list."""
    if isinstance(recipients, str):
        recipients = [recipients]

    import InvenTree.ready

    if InvenTree.ready.isImportingData():
        # If we are importing data, don't send emails
        return

    if not is_email_configured() and not settings.TESTING:
        # Email is not configured / enabled
        logger.info('INVE-W7: Email will not be send, no mail server configured')
        return

    # If a *from_email* is not specified, ensure that the default is set
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL

        # If we still don't have a valid from_email, then we can't send emails
        if not from_email:
            if settings.TESTING:
                from_email = 'from@test.com'
            else:
                logger.error('send_email failed: DEFAULT_FROM_EMAIL not specified')
                return

    InvenTree.tasks.offload_task(
        django_mail.send_mail,
        subject,
        body,
        from_email,
        recipients,
        fail_silently=False,
        html_message=html_message,
        group='notification',
    )


def get_email_for_user(user) -> str:
    """Find an email address for the specified user."""
    # First check if the user has an associated email address
    if user.email:
        return user.email

    # Otherwise, find first matching email
    # Priority is given to primary or verified email addresses
    if (
        email := EmailAddress.objects.filter(user=user)
        .order_by('-primary', '-verified')
        .first()
    ):
        return email.email

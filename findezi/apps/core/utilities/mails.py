import logging
from threading import Thread

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def async_operation(function):
    def start_thread(*args, **kwargs):
        thread = Thread(target=function, args=args, kwargs=kwargs)
        thread.start()

    return start_thread


logger = logging.getLogger(__name__)


@async_operation
def send_email(html_template, context):
    from_email = "microgels17@gmail.com"
    subject = context.get("subject")
    to_email = context.get("to_email")
    cc = context.get("cc")
    bcc = context.get("bcc")
    attachments = context.get("attachments")

    if not to_email:
        raise ValueError("The 'to_email' address must be provided and cannot be empty.")
    elif not isinstance(to_email, list):
        to_email = [to_email]

    try:
        html_message = render_to_string(html_template, context)
        message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=to_email,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
        )
        message.content_subtype = "html"
        result = message.send()
        logger.info(
            f"Sending email to {', '.join(to_email)} with subject: {subject} - Status {result}"
        )
    except Exception as e:
        logger.info(
            f"Sending email to {', '.join(to_email)} with subject: {subject} - Status 0"
        )
        logger.exception(e)


def send_claimed_doc_info_mail(email, doc_obj):

    template = "mails/claimed_doc.html"
    context = {
        "to_email": email,
        "subject": "Claimed Document Informations",
        "doc_obj": doc_obj,
    }
    send_email(template, context)


def send_picked_up_doc_mail(email):

    template = "mails/picked_up_doc.html"
    context = {
        "to_email": email,
        "subject": "Document Pick Up Report",
        # "doc_obj": doc_obj,
    }
    send_email(template, context)


def send_found_document_mail(email, doc_obj):

    template = "mails/found_document.html"
    context = {
        "to_email": email,
        "subject": "Your Document has been picked up",
        "doc_obj": doc_obj,
    }
    send_email(template, context)


def send_validated_found_document_mail(email, doc_obj):

    template = "mails/validated_found_doc.html"
    context = {
        "to_email": email,
        "subject": "Your Document was Found",
        "doc_obj": doc_obj,
    }
    send_email(template, context)

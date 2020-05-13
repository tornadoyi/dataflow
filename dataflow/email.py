import smtplib
from email.message import EmailMessage
from email.headerregistry import Address



def send(smtp, sender, receivers, subject='', content=None, html_content=None, payload_args=None, attachments=[]):

    # parse receivers
    recv_address = []
    for r in receivers:
        s = r.split('@')
        recv_address.append(Address('', s[0], s[1]))


    # make message
    msg = EmailMessage()

    # set sender, receivers
    msg['From'] = Address(sender)
    msg['To'] = tuple(recv_address)

    # set subject
    msg['Subject'] = subject

    # set content
    if content is not None: msg.set_content(content)

    # add html content
    if html_content is not None:
        msg.add_alternative(html_content, subtype='html')


    # payloads
    if payload_args is not None:
        args, kwargs = payload_args
        pl = msg.get_payload()
        msg.get_payload()[0].add_related(*args, **kwargs)


    # add attachments
    for a in attachments:
        filename, bcontents = a
        msg.add_attachment(bcontents, filename=filename)

    # send
    with smtplib.SMTP(smtp) as s:
        s.send_message(msg)

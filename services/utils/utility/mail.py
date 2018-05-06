import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
import traceback

mail_account = None

error_mail1 = None
error_mail2 = None


def setup(mail, error_mail_inner=[], error_mail_outer=[]):
    global mail_account, error_mail1, error_mail2
    mail_account = mail
    error_mail1 = error_mail_inner
    error_mail2 = error_mail_outer


def send_email(subject, to_email, cc=[], bcc=[], text_message='', attachment_fns=[]):
    for mail in to_email:
        send_email_single(subject, [mail], text_message=text_message, attachment_fns=attachment_fns)
    for mail in cc:
        send_email_single(subject, [mail], text_message=text_message, attachment_fns=attachment_fns)
    for mail in bcc:
        send_email_single(subject, [mail], text_message=text_message, attachment_fns=attachment_fns)


def send_email_single(subject, to_email, text_message, attachment_fns):
    from_email = mail_account['account']
    msg, mail_list, attachment_fn = get_msg(subject, from_email, to_email, text_message, attachment_fns)

    try:
        s = smtplib.SMTP()
        s.connect(mail_account['IP'], mail_account['port'])
        s.login(from_email, mail_account['password'])
        s.sendmail(from_email, to_email, msg.as_string())
        s.quit()
        logging.info('Send mail to ' + mail_list + ' with attachment: ' + attachment_fn)
    except:
        err_msg = '%s' % traceback.format_exc()
        # print err_msg
        msg, mail_list, attachment_fn = get_msg('Mail Error:' + subject, 'ml@fenqi.im',
                                                error_mail2,
                                                text_message=err_msg
                                                )
        s = smtplib.SMTP()
        s.connect()
        s.sendmail('ml@fenqi.im', error_mail2, msg.as_string())
        logging.info('Send Error mail to ' + mail_list + ' with attachment: ' + attachment_fn)
        logging.info(err_msg)
        s.close()


def send_error_email(subject, err_msg):
    from_email = 'ml@fenqi.im'
    to_email = error_mail2
    msg, mail_list, attachment_fn = get_msg(subject, from_email, to_email, err_msg)
    s = smtplib.SMTP()
    s.connect()
    s.sendmail(from_email, to_email, msg.as_string())
    logging.info('Send Error mail to ' + mail_list + ' with attachment: ' + attachment_fn)
    s.close()
    send_email(subject, error_mail1, text_message=err_msg)


def send_outer_email(subject, outer_mail_list, msg):
    from_email = 'ml@fenqi.im'
    msg, mail_list, attachment_fn = get_msg(subject, from_email, outer_mail_list, msg)
    s = smtplib.SMTP()
    s.connect()
    s.sendmail(from_email, outer_mail_list, msg.as_string())
    logging.info('Send outer mail to ' + mail_list + ' with attachment: ' + attachment_fn)
    s.close()


def get_msg(subject, from_email, to_email, text_message, msg_type='plain', attachment_fns=[]):
    """
    :param msg_type:  can support two type : plain(the normal text mail), html(the html mail)
    """
    assert isinstance(to_email, list)
    assert isinstance(attachment_fns, list)
    comma_space = ', '
    msg = MIMEMultipart()
    if not isinstance(subject, str):
        subject = str(subject)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = comma_space.join(to_email)
    '''
    if len(cc) > 0:
        msg['Cc'] = comma_space.join(cc)
        to_email += cc
    if len(bcc) > 0:
        msg['Bcc'] = comma_space.join(bcc)
        to_email += bcc
    '''
    msg["Accept-Language"] = "zh-CN"
    msg["Accept-Charset"] = "ISO-8859-1,utf-8"
    text = text_message
    body = MIMEMultipart('alternative', _charset='utf-8')
    part = MIMEText(text, msg_type, 'utf8')
    body.attach(part)
    msg.attach(body)
    s_fn = ''

    for fn in attachment_fns:

        if fn.find('pdf') > 0:
            s_fn += fn + ', '
            f = open(fn, 'r')
            attachment = MIMEApplication(f.read(), _subtype='pdf')
            if '/' in fn:
                fn_new = fn.split('/')
                fn = fn_new[-1]
                print(fn)
            else:
                print(fn)
            attachment.add_header('Content-Disposition', 'attachment', filename=fn)
            msg.attach(attachment)

        if fn.find('csv') > 0:
            s_fn += fn + ', '
            f = open(fn, 'r')
            attachment = MIMEApplication(f.read(), _subtype='csv')
            if '/' in fn:
                fn_new = fn.split('/')
                fn = fn_new[-1]
                print(fn)
            else:
                print(fn)
            fn = fn.encode('utf8')
            attachment.add_header('Content-Disposition', 'attachment', filename=fn)
            msg.attach(attachment)

        if fn.find('xlsx') > 0:
            s_fn += fn + ', '
            f = open(fn, 'r')
            attachment = MIMEApplication(f.read(), _subtype='xlsx')
            if '/' in fn:
                fn_new = fn.split('/')
                fn = fn_new[-1]
                print(fn)
            else:
                print(fn)
            fn = fn.encode('utf8')
            attachment.add_header('Content-Disposition', 'attachment', filename=fn)
            msg.attach(attachment)
    return msg, comma_space.join(to_email), s_fn

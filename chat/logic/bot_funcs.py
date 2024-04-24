from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decouple import config
import threading
from .telegram_bot import telegram_message


def send_customer_email(subject_customer, text_content, from_email, customer_email, html_content):
    email_to_customer = EmailMultiAlternatives(subject_customer, text_content, from_email, customer_email)
    email_to_customer.attach_alternative(html_content, "text/html")
    email_to_customer.send()

def send_technical_email(subject_technical, technical_message, from_email, technical_email):
    send_mail(subject_technical, technical_message, from_email, technical_email)

def send_emails(name, message, email_of_customer):
    subject_technical = 'Programming Order Alert'
    subject_customer = 'Your Order Confirmation'
    email = config('email')
    from_email = {email}
    technical_email = [email]
    customer_email = [email_of_customer]
    
    technical_message = f'New programming order received from {name}, email {email_of_customer}. Message: {message}'
    
    context = {'name': name}
    html_content = render_to_string('html/sent.html', context)
    text_content = strip_tags(html_content)

    

    thread_email_to_customer = threading.Thread(
        target=send_customer_email,
        args=(subject_customer, text_content, from_email, customer_email, html_content),
    )

    tread_email_to_me = threading.Thread(
        target=send_technical_email,
        args=(subject_technical, technical_message, from_email, technical_email),
        )


    mails = ['example@gmail.com', {str(config('email'))}, f'{name}example@gmail.com',
    'example@mail.ru'
    ]

    names = [
        'User', 'user', 'Unknown', 'unknown', 'No name', 'no name', 'Noname', 'noname',
        'No'
    ]


    try:
        if name not in names and customer_email not in mails:
            thread_email_to_customer.start()
            tread_email_to_me.start()
            tread_email_to_me.join()
            thread_email_to_customer.join()
            telegram_message(name, message, email_of_customer)
            return 'Email sent successfully'
        else:
            return 'need more is not correct'
    except Exception as e:
        return 'Sorry, something went wrong with sending the HTML email to the customer.'

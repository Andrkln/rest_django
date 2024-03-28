from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os


def send_emails(name, message, email_of_customer):
    subject_technical = 'Programming Order Alert'
    subject_customer = 'Your Order Confirmation'
    from_email = {str(os.getenv('email'))}
    technical_email = [{str(os.getenv('email'))}]
    customer_email = [email_of_customer]
    
    technical_message = f'New programming order received from {name}, email {email_of_customer}. Message: {message}'
    
    context = {'name': name}
    html_content = render_to_string('html/sent.html', context)
    text_content = strip_tags(html_content) 
    
    email_to_customer = EmailMultiAlternatives(subject_customer, text_content, from_email, customer_email)
    email_to_customer.attach_alternative(html_content, "text/html")

    mails = ['example@gmail.com', {str(os.getenv('email'))}, f'{name}example@gmail.com']
    names = [
        'User', 'user', 'Unknown', 'unknown', 'No name', 'no name', 'Noname', 'noname'
        
    ]


    try:
        if name not in names and customer_email not in mails:
            email_to_customer.send()
            send_mail(subject_technical, technical_message, from_email, technical_email)
            return 'Email sent successfully'
        else:
            return 'need more data'
    except Exception as e:
        return 'Sorry, something went wrong with sending the HTML email to the customer.'
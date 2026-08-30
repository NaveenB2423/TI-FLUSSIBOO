import razorpay
from django.conf import settings

def initiate_payment(amount, currency='INR'):
    client = razorpay.Client(auth=(
        getattr(settings, 'RAZORPAY_API_KEY', ''),
        getattr(settings, 'RAZORPAY_API_SECRET', '')
    ))
    data = {
        'amount': int(round(amount * 100)), # Amount in paise
        'currency': currency,
        'payment_capture': '1'
    }
    response = client.order.create(data=data)
    return response['id']




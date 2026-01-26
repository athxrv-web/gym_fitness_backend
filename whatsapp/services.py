"""
WhatsApp Business API Service
"""
import requests
from django.conf import settings


class WhatsAppService:
    """WhatsApp Business API Service"""
    
    def __init__(self):
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.api_version = settings.WHATSAPP_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
    
    def send_message(self, to_phone, message):
        """Send text message via WhatsApp"""
        
        if not self.phone_number_id or not self.access_token:
            return {
                'success': False,
                'error': 'WhatsApp API credentials not configured'
            }
        
        # Format phone number (remove +, spaces, etc.)
        to_phone = ''.join(filter(str.isdigit, to_phone))
        
        # Add country code if not present (assuming India)
        if not to_phone.startswith('91'):
            to_phone = '91' + to_phone
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to_phone,
            'type': 'text',
            'text': {
                'body': message
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json().get('messages', [{}])[0].get('id')
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}"
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_receipt(self, receipt):
        """Send receipt via WhatsApp"""
        
        member = receipt.member
        payment = receipt.payment
        gym = receipt.gym
        
        message = f"""
🏋️ *{gym.name}*
📋 Receipt #{receipt.receipt_number}

Dear {member.name},

Thank you for your payment!

💰 Amount: ₹{payment.amount}
📅 Date: {payment.payment_date.strftime('%d-%b-%Y')}
💳 Method: {payment.get_payment_method_display()}
📆 Month: {payment.month}

Your membership is valid until: {member.membership_end_date.strftime('%d-%b-%Y')}

For any queries, contact us:
📞 {gym.phone}
📧 {gym.email}

Thank you for being with us!
        """.strip()
        
        return self.send_message(member.phone, message)
    
    def send_reminder(self, reminder):
        """Send reminder via WhatsApp"""
        
        member = reminder.member
        return self.send_message(member.phone, reminder.message)
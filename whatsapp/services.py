"""
WhatsApp Business API Service
Optimized for Indian Phone Number Formats
"""
import requests
from django.conf import settings

class WhatsAppService:
    """WhatsApp Business API Service"""
    
    def __init__(self):
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', None)
        self.api_version = getattr(settings, 'WHATSAPP_API_VERSION', 'v18.0')
        
        if self.phone_number_id:
            self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        else:
            self.base_url = None
    
    def send_message(self, to_phone, message):
        """Send text message via WhatsApp"""
        
        if not self.base_url or not self.access_token:
            return {
                'success': False,
                'error': 'WhatsApp API credentials not configured'
            }
        
        # 🛡️ SMART PHONE NUMBER CLEANING
        # Step 1: Remove all non-numeric characters (+, -, space, etc)
        to_phone = ''.join(filter(str.isdigit, str(to_phone)))
        
        # Step 2: Remove leading '0' if present (Common mistake: 09826...)
        if to_phone.startswith('0'):
            to_phone = to_phone[1:]
            
        # Step 3: Add Country Code (91) if missing (assuming 10 digit number)
        if len(to_phone) == 10:
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
                timeout=10 # Timeout zaroori hai taaki server hang na ho
            )
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'message_id': response.json().get('messages', [{}])[0].get('id')
                }
            else:
                # Log error for debugging
                print(f"WhatsApp Error: {response.text}")
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
        try:
            member = receipt.member
            payment = receipt.payment
            gym = receipt.gym
            
            # Safe checking for month
            month_text = payment.month if payment.month else "N/A"
            method_text = payment.get_payment_method_display()
            
            message = f"""
🏋️ *{gym.name}*
📋 Receipt #{receipt.receipt_number}

Dear {member.name},

Thank you for your payment!

💰 Amount: ₹{payment.amount}
📅 Date: {payment.payment_date.strftime('%d-%b-%Y')}
💳 Method: {method_text}
📆 Month: {month_text}

Your membership is valid until: {member.membership_end_date.strftime('%d-%b-%Y')}

For any queries, contact us:
📞 {gym.phone}
📧 {gym.email}

Thank you for being with us!
            """.strip()
            
            return self.send_message(member.phone, message)
        except Exception as e:
            return {'success': False, 'error': f"Receipt formatting failed: {str(e)}"}
    
    def send_reminder(self, reminder):
        """Send reminder via WhatsApp"""
        if reminder and reminder.member:
            return self.send_message(reminder.member.phone, reminder.message)
        return {'success': False, 'error': 'Invalid reminder data'}
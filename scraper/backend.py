# backend.py
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def fetch_emails(email_addr, password, imap_server='imap.gmail.com', days_back=30):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_addr, password)
        mail.select('inbox')

        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')
        status, data = mail.search(None, f'SINCE {since_date}')

        if status != 'OK':
            return pd.DataFrame()

        email_ids = data[0].split()
        orders = {}
        SITES = ['pokemoncenter.com', 'target.com', 'walmart.com', 'bestbuy.com']

        for eid in reversed(email_ids):
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            from_header = msg.get('From')

            if from_header:
                decoded_from = decode_header(from_header)
                sender_parts = []
                for part, encoding in decoded_from:
                    if isinstance(part, bytes):
                        try:
                            sender_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
                        except (UnicodeDecodeError, LookupError):
                            sender_parts.append(part.decode('utf-8', errors='ignore'))
                    else:
                        sender_parts.append(str(part))
                sender = ''.join(sender_parts).lower()
            else:
                continue

            site_match = next((site for site in SITES if site in sender), None)
            if not site_match:
                continue

            subject_header = msg.get('Subject')
            subject = ''
            if subject_header:
                decoded_subject = decode_header(subject_header)
                subject_parts = []
                for part, encoding in decoded_subject:
                    if isinstance(part, bytes):
                        try:
                            subject_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
                        except (UnicodeDecodeError, LookupError):
                            subject_parts.append(part.decode('utf-8', errors='ignore'))
                    else:
                        subject_parts.append(str(part))
                subject = ''.join(subject_parts).lower()

            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                        except:
                            pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass

            body_lower = body.lower()

            order_id_match = re.search(r'order (?:number|#|id)[:\s]*([\w\-]+)', body_lower)
            order_id = order_id_match.group(1) if order_id_match else None

            if not order_id:
                continue

            if 'cancel' in subject or 'cancel' in body_lower:
                status = 'Canceled'
            elif 'deliver' in subject or 'deliver' in body_lower:
                status = 'Delivered'
            elif 'ship' in subject or 'ship' in body_lower:
                status = 'Shipped'
            elif 'confirm' in subject or 'confirm' in body_lower or 'thank you for your order' in body_lower:
                status = 'Confirmed'
            else:
                status = 'Unknown'

            date_str = msg.get('Date')
            date = parsedate_to_datetime(date_str) if date_str else datetime.now()

            if order_id not in orders or date > orders[order_id]['Date']:
                amount_match = re.search(r'\$?\s*(\d+(?:\.\d{1,2})?)', body)
                amount = float(amount_match.group(1)) if amount_match else 0.0

                item_match = re.search(r'(pokémon trading card game .*?)(?:qty|quantity|\n|$)', body_lower)
                item = item_match.group(1).strip().title() if item_match else 'Unknown Item'

                qty_match = re.search(r'(?:qty|quantity)[:\s]*(\d+)', body_lower)
                quantity = int(qty_match.group(1)) if qty_match else 1

                delivery_match = re.search(r'(?:expected delivery|arrives by|delivery date)[:\s]*(.*?)(?:\n|$)', body_lower)
                delivery_date = delivery_match.group(1).strip() if delivery_match else 'N/A'

                orders[order_id] = {
                    'Site': site_match.replace('.com', ''),
                    'Status': status,
                    'Amount': amount,
                    'Date': date,
                    'Item': item,
                    'Quantity': quantity,
                    'Delivery Date': delivery_date,
                    'Order ID': order_id,
                    'Subject': subject[:50] + '...' if len(subject) > 50 else subject
                }

        mail.close()
        mail.logout()

        df = pd.DataFrame(list(orders.values()))
        return df

    except imaplib.IMAP4.error as e:
        # Don't expose credential details in error messages
        error_msg = str(e)
        # Sanitize error message to avoid exposing email
        if email_addr in error_msg:
            error_msg = error_msg.replace(email_addr, "[EMAIL_REDACTED]")
        print(f"Error connecting to Gmail: {error_msg}")
        return pd.DataFrame()
    except Exception as e:
        # Generic error handling - don't expose sensitive info
        print(f"Error fetching emails: Unable to connect. Please check your credentials and internet connection.")
        return pd.DataFrame()

def get_ebay_avg_price(query):
    try:
        url = f'https://www.ebay.com/sch/i.html?_nkw={query.replace(" ", "+")}&_sacat=0&LH_Sold=1&LH_Complete=1&rt=nc&LH_PrefLoc=1'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        prices = []

        for item in soup.find_all('li', class_='s-item')[:10]:
            price_tag = item.find('span', class_='s-item__price')
            if price_tag:
                price_text = price_tag.text.strip()
                price_match = re.search(r'\$?\s*(\d+(?:\.\d{1,2})?)', price_text)
                if price_match:
                    prices.append(float(price_match.group(1)))

        return sum(prices) / len(prices) if prices else 0.0

    except Exception as e:
        print(f"Error fetching eBay prices for {query}: {str(e)}")
        return 0.0

import re

text = """
Carlos, It's a pleasure to greet you; I hope you are doing well. 
The place you need to go is Street Av. 1543, Montreal, Canada. If you would like to connect, you can call +1(514) 7261846 or 5148621618.
For any inquiries, please email me at example.email@example.com or contact@example.org.
"""

# Regular expression for the name
# Captures the name that may be preceded by "Dear", followed by a comma or simply at the beginning of the text
name_pattern = r'(?:Dear\s)?(\w+)(?:,|\s|$)'
name = re.search(name_pattern, text)

# Regular expression for address
address_pattern = r'Street\s.+?Canada'
address = re.search(address_pattern, text)

# Regular expression for phone numbers
phone_pattern = r'\+?\d[\d\s\(\)-]{7,}\d'
phones = re.findall(phone_pattern, text)

# Regular expression for email
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
emails = re.findall(email_pattern, text)

# Display the results
if name:
    print(f"Name: {name.group(1)}")
else:
    print("Name not found.")

if address:
    print(f"Address: {address.group(0)}")
else:
    print("Address not found.")

if phones:
    print("Phone numbers found:")
    for phone in phones:
        print(f"- {phone}")
else:
    print("No phone numbers found.")

if emails:
    print("Email addresses found:")
    for email in emails:
        print(f"- {email}")
else:
    print("No email addresses found.")

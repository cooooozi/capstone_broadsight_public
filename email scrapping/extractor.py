import sys
import os
import extract_msg
import re

def extract_text_from_html(html):
    # Remove HTML tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', html)
    # Remove URLs
    cleantext = re.sub(r'http\S+', '', cleantext)
    return cleantext

def process_msg_file(msg_file_path):
    msg = extract_msg.Message(msg_file_path)
    sender = msg.sender
    recipients = msg.recipients
    subject = msg.subject
    html_body = msg.body
    text_body = extract_text_from_html(html_body)

    return sender, recipients, subject, text_body

def main():
    if len(sys.argv) != 2:
        print("Usage: python extractor.py <msg_file_path>")
        sys.exit(1)

    msg_file_path = sys.argv[1]

    if not os.path.isfile(msg_file_path):
        print(f"Error: File '{msg_file_path}' not found.")
        sys.exit(1)

    sender, recipients, subject, text_body = process_msg_file(msg_file_path)

    print("Sender:", sender)
    print("Recipients:", recipients)
    print("Subject:", subject)
    print("Message Body:", text_body)

    output_file_name = msg_file_path + "_text.txt"

    # Writing to the constructed output file path
    with open(output_file_name, "w") as output_file:
        output_file.write(f"Sender: {sender}\n")
        output_file.write(f"Recipients: {recipients}\n")
        output_file.write(f"Subject: {subject}\n")
        output_file.write(f"Message Body: {text_body}\n")

    print("successfully save as "+output_file_name)
if __name__ == "__main__":
    main()
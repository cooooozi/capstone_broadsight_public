import extract_msg
import re
import os
import spacy
from spacy.language import Language


nlp = spacy.load("en_core_web_sm")

def remove_signature(text):
    """Remove common email signatures."""
    patterns = [
        r"--\s*$",  # line consisting of double dash
        r"Thanks,?|Best,?|Regards,?|Sincerely,?|Cheers,?",  # common closing phrases
        r"^\w+ \w+$"  # the start of a signature
    ]
    signature_regex = re.compile('|'.join(patterns), re.IGNORECASE | re.MULTILINE)
    lines = text.splitlines()
    signature_start_index = None
    for i, line in enumerate(lines):
        if signature_regex.search(line):
            signature_start_index = i
            break
    if signature_start_index is not None:
        return '\n'.join(lines[:signature_start_index]).strip()
    else:
        return text.strip()


def clean_text(text):
    """Clean the message body to make it suitable for LLM processing."""
    text = remove_signature(text)  # Remove signatures
    text = re.sub('<[^<]+?>', '', text)  # Remove HTML tags
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\S*@\S*\s?', '', text)  # Remove email addresses
    text = ' '.join(text.split())  # Normalize whitespace
    return text.strip()


def parse_msg(file_path):
    """Parse the .msg file and extract required details."""
    try:
        with extract_msg.Message(file_path) as msg:
            sender = msg.sender
            receiver = msg.to
            subject = msg.subject
            body = msg.body
            cleaned_body = clean_text(body)
    except Exception as e:
        print(f"Failed to process file {file_path: {e}}")
        return None
    
    return {
        "Sender": sender,
        "Receiver": receiver,
        "Subject": subject,
        "Cleaned Body": cleaned_body
    }


def process_directory(directory_path):
    results = []
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.msg'):
            file_path = os.path.join(directory_path, file_name)
            result = parse_msg(file_path)
            results.append(result)
    
    return results


def print_results(results):
    for index, result in enumerate(results):
        print(f"Message {index + 1}:")
        print(f"  Sender: {result['Sender']}")
        print(f"  Receiver: {result['Receiver']}")
        print(f"  Subject: {result['Subject']}")
        print(f"  Cleaned Body: {result['Cleaned Body']}")
        print("-" * 40)  # Separator


if __name__ == "__main__":
    results = process_directory('data')
    print_results(results)
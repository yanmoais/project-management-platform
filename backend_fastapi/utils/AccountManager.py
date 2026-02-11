import yaml
import os
import random
import string
import logging

logger = logging.getLogger(__name__)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
YAML_PATH = os.path.join(project_root, 'Auth_data', 'Auth_accouting_Data.yaml')

def _fix_duplicate_keys(content):
    """
    Fix duplicate 'by_address' keys in YAML content by merging them.
    Logic: If 'by_address:' appears multiple times within the same list item scope,
    remove the subsequent occurrences line, effectively merging their children.
    """
    lines = content.splitlines()
    new_lines = []
    current_list_indent = -1
    seen_by_address = False
    
    for line in lines:
        stripped = line.strip()
        # Skip empty lines
        if not stripped:
            new_lines.append(line)
            continue
            
        indent = len(line) - len(line.lstrip())
        
        # Check for list item start
        if stripped.startswith('- '):
            current_list_indent = indent
            seen_by_address = False
        
        elif current_list_indent != -1 and indent < current_list_indent:
             current_list_indent = -1
             seen_by_address = False
             
        if stripped.startswith('by_address:'):
            if current_list_indent != -1 and indent > current_list_indent:
                if seen_by_address:
                    continue 
                seen_by_address = True
        
        new_lines.append(line)
        
    return '\n'.join(new_lines)

def _merge_split_items(data):
    """
    Merge split list items (e.g. test_file in one item, step_index in next).
    """
    if not isinstance(data, dict):
        return data
        
    for product, processes in data.items():
        if not isinstance(processes, dict):
            continue
            
        for process_name, items in processes.items():
            if not isinstance(items, list):
                continue
                
            merged_items = []
            i = 0
            while i < len(items):
                current = items[i]
                if i + 1 < len(items):
                    next_item = items[i+1]
                    if isinstance(current, dict) and isinstance(next_item, dict):
                        if 'test_file' in current and 'step_index' not in current and 'step_index' in next_item:
                            # Merge them
                            merged = {**current, **next_item}
                            merged_items.append(merged)
                            i += 2
                            continue
                
                merged_items.append(current)
                i += 1
            
            processes[process_name] = merged_items
            
    return data

def _normalize_missing_fields(data):
    """
    Backfill missing 'test_file' fields in list items by propagating from previous items.
    """
    if not isinstance(data, dict):
        return data
    for product, processes in data.items():
        if not isinstance(processes, dict):
            continue
        for process_name, items in processes.items():
            if not isinstance(items, list):
                continue
            
            last_test_file = None
            for item in items:
                if isinstance(item, dict):
                    if 'test_file' in item:
                        last_test_file = item['test_file']
                    elif last_test_file and 'test_file' not in item:
                        item['test_file'] = last_test_file
    return data

def load_yaml():
    if not os.path.exists(YAML_PATH):
        return {}
    try:
        with open(YAML_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Pre-process to fix duplicate keys
        fixed_content = _fix_duplicate_keys(content)
        
        data = yaml.safe_load(fixed_content) or {}
        data = _merge_split_items(data)
        return _normalize_missing_fields(data)
    except Exception as e:
        logger.error(f"Error loading YAML: {e}")
        return {}

def save_yaml(data):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(YAML_PATH), exist_ok=True)
        with open(YAML_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    except Exception as e:
        logger.error(f"Error saving YAML: {e}")

def get_all_emails_for_url(url, data=None):
    """
    Recursively search for all emails associated with a specific URL in the YAML data.
    """
    if data is None:
        data = load_yaml()
    
    emails = set()
    
    def traverse(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'by_address' and isinstance(value, dict):
                    if url in value:
                        entry = value[url]
                        if isinstance(entry, dict) and 'email' in entry:
                            emails.add(str(entry['email']).strip())
                
                # Continue traversal
                traverse(value)
        elif isinstance(node, list):
            for item in node:
                traverse(item)
                
    traverse(data)
    return emails

def get_credentials_for_url(url, data=None):
    """
    Recursively search for credentials associated with a specific URL in the YAML data.
    Returns the first valid match found.
    """
    if data is None:
        data = load_yaml()
    
    result = None
    
    def traverse(node):
        nonlocal result
        if result: return # Stop if found
        
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'by_address' and isinstance(value, dict):
                    if url in value:
                        entry = value[url]
                        if isinstance(entry, dict) and 'email' in entry and 'password' in entry:
                            result = {
                                'email': str(entry['email']).strip(),
                                'password': str(entry['password']).strip()
                            }
                            return
                
                # Continue traversal
                traverse(value)
        elif isinstance(node, list):
            for item in node:
                traverse(item)
                
    traverse(data)
    return result

def generate_random_email():
    """
    Generate a random email address.
    """
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'test.com', 'example.com']
    # Generate 8-12 char random string for username
    username_len = random.randint(8, 12)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_len))
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_unique_email_for_url(url):
    """
    Generate a unique email for a specific URL by checking against existing YAML data.
    """
    existing_emails = get_all_emails_for_url(url)
    
    # Try up to 10 times to generate a unique email (though collision is unlikely)
    for _ in range(10):
        email = generate_random_email()
        if email not in existing_emails:
            return email
            
    # Fallback if somehow we fail (highly unlikely)
    return generate_random_email()

def update_account_data(product_name, process_name, test_file_name, step_index, step_name, operation_event, address_url_map):
    """
    Update the YAML file with new account data.
    address_url_map: dict of {url: {'email': email, 'password': password}}
    """
    data = load_yaml()
    
    # 1. Ensure Product exists
    if product_name not in data:
        data[product_name] = {}
    
    # 2. Ensure Process exists (it's a dict now)
    if process_name not in data[product_name]:
        data[product_name][process_name] = {}
    if test_file_name not in data[product_name][process_name]:
        if isinstance(data[product_name][process_name], list):
             old_list = data[product_name][process_name]
             data[product_name][process_name] = {}
             for item in old_list:
                 tf = item.get('test_file', 'unknown.py')
                 if tf not in data[product_name][process_name]:
                     data[product_name][process_name][tf] = []
                 if 'test_file' in item:
                     del item['test_file']
                 data[product_name][process_name][tf].append(item)

    if test_file_name not in data[product_name][process_name]:
        data[product_name][process_name][test_file_name] = []
        
    process_steps = data[product_name][process_name][test_file_name]
    
    target_item = None
    for item in process_steps:
        if item.get('step_index') == step_index:
            target_item = item
            break
            
    if not target_item:
        target_item = {
            'step_index': step_index,
            'step_name': step_name,
            'operation_events': operation_event,
            'by_address': {}
        }
        process_steps.append(target_item)
    else:
        target_item['step_name'] = step_name
        target_item['operation_events'] = operation_event
        if 'by_address' not in target_item:
            target_item['by_address'] = {}

    for url, creds in address_url_map.items():
        target_item['by_address'][url] = {
            'email': creds['email'],
            'password': creds['password']
        }
        
    save_yaml(data)

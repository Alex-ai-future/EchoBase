#!/usr/bin/env python3
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
INDEXS_DIR = os.path.join(PROJECT_ROOT, "indexs")
INDEX_MD_PATH = os.path.join(PROJECT_ROOT, "index.md")

MONTHS = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

TOPIC_HEADERS = {
    "agent": "Agent",
    "investment": "Investment",
    "vllm": "VLLM"
}

def parse_frontmatter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if not (content.startswith("---\n") or content.startswith("---\r\n")):
        return None
        
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
        
    yaml_content = parts[1]
    metadata = {}
    for line in yaml_content.strip().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                val = [item.strip().strip('"').strip("'") for item in val[1:-1].split(",")]
            else:
                val = val.strip('"').strip("'")
            metadata[key] = val
    return metadata

def get_month_year_header(date_str):
    # date_str: YYYY-MM-DD
    parts = date_str.split("-")
    if len(parts) >= 2:
        year = parts[0]
        month_num = parts[1]
        month_name = MONTHS.get(month_num, "Unknown")
        return f"--- {month_name} {year} ---"
    return "--- Unknown Date ---"

def generate_markdown_list(logs, is_root=False):
    # Group logs by month/year header, preserving sorted order
    grouped = {}
    headers_order = []
    
    for log in logs:
        header = get_month_year_header(log["date"])
        if header not in grouped:
            grouped[header] = []
            headers_order.append(header)
        grouped[header].append(log)
        
    lines = []
    for header in headers_order:
        lines.append(header)
        for log in grouped[header]:
            rel_path = f"logs/{log['filename']}" if is_root else f"../logs/{log['filename']}"
            lines.append(f"- {log['date']} - [{log['title']}]({rel_path})")
        # Add an empty line between groups, except possibly the last one
        lines.append("")
        
    # Join with newlines, stripping trailing whitespace
    return "\n".join(lines).strip()

def rebuild():
    # 1. Scan and parse all logs
    logs = []
    if not os.path.exists(LOGS_DIR):
        print(f"Error: logs directory not found at {LOGS_DIR}")
        return
        
    for filename in sorted(os.listdir(LOGS_DIR)):
        if filename.endswith(".md"):
            filepath = os.path.join(LOGS_DIR, filename)
            metadata = parse_frontmatter(filepath)
            if not metadata:
                print(f"Warning: No valid frontmatter found in {filename}, skipping.")
                continue
                
            title = metadata.get("title")
            date = metadata.get("date")
            topics = metadata.get("topics", [])
            
            if not title or not date:
                print(f"Warning: Missing title or date in frontmatter of {filename}, skipping.")
                continue
                
            logs.append({
                "filename": filename,
                "title": title,
                "date": date,
                "topics": topics
            })
            
    # Sort logs chronologically (oldest first)
    logs.sort(key=lambda x: (x["date"], x["filename"]))
    
    print(f"Found {len(logs)} valid logs.")
    
    # 2. Build indexs/all.md
    all_content = f"# All\n\n{generate_markdown_list(logs, is_root=False)}\n"
    os.makedirs(INDEXS_DIR, exist_ok=True)
    all_md_path = os.path.join(INDEXS_DIR, "all.md")
    with open(all_md_path, "w", encoding="utf-8") as f:
        f.write(all_content)
    print("Rebuilt indexs/all.md")
    
    # 3. Build topic files (indexs/<topic>.md)
    # Collect all topics
    topics_map = {}
    for log in logs:
        for topic in log["topics"]:
            if topic not in topics_map:
                topics_map[topic] = []
            topics_map[topic].append(log)
            
    for topic, topic_logs in topics_map.items():
        topic_title = TOPIC_HEADERS.get(topic, topic.capitalize())
        topic_content = f"# {topic_title}\n\n{generate_markdown_list(topic_logs, is_root=False)}\n"
        topic_path = os.path.join(INDEXS_DIR, f"{topic}.md")
        with open(topic_path, "w", encoding="utf-8") as f:
            f.write(topic_content)
        print(f"Rebuilt indexs/{topic}.md")
        
    # 4. Update index.md (All Logs section)
    if os.path.exists(INDEX_MD_PATH):
        with open(INDEX_MD_PATH, "r", encoding="utf-8") as f:
            index_content = f.read()
            
        # Match ## All Logs case-insensitively
        match = re.search(r"^(##\s+All\s+Logs.*)$", index_content, re.IGNORECASE | re.MULTILINE)
        if match:
            # Split before the header
            header_start = match.start()
            base_content = index_content[:header_start].rstrip()
        else:
            base_content = index_content.rstrip()
            
        new_all_logs_section = f"## All Logs\n\n{generate_markdown_list(logs, is_root=True)}"
        new_index_content = f"{base_content}\n\n{new_all_logs_section}\n"
        
        with open(INDEX_MD_PATH, "w", encoding="utf-8") as f:
            f.write(new_index_content)
        print("Updated index.md with latest logs list.")
    else:
        print(f"Warning: index.md not found at {INDEX_MD_PATH}")

if __name__ == "__main__":
    rebuild()

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

def parse_existing_topics(index_md_path):
    topics = {}
    if not os.path.exists(index_md_path):
        return topics
        
    with open(index_md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find table lines to parse existing descriptions
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            parts = [p.strip() for p in line.split("|")]
            # A split of '| A | B | C |' results in ['', 'A', 'B', 'C', '']
            if len(parts) >= 5:
                topic_name = parts[1]
                topic_desc = parts[2]
                topic_link_raw = parts[3]
                
                # Skip header and divider lines
                if topic_name.lower() in ("topic", "topicname") or all(c in "- :" for c in topic_name):
                    continue
                    
                # Extract link target from markdown link e.g., [indexs/agent.md](indexs/agent.md) -> indexs/agent.md
                link_match = re.search(r"\[.*\]\((.*)\)", topic_link_raw)
                topic_link = link_match.group(1) if link_match else topic_link_raw
                
                # Derive topic key from link or name, e.g. indexs/agent.md -> agent
                topic_key = os.path.basename(topic_link).replace(".md", "").lower()
                
                topics[topic_key] = {
                    "name": topic_name,
                    "desc": topic_desc,
                    "link": topic_link
                }
    return topics

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
    
    # 2. Collect all topics and dynamic mapping
    topics_map = {}
    for log in logs:
        for topic in log["topics"]:
            if topic not in topics_map:
                topics_map[topic] = []
            topics_map[topic].append(log)
            
    # Parse existing topics from current index.md
    topic_info = parse_existing_topics(INDEX_MD_PATH)
    
    # Dynamically register any new topic not in topic_info
    for topic in topics_map.keys():
        if topic not in topic_info:
            topic_info[topic] = {
                "name": topic.upper() if len(topic) <= 4 else topic.replace("-", " ").capitalize(),
                "desc": f"{topic.replace('-', ' ').capitalize()} related discussions and logs",
                "link": f"indexs/{topic}.md"
            }
    
    # 3. Build topic files (indexs/<topic>.md)
    os.makedirs(INDEXS_DIR, exist_ok=True)
    for topic, topic_logs in topics_map.items():
        topic_title = topic_info[topic]["name"] if topic in topic_info else topic.capitalize()
        topic_content = f"# {topic_title}\n\n{generate_markdown_list(topic_logs, is_root=False)}\n"
        topic_path = os.path.join(INDEXS_DIR, f"{topic}.md")
        with open(topic_path, "w", encoding="utf-8") as f:
            f.write(topic_content)
        print(f"Rebuilt indexs/{topic}.md")
        
    # 4. Rebuild index.md completely
    index_lines = [
        "# Index",
        "",
        "| Topic | Description | Link |",
        "|-------|-------------|------|"
    ]
    
    # Alphabetical active topics
    sorted_keys = sorted([k for k in topic_info.keys() if k in topics_map])
    for key in sorted_keys:
        info = topic_info[key]
        index_lines.append(f"| {info['name']} | {info['desc']} | [{info['link']}]({info['link']}) |")
        
    index_lines.append("")
    index_lines.append("## All Logs")
    index_lines.append("")
    index_lines.append(generate_markdown_list(logs, is_root=True))
    index_lines.append("")
    
    with open(INDEX_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))
    print("Rebuilt index.md completely.")

if __name__ == "__main__":
    rebuild()

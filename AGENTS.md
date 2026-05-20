# Project Structure

## logs
- **Naming Convention**: `YYYY.MM.D.N.md` (Year.Month.Day.Sequence)
  - Sequence starts from `0`, two digits with leading zeros (e.g., `00`, `01`, `10`)
  - Multiple logs per day are allowed, incremented by creation order
  - Example: `2026.05.16.00.md`, `2026.05.16.01.md`
- **Content Requirements**:
  - Must contain valid Markdown content, no empty files allowed
  - Language: Chinese
  - Style: Extremely concise, logically rigorous, maintain critical thinking
  - Recommended: Core ideas / Record topics / Key conclusions
- **Encoding**: UTF-8

## indexs
- **Naming Convention**: Filename (without extension) represents the topic name, use lowercase English or Chinese, spaces replaced with `-`
  - Example: `ai-thinking.md`, `项目管理.md`
- **Special Index**: `all.md` - Contains all logs in chronological order
- **Content Format**:
  ```markdown
  # Topic Name
  
  --- May 2026 ---
  - [Brief description of core idea](../logs/YYYY.MM.D.N.md)
  - [Brief description of core idea](../logs/YYYY.MM.D.N.md)
  
  --- June 2026 ---
  - [Brief description of core idea](../logs/YYYY.MM.D.N.md)
  ```
- **Time Divider**: Use `--- Month YYYY ---` format (English)
- **Encoding**: UTF-8

## index.md
- **Purpose**: Main page for GitHub Pages, displays all topics in table format and the list of all logs in chronological order.
- **Content Format**:
  ```markdown
  # Index
  
  | Topic | Description | Link |
  |-------|-------------|------|
  | TopicName | Brief description | [indexs/topic.md](indexs/topic.md) |

  ## All Logs

  --- Month YYYY ---
  - [Brief description of core idea](logs/YYYY.MM.D.N.md)
  ```
- **Encoding**: UTF-8

## README.md
- **Purpose**: Project introduction and documentation
- **Content Format**:
  ```markdown
  # EchoBase
  
  EchoBase is a knowledge management system for recording and organizing thought logs.
  
  🌐 Online: https://alex-ai-future.github.io/EchoBase/
  ```
- **Encoding**: UTF-8

## General Rules
- **Conflict Handling**: If filename already exists, auto-increment the sequence number
- **Version Control**: All files must be managed under Git
- **Path References**: Use relative paths from project root
- **Language Policy**: 
  - `logs/` files: Chinese
  - All other files (`indexs/`, `README.md`, `AGENTS.md`): English
- **Index Maintenance**: When a new log is created, the agent must update:
  - The corresponding topic index file in `indexs/`
  - The special index file `indexs/all.md`
  - The `All Logs` section in `index.md` (note: links in `index.md` must point directly to `logs/` instead of `../logs/`)
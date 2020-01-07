# Automation Script for DM Final Project (Steiner Tree)
### Requirements
- python 3.6
- networkx 2.4

```bash
pip install networkx
```

### Testcase
http://steinlib.zib.de/download.php

### Target Structure
```bash
data/
├── B
├── I640
└── ...
```

```bash
students/
├── 061xxxx
├── 071xxxx
├── 071xxxx
├── 071xxxx
└── ...
```

### Usage
#### parse steiner tree data for classical style
specify dataset name in the parse_classical.py (`dataset_name = "I640"`)
```bash
python parse_classical.py
```
#### run evaluate
```bash
source [env]
python run_evaluate.py [student_files_dir]
```

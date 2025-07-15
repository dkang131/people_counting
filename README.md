# People Counter

This project is a real-time people counting system using a webcam and a YOLO-based object detection model.

## Setup Instructions

### 1. Clone the Repository

```
git clone <your-repo-url>
cd people-counter
```

### 2. Create a Virtual Environment

#### Using Python venv
```
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
.venv\Scripts\activate    # On Windows
```

#### Using Conda
```
conda create -p .venv python=3.10 -y
conda activate ./venv
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Run the Application

```
python main.py
```

---

- The main entry point is `main.py`.
- Make sure your model file is in the `model/` directory.
- For any issues, please check your Python version and dependencies. 
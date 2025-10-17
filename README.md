# Python Blockchain Medical Ledger 🩺

This project is a fully functional, decentralized blockchain application built from scratch in Python. It simulates a secure medical record ledger where data is stored in immutable blocks, validated by a Proof of Work algorithm, and synchronized across a peer-to-peer network using a consensus mechanism.

The application is controlled via a simple web-based user interface.



---

## ✨ Features

* **Core Blockchain Logic:** Includes `Block` and `Blockchain` classes that manage the chain's integrity.
* **Proof of Work:** Secures the blockchain by requiring computational effort to mine new blocks.
* **Dynamic Difficulty:** The mining difficulty (number of leading zeros) can be adjusted in real-time from the user interface.
* **Decentralized P2P Network:** Run multiple nodes that can discover each other and synchronize their chains.
* **Consensus Algorithm:** Implements the "longest valid chain wins" rule to resolve conflicts between nodes.
* **Full API:** A Flask-based API to interact with the blockchain (mine blocks, add data, manage nodes).
* **Interactive Web UI:** A user-friendly frontend to add records, mine blocks, and manage the network without using the command line.

---

## 🛠️ Technology Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, JavaScript (Vanilla)
* **Networking:** `requests` library

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

You need to have Python 3 and Git installed on your system.

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/](https://github.com/)<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
    cd <YOUR_REPO_NAME>
    ```

2.  **Create and activate a Python virtual environment:**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

---

## ▶️ How to Run the Application

To test the decentralized features, you need to run at least two nodes on different ports.

1.  **Start your first node (on port 5000):**
    Open a terminal and run:
    ```sh
    python api.py 5000
    ```

2.  **Start your second node (on port 5001):**
    Open a **second, separate terminal**, activate the virtual environment again, and run:
    ```sh
    python api.py 5001
    ```

---

## 💡 How to Use the Interface

Here's a quick guide to testing the P2P network features:

1.  **Open two browser tabs:**
    * Tab 1: `http://127.0.0.1:5000`
    * Tab 2: `http://127.0.0.1:5001`

2.  **Register Node 2 with Node 1:**
    * In Tab 1 (Port 5000), go to the "Network & Difficulty" panel.
    * Enter `127.0.0.1:5001` in the "Node Address" box and click **Register Node**.

3.  **Create a Disagreement:**
    * In Tab 2 (Port 5001), add a new medical record.
    * Click the **Mine New Block** button.
    * The chain on Port 5001 will now be longer than the chain on Port 5000.

4.  **Achieve Consensus:**
    * Go back to Tab 1 (Port 5000).
    * Click the **Resolve Conflicts** button.
    * You will see the message "Our chain was replaced," and the blockchain display will update to match the longer chain from Node 5001.

You have now successfully synchronized the network!
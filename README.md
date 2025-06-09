# 📋 Stationery Management System

A professional Flask-based web application to streamline stationery inventory requests across employee, admin, and superadmin roles.

---

## ✨ Features

- 👩‍💼 **Employee Dashboard**  
  - Request stationery items  
  - View personal request history

- 🧑‍💼 **Admin Dashboard**  
  - View and manage all requests  
  - Approve or reject items  
  - Track issued quantities

- 👑 **Superadmin Panel**  
  - Full access to all requests  
  - Manage (Add/Edit/Delete) users  
  - Download requests in Excel  
  - Approve requests on behalf of admin

- 📅 **Date, Department, and Status Filtering**
- 📦 Pre-defined item dropdown for clean submissions
- ✅ Flash messages and validations
- 📁 SQLite database included (`stationary.db`)

---

## 🚀 Installation & Setup

### 📦 Prerequisites

- Python 3.8+
- Git installed

---

### ⚙️ Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/stationery-management-system.git
cd stationery-management-system

# 2. Create and activate virtual environment
python -m venv env
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

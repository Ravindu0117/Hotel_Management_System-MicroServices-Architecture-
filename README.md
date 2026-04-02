# 🏨 Hotel Booking System — Microservices Architecture

A modular hotel booking system built with FastAPI, using a centralized API Gateway as the single entry point for all services.

---

## ✨ Features

- Modular microservices architecture
- Centralized API Gateway (single entry point)
- Independent service deployment
- Built-in Swagger API documentation
- Gateway-based routing for all services
- Optional micro-frontend support

---

## 🛠 Tech Stack

| Layer       | Technology          |
|-------------|---------------------|
| Language    | Python 3.10+        |
| Framework   | FastAPI             |
| API Gateway | FastAPI + httpx proxy |

---

## 📁 Project Structure

```
hotel-booking-system/
├── api-gateway/         → Port 8000 (single entry point)
├── guest-service/       → Port 8001
├── room-service/        → Port 8002
├── booking-service/     → Port 8003
├── payment-service/     → Port 8004
├── staff-service/       → Port 8005
└── feedback-service/    → Port 8006
```

---

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install fastapi uvicorn
pip install httpx
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```
### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Services

Open **7 terminal windows** and run one command in each:

```bash
# Terminal 1 - API Gateway
cd api-gateway; python main.py

# Terminal 2 - Guest Service
cd guest-service; python main.py

# Terminal 3 - Room Service
cd room-service; python main.py

# Terminal 4 - Booking Service
cd booking-service; python main.py

# Terminal 5 - Payment Service
cd payment-service; python main.py

# Terminal 6 - Staff Service
cd staff-service; python main.py

# Terminal 7 - Feedback Service
cd feedback-service; python main.py

# Terminal 8 - Feedback Service
cd api-gateway; python frontend.py

```

---

## 🌐 API Gateway Usage

Instead of accessing multiple ports, use the API Gateway at `http://localhost:8000`:

- `http://localhost:8000` → Swagger UI (redirects to `/docs`)
- `http://localhost:8000/ui` → Frontend UI (redirects to `http://localhost:8007`)

| Service  | Gateway Endpoint                          |
|----------|-------------------------------------------|
| Guests   | http://localhost:8000/api/guests          |
| Rooms    | http://localhost:8000/api/rooms           |
| Bookings | http://localhost:8000/api/bookings        |
| Payments | http://localhost:8000/api/payments        |
| Staff    | http://localhost:8000/api/staff           |
| Feedback | http://localhost:8000/api/feedbacks       |

---

## 📖 Swagger UI

| Service          | Direct Access                    | Via Gateway    |
|------------------|----------------------------------|----------------|
| API Gateway      | http://localhost:8000/docs       | —              |
| Guest Service    | http://localhost:8001/docs       | /api/guests    |
| Room Service     | http://localhost:8002/docs       | /api/rooms     |
| Booking Service  | http://localhost:8003/docs       | /api/bookings  |
| Payment Service  | http://localhost:8004/docs       | /api/payments  |
| Staff Service    | http://localhost:8005/docs       | /api/staff     |
| Feedback Service | http://localhost:8006/docs       | /api/feedbacks |

---


## 📖 API point

| Service          | Direct Access              |
|------------------|----------------------------|
| API Gateway      | http://localhost:8000      | 
| Guest Service    | http://localhost:8001      | 
| Room Service     | http://localhost:8002      | 
| Booking Service  | http://localhost:8003      | 
| Payment Service  | http://localhost:8004      | 
| Staff Service    | http://localhost:8005      | 
| Feedback Service | http://localhost:8006      | 

---

## 📖 Frontend UI

.................................................
| Service          | Direct Access              |
|------------------|----------------------------|
| Frontend UI      | http://localhost:8000/ui   | 
|                  | http://localhost:8007      | 
.................................................

---

## 🖥️ Web UI

After starting all services, open the UI in your browser:

```
http://localhost:8007
```

This UI calls all services through the API Gateway paths:

- `GET /api/guests`
- `GET /api/rooms`
- `GET /api/bookings`
- `GET /api/payments`
- `GET /api/staff`
- `GET /api/feedbacks`

---

## 📡 Example API Requests

### Get All Guests
```bash
GET http://localhost:8000/api/guests
```

### Get Available Rooms
```bash
GET http://localhost:8000/api/rooms?available_only=true
```

### Create a Booking
```bash
POST http://localhost:8000/api/bookings
Content-Type: application/json

{
  "guest_id": 1,
  "room_id": 2,
  "check_in_date": "2026-04-20",
  "check_out_date": "2026-04-25",
  "total_price": 650.0
}
```

### Process a Payment
```bash
POST http://localhost:8000/api/payments
Content-Type: application/json

{
  "booking_id": 1,
  "amount": 650.0,
  "payment_method": "card"
}
```

### Submit Feedback
```bash
POST http://localhost:8000/api/feedbacks
Content-Type: application/json

{
  "guest_id": 1,
  "booking_id": 1,
  "rating": 5,
  "comment": "Amazing stay!"
}
```

---

## 🧩 Micro-Frontend Setup (Optional)

Each backend service supports CORS for frontend ports 3000–3006 and the gateway port 8000.

### Steps

1. **Create a frontend app for each service:**
   ```bash
   npx create-react-app frontend/guest-ui
   npx create-react-app frontend/room-ui
   ```

2. **In each app, point API calls to the gateway:**
   ```
   GET /api/guests
   GET /api/rooms
   ```

3. **Run service + gateway + UI in separate terminals:**
   ```bash
   cd guest-service && python main.py
   cd api-gateway && python main.py
   cd frontend/guest-ui && npm start
   ```

4. **Access via browser:**
   - `http://localhost:3000` — Guest UI
   - `http://localhost:8000/api/guests` — Gateway route

---

## 📝 License

This project is licensed under the **MIT License**.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this project, as long as you include the original license and copyright notice.

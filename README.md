# 📡 DRF SMS Gateway — Uzbekistan (Beeline & Uzmobile)

Production-ready **SMS service platform** built with **Django REST Framework + Celery**.  
It provides a secure and scalable way to send, receive, and track SMS messages — with support for **Beeline** and **Uzmobile** routing.

---

## ✨ Features
- 📱 Multi-operator routing by prefix (Beeline + Uzmobile)
- 🔑 API key authentication for customers
- 📤 Outbound SMS via HTTP/SMPP upstreams
- 📥 Inbound MO & DLR webhooks
- 📊 Django Admin for customers, routes, delivery logs
- ⚡ Celery + Redis for async background processing
- 🐳 Ready to deploy with Docker Compose

---

## 🛠 Tech Stack
- **Backend:** Django 5 + Django REST Framework
- **Tasks:** Celery 5 + Redis
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Protocols:** HTTP (JSON), optional SMPP

---

## 🚀 Quick start

### 1. Clone & configure
```bash
git clone https://github.com/ShohjahonObruyevOybekovich/Notiq_uz.git
cd Notiq_uz
cp .env.example .env
# edit .env -> add Beeline/Uzmobile upstream URLs & tokens
2. Run with Docker
bash
Copy code
docker compose up -d --build
3. Apply migrations & create superuser
bash
Copy code
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
4. Create customer + API key
bash
Copy code
docker compose exec web python manage.py create_apikey "Company name"
5. Bootstrap Beeline/Uzmobile routes
bash
Copy code
docker compose exec web python manage.py bootstrap_routes
📤 Sending an SMS
bash
Copy code
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <PASTE_API_KEY>" \
  -d '{"to":"+998901234567","text":"Salom, dunyo!","sender_id":"Company_id"}'
Response:

json
Copy code
{"id": "e3f…", "status": "queued"}
📥 Simulating a DLR (Delivery Report)
bash
Copy code
curl -X POST http://localhost:8000/api/v1/webhooks/dlr \
  -H "Content-Type: application/json" \
  -d '{"message_id":"<uuid>","status":"DELIVRD"}'
🗂 Project Structure
bash
Copy code
core/         # Django core settings
accounts/     # Customers & API keys
messaging/    # Messages, routes, webhooks, Celery tasks
integrations/ # HTTP/SMPP upstream connectors
common/       # Utils, custom authentication
📌 Roadmap
 Add billing & CDRs per customer

 Add sender-ID approval workflow

 Add monitoring (Prometheus + Grafana)

 Improve webhook security (HMAC signatures)

📄 License
MIT License.
You are free to use, modify, and distribute this project with attribution.

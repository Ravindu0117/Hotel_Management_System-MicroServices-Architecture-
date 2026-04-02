#!/bin/bash
echo "Starting Hotel Booking System Microservices..."
echo ""

cd "$(dirname "$0")"

# Start all microservices in background
python services/guest-service/main.py &
echo "Guest Service started on port 8001"

python services/room-service/main.py &
echo "Room Service started on port 8002"

python services/booking-service/main.py &
echo "Booking Service started on port 8003"

python services/payment-service/main.py &
echo "Payment Service started on port 8004"

python services/housekeeping-service/main.py &
echo "Housekeeping Service started on port 8005"

python services/notification-service/main.py &
echo "Notification Service started on port 8006"

sleep 2

python api-gateway/main.py &
echo "API Gateway started on port 8000"

python api-gateway/frontend.py &
echo "Frontend started on port 8007"

echo ""
echo "All services running!"
echo ""
echo "Direct Swagger URLs:"
echo "  Guest Service:         http://localhost:8001/docs"
echo "  Room Service:          http://localhost:8002/docs"
echo "  Booking Service:       http://localhost:8003/docs"
echo "  Payment Service:       http://localhost:8004/docs"
echo "  Housekeeping Service:  http://localhost:8005/docs"
echo "  Notification Service:  http://localhost:8006/docs"
echo ""
echo "Gateway Swagger URL:"
echo "  API Gateway:           http://localhost:8000/docs"
echo ""
echo "Frontend URL:"
echo "  UI:                    http://localhost:8007"
echo ""
echo "Press Ctrl+C to stop all services"
wait

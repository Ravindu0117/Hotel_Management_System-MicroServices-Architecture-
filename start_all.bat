@echo off
echo Starting Hotel Booking System Microservices...
echo.

start "Guest Service" cmd /k "cd services\guest-service && python main.py"
timeout /t 1 >nul

start "Room Service" cmd /k "cd services\room-service && python main.py"
timeout /t 1 >nul

start "Booking Service" cmd /k "cd services\booking-service && python main.py"
timeout /t 1 >nul

start "Payment Service" cmd /k "cd services\payment-service && python main.py"
timeout /t 1 >nul

start "Housekeeping Service" cmd /k "cd services\housekeeping-service && python main.py"
timeout /t 1 >nul

start "Notification Service" cmd /k "cd services\notification-service && python main.py"
timeout /t 1 >nul

timeout /t 2 >nul
start "API Gateway" cmd /k "cd api-gateway && python main.py"
timeout /t 1 >nul
start "Frontend" cmd /k "cd api-gateway && python frontend.py"

echo.
echo All services started!
echo.
echo Swagger URLs (Direct):
echo   Guest Service:         http://localhost:8001/docs
echo   Room Service:          http://localhost:8002/docs
echo   Booking Service:       http://localhost:8003/docs
echo   Payment Service:       http://localhost:8004/docs
echo   Housekeeping Service:  http://localhost:8005/docs
echo   Notification Service:  http://localhost:8006/docs
echo.
echo Swagger URL (via API Gateway):
echo   API Gateway:           http://localhost:8000/docs
echo.
echo Frontend URL:
echo   UI:                    http://localhost:8007
echo.
pause

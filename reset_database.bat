@echo off
echo ===== FRC Project Management System: Database Reset =====
echo.
echo WARNING: This will delete your current database and create a new one.
echo All project data will be lost!
echo.
set /p confirm=Are you sure you want to continue? (y/n): 

if /i "%confirm%" neq "y" (
    echo Operation cancelled.
    pause
    exit /b
)

echo.
echo Deleting database...
if exist db.sqlite3 del db.sqlite3

echo.
echo Database has been reset. 
echo Please restart the application to set up a new database.
echo.
pause
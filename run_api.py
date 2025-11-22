"""
Script to run the FastAPI server.
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 80)
    print("Starting Sales Analytics API")
    print("=" * 80)
    print("\nAPI Documentation available at:")
    print("   - Swagger UI: http://localhost:8000/api/docs")
    print("   - ReDoc:      http://localhost:8000/api/redoc")
    print("\nDefault admin credentials:")
    print("   Email:    admin@salesanalytics.com")
    print("   Password: admin123")
    print("\nNote: Change admin password in production!")
    print("=" * 80)
    print()

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

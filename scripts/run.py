"""
Quick start script for the Traffic Forecasting System
"""

import uvicorn
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    print("=" * 60)
    print("Smart City Traffic Forecasting System")
    print("=" * 60)
    print("\nStarting FastAPI server...")
    print("Dashboard will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        "src.SmartTrafficForcastingSystem:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


# src/hw_agent/main.py

import argparse
from fastapi import FastAPI
import uvicorn
from hw_agent.routers.configuration_router import router as config_router
from hw_agent.routers.computational_data_router import router as computational_data_router
from hw_agent.routers.plugin_router import router as plugin_router
from hw_agent.routers.catalogue_router import router as catalogue_router 
from hw_agent.exceptions.error_handling import add_exception_handlers
from fastapi.middleware.cors import CORSMiddleware


# Create the FastAPI app instance
app = FastAPI(description="HW Agent Plugins API", version="1.0.0", title="HW Agent Plugins API")

# Add custom exception handlers
add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(config_router)
app.include_router(computational_data_router)
app.include_router(plugin_router)
app.include_router(catalogue_router)


def main():
    parser = argparse.ArgumentParser(description="Run the HW Agent service with optional reload.")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Run Uvicorn in reload mode, automatically reloading on code changes."
    )
    args = parser.parse_args()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=args.reload
    )
if __name__ == "__main__":
    main()

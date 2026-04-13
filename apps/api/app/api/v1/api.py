from fastapi import APIRouter

from app.api.v1.routers import administration, auth, cabinets, contacts_capture, dashboards, demands, demo, mobile, persons, polos, relationships, tasks, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(cabinets.router, prefix="/cabinets", tags=["Cabinets"])
api_router.include_router(persons.router, prefix="/persons", tags=["Persons"])
api_router.include_router(contacts_capture.router, prefix="/contacts-capture", tags=["ContactsCapture"])
api_router.include_router(demands.router, prefix="/demands", tags=["Demands"])
api_router.include_router(polos.router, prefix="/polos", tags=["Polos"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(mobile.router, prefix="/mobile", tags=["Mobile"])
api_router.include_router(relationships.router, prefix="/relationships", tags=["Relationships"])
api_router.include_router(administration.router, prefix="/administration", tags=["Administration"])
api_router.include_router(demo.router, prefix="/demo", tags=["Demo"])
api_router.include_router(dashboards.router, prefix="", tags=["Dashboards"])

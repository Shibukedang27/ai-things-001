"""Learning roadmap CRUD endpoints."""

from app.api.crud_router import create_crud_router
from app.schemas.learning_roadmap import LearningRoadmapCreate, LearningRoadmapRead, LearningRoadmapUpdate
from app.services.resources import LearningRoadmapCRUDService

router = create_crud_router(
    service_cls=LearningRoadmapCRUDService,
    create_schema=LearningRoadmapCreate,
    update_schema=LearningRoadmapUpdate,
    read_schema=LearningRoadmapRead,
    resource_name="learning roadmaps",
)

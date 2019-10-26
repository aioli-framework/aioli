from aioli import Unit

from .service import VisitService, VisitorService
from .controller import HttpController
from .config import ConfigSchema


export = Unit(
    controllers=[HttpController],
    services=[VisitService, VisitorService],
    config=ConfigSchema,
)

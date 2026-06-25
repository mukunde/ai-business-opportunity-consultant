"""ORM models. Import models here so Alembic autogenerate sees them."""

from app.models.opportunity import Opportunity, OpportunityStatus

__all__ = ["Opportunity", "OpportunityStatus"]

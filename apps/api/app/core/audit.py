import json
from functools import wraps

from sqlalchemy.orm import Session

from app.shared.audit import write_audit_log


def audited_mutation(action: str, entity_schema: str, entity_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            db: Session | None = kwargs.get("db")
            current_user = kwargs.get("current_user")
            if db is None:
                for arg in args:
                    if isinstance(arg, Session):
                        db = arg
                        break
            if current_user is None:
                current_user = kwargs.get("user")

            entity_id = getattr(result, "id", None)
            if db is not None:
                write_audit_log(
                    db,
                    user_id=getattr(current_user, "id", None),
                    action=action,
                    entity_schema=entity_schema,
                    entity_name=entity_name,
                    entity_id=entity_id,
                    old_values_json=None,
                    new_values_json=json.dumps({"id": str(entity_id)}) if entity_id else None,
                )
            return result

        return wrapper

    return decorator

from sqlalchemy import text
from sqlalchemy.orm import Session


def write_audit_log(
    db: Session,
    *,
    user_id,
    action: str,
    entity_schema: str,
    entity_name: str,
    entity_id,
    old_values_json=None,
    new_values_json=None,
):
    stmt = text(
        """
        insert into governance.audit_logs (
            user_id, action, entity_schema, entity_name, entity_id, old_values_json, new_values_json
        ) values (
            :user_id, :action, :entity_schema, :entity_name, :entity_id, cast(:old_values_json as jsonb), cast(:new_values_json as jsonb)
        )
        """
    )
    db.execute(
        stmt,
        {
            "user_id": user_id,
            "action": action,
            "entity_schema": entity_schema,
            "entity_name": entity_name,
            "entity_id": entity_id,
            "old_values_json": old_values_json,
            "new_values_json": new_values_json,
        },
    )


def write_access_log(db: Session, *, user_id=None, event_type: str, success: bool):
    stmt = text(
        """
        insert into governance.access_logs (
            user_id, event_type, success
        ) values (
            :user_id, :event_type, :success
        )
        """
    )
    db.execute(stmt, {"user_id": user_id, "event_type": event_type, "success": success})


def write_export_log(db: Session, *, user_id, export_type: str, filter_json=None, row_count: int | None = None):
    stmt = text(
        """
        insert into governance.export_logs (
            user_id, export_type, filter_json, row_count
        ) values (
            :user_id, :export_type, cast(:filter_json as jsonb), :row_count
        )
        """
    )
    db.execute(
        stmt,
        {
            "user_id": user_id,
            "export_type": export_type,
            "filter_json": filter_json,
            "row_count": row_count,
        },
    )

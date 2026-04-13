class PoloPolicy:
    @staticmethod
    def can_manage_polo(current_user, polo_id) -> bool:
        if current_user.is_global_admin:
            return True
        return polo_id in current_user.allowed_polo_ids

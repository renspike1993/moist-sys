class RegistrarRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'registrar':
            return 'registrar'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'registrar':
            return 'registrar'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'registrar':
            return db == 'registrar'
        return db == 'default'

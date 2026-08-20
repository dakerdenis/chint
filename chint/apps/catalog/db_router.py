class CatalogRouter:
    route_app_labels = {"catalog"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "catalog"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "catalog"
        return None

    def allow_migrate(self, db, app_label, **hints):
        if app_label in self.route_app_labels:
            return db == "catalog"
        return db == "default"

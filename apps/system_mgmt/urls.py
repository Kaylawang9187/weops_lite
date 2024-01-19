from django.urls import include, path
from rest_framework import routers

from apps.system_mgmt.views.log_entry_viewset import LogEntryViewSet
from apps.system_mgmt.views.logo import LogoViewSet
from apps.system_mgmt.views.menu_manage import MenuManageModelViewSet
from apps.system_mgmt.views.operation_log import OperationLogViewSet
from apps.system_mgmt.views.user_manage import KeycloakGroupViewSet, KeycloakUserViewSet, KeycloakRoleViewSet

router = routers.DefaultRouter()
router.register(r"audit_log", LogEntryViewSet, basename="audit_log")

router.register(r"group", KeycloakGroupViewSet, basename="group")
router.register(r"user", KeycloakUserViewSet, basename="user")
router.register(r"role", KeycloakRoleViewSet, basename="role")

router.register(r"menu", MenuManageModelViewSet, basename="menu")
router.register(r"operation_log", OperationLogViewSet, basename="operation_log")
router.register(r"logo", LogoViewSet, basename="logo")

urlpatterns = [path("api/", include(router.urls)), ]

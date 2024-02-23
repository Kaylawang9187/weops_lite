from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.core.decorators.uma_permission import uma_permission
from apps.core.utils.web_utils import WebUtils
from apps.system_mgmt.services.user_manage import UserManage


class KeycloakRoleViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_id="role_list",
        operation_description="获取所有角色",
    )
    @uma_permission("role_list")
    def list(self, request):
        data = UserManage().role_list()
        return WebUtils.response_success(data)

    @swagger_auto_schema(
        operation_id="role_permissions",
        operation_description="获取角色拥有的权限",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色英文名称", type=openapi.TYPE_STRING)
        ],
    )
    @uma_permission("role_permissions")
    @action(detail=True, methods=["get"], url_path="permissions")
    def role_permissions(self, request, pk: str):
        data = UserManage().role_permissions(pk)
        return WebUtils.response_success(data)

    @swagger_auto_schema(
        operation_id="role_create",
        operation_description="创建角色",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="角色名称"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, description="描述"),
            },
            required=["name"]
        ),
    )
    @uma_permission("role_create")
    def create(self, request):
        data = UserManage().role_create(request.data, request.userinfo.get("username"))
        return WebUtils.response_success(data)

    @swagger_auto_schema(
        operation_id="role_delete",
        operation_description="删除角色",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色英文名称", type=openapi.TYPE_STRING),
        ],
    )
    @uma_permission("role_delete")
    def destroy(self, request, pk: str):
        data = UserManage().role_delete(pk, request.userinfo.get("username"))
        return WebUtils.response_success(data)

    @swagger_auto_schema(
        operation_id="role_update",
        operation_description="修改角色信息",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色英文名称", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="角色英文名"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, description="描述"),
            }
        )
    )
    @uma_permission("role_update")
    def update(self, request, pk: str):
        UserManage().role_update(request.data, pk, request.userinfo.get("username"))
        return WebUtils.response_success()

    @swagger_auto_schema(
        operation_id="role_set_permissions",
        operation_description="设置角色权限",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色英文名称", type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING, description="权限名称")
        ),
    )
    @role_permissions.mapping.patch
    @uma_permission("role_set_permissions")
    def ch_permission(self, request, pk: str):
        UserManage().role_set_permissions(request.data, pk, request.userinfo.get("username"))
        return WebUtils.response_success()

    @swagger_auto_schema(
        operation_id="role_add_user",
        operation_description="将一个用户添加到角色",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色的ID", type=openapi.TYPE_STRING),
            openapi.Parameter("user_id", openapi.IN_PATH, description="用户的ID", type=openapi.TYPE_STRING),
        ],
    )
    @action(detail=True, methods=["put"], url_path="assign/(?P<user_id>[^/.]+)")
    @uma_permission("role_add_user")
    def assign_role(self, request, pk: str, user_id: str):
        UserManage().role_add_user(pk, user_id, request.userinfo.get("username"))
        return WebUtils.response_success()

    @swagger_auto_schema(
        operation_id="role_remove_user",
        operation_description="将一个用户从角色移除",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色的ID", type=openapi.TYPE_STRING),
            openapi.Parameter("user_id", openapi.IN_PATH, description="用户的ID", type=openapi.TYPE_STRING),
        ],
    )
    @action(detail=True, methods=["delete"], url_path="withdraw/(?P<user_id>[^/.]+)")
    @uma_permission("role_remove_user")
    def withdraw_role(self, request, pk: str, user_id: str):
        UserManage().role_remove_user(pk, user_id, request.userinfo.get("username"))
        return WebUtils.response_success()

    @swagger_auto_schema(
        operation_id="role_add_groups",
        operation_description="将该角色添加到一系列组中",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色的ID", type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING, description="组ID")
        ),
    )
    @action(detail=True, methods=["patch"], url_path="assign_groups")
    @uma_permission("role_add_groups")
    def assign_groups(self, request, pk: str):
        UserManage().role_add_groups(request.data, pk, request.userinfo.get("username"))
        return WebUtils.response_success()

    @swagger_auto_schema(
        operation_id="role_remove_groups",
        operation_description="将该角色从一系列组中移除",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="角色ID", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING, description="组ID")
        ),
    )
    @action(detail=True, methods=["delete"], url_path="unassign_groups")
    @uma_permission("role_remove_groups")
    def unassign_groups(self, request, pk: str):
        UserManage().role_remove_groups(request.data, pk, request.userinfo.get("username"))
        return WebUtils.response_success()

    @swagger_auto_schema(
        operation_id="role_groups",
        operation_description="获取该角色下的所有组",
        manual_parameters=[
            openapi.Parameter("role_name", openapi.IN_PATH, description="角色英文名称", type=openapi.TYPE_STRING)
        ],
    )
    @action(detail=False, methods=["get"], url_path="groups/(?P<role_name>.+?)")
    @uma_permission("role_groups")
    def get_groups_by_role(self, request, role_name: str):
        data = UserManage().role_groups(role_name)
        return WebUtils.response_success(data)
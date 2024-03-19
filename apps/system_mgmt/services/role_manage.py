from apps.core.exceptions.base_app_exception import BaseAppException
from apps.core.utils.keycloak_client import KeyCloakClient
from apps.system_mgmt.constants import APP_MODULE, ROLE
from apps.system_mgmt.models import OperationLog
from apps.system_mgmt.utils.keycloak import SupplementApi, get_realm_roles


class RoleManage(object):
    def __init__(self):
        self.keycloak_client = KeyCloakClient()

    def role_list(self):
        """角色列表"""
        result = get_realm_roles(self.keycloak_client.realm_client)
        return result

    def role_permissions(self, role_name):
        """获取角色权限"""
        client_id = self.keycloak_client.get_client_id()
        policies = self.keycloak_client.realm_client.get_client_authz_policies(client_id)
        policy_id = None
        for policy in policies:
            if policy["name"] == role_name:
                policy_id = policy["id"]
                break
        if not policy_id:
            return []
        permissions = SupplementApi(
            self.keycloak_client.realm_client.connection).get_permission_by_policy_id(client_id, policy_id)
        return [i["name"] for i in permissions]

    def role_create(self, data, operator):
        """创建角色，先创建角色再创建角色对应的策略"""
        self.keycloak_client.realm_client.create_realm_role(data, True)
        role_name = data["name"]
        role_info = self.keycloak_client.realm_client.get_realm_role(role_name=role_name)
        client_id = self.keycloak_client.get_client_id()
        policy_data = {
            "type": "role",
            "logic": "POSITIVE",
            "decisionStrategy": "UNANIMOUS",
            "name": role_name,
            "roles": [
                {
                    "id": role_info["id"]
                }
            ]
        }
        self.keycloak_client.realm_client.create_client_authz_role_based_policy(client_id, policy_data, True)

        OperationLog.objects.create(
            operator=operator,
            operate_type=OperationLog.ADD,
            operate_obj=role_name,
            operate_summary=f"创建角色！",
            app_module=APP_MODULE,
            obj_type=ROLE,
        )

        return role_info

    def role_delete(self, role_name, operator):
        """
            删除角色
            1.角色关联校验（校验角色是否被用户或者组织关联）
            2.移除角色绑定的权限
            3.删除角色
        """
        # 角色关联校验（校验角色是否被用户或者组织关联）
        groups = self.keycloak_client.realm_client.get_realm_role_groups(role_name)
        if groups:
            msg = "、".join([i["name"] for i in groups])
            raise BaseAppException(f"角色已被下列组织使用：{msg}！")

        users = self.keycloak_client.realm_client.get_realm_role_members(role_name)
        if users:
            msg = "、".join([i["username"] for i in users])
            raise BaseAppException(f"角色已被下列用户使用：{msg}！")

        # 移除角色权限
        client_id = self.keycloak_client.get_client_id()
        policies = self.keycloak_client.realm_client.get_client_authz_policies(client_id)
        policy_id = None
        for policy in policies:
            if policy["name"] == role_name:
                policy_id = policy["id"]
                break
        permissions = SupplementApi(
            self.keycloak_client.realm_client.connection).get_permission_by_policy_id(client_id, policy_id)
        supplement_api = SupplementApi(self.keycloak_client.realm_client.connection)
        for permission_info in permissions:
            del permission_info["config"]
            permission_policies = supplement_api.get_policies_by_permission_id(client_id, permission_info["id"])
            permission_policy_ids = [i["id"] for i in permission_policies]
            permission_policy_ids.remove(policy_id)
            permission_info.update(policies=permission_policy_ids, description="")
            supplement_api.update_permission(client_id, permission_info["id"], permission_info)

        # 删除角色
        role_info = self.keycloak_client.realm_client.get_realm_role(role_name=role_name)
        result = self.keycloak_client.realm_client.delete_realm_role(role_name)

        OperationLog.objects.create(
            operator=operator,
            operate_type=OperationLog.DELETE,
            operate_obj=role_info["name"],
            operate_summary=f"删除角色！",
            app_module=APP_MODULE,
            obj_type=ROLE,
        )
        return result

    def role_update(self, description, role_name, operator):
        """修改角色信息"""
        role_info = self.keycloak_client.realm_client.get_realm_role(role_name=role_name)

        self.keycloak_client.realm_client.update_realm_role(role_name, dict(description=description, name=role_name))

        mes = f"{role_info['description']}->{description}"

        OperationLog.objects.create(
            operator=operator,
            operate_type=OperationLog.MODIFY,
            operate_obj=role_info["name"],
            operate_summary=f"修改角色描述！[{str(mes)}]",
            app_module=APP_MODULE,
            obj_type=ROLE,
        )

    def role_set_permissions(self, data, role_name, operator):
        """设置角色权限"""
        client_id = self.keycloak_client.get_client_id()
        all_resources = self.keycloak_client.realm_client.get_client_authz_resources(client_id)
        resource_mapping = {i["name"]: i["_id"] for i in all_resources}
        # 获取角色映射的policy_id（角色与policy一对一映射）
        policies = self.keycloak_client.realm_client.get_client_authz_policies(client_id)
        policy_id = None
        for policy in policies:
            if policy["name"] == role_name:
                policy_id = policy["id"]
                break

        permission_name_set = set(data)

        # 判断是否需要初始化权限，若需要就进行资源与权限的初始化
        all_permissions = self.keycloak_client.realm_client.get_client_authz_permissions(client_id)
        need_init_permissions = permission_name_set - {i["name"] for i in all_permissions}
        for permission_name in need_init_permissions:
            resource_id = resource_mapping.get(permission_name)
            if not resource_id:
                resource = {
                    "name": permission_name,
                    "displayName": "",
                    "type": "",
                    "icon_uri": "",
                    "scopes": [],
                    "ownerManagedAccess": False,
                    "attributes": {}
                }
                resource_resp = self.keycloak_client.realm_client.create_client_authz_resource(client_id, resource, True)
                resource_id = resource_resp["_id"]
            permission = {
                "resources": [resource_id],
                "policies": [],
                "name": permission_name,
                "description": "",
                "decisionStrategy": "UNANIMOUS",
                "resourceType": ""
            }
            self.keycloak_client.realm_client.create_client_authz_resource_based_permission(client_id, permission, True)

        # 判断权限是否需要更新
        all_permissions = self.keycloak_client.realm_client.get_client_authz_permissions(client_id)
        supplement_api = SupplementApi(self.keycloak_client.realm_client.connection)
        for permission_info in all_permissions:

            permission_policies = supplement_api.get_policies_by_permission_id(client_id, permission_info["id"])
            permission_policy_ids = [i["id"] for i in permission_policies]

            # 需要绑定权限与角色的
            if permission_info["name"] in permission_name_set:
                if policy_id in permission_policy_ids:
                    continue
                permission_policy_ids.append(policy_id)

            # 需求解绑权限与角色的
            else:
                if policy_id not in permission_policy_ids:
                    continue
                permission_policy_ids.remove(policy_id)

            # 执行权限更新
            permission_info.update(policies=permission_policy_ids)
            supplement_api.update_permission(client_id, permission_info["id"], permission_info)

        OperationLog.objects.create(
            operator=operator,
            operate_type=OperationLog.MODIFY,
            operate_obj=role_name,
            operate_summary=f"修改角色权限！",
            app_module=APP_MODULE,
            obj_type=ROLE,
        )

    def role_add_user(self, role_id, user_id, operator):
        """为某个用户设置一个角色"""
        role = self.keycloak_client.realm_client.get_realm_role_by_id(role_id)
        self.keycloak_client.realm_client.assign_realm_roles(user_id, role)

        user_info = self.keycloak_client.realm_client.get_user(user_id)

        OperationLog.objects.create(
            operator=operator,
            operate_type=OperationLog.INCREASE,
            operate_obj=role["name"],
            operate_summary=f"对用户{user_info['username']}添加角色{role['name']}！",
            app_module=APP_MODULE,
            obj_type=ROLE,
        )

    def role_remove_user(self, role_id, user_id, operator):
        """移除角色下的某个用户"""
        role = self.keycloak_client.realm_client.get_realm_role_by_id(role_id)
        self.keycloak_client.realm_client.delete_realm_roles_of_user(user_id, role)

        user_info = self.keycloak_client.realm_client.get_user(user_id)

        OperationLog.objects.create(
            operator=operator,
            operate_type=OperationLog.REMOVE,
            operate_obj=role["name"],
            operate_summary=f"将用户{user_info['username']}的角色{role['name']}移除！",
            app_module=APP_MODULE,
            obj_type=ROLE,
        )

    def role_add_groups(self, data, role_id, operator):
        """为一些组添加某个角色"""
        role = self.keycloak_client.realm_client.get_realm_role_by_id(role_id)
        groups = []
        for group_id in data:
            self.keycloak_client.realm_client.assign_group_realm_roles(group_id, role)
            group = self.keycloak_client.realm_client.get_group(group_id)
            groups.append(group["name"])

        objs = [
            OperationLog(
                operator=operator,
                operate_type=OperationLog.INCREASE,
                operate_obj=role['name'],
                operate_summary=f"将角色[{role['name']}]加到用户组织[{group_name}]下",
                app_module=APP_MODULE,
                obj_type=ROLE,
            ) for group_name in groups
        ]
        OperationLog.objects.bulk_create(objs, batch_size=100)

    def role_remove_groups(self, data, role_id, operator):
        """将一些组移除某个角色"""
        role = self.keycloak_client.realm_client.get_realm_role_by_id(role_id)
        groups = []

        for group_id in data:
            self.keycloak_client.realm_client.delete_group_realm_roles(group_id, role)
            group = self.keycloak_client.realm_client.get_group(group_id)
            groups.append(group["name"])

        objs = [
            OperationLog(
                operator=operator,
                operate_type=OperationLog.REMOVE,
                operate_obj=role['name'],
                operate_summary=f"将角色[{role['name']}]从用户组织[{group_name}]移除",
                app_module=APP_MODULE,
                obj_type=ROLE,
            ) for group_name in groups
        ]
        OperationLog.objects.bulk_create(objs, batch_size=100)

    def role_groups(self, role_name):
        """获取角色关联的组"""
        result = self.keycloak_client.realm_client.get_realm_role_groups(role_name)
        return result
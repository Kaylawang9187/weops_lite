# Generated by Django 4.2.7 on 2024-06-27 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cmdb_mgmt", "0005_instancepermission_resource_type_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="RoleCredentialPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "model_id",
                    models.CharField(
                        db_index=True, max_length=100, verbose_name="模型ID"
                    ),
                ),
                (
                    "inst_id",
                    models.IntegerField(
                        db_index=True, max_length=100, verbose_name="凭据实例ID"
                    ),
                ),
                (
                    "role",
                    models.CharField(db_index=True, max_length=100, verbose_name="角色"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserCredentialPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "model_id",
                    models.CharField(
                        db_index=True, max_length=100, verbose_name="模型ID"
                    ),
                ),
                (
                    "inst_id",
                    models.IntegerField(
                        db_index=True, max_length=100, verbose_name="凭据实例ID"
                    ),
                ),
                (
                    "user",
                    models.CharField(db_index=True, max_length=100, verbose_name="用户"),
                ),
            ],
        ),
    ]
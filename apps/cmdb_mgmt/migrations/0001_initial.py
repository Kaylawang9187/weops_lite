# Generated by Django 4.2.7 on 2024-04-22 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InstancePermission",
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
                    "created_by",
                    models.CharField(default="", max_length=32, verbose_name="创建者"),
                ),
                (
                    "updated_by",
                    models.CharField(default="", max_length=32, verbose_name="更新者"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="创建时间"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="修改时间"),
                ),
                (
                    "role_id",
                    models.CharField(
                        db_index=True, max_length=100, verbose_name="角色ID"
                    ),
                ),
                (
                    "model_id",
                    models.CharField(
                        db_index=True, max_length=100, verbose_name="模型ID"
                    ),
                ),
                ("conditions", models.JSONField(default=list, verbose_name="条件列表")),
            ],
            options={
                "verbose_name": "时间相关字段",
                "abstract": False,
            },
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0002_logentry_remove_auto_add'),
    ]

    # 没有数据库变化; 为action_flag添加选项。
    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='action_flag',
            field=models.PositiveSmallIntegerField(
                choices=[(1, 'Addition'), (2, 'Change'), (3, 'Deletion')],
                verbose_name='action flag',
            ),
        ),
    ]

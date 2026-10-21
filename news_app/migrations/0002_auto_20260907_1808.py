from django.db import migrations


def create_roles_and_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    roles = ['Reader', 'Journalist', 'Editor']
    for role in roles:
        Group.objects.get_or_create(name=role)


class Migration(migrations.Migration):

    dependencies = [
        ('news_app', '0001_initial'),  # Ensures this runs after your initial migration
    ]

    operations = [
        migrations.RunPython(create_roles_and_groups),
    ]

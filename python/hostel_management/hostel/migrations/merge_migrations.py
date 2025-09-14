from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0002_add_is_paid_field'),
        ('hostel', 'add_is_paid_field'),
        ('hostel', 'ensure_is_paid_field'),
    ]

    operations = [
        # No operations needed, this migration just merges the dependency tree
    ]
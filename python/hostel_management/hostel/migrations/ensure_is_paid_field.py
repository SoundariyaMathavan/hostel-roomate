from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0007_notification'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE hostel_booking ADD COLUMN is_paid boolean DEFAULT 0;
            """,
            reverse_sql="""
            -- No reverse operation needed
            SELECT 1;
            """
        ),
    ]
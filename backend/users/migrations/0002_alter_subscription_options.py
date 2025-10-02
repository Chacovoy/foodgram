from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='unique_subscription',
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(
                check=~Q(user=models.F('author')),
                name='prevent_self_subscription'
            ),
        ),
    ]


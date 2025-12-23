from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models.main import Task
from core.serializers.main import BlockSerializer


class BlockSerializerValidationTests(TestCase):
	def test_rejects_end_date_before_start_date(self):
		User = get_user_model()
		user = User.objects.create_user(username="u1", password="pw")

		task = Task.objects.create(user=user, title="T", description="", estimated_minutes=0)

		start = timezone.now()
		end = start - timedelta(minutes=5)

		serializer = BlockSerializer(
			data={
				"task": task.id,
				"start_date": start,
				"end_date": end,
				"done": False,
			}
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn("end_date", serializer.errors)

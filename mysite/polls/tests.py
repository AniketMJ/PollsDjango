import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Global Function.
def create_question(question_text, days):
	"""
	Create a question with the given `question_text` and published the
	given number of `days` offset to now (negative for questions published
	in the past, positive for questions that have yet to be published).
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)

# Create your tests here.
class QuestionModelTests(TestCase):

	def test_was_published_recently_with_future_question(self):
		"""
		was_published_recently() returns False for the questions whose 'pub_date'
		is in the future.
		"""
		time = timezone.now() + datetime.timedelta(days=30)
		future_que = Question(pub_date=time)
		self.assertIs(future_que.was_published_recently(), False)

	def test_was_published_recently_with_old_question(self):
		"""
		was_published_recently() returns False for the questions whose 'pub_date'
		is older than 1 day.
		"""
		time = timezone.now() - datetime.timedelta(days=1, seconds=1)
		old_que = Question(pub_date=time)
		self.assertIs(old_que.was_published_recently(), False)

	def test_was_published_recently_with_recent_question(self):
		"""
		was_published_recently() returns True for the questions whose 'pub_date'
		is within the last day.
		"""
		time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
		recent_que = Question(pub_date=time)
		self.assertIs(recent_que.was_published_recently(), True)

class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		"""
		If no questions exist, an appropriate message is displayed.
		"""
		response = self.client.get(reverse('polls:polls-index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No polls are available.')	# response.content
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_past_question(self):
		"""
		Questions with a pub_date in the past are displayed on the
		index page.
		"""
		# create_question('Past Question.', -30)
		que = create_question(question_text='Past Question.', days=-30)
		que.choice_set.create(choice_text='A Choice.', votes=10)
		response = self.client.get(reverse('polls:polls-index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past Question.>']
		)

	def test_future_question(self):
		"""
		Questions with a pub_date in the future aren't displayed on
		the index page.
		"""
		que = create_question(question_text='Future Question.', days=30)
		que.choice_set.create(choice_text='A Choice.', votes=10)
		response = self.client.get(reverse('polls:polls-index'))
		self.assertContains(response, 'No polls are available.')
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_future_question_and_past_question(self):
		"""
		Even if both past and future questions exist, only past questions
		are displayed.
		"""
		que1 = create_question(question_text='Past Question.', days=-30)
		que2 = create_question(question_text='Future Question.', days=30)
		que1.choice_set.create(choice_text='Choice 1.', votes=10)
		que2.choice_set.create(choice_text='Choice 2.', votes=20)
		response = self.client.get(reverse('polls:polls-index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past Question.>']
		)

	def test_two_past_questions(self):
		"""
		The questions index page may display multiple questions.
		"""
		que1 = create_question(question_text='Past Question 1.', days=-30)
		que2 = create_question(question_text='Past Question 2.', days=-5)
		que1.choice_set.create(choice_text='Choice 1.', votes=10)
		que2.choice_set.create(choice_text='Choice 2.', votes=10)
		response = self.client.get(reverse('polls:polls-index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past Question 2.>', '<Question: Past Question 1.>']
		)

	def test_que_with_choice(self):
		que = create_question('A Question with choice.', 0)
		que.choice_set.create(choice_text='A Choice.', votes=10)
		url = reverse('polls:polls-index')
		response = self.client.get(url)
		self.assertContains(response, que.question_text)

	def test_que_without_choice(self):
		que = create_question('A Question without choice.', -4)
		url = reverse('polls:polls-index')
		response = self.client.get(url)
		self.assertContains(response, 'No polls are available.')

class QuestionDetailViewTests(TestCase):
	def test_future_question(self):
		future_que = create_question(question_text='Future Question.', days=5)
		future_que.choice_set.create(choice_text='A Choice.', votes=10)
		url = reverse('polls:polls-detail', args=(future_que.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_past_question(self):
		past_que = create_question('Past Question.', -5)
		past_que.choice_set.create(choice_text='A Choice.', votes=10)
		# url = reverse('polls:polls-detail', kwargs={'pk': past_que.id})
		url = reverse('polls:polls-detail', args=(past_que.id,))
		response = self.client.get(url)
		self.assertContains(response, past_que.question_text)

	def test_past_question_with_choices(self):
		past_que = create_question('Past Question.', -5)
		past_que.choice_set.create(choice_text='A Choice.', votes=10)
		url = reverse('polls:polls-detail', args=(past_que.id,))
		response = self.client.get(url)
		self.assertContains(response, past_que.question_text)
		self.assertContains(response, past_que.choice_set.first())


class QuestionResultsViewTests(TestCase):
	def test_future_question(self):
		future_que = create_question('Future Question.', 30)
		future_que.choice_set.create(choice_text='A Choice.', votes=10)
		url = reverse('polls:polls-results', args=(future_que.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_past_question(self):
		past_que = create_question('Past Question.', -30)
		past_que.choice_set.create(choice_text='A Choice.', votes=10)
		url = reverse('polls:polls-results', args=(past_que.id,))
		response = self.client.get(url)
		self.assertContains(response, past_que.question_text)

	def test_past_que_with_choices(self):
		past_que = create_question('Past Question.', -10)
		past_que.choice_set.create(choice_text='Test Choice 1.', votes=5)
		url = reverse('polls:polls-results', args=(past_que.id,))
		response = self.client.get(url)
		self.assertContains(response, past_que.question_text)
		# self.assertContains(response, past_que.choice_set.get(pk=1))
		self.assertContains(response, past_que.choice_set.first())
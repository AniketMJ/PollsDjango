from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
# from django.template import loader

from .models import Question, Choice


def home(request):
    return render(request, 'home.html')


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    # default context_object_name = <model>_list i.e. question_list
    context_object_name = 'latest_question_list'
    # queryset = Question.objects.order_by('-pub_date')[:5]

    def get_queryset(self):
        """Returns the last five published questions."""
        # return Question.objects.order_by('-pub_date')[:5]
        # return Question.objects.filter(
        # 		pub_date__lte=timezone.now() & choice__choice_text_exact=None
        # 	).order_by('-pub_date')[:5]

        # adding more filters is not allowed,
        # since that does not translate well into SQL and it would not have a clear meaning either.
        filtered_que = Question.objects.filter(
            pub_date__lte=timezone.now()
        ).exclude(choice__choice_text__exact=None)
        return filtered_que.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    # for detail view the 'question' variable is provided automatically - since we are using a django model 'Question'
    # django is able to determine an appropriate name for the context variable.
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        # adding more filters is not allowed,
        # since that does not translate well into SQL and it would not have a clear meaning either.
        filtered_que = Question.objects.filter(
            pub_date__lte=timezone.now()
        ).exclude(choice__choice_text__exact=None)
        return filtered_que.order_by('-pub_date')


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        filtered_que = Question.objects.filter(
            pub_date__lte=timezone.now()
        ).exclude(choice__choice_text__exact=None)
        return filtered_que.order_by('-pub_date')


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        # print(question.question_text)
        # print("question.choice_set.all(): ", question.choice_set.all())
        # print("request.POST['choice']:",request.POST['choice'])	# will print value of that choice e.g. 1,2,etc.
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        # print('selected_choice:', selected_choice)
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        context = {
            'question': question,
            'error_message': "You didn't select a choice.",
        }
        return render(request, 'polls/detail.html', context)
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:polls-results', args=(question.id,)))

# Create your views here.
# def index(request):
# 	latest_question_list = Question.objects.order_by('-pub_date')[:5]	# -pub_date means in descending order or you can say the latest ones are first
# 	context = {
# 		'latest_question_list': latest_question_list,
# 	}

# 	return render(request, 'polls/index.html', context)

# def index(requset):
# 	template = loader.get_template('polls/index.html')
# 	# output = ', '.join([q.question_text for q in latest_question_list])
# 	# return HttpResponse("<h1>"+output+"</h1>")
# 	return HttpResponse(template.render(context, request))

# def detail(request, question_id):
# 	question = get_object_or_404(Question, pk=question_id)
# 	# question = get_list_or_404(Question, pk=question_id)
# 	return render(request, 'polls/detail.html', {'question':question})

# def detail(request, question_id):
# 	try:
# 		question = Question.objects.get(pk=question_id)
# 	except Question.DoesNotExist:
# 		# return HttpResponse("Question does not exist!")
# 		raise Http404("Question does not exist!")
# 	else:
# 		context = {'question': question}
# 	return render(request, 'polls/detail.html', context)

# def results(request, question_id):
# 	question = get_object_or_404(Question, pk=question_id)
# 	context = {
# 		'question': question,
# 	}
# 	return render(request, 'polls/results.html', context)

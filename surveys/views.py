from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, reverse
from django.views import View
import json
import pandas as pd

from .models import Question
from .diagnoseProcess import DiagnoseProcess


class InitialView(View):
    template_name = 'surveys/initial.html'

    def render_invalid_post(self, request, error_message):
        return render(request,
                      self.template_name, {
                          'error_message': error_message
                      },
                      status=400)

    def get(self, request):
        return render(request, self.template_name, {'symptom_list': json.dumps(list(DiagnoseProcess.weight_matrix.columns))})

    def post(self, request):
        selected = request.POST.get('selected', '')
        request.session['init_symptom'] = selected
        return redirect(reverse('index'))


class QuestionView(View):
    template_name = 'surveys/index.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dp = DiagnoseProcess()

    def render_invalid_post(self, request, question, error_message):
        return render(request,
                      self.template_name, {
                          'question': question,
                          'error_message': error_message
                      },
                      status=400)

    def get(self, request):
        selected = request.session.get('init_symptom')
        self.dp.asked.append(selected)
        self.dp.positive.append(selected)
        self.dp.reduce()
        question = self.dp.next_symptom()
        return render(request, self.template_name, {'question': question})

    def post(self, request):
        choice_id = request.POST.get('choice', 0)
        question_id = request.POST.get('question-id', 0)

        if (question_id == 0):
            # An invalid question id was sent, something is not right redirect to home
            # TODO: Log that something is wrong
            return redirect(reverse('index'))

        try:
            question = Question.objects.get(pk=question_id)
        except ObjectDoesNotExist:
            # The question might have been deleted before a submit
            messages.add_message(
                request, messages.WARNING,
                'We are sorry, the question is no longer aviable, try this one'
            )
            return redirect(reverse('index'))

        if (choice_id == 0):
            # A choice was not selected
            return self.render_invalid_post(request, question,
                                            'Please select a choice')

        try:
            choice = question.choices.get(pk=choice_id)
        except ObjectDoesNotExist:
            return self.render_invalid_post(request, question,
                                            'Please select a valid choice')

        # If it is a guest user
        if (request.user.is_anonymous):
            # Make sure session exist
            if not request.session.session_key:
                request.session.save()

            choice.answers.create(session_key=request.session.session_key)
            messages.add_message(request, messages.SUCCESS,
                                 'Your answer was saved')
        else:
            # If it's a register user, requirements does not specify what to do
            messages.add_message(
                request, messages.INFO, 'You are a registered user, '
                'surveys are only for guest users right now '
                '<a href="/admin/logout/">log out</a> if you want to add answers'
            )

        return redirect(reverse('index'))


def restart(request):
    request.session.flush()
    messages.add_message(request, messages.INFO, 'Here we go again! 🚀')
    return redirect(reverse('index'))


def about(request):
    return render(request, 'surveys/about.html')

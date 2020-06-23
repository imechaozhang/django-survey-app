from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, reverse
from django.views import View
import json
import pandas as pd
from django.utils import timezone

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
        request.session['asked'] = [selected]
        request.session['positive'] = [selected]
        return redirect(reverse('index'))


class QuestionView(View):
    template_name = 'surveys/index.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dp = DiagnoseProcess()

    def get(self, request):
        asked = request.session.get('asked')
        positive = request.session.get('positive')
        self.dp.asked = asked
        self.dp.positive = positive
        self.dp.reduce()

        if self.dp.time_to_conclude():
            diagnosis = self.dp.check()
            request.session['diagnosis'] = diagnosis
            request.session.flush()
            messages.add_message(request, messages.INFO, 'Here we go again! 🚀')
            return redirect(reverse('initial'))

        symptom = self.dp.next_symptom()
        question = Question(
            question_text='Are you suffering from ' + str(symptom) + '? If yes, how severe is it?' + str(request.session.get('asked')),
            pub_date=timezone.now())
        question.save()
        for t in ['Severe', 'Moderate', 'light', 'No']:
            question.choices.create(choice_text=t)
        return render(request, self.template_name, {'question': question})

    def post(self, request):
        asked = request.session.get('asked')
        positive = request.session.get('positive')
        self.dp.asked = asked
        self.dp.positive = positive
        self.dp.reduce()
        symptom = self.dp.next_symptom()

        choice = request.POST.get('choice', '')
        request.session['asked'].append(symptom)
        if choice in ['Severe', 'Moderate', 'light']:
            request.session['positive'].append(symptom)
        request.session.save()
        messages.add_message(request, messages.INFO, 'post')
        return redirect(reverse('index'))


def restart(request):
    request.session.flush()
    messages.add_message(request, messages.INFO, 'Here we go again! 🚀')
    return redirect(reverse('index'))


def about(request):
    return render(request, 'surveys/about.html')

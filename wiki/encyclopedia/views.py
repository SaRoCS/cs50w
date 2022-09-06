from django.shortcuts import render
from . import util
from markdown2 import Markdown
from django.http import HttpResponseRedirect
from django.urls import reverse
import re
from django import forms
import random


class NewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name')
        super(NewForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.CharField(label= '', widget=forms.TextInput({
        'name' : 'title',
        'placeholder' : 'Title of Page',
        'value' : name
    }))
class NewTextArea(forms.Form):
    def __init__(self, *args, **kwargs):
        page = kwargs.pop('page')
        super(NewTextArea, self).__init__(*args, **kwargs)
        self.fields['content'] = forms.CharField(label = '', widget=forms.Textarea({
            'name' : 'content',
            'id' : 'content',
            'class' : 'new_page',
            'placeholder' : "Page Markdown" 
        }), initial = page)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def load(request, title):
    if not request.GET :
        entry = util.get_entry(title)
        if not entry:
            message = "Page not found."
            return render(request, "encyclopedia/error.html", {
                'message' : message
            })
        else:
            markdowner = Markdown()
            page = markdowner.convert(entry)
            return render(request, 'encyclopedia/entry.html', {
                "page" : page,
                "title" : title
            })
    else:
        form = NewForm(name = title)
        content = util.get_entry(title)
        textarea = NewTextArea(page = content)
        return render(request, "encyclopedia/edit.html",{
            'textarea' : textarea,
            'content' : content,
            'form' : form
        })
        

def search(request):
    search = request.GET['q']
    if not util.get_entry(search):
        results = []
        entries = util.list_entries()
        for entry in entries:
            if re.search(f".*{search}.*", entry, re.IGNORECASE):
                results.append(entry)
        return render(request, 'encyclopedia/results.html', {
            "results" : results
        })
    else:
        return HttpResponseRedirect(f"/wiki/{search}")

def create(request):
    if request.method == "POST":
        titleF = NewForm(request.POST, name=request.POST['title'])
        contentF = NewTextArea(request.POST, page=request.POST['content'])
        if titleF.is_valid() and contentF.is_valid():
            title = titleF.cleaned_data['title']
            content = contentF.cleaned_data['content']

            entries = util.list_entries()
            if title in entries:
                return render(request, 'encyclopedia/error.html', {
                    'message' : "Page already exists."
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(f'/wiki/{title}')
        else:
            return render(request, 'encyclopedia/create.html', {
                'form' : titleF,
                'textarea' : contentF,
            })
    else:
        form = NewForm(name='')
        textarea = NewTextArea(page=None)
        return render(request, "encyclopedia/create.html", {
            "form" : form,
            'textarea' : textarea
        }) 

def edit(request):
    util.save_entry(request.POST['title'], request.POST['content'])
    return HttpResponseRedirect(f'/wiki/{request.POST["title"]}')

def randomPage(request):
    entries = util.list_entries()
    entry = random.randint(0,len(entries) - 1)
    title = entries[entry]
    return HttpResponseRedirect(f'/wiki/{title}')
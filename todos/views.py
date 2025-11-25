from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from .models import Todo
from .forms import TodoForm

class TodoListView(ListView):
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_resolved=False)
        elif status == 'resolved':
            queryset = queryset.filter(is_resolved=True)
        return queryset

class TodoCreateView(View):
    def get(self, request):
        form = TodoForm()
        return render(request, 'todos/todo_form.html', {'form': form, 'action': 'Create'})

    def post(self, request):
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
        return render(request, 'todos/todo_form.html', {'form': form, 'action': 'Create'})

class TodoUpdateView(View):
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        form = TodoForm(instance=todo)
        return render(request, 'todos/todo_form.html', {'form': form, 'action': 'Edit', 'todos': todo})

    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
        return render(request, 'todos/todo_form.html', {'form': form, 'action': 'Edit', 'todos': todo})

class TodoDeleteView(View):
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        todo.delete()
        return redirect('todo_list')

class TodoToggleResolveView(View):
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        todo.is_resolved = not todo.is_resolved
        todo.save()
        return redirect('todo_list')

from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from .models import Todo
from .forms import TodoForm

class TodoModelTest(TestCase):
    def setUp(self):
        self.todo = Todo.objects.create(
            title="Test TODO",
            description="Test description",
            due_date=date.today() + timedelta(days=7)
        )

    def test_create_todo_with_all_fields(self):
        todo = Todo.objects.create(
            title="Complete TODO",
            description="This is a complete TODO",
            due_date=date.today() + timedelta(days=5)
        )
        self.assertEqual(todo.title, "Complete TODO")
        self.assertEqual(todo.description, "This is a complete TODO")
        self.assertIsNotNone(todo.due_date)
        self.assertFalse(todo.is_resolved)

    def test_create_todo_with_only_title(self):
        todo = Todo.objects.create(title="Minimal TODO")
        self.assertEqual(todo.title, "Minimal TODO")
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.is_resolved)

    def test_todo_str_method(self):
        self.assertEqual(str(self.todo), "Test TODO")

    def test_todo_default_is_unresolved(self):
        todo = Todo.objects.create(title="New TODO")
        self.assertFalse(todo.is_resolved)

    def test_todo_timestamps_are_set(self):
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)

    def test_is_overdue_returns_true_when_past_due(self):
        todo = Todo.objects.create(
            title="Overdue TODO",
            due_date=date.today() - timedelta(days=1),
            is_resolved=False
        )
        self.assertTrue(todo.is_overdue())

    def test_is_overdue_returns_false_when_no_due_date(self):
        todo = Todo.objects.create(title="No due date TODO")
        self.assertFalse(todo.is_overdue())

    def test_is_overdue_returns_false_when_resolved(self):
        todo = Todo.objects.create(
            title="Resolved TODO",
            due_date=date.today() - timedelta(days=1),
            is_resolved=True
        )
        self.assertFalse(todo.is_overdue())

    def test_is_overdue_returns_false_when_due_in_future(self):
        todo = Todo.objects.create(
            title="Future TODO",
            due_date=date.today() + timedelta(days=5)
        )
        self.assertFalse(todo.is_overdue())

    def test_todo_ordering(self):
        todo1 = Todo.objects.create(title="First TODO")
        todo2 = Todo.objects.create(title="Second TODO")
        todo3 = Todo.objects.create(title="Third TODO")

        todos = Todo.objects.all()

        self.assertEqual(todos[0].title, "Third TODO")
        self.assertEqual(todos[1].title, "Second TODO")
        self.assertEqual(todos[2].title, "First TODO")

class TodoFormTest(TestCase):
    def test_form_with_valid_data(self):
        form_data = {
            'title': 'Test TODO',
            'description': 'Test description',
            'due_date': date.today() + timedelta(days=7)
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_empty_title(self):
        form_data = {
            'title': '',
            'description': 'Test description'
        }
        form = TodoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_accepts_missing_description(self):
        form_data = {
            'title': 'Test TODO',
            'description': ''
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_accepts_missing_due_date(self):
        form_data = {
            'title': 'Test TODO',
            'description': 'Test description'
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_has_correct_fields(self):
        form = TodoForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('due_date', form.fields)
        self.assertNotIn('is_resolved', form.fields)

class TodoListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('todo_list')

        self.todo1 = Todo.objects.create(
            title="Active TODO 1",
            is_resolved=False
        )
        self.todo2 = Todo.objects.create(
            title="Resolved TODO 1",
            is_resolved=True
        )
        self.todo3 = Todo.objects.create(
            title="Active TODO 2",
            is_resolved=False
        )

    def test_can_access_todo_list_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_list.html')

    def test_can_see_all_todos(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Active TODO 1")
        self.assertContains(response, "Resolved TODO 1")
        self.assertContains(response, "Active TODO 2")

    def test_filter_shows_only_active_todos(self):
        response = self.client.get(self.url + '?status=active')
        self.assertContains(response, "Active TODO 1")
        self.assertContains(response, "Active TODO 2")
        self.assertNotContains(response, "Resolved TODO 1")

    def test_filter_shows_only_resolved_todos(self):
        response = self.client.get(self.url + '?status=resolved')
        self.assertContains(response, "Resolved TODO 1")
        self.assertNotContains(response, "Active TODO 1")
        self.assertNotContains(response, "Active TODO 2")

    def test_shows_newest_first(self):
        response = self.client.get(self.url)
        todos = response.context['todos']
        self.assertEqual(todos[0].title, "Active TODO 2")
        self.assertEqual(todos[1].title, "Resolved TODO 1")
        self.assertEqual(todos[2].title, "Active TODO 1")

    def test_empty_todo_list(self):
        Todo.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "No TODOs found")

class TodoCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('todo_create')

    def test_can_access_create_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')

    def test_can_create_todo_with_valid_data(self):
        data = {
            'title': 'New TODO',
            'description': 'New description',
            'due_date': date.today() + timedelta(days=7)
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('todo_list'))

        self.assertEqual(Todo.objects.count(), 1)
        todo = Todo.objects.first()
        self.assertEqual(todo.title, 'New TODO')
        self.assertEqual(todo.description, 'New description')

    def test_shows_error_when_title_missing(self):
        data = {
            'title': '',
            'description': 'Description without title'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Todo.objects.count(), 0)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_can_create_todo_without_due_date(self):
        data = {
            'title': 'TODO without due date',
            'description': 'This has no deadline'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 1)
        todo = Todo.objects.first()
        self.assertIsNone(todo.due_date)

    def test_can_create_todo_without_description(self):
        data = {
            'title': 'TODO without description',
            'due_date': date.today() + timedelta(days=3)
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 1)
        todo = Todo.objects.first()
        self.assertEqual(todo.description, '')

class TodoUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Original Title",
            description="Original description",
            due_date=date.today() + timedelta(days=5)
        )
        self.url = reverse('todo_update', kwargs={'pk': self.todo.pk})

    def test_can_access_edit_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')

    def test_form_is_prefilled(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Original Title")
        self.assertContains(response, "Original description")

    def test_can_update_todo(self):
        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'due_date': date.today() + timedelta(days=10)
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('todo_list'))

        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title')
        self.assertEqual(self.todo.description, 'Updated description')

    def test_error_when_editing_nonexistent_todo(self):
        url = reverse('todo_update', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_error_with_invalid_data(self):
        data = {
            'title': '',
            'description': 'Updated description'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Original Title')

class TodoDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(title="TODO to delete")
        self.url = reverse('todo_delete', kwargs={'pk': self.todo.pk})

    def test_can_delete_todo(self):
        self.assertEqual(Todo.objects.count(), 1)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('todo_list'))

        self.assertEqual(Todo.objects.count(), 0)

    def test_todo_is_removed_from_database(self):
        todo_id = self.todo.pk
        self.client.post(self.url)

        with self.assertRaises(Todo.DoesNotExist):
            Todo.objects.get(pk=todo_id)

    def test_error_when_deleting_nonexistent_todo(self):
        url = reverse('todo_delete', kwargs={'pk': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

class TodoToggleResolveViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.unresolved_todo = Todo.objects.create(
            title="Unresolved TODO",
            is_resolved=False
        )
        self.resolved_todo = Todo.objects.create(
            title="Resolved TODO",
            is_resolved=True
        )

    def test_can_mark_unresolved_as_resolved(self):
        url = reverse('todo_toggle', kwargs={'pk': self.unresolved_todo.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.unresolved_todo.refresh_from_db()
        self.assertTrue(self.unresolved_todo.is_resolved)

    def test_can_mark_resolved_as_unresolved(self):
        url = reverse('todo_toggle', kwargs={'pk': self.resolved_todo.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.resolved_todo.refresh_from_db()
        self.assertFalse(self.resolved_todo.is_resolved)

    def test_redirects_to_todo_list(self):
        url = reverse('todo_toggle', kwargs={'pk': self.unresolved_todo.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('todo_list'))

    def test_error_when_toggling_nonexistent_todo(self):
        url = reverse('todo_toggle', kwargs={'pk': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

class URLTest(TestCase):
    def test_todo_list_url_resolves(self):
        url = reverse('todo_list')
        self.assertEqual(url, '/todos/')

    def test_todo_create_url_resolves(self):
        url = reverse('todo_create')
        self.assertEqual(url, '/todos/create/')

    def test_todo_update_url_resolves(self):
        url = reverse('todo_update', kwargs={'pk': 1})
        self.assertEqual(url, '/todos/edit/1/')

    def test_todo_delete_url_resolves(self):
        url = reverse('todo_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/todos/delete/1/')

    def test_todo_toggle_url_resolves(self):
        url = reverse('todo_toggle', kwargs={'pk': 1})
        self.assertEqual(url, '/todos/toggle/1/')

class IntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_complete_todo_lifecycle(self):
        create_data = {
            'title': 'Integration Test TODO',
            'description': 'Testing the complete workflow',
            'due_date': date.today() + timedelta(days=7)
        }
        response = self.client.post(reverse('todo_create'), create_data)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('todo_list'))
        self.assertContains(response, 'Integration Test TODO')

        todo = Todo.objects.first()
        update_data = {
            'title': 'Updated Integration TODO',
            'description': 'Updated description',
            'due_date': date.today() + timedelta(days=10)
        }
        response = self.client.post(
            reverse('todo_update', kwargs={'pk': todo.pk}),
            update_data
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('todo_list'))
        self.assertContains(response, 'Updated Integration TODO')
        self.assertNotContains(response, 'Integration Test TODO')

        response = self.client.post(
            reverse('todo_delete', kwargs={'pk': todo.pk})
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Todo.objects.count(), 0)

    def test_filter_and_toggle_workflow(self):
        Todo.objects.create(title="TODO 1", is_resolved=False)
        Todo.objects.create(title="TODO 2", is_resolved=False)
        Todo.objects.create(title="TODO 3", is_resolved=True)

        response = self.client.get(reverse('todo_list') + '?status=active')
        self.assertContains(response, "TODO 1")
        self.assertContains(response, "TODO 2")
        self.assertNotContains(response, "TODO 3")

        todo1 = Todo.objects.get(title="TODO 1")
        self.client.post(reverse('todo_toggle', kwargs={'pk': todo1.pk}))

        response = self.client.get(reverse('todo_list') + '?status=active')
        self.assertNotContains(response, "TODO 1")
        self.assertContains(response, "TODO 2")

        response = self.client.get(reverse('todo_list') + '?status=resolved')
        self.assertContains(response, "TODO 1")
        self.assertContains(response, "TODO 3")

    def test_overdue_detection_workflow(self):
        overdue_todo = Todo.objects.create(
            title="Overdue TODO",
            due_date=date.today() - timedelta(days=1),
            is_resolved=False
        )

        self.assertTrue(overdue_todo.is_overdue())

        self.client.post(reverse('todo_toggle', kwargs={'pk': overdue_todo.pk}))

        overdue_todo.refresh_from_db()
        self.assertFalse(overdue_todo.is_overdue())
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Patient


class RegistrationViewTests(TestCase):
    def test_get_displays_registration_form(self):
        response = self.client.get('/patients/index/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register Here')
        self.assertIn('form', response.context)

    def test_invalid_post_keeps_registration_form_errors(self):
        response = self.client.post('/patients/index/', {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertTrue(response.context['form'].errors)

    def test_successful_registration_redirects_to_dashboard(self):
        response = self.client.post('/patients/index/')

        self.assertRedirects(response, '/patients/dashboard/')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        dashboard_response = self.client.get('/patients/dashboard/')
        self.assertEqual(dashboard_response.status_code, 200)


class PatientPageViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='patient', password='test-password')
        self.client.force_login(user)
        self.patient = Patient.objects.create(
            patient_id='PAT-0001',
            name='Test Patient',
            age=30,
            gender='Other',
            address='Test address',
            phone_number='5551234567',
            email='patient@example.com',
        )

    def test_registered_patient_pages_render(self):
        pages = (
            reverse('bookappointment'),
            reverse('Profile'),
            reverse('patient_detail', args=[self.patient.pk]),
        )

        for page in pages:
            with self.subTest(page=page):
                self.assertEqual(self.client.get(page).status_code, 200)

    def test_dashboard_shows_patient_actions_and_filters_search(self):
        Patient.objects.create(
            patient_id='PAT-0002',
            name='Another Person',
            age=40,
            gender='Other',
            address='Other address',
            phone_number='5559876543',
            email='another@example.com',
        )

        response = self.client.get(reverse('dashboard'), {'q': 'Test'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['patients']), [self.patient])
        self.assertContains(response, reverse('add_patient'))
        self.assertContains(response, reverse('patient_detail', args=[self.patient.pk]))
        self.assertContains(response, reverse('edit_patient', args=[self.patient.pk]))
        self.assertContains(response, reverse('delete_patient', args=[self.patient.pk]))
        self.assertContains(response, 'name="q"')

    def test_patient_can_be_added_edited_and_deleted(self):
        add_url = reverse('add_patient')
        add_page = self.client.get(add_url)
        self.assertEqual(add_page.status_code, 200)
        self.assertContains(add_page, '<input type="text" name="gender"')
        patient_data = {
            'patient_id': 'PAT-0002',
            'name': 'New Patient',
            'age': 25,
            'gender': 'Other',
            'address': 'New address',
            'phone_number': '5551112222',
            'email': 'new@example.com',
        }

        response = self.client.post(add_url, patient_data)
        self.assertRedirects(response, reverse('dashboard'))
        patient = Patient.objects.get(patient_id='PAT-0002')

        edit_url = reverse('edit_patient', args=[patient.pk])
        self.assertEqual(self.client.get(edit_url).status_code, 200)
        response = self.client.post(edit_url, {
            **patient_data,
            'name': 'Updated Patient',
        })
        self.assertRedirects(response, reverse('dashboard'))
        patient.refresh_from_db()
        self.assertEqual(patient.name, 'Updated Patient')

        response = self.client.post(reverse('delete_patient', args=[patient.pk]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Patient.objects.filter(pk=patient.pk).exists())
